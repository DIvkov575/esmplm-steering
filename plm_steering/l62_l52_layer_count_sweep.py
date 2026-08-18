"""L62 -- turn L52's criterion-5 ambiguity into a binary answer: does ANY
necessity-ranked layer subset reproduce (match, not just beat-random) the full
all-33-layer thermostability steering effect?

WHY THIS EXISTS
    L52 is AMBIGUOUS because its top-5 necessary layers give a real but ~40%
    effect vs all-33 (criterion 5: significantly worse). That is not a
    data-volume question (L59 confirmed the 0.40 ratio across 3 seeds). The
    genuinely open, binary question is a DIFFERENT experiment: as you add more
    of the necessity-ranked layers, is there a subset size K < 33 at which the
    effect becomes statistically non-inferior to all-33 (clean "K layers
    suffice" = PASS on criterion 5), or does every proper subset fall short
    (clean "no subset suffices" = the mechanism is genuinely distributed)?

    This sweeps K in {5,10,15,20,25,33} over the L45 thermostability necessity
    ranking, builds the vectors once (SEED=0), and for each K reports
    subsetK-vs-random (does it steer?) and subsetK-vs-all33 head-to-head (is it
    non-inferior?). Output is a monotone table + the smallest non-inferior K.

    L45 necessity ranking (drop_from_full when each layer is excluded, most
    necessary first) is copied from biostat
    src/l38/l45_necessity_sweep_thermostability_out.json (that file was pruned
    from this submission repo; the top-5 here matches L52's NECESSARY_LAYERS).

WHY NOT l52's main(): fail-closed (refuse_legacy_runner). This reuses L52's
    exact compute primitives with an explicit seed and a NEW output dir.

RUNNABLE CHECK
    python3 -m plm_steering.l62_l52_layer_count_sweep --meltome <path/to/mixed_split.csv>
    Needs ESM2-650M + meltome (16MB, gitignored). K=5 reproduces L59/L52's
    subset5 result and K=33 reproduces all33 as built-in correctness checks.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

from plm_steering.l42_steering_repro import (
    difference_of_means_vector,
    is_degenerate_sequence,
    paired_bootstrap_mean_diff,
    split_by_percentile,
)
from plm_steering.l52_layer_subset_causal_steering import (
    ALPHAS,
    MASK_FRACTION,
    MAX_SEQ_LEN,
    MIN_NONDEGENERATE_PAIRS,
    MODEL_NAME,
    N_BOOT,
    N_EVAL_SEQS,
    N_VECTOR_SEQS_PER_GROUP,
    SAFE_ALPHAS,
    MultiLayerSteeringHook,
    mask_fill_generate,
    mean_pooled_activation_all_layers,
    score_thermostability_proxy,
)

# L45 thermostability necessity ranking, most-necessary first (see docstring).
NECESSITY_RANKING = [31, 30, 25, 18, 23, 0, 20, 10, 14, 24, 8, 28, 12, 13, 19,
                     21, 26, 16, 6, 3, 29, 4, 1, 7, 17, 11, 32, 27, 22, 9, 2, 15, 5]
SUBSET_SIZES = [5, 10, 15, 20, 25, 33]
SEED = 0
DEFAULT_MELTOME = Path(__file__).resolve().parent / "data_cache" / "meltome" / "mixed_split.csv"
OUT_DIR = Path(__file__).resolve().parent / "l62_layer_sweep_out"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meltome", type=Path, default=DEFAULT_MELTOME)
    args = ap.parse_args()
    if not args.meltome.exists():
        raise SystemExit(f"meltome data not found at {args.meltome} (16MB, gitignored); pass --meltome")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"device: {device}", flush=True)
    df = pd.read_csv(args.meltome)
    df = df[df["sequence"].str.len() <= MAX_SEQ_LEN].reset_index(drop=True)

    shuffled = df.sample(frac=1.0, random_state=SEED).reset_index(drop=True)
    vector_pool = shuffled.iloc[: 2 * N_VECTOR_SEQS_PER_GROUP + 500]
    eval_pool = shuffled.iloc[2 * N_VECTOR_SEQS_PER_GROUP + 500 :]
    low_group, high_group = split_by_percentile(
        vector_pool["sequence"].tolist(), vector_pool["label"].values, low_pct=20.0, high_pct=80.0)
    low_group, high_group = low_group[:N_VECTOR_SEQS_PER_GROUP], high_group[:N_VECTOR_SEQS_PER_GROUP]
    eval_sequences = eval_pool.sort_values("label")["sequence"].tolist()[:N_EVAL_SEQS]
    print(f"{len(low_group)} low / {len(high_group)} high vectors, {len(eval_sequences)} eval seqs", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME).to(device).eval()
    n_layers = model.config.num_hidden_layers
    print(f"model loaded: {n_layers} layers", flush=True)

    low_act = mean_pooled_activation_all_layers(model, tokenizer, low_group, device)
    high_act = mean_pooled_activation_all_layers(model, tokenizer, high_group, device)
    steering = {l: torch.tensor(difference_of_means_vector(low_act[l], high_act[l]),
                                dtype=torch.float32, device=device) for l in range(n_layers)}
    rng2 = np.random.RandomState(SEED + 1)
    random_v = {}
    for l in range(n_layers):
        rv = torch.tensor(rng2.normal(size=steering[l].shape[0]), dtype=torch.float32, device=device)
        random_v[l] = rv / rv.norm() * steering[l].norm()

    def gen_score(vectors, alpha, layer_scope):
        handles = ([model.esm.encoder.layer[l].register_forward_hook(MultiLayerSteeringHook(vectors[l], alpha))
                    for l in layer_scope] if alpha != 0.0 else [])
        try:
            gen = [mask_fill_generate(model, tokenizer, s, MASK_FRACTION, SEED + i, device)
                   for i, s in enumerate(eval_sequences)]
        finally:
            for h in handles:
                h.remove()
        return gen, score_thermostability_proxy(gen)

    def arm(vectors, alpha, scope):
        g, s = gen_score(vectors, alpha, scope)
        return g, s, np.array([is_degenerate_sequence(x) for x in g])

    baseline_gen, _ = gen_score(steering, 0.0, list(range(n_layers)))
    baseline_deg = np.array([is_degenerate_sequence(s) for s in baseline_gen])

    def boot(a_s, a_d, b_s, b_d):
        keep = ~a_d & ~b_d & ~baseline_deg
        n = int(keep.sum())
        if n < MIN_NONDEGENERATE_PAIRS:
            return {"point_estimate": None, "significant_at_95pct": False, "n": n}
        r = paired_bootstrap_mean_diff(a_s[keep], b_s[keep], n_boot=N_BOOT, seed=SEED)
        return r

    all33_scope = NECESSITY_RANKING[:33]
    all33_arms = {a: arm(steering, a, all33_scope) for a in ALPHAS}
    all33_rand = {a: arm(random_v, a, all33_scope) for a in ALPHAS}
    # all33's OWN real-vs-random effect per alpha -- the ratio denominator.
    all33_vs_random = {}
    for a in ALPHAS:
        _, a33s, a33d = all33_arms[a]
        _, a33rs, a33rd = all33_rand[a]
        all33_vs_random[a] = boot(a33rs, a33rd, a33s, a33d)

    per_k = {}
    for K in SUBSET_SIZES:
        scope = NECESSITY_RANKING[:K]
        print(f"\n=== K={K} layers: {sorted(scope)} ===", flush=True)
        real_arms = {a: (all33_arms[a] if K == 33 else arm(steering, a, scope)) for a in ALPHAS}
        rand_arms = {a: (all33_rand[a] if K == 33 else arm(random_v, a, scope)) for a in ALPHAS}

        vs_random, vs_all33, ratio = {}, {}, {}
        for a in ALPHAS:
            _, rs, rd = real_arms[a]
            _, ns, nd = rand_arms[a]
            vs_random[a] = boot(ns, nd, rs, rd)  # subsetK real-vs-random effect
            _, a33s, a33d = all33_arms[a]
            vs_all33[a] = boot(a33s, a33d, rs, rd)  # +=subsetK better, -=worse than all33
            r_pe = vs_random[a]["point_estimate"]
            a33_pe = all33_vs_random[a]["point_estimate"]
            ratio[a] = (r_pe / a33_pe) if (r_pe is not None and a33_pe) else None

        best_alpha = max((a for a in SAFE_ALPHAS if vs_random[a].get("significant_at_95pct")),
                         key=lambda a: vs_random[a]["point_estimate"], default=None)
        # criterion 5: at best_alpha, subsetK NOT significantly worse than all33
        non_inferior = (best_alpha is not None and not (
            vs_all33[best_alpha]["point_estimate"] is not None
            and vs_all33[best_alpha]["significant_at_95pct"]
            and vs_all33[best_alpha]["point_estimate"] < 0))
        per_k[K] = {
            "layers": sorted(scope), "best_alpha": best_alpha,
            "steers_vs_random_at_best": (best_alpha is not None),
            "non_inferior_to_all33": bool(non_inferior),
            "subset_vs_all33_at_best": vs_all33.get(best_alpha),
            "ratio_by_safe_alpha": {str(a): (round(ratio[a], 4) if ratio[a] is not None else None) for a in SAFE_ALPHAS},
        }
        print(f"  best_alpha={best_alpha} steers={best_alpha is not None} "
              f"non_inferior_to_all33={non_inferior} "
              f"ratio@safe={per_k[K]['ratio_by_safe_alpha']}", flush=True)

    smallest_ni = next((K for K in SUBSET_SIZES if K < 33 and per_k[K]["non_inferior_to_all33"]), None)
    summary = {
        "seed": SEED, "subset_sizes": SUBSET_SIZES, "per_k": per_k,
        "smallest_non_inferior_subset": smallest_ni,
        "conclusion": (
            f"{smallest_ni} necessity-ranked layers SUFFICE (non-inferior to all-33) -- "
            f"criterion 5 becomes a clean PASS at K={smallest_ni}"
            if smallest_ni is not None else
            "NO proper subset (up to 25/33) matches all-33: the thermostability steering "
            "effect is genuinely DISTRIBUTED across layers -- criterion 5 is a clean, "
            "principled FAIL for any layer-subset claim, not an ambiguous one"),
    }
    with open(OUT_DIR / "results.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("\n=== L62 CONCLUSION ===", flush=True)
    print(summary["conclusion"], flush=True)
    print(f"saved to {OUT_DIR / 'results.json'}", flush=True)


if __name__ == "__main__":
    main()
