"""L61: config-driven candidate rig for mining new steering targets.

Instead of hand-cloning a fetch + proxy + run triple per candidate (the L54/
L59/L60 pattern), this registers candidates as data + a compositional proxy,
so a new intrinsic-property candidate is a few lines here plus one fetch and
one run invocation. Every candidate goes through the identical L50 6-criteria
harness in l61_run.py.

A candidate is admissible only if (L56) its label is intrinsic to the single
sequence. Each is a binary UniProt-keyword contrast (has-property vs control),
which is the cross-protein regime L54 showed the difference-of-means vector
needs. The offline screen (l61_candidate_screen results) reports each one's
group separation, which predicts steerability before any GPU work.
"""
import re
from typing import Callable, Dict

CANON = frozenset("ACDEFGHIKLMNPQRSTVWY")
KYTE_DOOLITTLE = {
    "I": 4.5, "V": 4.2, "L": 3.8, "F": 2.8, "C": 2.5, "M": 1.9, "A": 1.8,
    "G": -0.4, "T": -0.7, "S": -0.8, "W": -0.9, "Y": -1.3, "P": -1.6,
    "H": -3.2, "E": -3.5, "Q": -3.5, "D": -3.5, "N": -3.5, "K": -3.9, "R": -4.5,
}


def _frac(seq: str, residues: frozenset) -> float:
    if not seq:
        raise ValueError("empty sequence")
    return sum(1 for c in seq if c in residues) / len(seq)


def cys_frac(seq: str) -> float:
    return _frac(seq, frozenset("C"))


def ch_frac(seq: str) -> float:
    return _frac(seq, frozenset("CH"))


def his_frac(seq: str) -> float:
    return _frac(seq, frozenset("H"))


def kr_frac(seq: str) -> float:
    return _frac(seq, frozenset("KR"))


def de_frac(seq: str) -> float:
    return _frac(seq, frozenset("DE"))


def nterm_hydropathy(seq: str) -> float:
    vals = [KYTE_DOOLITTLE[c] for c in seq[:30] if c in KYTE_DOOLITTLE]
    if not vals:
        raise ValueError("no canonical residues in N-terminal window")
    return sum(vals) / len(vals)


_SEQUON = re.compile(r"N[^P][ST]")


def sequon_density(seq: str) -> float:
    if not seq:
        raise ValueError("empty sequence")
    return len(_SEQUON.findall(seq)) / len(seq)


PROXIES: Dict[str, Callable[[str], float]] = {
    "cys_frac": cys_frac, "ch_frac": ch_frac, "his_frac": his_frac,
    "kr_frac": kr_frac, "de_frac": de_frac,
    "nterm_hydropathy": nterm_hydropathy, "sequon_density": sequon_density,
}


def proxy_excluding(proxy_name: str, seq: str, excluded: frozenset) -> float:
    """Criterion-3 residue-exclusion form: delete residues, then re-score.
    N-terminal / motif proxies operate on the filtered string too -- deleting
    the residues the vector most exploits and checking the effect survives."""
    filtered = "".join(c for c in seq if c not in excluded)
    if not filtered or not any(c in CANON for c in filtered):
        raise ValueError("no residues remain after exclusion")
    return PROXIES[proxy_name](filtered)


LEN = "(reviewed:true) AND (length:[50 TO 400])"

# name -> {pos, neg queries, proxy, keyword}. Sign chosen so proxy correlates
# POSITIVELY with the has-property label (calcium flips to acidic de_frac).
CANDIDATES = {
    "signal_pep": {
        "pos": f"(keyword:KW-0732) AND {LEN}",
        "neg": f"{LEN} NOT (keyword:KW-0732) NOT (keyword:KW-0812)",  # exclude TM: signal peptides overlap membrane
        "proxy": "nterm_hydropathy",
    },
    "glycoprotein": {
        "pos": f"(keyword:KW-0325) AND {LEN}",
        "neg": f"{LEN} NOT (keyword:KW-0325)",
        "proxy": "sequon_density",
    },
    "zinc_finger": {
        "pos": f"(keyword:KW-0863) AND {LEN}",
        "neg": f"{LEN} NOT (keyword:KW-0863) NOT (keyword:KW-0479)",
        "proxy": "ch_frac",
    },
    "disulfide": {
        "pos": f"(keyword:KW-1015) AND {LEN}",
        "neg": f"{LEN} NOT (keyword:KW-1015)",
        "proxy": "cys_frac",
    },
    "calcium": {
        "pos": f"(keyword:KW-0106) AND {LEN}",
        "neg": f"{LEN} NOT (keyword:KW-0106)",
        "proxy": "de_frac",
    },
}
