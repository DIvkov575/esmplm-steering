"""L61 -- is L57's expression-steering effect specific to its charge/E proxy, or
does it show up on an INDEPENDENT, E-free, eSol-validated proxy?

WHY THIS EXISTS
    L57's residue-exclusion failure is partly circular: the proxy is
    |(K+R)-(D+E)|/len, E is one of its four defining residues, and E is exactly
    the residue whose exclusion collapses the effect. A fair question: is the
    steering effect an artifact of inserting the proxy's own charged residues,
    or does steering move a DIFFERENT, E-free solubility measure too?

    This re-scores L57's ALREADY-GENERATED sequences (saved in
    l57_repro_out/results.json -- no model needed) with candidate E-free proxies,
    after first validating each proxy against eSol's real soluble-fraction
    labels (same bar L57's own proxy had to clear). Each proxy is oriented so
    HIGHER = more soluble; a positive real-vs-random diff means steering pushed
    toward more soluble on THAT proxy. If every E-free validated proxy shows no
    (or reversed) effect while the original charge proxy shows +~0.0125, the L57
    effect is charge/E-specific -- the artifact reading is confirmed.

RUNNABLE CHECK
    python3 -m plm_steering.l61_l57_altproxy_validation
    CPU only, seconds. Reproduces the original charge-proxy +effect@0.5 from the
    saved sequences as a built-in sanity check.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

from plm_steering.l42_steering_repro import is_degenerate_sequence, paired_bootstrap_mean_diff
from plm_steering.l57_expression_yield_steering import expression_yield_proxy

L57_RESULTS = Path(__file__).resolve().parent / "l57_repro_out" / "results.json"
ESOL = Path(__file__).resolve().parent / "data_cache" / "expression" / "esol_clean.csv"
OUT_DIR = Path(__file__).resolve().parent / "l61_l57_altproxy_out"
BEST_ALPHA = "0.5"  # L57's committed best_alpha
N_BOOT = 10000
SEED = 0

# Kyte-Doolittle hydropathy -- E-free by construction (no charge-difference term).
KD = {"A": 1.8, "R": -4.5, "N": -3.5, "D": -3.5, "C": 2.5, "Q": -3.5, "E": -3.5,
      "G": -0.4, "H": -3.2, "I": 4.5, "L": 3.8, "K": -3.9, "M": 1.9, "F": 2.8,
      "P": -1.6, "S": -0.8, "T": -0.7, "W": -0.9, "Y": -1.3, "V": 4.2}
TURN = set("NGPS")       # turn-forming fraction (module notes r=-0.10 vs eSol)
AROMATIC = set("FWY")
ALIPHATIC = set("AVLIM")


def gravy(seq):
    vals = [KD[c] for c in seq if c in KD]
    return float(np.mean(vals)) if vals else 0.0


def frac(seq, residues):
    return sum(1 for c in seq if c in residues) / len(seq) if seq else 0.0


# Candidate E-free proxies: name -> callable(seq)->float (raw, un-oriented).
CANDIDATES = {
    "gravy_hydropathy": gravy,
    "turn_forming_NGPS_frac": lambda s: frac(s, TURN),
    "aromatic_FWY_frac": lambda s: frac(s, AROMATIC),
    "aliphatic_AVLIM_frac": lambda s: frac(s, ALIPHATIC),
}


def validate_against_esol(proxy_fn):
    """Pearson r of proxy vs eSol label on the held-out test split."""
    df = pd.read_csv(ESOL)
    df = df[df["sequence"].str.len() <= 400].reset_index(drop=True)
    test = df[df["split"] == "test"] if "test" in set(df["split"]) else df
    x = np.array([proxy_fn(s) for s in test["sequence"]])
    y = test["label"].astype(float).values
    r, p = pearsonr(x, y)
    return {"r": float(r), "p": float(p), "n": int(len(y))}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = json.load(open(L57_RESULTS))
    seqs = data["raw_sequences"]
    baseline = seqs["baseline"]
    real = seqs[f"real__{BEST_ALPHA}"]
    random_ = seqs[f"random__{BEST_ALPHA}"]
    print(f"loaded {len(real)} real / {len(random_)} random / {len(baseline)} baseline generations "
          f"at alpha={BEST_ALPHA}", flush=True)

    base_deg = np.array([is_degenerate_sequence(s) for s in baseline])
    real_deg = np.array([is_degenerate_sequence(s) for s in real])
    rand_deg = np.array([is_degenerate_sequence(s) for s in random_])
    keep = ~base_deg & ~real_deg & ~rand_deg
    print(f"non-degenerate pairs kept: {keep.sum()}/{len(keep)}", flush=True)
    real_k = [s for s, k in zip(real, keep) if k]
    rand_k = [s for s, k in zip(random_, keep) if k]

    def diff_on(proxy_fn, orient):
        """Paired bootstrap real-vs-random, proxy oriented so + = more soluble."""
        r = np.array([orient * proxy_fn(s) for s in real_k])
        n = np.array([orient * proxy_fn(s) for s in rand_k])
        b = paired_bootstrap_mean_diff(n, r, n_boot=N_BOOT, seed=SEED)
        b["real_mean"] = float(r.mean())
        b["random_mean"] = float(n.mean())
        return b

    results = {"alpha": BEST_ALPHA, "n_kept": int(keep.sum()), "proxies": {}}

    # sanity: reproduce the original charge proxy +effect from saved sequences
    sanity = diff_on(expression_yield_proxy, +1.0)
    results["sanity_original_charge_proxy"] = sanity
    print(f"\n[sanity] original charge proxy real-vs-random diff = {sanity['point_estimate']:+.4f} "
          f"[{sanity['ci_lower']:+.4f},{sanity['ci_upper']:+.4f}] sig={sanity['significant_at_95pct']} "
          f"(should be ~ +0.0125, sig=True)", flush=True)

    for name, fn in CANDIDATES.items():
        val = validate_against_esol(fn)
        # orient toward solubility using the SIGN of the validated correlation
        orient = 1.0 if val["r"] >= 0 else -1.0
        validated = abs(val["r"]) >= 0.20 and val["p"] < 0.05  # same bar L57's proxy cleared
        d = diff_on(fn, orient)
        results["proxies"][name] = {
            "esol_validation": val,
            "validated_as_proxy": bool(validated),
            "orientation_toward_soluble": orient,
            "real_vs_random_diff": d,
            "steers_toward_soluble": bool(d["point_estimate"] > 0 and d["significant_at_95pct"]),
        }
        tag = "VALIDATED" if validated else "weak/invalid proxy"
        print(f"\n{name}: eSol r={val['r']:+.3f} (p={val['p']:.1e}, n={val['n']}) [{tag}]", flush=True)
        print(f"    real-vs-random (oriented + = more soluble) = {d['point_estimate']:+.4f} "
              f"[{d['ci_lower']:+.4f},{d['ci_upper']:+.4f}] sig={d['significant_at_95pct']}", flush=True)

    any_indep = any(
        p["validated_as_proxy"] and p["steers_toward_soluble"]
        for p in results["proxies"].values()
    )
    results["conclusion"] = (
        "INDEPENDENT solubility gain: at least one E-free eSol-validated proxy is steered "
        "toward more soluble -- effect is not merely the charge/E artifact"
        if any_indep else
        "CHARGE/E-SPECIFIC: no E-free eSol-validated proxy is steered toward more soluble; "
        "the L57 effect is specific to its own charge proxy (artifact reading holds)"
    )
    with open(OUT_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n=== L61 CONCLUSION ===\n{results['conclusion']}", flush=True)
    print(f"saved to {OUT_DIR / 'results.json'}", flush=True)


if __name__ == "__main__":
    main()
