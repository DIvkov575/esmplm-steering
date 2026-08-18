"""L59: extend the L42/L54 activation-steering harness to a NEW target
property -- transmembrane-residue fraction -- with a purely compositional
proxy validated against real UniProt TRANSMEM labels BEFORE the steering run
(L50 criterion 4).

Target property is intrinsic to the single sequence (L56 gate) and varies
across proteins (L54 cross-protein regime): soluble cytoplasmic proteins
(tm_fraction=0) .. multipass membrane proteins (tm_fraction up to ~0.8).

Proxy: mean Kyte-Doolittle hydropathy (a.k.a. GRAVY). Kyte & Doolittle (1982)
designed this scale specifically so that a sliding-window average identifies
membrane-spanning segments, so unlike the GRAVY-vs-solubility misuse in L43
(r=-0.03 against real labels), mean hydropathy is the *mechanistically
correct* compositional signal for the transmembrane property. Sign convention
matches the project's "higher score = more of the property": more positive
mean hydropathy = more transmembrane-like.

The residue-exclusion robustness check (L50 criterion 3) is the crux here:
membrane vs soluble proteins separate strongly on a handful of hydrophobic
residues (I/V/L/F), so an effect that vanishes once the top-2 substituted
residues are removed would be a compositional-collapse artifact, not a
capability. Whether the effect survives that exclusion is the open question.
"""
from typing import List

# Kyte & Doolittle (1982) hydropathy scale.
KYTE_DOOLITTLE = {
    "I": 4.5, "V": 4.2, "L": 3.8, "F": 2.8, "C": 2.5, "M": 1.9, "A": 1.8,
    "G": -0.4, "T": -0.7, "S": -0.8, "W": -0.9, "Y": -1.3, "P": -1.6,
    "H": -3.2, "E": -3.5, "Q": -3.5, "D": -3.5, "N": -3.5, "K": -3.9, "R": -4.5,
}

# The residues that dominate the membrane/soluble compositional contrast,
# used only for documentation of the criterion-3 risk (the run computes the
# actual top-2 substituted residues empirically).
HYDROPHOBIC_CORE = frozenset("IVLF")


def mean_hydropathy(sequence: str) -> float:
    """Mean Kyte-Doolittle hydropathy over canonical residues in the sequence
    (non-canonical residues are ignored). No model, no likelihood."""
    vals = [KYTE_DOOLITTLE[c] for c in sequence if c in KYTE_DOOLITTLE]
    if not vals:
        raise ValueError("mean_hydropathy requires at least one canonical residue")
    return sum(vals) / len(vals)


def transmembrane_proxy(sequence: str) -> float:
    """Higher = predicted MORE transmembrane. Positive correlation with real
    UniProt tm_fraction (validated in-run per L50 criterion 4)."""
    return mean_hydropathy(sequence)


def transmembrane_proxy_excluding(sequence: str, excluded_residues: frozenset) -> float:
    """Same proxy after deleting excluded_residues -- L50 criterion 3's
    residue-exclusion robustness check. If the whole transmembrane effect is
    the steering vector pumping out one or two hydrophobic residues, the
    excluded score cannot reproduce it."""
    filtered = "".join(c for c in sequence if c not in excluded_residues)
    if not any(c in KYTE_DOOLITTLE for c in filtered):
        raise ValueError("transmembrane_proxy_excluding: no canonical residues remain")
    return mean_hydropathy(filtered)


def score_transmembrane(sequences: List[str]):
    import numpy as np
    return np.array([transmembrane_proxy(s) for s in sequences])
