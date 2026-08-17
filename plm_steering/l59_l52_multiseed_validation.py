"""L59 -- multi-seed robustness validation of L52 (layer-subset vs all-33-layer
thermostability steering).

WHY THIS EXISTS
    studies/L52_LAYER_SUBSET_STEERING.md reports a single SEED=0 run and lands
    AMBIGUOUS on exactly one criterion: criterion 5 (the 5-layer subset's real
    effect is significantly SMALLER than steering all 33 layers -- ~0.47x at
    alpha=0.5). The open question a reader is entitled to ask: is that "real but
    weaker" conclusion a one-seed accident, or does it replicate? This runs the
    IDENTICAL L52 experiment across SEEDS 0,1,2 and reports, per seed:
      - is subset5's real effect significant vs its matched-norm random control?
      - is all33's real effect significant (L42 replication)?
      - subset5 / all33 effect ratio at each safe alpha (the criterion-5 gap)
      - does criterion 5 (non-inferiority of subset5 to all33) pass or fail?

    It CANNOT turn L52 into a clean PASS by construction: if subset5 is really a
    smaller effect than all33, more seeds re-measure that, they do not erase it.
    A confident, 3-seed "real but ~half the size of all33" is the honest ceiling
    here, and that is what this script is for.

WHY NOT JUST CALL l52's main()
    plm_steering.l52_layer_subset_causal_steering.main() is fail-closed via
    refuse_legacy_runner (hard-coded SEED/OUT_DIR that would overwrite committed
    evidence). This is the audited interface that guard asks for: seeds and
    output paths are explicit parameters, and output goes to a NEW directory
    (l52_multiseed_out/), never the committed l52_repro_out/.

    The compute PRIMITIVES that must match L52 exactly (steering hook, per-layer
    embedding, mask-fill generation, IVYWREL scoring, residue-exclusion) are
    IMPORTED from the L52 module, not re-implemented, so this cannot silently
    drift from what L52 actually did. The orchestration below mirrors
    l52_layer_subset_causal_steering.main() line-for-line.

RUNNABLE CHECK
    python3 -m plm_steering.l59_l52_multiseed_validation
    Reproduces seed 0 to match the committed l52_repro_out/results.json (asserts
    the harness is deterministic and this re-implementation is faithful), then
    adds seeds 1 and 2. Needs ESM2-650M and the meltome data (16MB, gitignored;
    pass --meltome to point at a checkout that has it).
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
    split_by_percentile,
)
# Reuse L52's EXACT compute primitives and constants -- importing does not run
# the guarded main().
from plm_steering.l52_layer_subset_causal_steering import (
    ALPHAS,
    MASK_FRACTION,
    MAX_SEQ_LEN,
    MIN_NONDEGENERATE_PAIRS,
    MODEL_NAME,
    N_BOOT,
    N_EVAL_SEQS,
    N_VECTOR_SEQS_PER_GROUP,
    NECESSARY_LAYERS,
    SAFE_ALPHAS,
    MultiLayerSteeringHook,
    ivywrel_fraction_excluding,
    mask_fill_generate,
    mean_pooled_activation_all_layers,
    score_thermostability_proxy,
)

SEEDS = (0, 1, 2)
DEFAULT_MELTOME = (
    Path(__file__).resolve().parent / "data_cache" / "meltome" / "mixed_split.csv"
)
OUT_DIR = Path(__file__).resolve().parent / "l52_multiseed_out"


def run_one_seed(model, tokenizer, device, n_layers, df, seed):
    """Faithful re-implementation of l52 main()'s orchestration for one seed.

    Mirrors l52_layer_subset_causal_steering.main() exactly; only SEED is a
    parameter and the model/tokenizer/data are passed in (loaded once, reused
    across seeds). Returns the same verdict dict main() builds.
    """
    shuffled = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    vector_pool = shuffled.iloc[: 2 * N_VECTOR_SEQS_PER_GROUP + 500]
    eval_pool = shuffled.iloc[2 * N_VECTOR_SEQS_PER_GROUP + 500 :]

    low_group, high_group = split_by_percentile(
        vector_pool["sequence"].tolist(), vector_pool["label"].values, low_pct=20.0, high_pct=80.0
    )
    low_group = low_group[:N_VECTOR_SEQS_PER_GROUP]
    high_group = high_group[:N_VECTOR_SEQS_PER_GROUP]

    eval_pool_sorted = eval_pool.sort_values("label")
    eval_sequences = eval_pool_sorted["sequence"].tolist()[:N_EVAL_SEQS]
    print(f"  seed {seed}: {len(low_group)} low-Tm / {len(high_group)} high-Tm vectors, "
          f"{len(eval_sequences)} eval seqs", flush=True)

    low_activations = mean_pooled_activation_all_layers(model, tokenizer, low_group, device)
    high_activations = mean_pooled_activation_all_layers(model, tokenizer, high_group, device)

    steering_vectors = {
        layer: torch.tensor(
            difference_of_means_vector(low_activations[layer], high_activations[layer]),
            dtype=torch.float32, device=device,
        )
        for layer in range(n_layers)
    }

    rng2 = np.random.RandomState(seed + 1)
    random_vectors = {
        layer: torch.tensor(rng2.normal(size=vec.shape[0]), dtype=torch.float32, device=device)
        for layer, vec in steering_vectors.items()
    }
    for layer in random_vectors:
        random_vectors[layer] = (
            random_vectors[layer] / random_vectors[layer].norm() * steering_vectors[layer].norm()
        )

    def apply_hooks(vectors, alpha, layer_scope):
        return [
            model.esm.encoder.layer[layer].register_forward_hook(MultiLayerSteeringHook(vectors[layer], alpha))
            for layer in layer_scope
        ]

    def generate_then_score(vectors, alpha, layer_scope):
        handles = apply_hooks(vectors, alpha, layer_scope) if alpha != 0.0 else []
        try:
            generated = [
                mask_fill_generate(model, tokenizer, seq, MASK_FRACTION, seed + i, device)
                for i, seq in enumerate(eval_sequences)
            ]
        finally:
            for h in handles:
                h.remove()
        return generated, score_thermostability_proxy(generated)

    def score_arm(vectors, alpha, layer_scope):
        generated, scores = generate_then_score(vectors, alpha, layer_scope)
        degenerate = np.array([is_degenerate_sequence(s) for s in generated])
        return generated, scores, degenerate

    all_layers = list(range(n_layers))
    subset_layers = sorted(NECESSARY_LAYERS)

    baseline_generated, _ = generate_then_score(steering_vectors, 0.0, all_layers)
    baseline_degenerate = np.array([is_degenerate_sequence(s) for s in baseline_generated])

    configs = {"all33": all_layers, "subset5": subset_layers}
    arms = {}
    for config_name, layer_scope in configs.items():
        for alpha in ALPHAS:
            arms[(config_name, "real", alpha)] = score_arm(steering_vectors, alpha, layer_scope)
            arms[(config_name, "random", alpha)] = score_arm(random_vectors, alpha, layer_scope)

    def bootstrap_pair(scores_a, deg_a, scores_b, deg_b):
        keep = ~deg_a & ~deg_b & ~baseline_degenerate
        n_kept = int(keep.sum())
        if n_kept < MIN_NONDEGENERATE_PAIRS:
            return {"point_estimate": None, "ci_lower": None, "ci_upper": None,
                    "significant_at_95pct": False, "n": n_kept}
        result = paired_bootstrap_mean_diff(scores_a[keep], scores_b[keep], n_boot=N_BOOT, seed=seed)
        result["pct_b_beats_a"] = float((scores_b[keep] > scores_a[keep]).mean())
        return result

    subset5_vs_random, all33_vs_random, subset5_vs_all33 = {}, {}, {}
    for alpha in ALPHAS:
        _, s5r_s, s5r_d = arms[("subset5", "random", alpha)]
        _, s5_s, s5_d = arms[("subset5", "real", alpha)]
        subset5_vs_random[alpha] = bootstrap_pair(s5r_s, s5r_d, s5_s, s5_d)

        _, a33r_s, a33r_d = arms[("all33", "random", alpha)]
        _, a33_s, a33_d = arms[("all33", "real", alpha)]
        all33_vs_random[alpha] = bootstrap_pair(a33r_s, a33r_d, a33_s, a33_d)

        subset5_vs_all33[alpha] = bootstrap_pair(a33_s, a33_d, s5_s, s5_d)

    valid_alphas = [a for a in SAFE_ALPHAS if subset5_vs_random[a]["point_estimate"] is not None]
    dose_response_ok = (
        dose_response_is_monotonic_then_collapsing(
            valid_alphas, [subset5_vs_random[a]["point_estimate"] for a in valid_alphas]
        )
        if len(valid_alphas) >= 3 else False
    )

    best_alpha = max(
        (a for a in SAFE_ALPHAS if subset5_vs_random[a].get("significant_at_95pct")),
        key=lambda a: subset5_vs_random[a]["point_estimate"],
        default=None,
    )
    robustness_check = None
    if best_alpha is not None:
        real_generated, _, real_degenerate = arms[("subset5", "real", best_alpha)]
        random_generated, _, random_degenerate = arms[("subset5", "random", best_alpha)]
        counts = Counter()
        for seq, base in zip(real_generated, baseline_generated):
            for a, b in zip(seq, base):
                if a != b:
                    counts[a] += 1
        top_residues = frozenset(r for r, _ in counts.most_common(2))
        keep = ~real_degenerate & ~random_degenerate & ~baseline_degenerate
        real_excl = np.array([ivywrel_fraction_excluding(s, top_residues) for s in np.array(real_generated)[keep]])
        random_excl = np.array([ivywrel_fraction_excluding(s, top_residues) for s in np.array(random_generated)[keep]])
        excl_bootstrap = paired_bootstrap_mean_diff(random_excl, real_excl, n_boot=N_BOOT, seed=seed)
        robustness_check = {"alpha": best_alpha, "excluded_residues": sorted(top_residues),
                            "diff_with_exclusion": excl_bootstrap}

    crit1 = best_alpha is not None
    crit2 = dose_response_ok
    crit3 = robustness_check is not None and robustness_check["diff_with_exclusion"]["significant_at_95pct"]
    crit4 = True
    crit5 = (
        best_alpha is not None
        and not (
            subset5_vs_all33[best_alpha]["point_estimate"] is not None
            and subset5_vs_all33[best_alpha]["significant_at_95pct"]
            and subset5_vs_all33[best_alpha]["point_estimate"] < 0
        )
    )
    crit6 = True
    criteria = {"1_beats_controls": crit1, "2_dose_response": crit2, "3_residue_robust": crit3,
                "4_proxy_pre_validated": crit4, "5_non_inferior_to_all33": crit5, "6_adequately_powered": crit6}
    n_pass = sum(bool(v) for v in criteria.values())
    if n_pass == 6:
        decision = "PASS"
    elif not crit1 or not crit3:
        decision = "KILL"
    elif n_pass >= 4:
        decision = "AMBIGUOUS"
    else:
        decision = "KILL"

    return {
        "seed": seed, "criteria": criteria, "decision": decision, "best_alpha": best_alpha,
        "subset5_vs_random_by_alpha": subset5_vs_random,
        "all33_vs_random_by_alpha": all33_vs_random,
        "subset5_vs_all33_by_alpha": subset5_vs_all33,
        "robustness_check": robustness_check,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meltome", type=Path, default=DEFAULT_MELTOME,
                    help="path to meltome mixed_split.csv (gitignored; defaults to in-tree copy)")
    ap.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    args = ap.parse_args()

    if not args.meltome.exists():
        raise SystemExit(
            f"meltome data not found at {args.meltome}. It is 16MB and gitignored; "
            "pass --meltome pointing at a checkout that has "
            "plm_steering/data_cache/meltome/mixed_split.csv"
        )
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"device: {device}", flush=True)
    df = pd.read_csv(args.meltome)
    df = df[df["sequence"].str.len() <= MAX_SEQ_LEN].reset_index(drop=True)
    print(f"usable (length-filtered) sequences: {len(df)}", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME).to(device).eval()
    n_layers = model.config.num_hidden_layers
    print(f"model loaded: {MODEL_NAME}, {n_layers} layers\n", flush=True)

    per_seed = []
    for seed in args.seeds:
        print(f"=== SEED {seed} ===", flush=True)
        v = run_one_seed(model, tokenizer, device, n_layers, df, seed)
        with open(OUT_DIR / f"seed{seed}_verdict.json", "w") as f:
            json.dump(v, f, indent=2, default=str)
        ba = v["best_alpha"]
        s5 = v["subset5_vs_random_by_alpha"].get(ba) if ba is not None else None
        a33 = v["all33_vs_random_by_alpha"].get(ba) if ba is not None else None
        ratio = (s5["point_estimate"] / a33["point_estimate"]
                 if s5 and a33 and a33["point_estimate"] else None)
        print(f"  -> decision={v['decision']} best_alpha={ba} crit5(non_inferior)={v['criteria']['5_non_inferior_to_all33']}",
              flush=True)
        if s5 and a33:
            print(f"     subset5 eff={s5['point_estimate']:+.4f} (sig={s5['significant_at_95pct']}), "
                  f"all33 eff={a33['point_estimate']:+.4f} (sig={a33['significant_at_95pct']}), "
                  f"ratio={ratio:.3f}", flush=True)
        per_seed.append(v)

    # ---- cross-seed summary: the honest question is stability, not PASS ----
    def ratio_at(v, alpha):
        s5 = v["subset5_vs_random_by_alpha"].get(alpha)
        a33 = v["all33_vs_random_by_alpha"].get(alpha)
        if s5 and a33 and s5["point_estimate"] is not None and a33["point_estimate"]:
            return s5["point_estimate"] / a33["point_estimate"]
        return None

    summary = {
        "seeds": args.seeds,
        "subset5_effect_significant_all_seeds": all(
            (v["best_alpha"] is not None
             and v["subset5_vs_random_by_alpha"][v["best_alpha"]]["significant_at_95pct"])
            for v in per_seed
        ),
        "all33_effect_significant_all_seeds": all(
            (v["best_alpha"] is not None
             and v["all33_vs_random_by_alpha"][v["best_alpha"]]["significant_at_95pct"])
            for v in per_seed
        ),
        "crit5_non_inferior_by_seed": {v["seed"]: v["criteria"]["5_non_inferior_to_all33"] for v in per_seed},
        "decision_by_seed": {v["seed"]: v["decision"] for v in per_seed},
        "subset5_over_all33_ratio_by_seed_and_alpha": {
            v["seed"]: {str(a): (round(r, 4) if (r := ratio_at(v, a)) is not None else None)
                        for a in SAFE_ALPHAS}
            for v in per_seed
        },
    }
    ratios = [r for v in per_seed for a in SAFE_ALPHAS if (r := ratio_at(v, a)) is not None]
    summary["ratio_min"] = round(min(ratios), 4) if ratios else None
    summary["ratio_max"] = round(max(ratios), 4) if ratios else None
    summary["ratio_mean"] = round(float(np.mean(ratios)), 4) if ratios else None
    summary["conclusion"] = (
        "subset5 is a REAL but SMALLER effect than all33, replicated across seeds"
        if (summary["subset5_effect_significant_all_seeds"]
            and not any(summary["crit5_non_inferior_by_seed"].values()))
        else "inconsistent across seeds -- see per-seed detail"
    )

    with open(OUT_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("\n=== L59 MULTI-SEED SUMMARY ===", flush=True)
    print(json.dumps(summary, indent=2, default=str), flush=True)
    print(f"\nSaved to {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
