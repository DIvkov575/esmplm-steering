"""L64 -- multi-seed rescue attempt for L55 (intrinsic-disorder steering).

WHY THIS EXISTS
    L55 is the project's best near-miss: it passes criteria 1 (beats matched
    random control) and 2 (dose-response) on 3/3 seeds, and its ONLY shortfall
    is criterion 3 (residue-exclusion robustness), which passed 2 of 3 seeds ->
    AMBIGUOUS. Unlike L52 (a stable smaller-than-all33 gap) or L57 (a structural
    E/L artifact), L55's failing criterion is SEED-VARIABLE: right at the
    significance boundary. So gathering more seeds legitimately estimates the
    true residue-exclusion pass-rate -- this is the one place "just run more
    datapoints" actually bears on the verdict.

    This runs L55's IDENTICAL experiment across N seeds (default 0-9), reusing
    L55's exact compute primitives, and reports the per-seed criteria plus the
    residue-exclusion pass-rate. Seed 0 reproduces l55_repro_out (determinism +
    faithfulness check). Decision rule for the rescue:
      - residue-exclusion holds in a clear majority (>=70%) AND crit1/2 hold all
        seeds  -> promote toward SUPPORTED (robust real effect).
      - residue-exclusion ~50/50 -> genuinely fragile; stays AMBIGUOUS but now
        with a confident characterization, not a 1-seed guess.

WHY NOT l55's main(): fail-closed (refuse_legacy_runner, hard-coded SEED/paths).
    This is the audited interface: explicit seeds, NEW output dir, primitives
    imported so the run is identical to what L55 did.

RUNNABLE CHECK
    python3 -m plm_steering.l64_l55_multiseed_validation            # seeds 0-9
    python3 -m plm_steering.l64_l55_multiseed_validation --seeds 0 1 2
    Needs ESM2-650M; DisProt data ships in-tree. ~6-10 min per seed.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

from plm_steering.l42_steering_repro import (
    difference_of_means_vector,
    dose_response_is_monotonic_then_collapsing,
    is_degenerate_sequence,
    paired_bootstrap_mean_diff,
)
from plm_steering.l55_disorder_steering import disorder_proxy_excluding
from plm_steering.l55_run_repro import (
    ALPHAS,
    DATA_PATH,
    MASK_FRACTION,
    MAX_SEQ_LEN,
    MIN_NONDEGENERATE_PAIRS,
    MODEL_NAME,
    N_BOOT,
    N_EVAL_SEQS,
    N_VECTOR_SEQS_PER_GROUP,
    SAFE_ALPHAS,
    VECTOR_POOL_SIZE,
    MultiLayerSteeringHook,
    mask_fill_generate,
    mean_pooled_activation_all_layers,
    score_disorder,
)

OUT_DIR = Path(__file__).resolve().parent / "l55_multiseed_out"


def run_one_seed(model, tokenizer, device, n_layers, df, seed):
    """Faithful re-implementation of l55_run_repro.main()'s orchestration, seed
    parameterized. Mirrors that file line-for-line; primitives are imported."""
    shuffled = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    vector_pool = shuffled.iloc[:VECTOR_POOL_SIZE]
    eval_pool = shuffled.iloc[VECTOR_POOL_SIZE:]

    labels = vector_pool["disorder_fraction"].astype(float).values
    low_t = np.percentile(labels, 20.0)
    high_t = np.percentile(labels, 80.0)
    low_group = vector_pool[vector_pool["disorder_fraction"].astype(float) <= low_t]["sequence"].tolist()[:N_VECTOR_SEQS_PER_GROUP]
    high_group = vector_pool[vector_pool["disorder_fraction"].astype(float) >= high_t]["sequence"].tolist()[:N_VECTOR_SEQS_PER_GROUP]
    assert len(low_group) == N_VECTOR_SEQS_PER_GROUP and len(high_group) == N_VECTOR_SEQS_PER_GROUP

    eval_labels = eval_pool["disorder_fraction"].astype(float).values
    eval_threshold = np.percentile(eval_labels, 50.0)
    eval_sequences = eval_pool[eval_pool["disorder_fraction"].astype(float) <= eval_threshold]["sequence"].tolist()[:N_EVAL_SEQS]
    print(f"  seed {seed}: {len(low_group)}/{len(high_group)} vectors, {len(eval_sequences)} eval seqs", flush=True)

    low_act = mean_pooled_activation_all_layers(model, tokenizer, low_group, device)
    high_act = mean_pooled_activation_all_layers(model, tokenizer, high_group, device)
    steering = {l: torch.tensor(difference_of_means_vector(low_act[l], high_act[l]),
                                dtype=torch.float32, device=device) for l in range(n_layers)}
    rng2 = np.random.RandomState(seed + 1)
    random_v = {}
    for l in range(n_layers):
        rv = torch.tensor(rng2.normal(size=steering[l].shape[0]), dtype=torch.float32, device=device)
        random_v[l] = rv / rv.norm() * steering[l].norm()

    def gen_score(vectors, alpha):
        handles = ([model.esm.encoder.layer[l].register_forward_hook(MultiLayerSteeringHook(vectors[l], alpha))
                    for l in range(n_layers)] if alpha != 0.0 else [])
        try:
            gen = [mask_fill_generate(model, tokenizer, s, MASK_FRACTION, seed + i, device)
                   for i, s in enumerate(eval_sequences)]
        finally:
            for h in handles:
                h.remove()
        return gen, score_disorder(gen)

    def arm(vectors, alpha):
        g, s = gen_score(vectors, alpha)
        return g, s, np.array([is_degenerate_sequence(x) for x in g])

    baseline_gen, _ = gen_score(steering, 0.0)
    baseline_deg = np.array([is_degenerate_sequence(s) for s in baseline_gen])
    real = {a: arm(steering, a) for a in ALPHAS}
    rand = {a: arm(random_v, a) for a in ALPHAS}

    rvr = {}
    for a in ALPHAS:
        _, rs, rd = real[a]
        _, ns, nd = rand[a]
        keep = ~rd & ~nd & ~baseline_deg
        if int(keep.sum()) < MIN_NONDEGENERATE_PAIRS:
            rvr[a] = {"point_estimate": None, "significant_at_95pct": False, "n": int(keep.sum())}
            continue
        b = paired_bootstrap_mean_diff(ns[keep], rs[keep], n_boot=N_BOOT, seed=seed)
        rvr[a] = b

    valid = [a for a in SAFE_ALPHAS if rvr[a]["point_estimate"] is not None]
    dose_ok = (dose_response_is_monotonic_then_collapsing(valid, [rvr[a]["point_estimate"] for a in valid])
               if len(valid) >= 3 else False)
    best_alpha = max((a for a in SAFE_ALPHAS if rvr[a].get("significant_at_95pct")),
                     key=lambda a: rvr[a]["point_estimate"], default=None)

    robustness = None
    if best_alpha is not None:
        rgen, _, rdeg = real[best_alpha]
        ngen, _, ndeg = rand[best_alpha]
        counts = Counter()
        for seq, base in zip(rgen, baseline_gen):
            for x, y in zip(seq, base):
                if x != y:
                    counts[x] += 1
        top = frozenset(r for r, _ in counts.most_common(2))
        keep = ~rdeg & ~ndeg & ~baseline_deg
        re_ = np.array([disorder_proxy_excluding(s, top) for s in np.array(rgen)[keep]])
        ne_ = np.array([disorder_proxy_excluding(s, top) for s in np.array(ngen)[keep]])
        eb = paired_bootstrap_mean_diff(ne_, re_, n_boot=N_BOOT, seed=seed)
        robustness = {"alpha": best_alpha, "excluded_residues": sorted(top), "diff_with_exclusion": eb}

    crit1 = best_alpha is not None
    crit3 = (robustness is not None
             and robustness["diff_with_exclusion"]["significant_at_95pct"]
             and robustness["diff_with_exclusion"]["point_estimate"] > 0)  # same (disorder-increasing) direction
    decision = ("KILL" if not crit1 else "PASS" if (dose_ok and crit3) else "AMBIGUOUS")
    return {"seed": seed, "best_alpha": best_alpha,
            "crit1_beats_control": crit1, "crit2_dose_response": dose_ok, "crit3_residue_robust": crit3,
            "decision": decision,
            "effect_at_best": (rvr[best_alpha]["point_estimate"] if best_alpha else None),
            "residue_exclusion_diff": (robustness["diff_with_exclusion"]["point_estimate"] if robustness else None),
            "excluded_residues": (robustness["excluded_residues"] if robustness else None),
            "real_vs_random_by_alpha": rvr}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"device: {device}", flush=True)
    df = pd.read_csv(DATA_PATH)
    df = df[df["sequence"].str.len() <= MAX_SEQ_LEN].reset_index(drop=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME).to(device).eval()
    n_layers = model.config.num_hidden_layers
    print(f"model loaded: {n_layers} layers; {len(df)} usable sequences\n", flush=True)

    per_seed = []
    for seed in args.seeds:
        print(f"=== SEED {seed} ===", flush=True)
        v = run_one_seed(model, tokenizer, device, n_layers, df, seed)
        with open(OUT_DIR / f"seed{seed}_verdict.json", "w") as f:
            json.dump(v, f, indent=2, default=str)
        print(f"  -> decision={v['decision']} best_alpha={v['best_alpha']} "
              f"crit1={v['crit1_beats_control']} crit2={v['crit2_dose_response']} crit3={v['crit3_residue_robust']} "
              f"| effect={v['effect_at_best']} excl_diff={v['residue_exclusion_diff']} "
              f"(excl {v['excluded_residues']})", flush=True)
        per_seed.append(v)

    n = len(per_seed)
    n_c1 = sum(v["crit1_beats_control"] for v in per_seed)
    n_c2 = sum(v["crit2_dose_response"] for v in per_seed)
    n_c3 = sum(v["crit3_residue_robust"] for v in per_seed)
    n_pass = sum(v["decision"] == "PASS" for v in per_seed)
    c3_rate = n_c3 / n if n else 0.0
    summary = {
        "seeds": args.seeds, "n_seeds": n,
        "crit1_beats_control_rate": f"{n_c1}/{n}",
        "crit2_dose_response_rate": f"{n_c2}/{n}",
        "crit3_residue_robust_rate": f"{n_c3}/{n}",
        "full_PASS_rate": f"{n_pass}/{n}",
        "decision_by_seed": {v["seed"]: v["decision"] for v in per_seed},
        "conclusion": (
            f"PROMOTE toward SUPPORTED: residue-exclusion holds {n_c3}/{n} ({c3_rate:.0%}), "
            f"crit1 {n_c1}/{n}, crit2 {n_c2}/{n} -- the effect is robustly real, not a 1-seed fluke"
            if c3_rate >= 0.70 and n_c1 == n and n_c2 == n else
            f"GENUINELY FRAGILE: residue-exclusion holds only {n_c3}/{n} ({c3_rate:.0%}); "
            f"L55 stays AMBIGUOUS but now with a measured pass-rate, not a 2/3 guess"
            if 0.30 <= c3_rate < 0.70 else
            f"DOES NOT SURVIVE: residue-exclusion holds {n_c3}/{n} ({c3_rate:.0%}) -- trends KILL"),
    }
    with open(OUT_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("\n=== L64 MULTI-SEED SUMMARY (L55 disorder) ===", flush=True)
    print(json.dumps(summary, indent=2, default=str), flush=True)
    print(f"\nsaved to {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
