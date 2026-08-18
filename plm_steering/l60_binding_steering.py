"""L60: extend the harness to a cross-protein, intrinsic BINDING capability --
DNA-binding propensity -- with a compositional proxy validated against real
UniProt DNA-binding labels BEFORE the run (L50 criterion 4).

See l60_fetch_binding.py for why this reframes L53's relational
protein-protein affinity (which fails L56's intrinsic gate) into an intrinsic,
cross-protein binding property.

Proxy: positive-charge fraction (Lys + Arg). Nucleic-acid-binding interfaces
are documented to be strongly enriched in Lys/Arg, whose guanidinium/amine
groups form salt bridges and H-bonds with the DNA phosphate backbone (Luscombe
et al. 2001, NAR, on Arg/Lys over-representation at protein-DNA interfaces).
Sign convention: higher = more DNA-binding-like.

As with L59 transmembrane, the residue-exclusion check (criterion 3) is the
crux: if the whole effect is the steering vector pumping out K/R, excluding
the top-2 substituted residues should erase it.
"""
from typing import List

POSITIVE = frozenset("KR")


def _fraction(sequence: str, residues: frozenset) -> float:
    if len(sequence) == 0:
        raise ValueError("fraction requires a non-empty sequence")
    return sum(1 for c in sequence if c in residues) / len(sequence)


def positive_charge_fraction(sequence: str) -> float:
    """(fraction of K) + (fraction of R). Purely compositional, no model."""
    return _fraction(sequence, POSITIVE)


def binding_proxy(sequence: str) -> float:
    """Higher = predicted MORE DNA-binding. Positive correlation with the real
    UniProt DNA-binding label (validated in-run per criterion 4)."""
    return positive_charge_fraction(sequence)


def binding_proxy_excluding(sequence: str, excluded_residues: frozenset) -> float:
    """Same proxy after deleting excluded_residues -- criterion 3's
    residue-exclusion robustness check. Note that excluding K or R removes one
    of the proxy's own terms; that is intentional and is the strictest form of
    the check (if the effect is just steering pumping out K/R, the excluded
    score cannot reproduce it)."""
    filtered = "".join(c for c in sequence if c not in excluded_residues)
    if len(filtered) == 0:
        raise ValueError("binding_proxy_excluding: no residues remain after exclusion")
    return binding_proxy(filtered)


def score_binding(sequences: List[str]):
    import numpy as np
    return np.array([binding_proxy(s) for s in sequences])
