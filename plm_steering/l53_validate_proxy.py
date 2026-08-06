"""L53 criterion-4 check, runnable: re-derive the binding-affinity proxy's
correlation against ProteinGym's real DMS labels, and re-derive the
weight-shuffle null control cited in l53_binding_affinity_steering.py's
docstring (r=+0.795 full / +0.797 held-out test, shuffle r=-0.001).

This exists so those numbers are verifiable rather than asserted --
L50 criterion 4 requires the proxy to be validated against real labels
BEFORE a steering run, and unlike L54/L57, l53_run_repro.py itself never
recomputes them (it hardcodes crit4 = True). Fills that gap the same way
l57_validate_proxy.py does for L57's proxy.

    python3 -m plm_steering.l53_validate_proxy

Exits non-zero if the chosen proxy's held-out |r| falls below MIN_ABS_R or
if the weight-shuffle control fails to collapse to near-zero.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from Bio.Align import substitution_matrices
from scipy import stats

from plm_steering.l53_binding_affinity_steering import (
    binding_affinity_proxy,
    mutational_sensitivity_weights,
    unweighted_identity,
    weighted_wildtype_preservation,
)

DATA_PATH = (
    Path(__file__).resolve().parent
    / "data_cache"
    / "binding"
    / "RASK_HUMAN_Weng_2022_binding-DARPin_K55.parquet"
)
MAX_SEQ_LEN = 400  # matches l53_run_repro.py's convention
SEED = 0  # matches l53_run_repro.py's vector/eval split seed
MIN_ABS_R = 0.5  # the bar this proxy must clear; far below its measured ~0.80
N_SHUFFLES = 10
SHUFFLE_MAX_ABS_R = 0.2  # a real weight-shuffle null should collapse near zero

BLOSUM62 = substitution_matrices.load("BLOSUM62")


def blosum62_to_wt(sequence, reference):
    n = min(len(sequence), len(reference))
    return float(np.mean([BLOSUM62[sequence[i], reference[i]] for i in range(n)]))


def net_charge(sequence):
    pos = sum(1 for c in sequence if c in "KR")
    neg = sum(1 for c in sequence if c in "DE")
    return (pos - neg) / len(sequence)


def gravy(sequence):
    kd = {
        "A": 1.8, "R": -4.5, "N": -3.5, "D": -3.5, "C": 2.5, "Q": -3.5, "E": -3.5,
        "G": -0.4, "H": -3.2, "I": 4.5, "L": 3.8, "K": -3.9, "M": 1.9, "F": 2.8,
        "P": -1.6, "S": -0.8, "T": -0.7, "W": -0.9, "Y": -1.3, "V": 4.2,
    }
    return sum(kd[c] for c in sequence) / len(sequence)


def aromatic_fraction(sequence):
    return sum(1 for c in sequence if c in "FWY") / len(sequence)


def load_split():
    """Reproduces l53_run_repro.py's exact vector/eval split and weight fit."""
    df = pd.read_parquet(DATA_PATH)
    df = df[~df["is_indel"].astype(bool)]
    df = df[df["mutated_seq"].str.len() <= MAX_SEQ_LEN].reset_index(drop=True)
    reference_seq = df["target_seq"].iloc[0]

    shuffled = df.sample(frac=1.0, random_state=SEED).reset_index(drop=True)
    n_vector = int(0.7 * len(shuffled))
    vector_pool = shuffled.iloc[:n_vector].reset_index(drop=True)
    eval_pool = shuffled.iloc[n_vector:].reset_index(drop=True)

    weights = mutational_sensitivity_weights(
        vector_pool["mutant"].tolist(), vector_pool["DMS_score"].values, len(reference_seq)
    )
    return df, vector_pool, eval_pool, reference_seq, weights


def main():
    df, vector_pool, eval_pool, reference_seq, weights = load_split()
    print(f"usable variants: {len(df)}, vector pool: {len(vector_pool)}, "
          f"eval pool (held-out test): {len(eval_pool)}")

    candidates = {
        "weighted_id_raw": lambda s: weighted_wildtype_preservation(s, reference_seq, weights),
        "normalized (CHOSEN)": lambda s: binding_affinity_proxy(s, reference_seq, weights),
        "blosum62_to_wt": lambda s: blosum62_to_wt(s, reference_seq),
        "net_charge": net_charge,
        "unweighted_identity": lambda s: unweighted_identity(s, reference_seq),
        "gravy": gravy,
        "aromatic_fraction": aromatic_fraction,
    }

    failures = []
    for label, subset in [("FULL SET", df), ("HELD-OUT EVAL POOL", eval_pool)]:
        y = subset["DMS_score"].astype(float).values
        print(f"\n=== {label} (n={len(subset)}) ===")
        print(f"{'proxy':24s} {'pearson':>9s} {'p':>10s} {'spearman':>9s}")
        rows = []
        for name, fn in candidates.items():
            x = np.array([fn(s) for s in subset["mutated_seq"]])
            pr, pp = stats.pearsonr(x, y)
            sr, _ = stats.spearmanr(x, y)
            rows.append((name, pr, pp, sr))
        for name, pr, pp, sr in sorted(rows, key=lambda r: -abs(r[1])):
            print(f"{name:24s} {pr:+9.4f} {pp:10.2e} {sr:+9.4f}")
        chosen_r = next(pr for name, pr, _, _ in rows if name.endswith("(CHOSEN)"))
        if abs(chosen_r) < MIN_ABS_R:
            failures.append(f"{label}: chosen proxy |r|={abs(chosen_r):.4f} < {MIN_ABS_R}")

    print("\n=== weight-shuffle null control ===")
    eval_labels = eval_pool["DMS_score"].astype(float).values
    rng = np.random.RandomState(123)
    shuffle_rs = []
    for _ in range(N_SHUFFLES):
        shuffled_weights = weights[rng.permutation(len(weights))]
        scores = np.array([
            binding_affinity_proxy(s, reference_seq, shuffled_weights) for s in eval_pool["mutated_seq"]
        ])
        r, _ = stats.pearsonr(scores, eval_labels)
        shuffle_rs.append(r)
    shuffle_mean, shuffle_sd = float(np.mean(shuffle_rs)), float(np.std(shuffle_rs))
    print(f"shuffle r: mean={shuffle_mean:+.4f} sd={shuffle_sd:.4f} over {N_SHUFFLES} shuffles "
          f"(real weights: r={chosen_r:+.4f})")
    if abs(shuffle_mean) >= SHUFFLE_MAX_ABS_R:
        failures.append(
            f"weight-shuffle null did not collapse: mean|r|={abs(shuffle_mean):.4f} >= {SHUFFLE_MAX_ABS_R}"
        )

    if failures:
        print("\nFAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"\nOK: chosen proxy clears |r|>={MIN_ABS_R} on both splits; weight-shuffle control collapses.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
