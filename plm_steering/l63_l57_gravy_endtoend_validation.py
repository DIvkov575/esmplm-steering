"""L63 -- non-circular PASS/KILL verdict for L57 using an independent, E-free,
eSol-validated scoring proxy (GRAVY hydropathy) run through the FULL L50
pipeline (criteria 1/2/3), not just re-scored at one alpha.

WHY THIS EXISTS
    L57's AMBIGUOUS verdict comes from a residue-exclusion collapse that is
    partly circular: its charge proxy |(K+R)-(D+E)| contains E, and E is one of
    the two residues whose exclusion kills the effect. The clean binary test is
    to score with a proxy that (a) contains no charge/E term and (b) validates
    against eSol's real solubility labels on its own -- then run L57's exact
    criteria 1-3 on it. If steering (a vector built from REAL eSol labels, so
    the vector is already non-circular) moves GRAVY toward soluble, with a
    dose-response, that SURVIVES residue-exclusion -> PASS. If GRAVY's effect
    also collapses under residue-exclusion -> clean KILL of the "real solubility
    steering" claim. Either way, no more AMBIGUOUS.

    Because L57's steering vector is built on real labels (not on any proxy) and
    mask-fill generation is deterministic given the vector+seed, the committed
    l57_repro_out generations ARE what an end-to-end "score-by-GRAVY" run with
    that same vector produces at every alpha. So this needs no model -- it runs
    the full verdict pipeline over the saved generations with GRAVY as the proxy.
    (GRAVY vs eSol test-split label: r=-0.29, p=7e-6 -- see l61; it clears the
    same |r|>=0.2 bar L57's own proxy did.)

RUNNABLE CHECK
    python3 -m plm_steering.l63_l57_gravy_endtoend_validation
    CPU only, seconds. Prints the GRAVY-scored L50 verdict for L57.
"""
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

from plm_steering.l42_steering_repro import (
    dose_response_is_monotonic_then_collapsing,
    is_degenerate_sequence,
    paired_bootstrap_mean_diff,
)
from plm_steering.l61_l57_altproxy_validation import KD  # Kyte-Doolittle scale

L57_RESULTS = Path(__file__).resolve().parent / "l57_repro_out" / "results.json"
ESOL = Path(__file__).resolve().parent / "data_cache" / "expression" / "esol_clean.csv"
OUT_DIR = Path(__file__).resolve().parent / "l63_l57_gravy_out"
ALPHAS = [0.1, 0.25, 0.5, 1.0, 2.0]
SAFE_ALPHAS = (0.1, 0.25, 0.5)
MIN_NONDEGENERATE_PAIRS = 30
N_BOOT = 10000
SEED = 0


def gravy_soluble(seq, excluded=frozenset()):
    """-GRAVY over residues not in `excluded`. Oriented so HIGHER = more soluble
    (GRAVY correlates negatively with eSol solubility), matching L57's convention
    that a positive real-vs-random diff = steered toward more soluble."""
    vals = [KD[c] for c in seq if c in KD and c not in excluded]
    return -float(np.mean(vals)) if vals else 0.0


def validate_gravy():
    df = pd.read_csv(ESOL)
    df = df[df["sequence"].str.len() <= 400].reset_index(drop=True)
    test = df[df["split"] == "test"] if "test" in set(df["split"]) else df
    x = np.array([gravy_soluble(s) for s in test["sequence"]])
    y = test["label"].astype(float).values
    r, p = pearsonr(x, y)
    return {"r": float(r), "p": float(p), "n": int(len(y))}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = json.load(open(L57_RESULTS))
    seqs = data["raw_sequences"]
    baseline = seqs["baseline"]
    base_deg = np.array([is_degenerate_sequence(s) for s in baseline])

    val = validate_gravy()
    print(f"GRAVY(soluble-oriented) vs eSol test labels: r={val['r']:+.3f} p={val['p']:.1e} n={val['n']} "
          f"[{'VALIDATED' if abs(val['r'])>=0.2 and val['p']<0.05 else 'INVALID'}]", flush=True)

    def arms(alpha):
        real = seqs[f"real__{alpha}"]
        rand = seqs[f"random__{alpha}"]
        rdeg = np.array([is_degenerate_sequence(s) for s in real])
        ndeg = np.array([is_degenerate_sequence(s) for s in rand])
        return real, rand, rdeg, ndeg

    # criterion 1: GRAVY real-vs-random per alpha
    rvr = {}
    for a in ALPHAS:
        real, rand, rdeg, ndeg = arms(a)
        keep = ~base_deg & ~rdeg & ~ndeg
        if int(keep.sum()) < MIN_NONDEGENERATE_PAIRS:
            rvr[a] = {"point_estimate": None, "significant_at_95pct": False, "n": int(keep.sum())}
            continue
        rs = np.array([gravy_soluble(s) for s, k in zip(real, keep) if k])
        ns = np.array([gravy_soluble(s) for s, k in zip(rand, keep) if k])
        b = paired_bootstrap_mean_diff(ns, rs, n_boot=N_BOOT, seed=SEED)
        rvr[a] = b
        print(f"alpha={a}: GRAVY real-vs-random={b['point_estimate']:+.4f} "
              f"[{b['ci_lower']:+.4f},{b['ci_upper']:+.4f}] sig={b['significant_at_95pct']}", flush=True)

    # criterion 2: dose-response over safe alphas
    valid = [a for a in SAFE_ALPHAS if rvr[a]["point_estimate"] is not None]
    dose_ok = (dose_response_is_monotonic_then_collapsing(valid, [rvr[a]["point_estimate"] for a in valid])
               if len(valid) >= 3 else False)

    # criterion 3: residue-exclusion at best safe alpha, excluding GRAVY's top-2
    # substituted residues (vs baseline).
    best_alpha = max((a for a in SAFE_ALPHAS if rvr[a].get("significant_at_95pct")),
                     key=lambda a: rvr[a]["point_estimate"], default=None)
    robustness = None
    if best_alpha is not None:
        real, rand, rdeg, ndeg = arms(best_alpha)
        counts = Counter()
        for s, base in zip(real, baseline):
            for x, y in zip(s, base):
                if x != y:
                    counts[x] += 1
        top = frozenset(r for r, _ in counts.most_common(2))
        keep = ~base_deg & ~rdeg & ~ndeg
        re_ = np.array([gravy_soluble(s, top) for s, k in zip(real, keep) if k])
        ne_ = np.array([gravy_soluble(s, top) for s, k in zip(rand, keep) if k])
        eb = paired_bootstrap_mean_diff(ne_, re_, n_boot=N_BOOT, seed=SEED)
        robustness = {"alpha": best_alpha, "excluded_residues": sorted(top),
                      "substitution_counts_top5": counts.most_common(5), "diff_with_exclusion": eb}
        print(f"\nresidue-exclusion (excluding {sorted(top)}): GRAVY diff={eb['point_estimate']:+.4f} "
              f"[{eb['ci_lower']:+.4f},{eb['ci_upper']:+.4f}] sig={eb['significant_at_95pct']}", flush=True)

    crit1 = best_alpha is not None
    # crit3 must SURVIVE in the SAME (soluble) direction: a significant effect
    # that REVERSES sign after excluding the inserted residues is a collapse
    # (the effect was carried by those residues), NOT a pass.
    crit3 = (robustness is not None
             and robustness["diff_with_exclusion"]["significant_at_95pct"]
             and robustness["diff_with_exclusion"]["point_estimate"] > 0)
    exclusion_reversed = (robustness is not None
                          and robustness["diff_with_exclusion"]["significant_at_95pct"]
                          and robustness["diff_with_exclusion"]["point_estimate"] < 0)
    decision = ("KILL" if not crit1 else "AMBIGUOUS" if not crit3
                else "PASS" if dose_ok else "AMBIGUOUS")
    if decision == "PASS":
        conclusion = ("CLEAN PASS on an independent E-free proxy: steering raises GRAVY-solubility, "
                      "dose-responsively, and it SURVIVES residue-exclusion in the same direction -- "
                      "L57 is a real solubility effect, not a charge-proxy artifact. Upgrade L57.")
    elif exclusion_reversed:
        conclusion = ("ARTIFACT CONFIRMED on an independent proxy: the GRAVY soluble-direction effect "
                      f"(+{rvr[best_alpha]['point_estimate']:.4f} @alpha={best_alpha}) REVERSES to "
                      f"{robustness['diff_with_exclusion']['point_estimate']:+.4f} once its inserted "
                      f"residues {robustness['excluded_residues']} are excluded -- the whole "
                      "soluble-direction shift was carried by those residues (E is hydrophilic, so "
                      "inserting it lowers GRAVY). GRAVY being an E-free FORMULA does not make the "
                      "effect E-independent. Same collapse as the charge proxy -> the L57 effect is a "
                      "composition artifact, not a broad solubility gain. Trends toward KILL.")
    elif not crit3:
        conclusion = ("Still AMBIGUOUS on GRAVY: significant soluble-direction effect that does not "
                      "survive residue-exclusion (drops to non-significant), same failure mode as the "
                      "charge proxy.")
    else:
        conclusion = ("CLEAN KILL on GRAVY: no significant soluble-direction effect on an independent "
                      "E-free proxy at all.")

    out = {"proxy": "GRAVY hydropathy (soluble-oriented = -mean KD), E-free FORMULA (but E-content-driven)",
           "esol_validation": val,
           "criteria": {"1_beats_random": crit1, "2_dose_response": dose_ok, "3_residue_robust_same_direction": crit3},
           "residue_exclusion_reversed_sign": bool(exclusion_reversed),
           "decision": decision, "best_alpha": best_alpha,
           "real_vs_random_by_alpha": rvr, "robustness_check": robustness,
           "conclusion": conclusion}
    with open(OUT_DIR / "results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n=== L63 VERDICT (L57 scored by independent GRAVY proxy): {decision} ===", flush=True)
    print(conclusion, flush=True)
    print(f"saved to {OUT_DIR / 'results.json'}", flush=True)


if __name__ == "__main__":
    main()
