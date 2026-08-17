"""L60 -- is L57 (expression-yield steering) ANY independent of L55 (disorder)?

WHY THIS EXISTS
    studies/L57_EXPRESSION_STEERING.md lands AMBIGUOUS and argues -- from vector
    COSINE similarity alone (+0.376 full, up to +0.67 in deep layers vs. L55) --
    that L57 is "not independent evidence for expression yield as a 6th distinct
    steerable property," but a partial echo of L55's disorder direction. Cosine
    is suggestive, not decisive: two directions can be correlated and still each
    carry real, separable steering signal.

    This runs the decisive causal test. It rebuilds L57's per-layer steering
    vectors and L55's, then per layer removes L57's L55-parallel component
    (Gram-Schmidt) and renormalizes the RESIDUAL to L57's original per-layer
    norm, so the residual applies the SAME steering magnitude as L57 did, just in
    the disorder-orthogonal direction. It then runs L57's exact eval on three
    arms against one shared random control:
        A. l57_original   -- should reproduce the known AMBIGUOUS effect
                             (+~0.0125 @ alpha=0.5, collapses under E/L exclusion)
        B. l57_resid_l55  -- L57 with its disorder component projected out
    Reading:
        - if B shows NO significant real-vs-random effect (or one that dies under
          residue-exclusion) -> L57's steering is carried by its shared-with-
          disorder component; "not an independent 6th property" is CONFIRMED.
        - if B keeps a significant, residue-exclusion-robust effect -> there IS
          an independent expression signal beyond disorder, and the study's
          conclusion would need revising.

WHY NOT l57's main(): it is fail-closed (refuse_legacy_runner) with hard-coded
    seed/output paths. This is the audited interface: explicit seed, a NEW output
    dir (l60_l57_ortho_out/), and the compute primitives IMPORTED from L57 so
    the eval is identical to what L57 actually ran.

RUNNABLE CHECK
    python3 -m plm_steering.l60_l57_orthogonalized_validation
    Needs ESM2-650M; ~3 real arms x 150 seqs + vector builds. Arm A reproducing
    L57's AMBIGUOUS verdict is the built-in correctness check.
"""
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
# L57's exact eval primitives + constants (import does not run guarded main()).
from plm_steering.l57_run_repro import (
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
    SEED,
    MultiLayerSteeringHook,
    mask_fill_generate,
    mean_pooled_activation_all_layers,
    score_expression_yield,
)
from plm_steering.l57_expression_yield_steering import expression_yield_proxy_excluding
# L55 disorder groups, built exactly as l55_run_repro / l58 build them.
from plm_steering.l58_vector_geometry_crosscheck import build_vectors as l58_build_vectors
from plm_steering.l58_vector_geometry_crosscheck import l55_groups
from plm_steering.l55_run_repro import MAX_SEQ_LEN as L55_MAX_SEQ_LEN

OUT_DIR = Path(__file__).resolve().parent / "l60_l57_ortho_out"
DEEP_LAYERS = (30, 31, 32)


def l57_groups_and_eval(seed):
    """Exact reproduction of l57_run_repro.main()'s group + eval construction."""
    df = pd.read_csv(DATA_PATH)
    df = df[df["sequence"].str.len() <= MAX_SEQ_LEN].reset_index(drop=True)
    train_df = df[df["split"] == "train"].reset_index(drop=True)
    held_df = df[df["split"].isin(["valid", "test"])].reset_index(drop=True)

    train_shuffled = train_df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    labels = train_shuffled["label"].astype(float).values
    low_threshold = np.percentile(labels, 20.0)
    high_threshold = np.percentile(labels, 80.0)
    low_group = train_shuffled[train_shuffled["label"].astype(float) <= low_threshold]["sequence"].tolist()[:N_VECTOR_SEQS_PER_GROUP]
    high_group = train_shuffled[train_shuffled["label"].astype(float) >= high_threshold]["sequence"].tolist()[:N_VECTOR_SEQS_PER_GROUP]

    held_shuffled = held_df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    held_median = np.percentile(held_shuffled["label"].astype(float).values, 50.0)
    eval_sequences = held_shuffled[held_shuffled["label"].astype(float) <= held_median]["sequence"].tolist()[:N_EVAL_SEQS]
    return low_group, high_group, eval_sequences


def orthogonalize_residual(v57, v55):
    """Remove v57's component parallel to v55, renormalize residual to ||v57||.

    Returns (residual_at_original_norm, fraction_of_norm_removed). If v55 is ~0
    the residual is v57 unchanged.
    """
    n55 = np.linalg.norm(v55)
    if n55 < 1e-12:
        return v57.copy(), 0.0
    proj = (np.dot(v57, v55) / (n55 ** 2)) * v55
    resid = v57 - proj
    n57 = np.linalg.norm(v57)
    nresid = np.linalg.norm(resid)
    frac_removed = 1.0 - (nresid / n57) if n57 > 1e-12 else 0.0
    if nresid < 1e-12:
        return np.zeros_like(v57), 1.0
    resid_at_orig_norm = resid * (n57 / nresid)
    return resid_at_orig_norm, float(frac_removed)


def run_eval_arm(model, tokenizer, device, eval_sequences, vectors, random_vectors, seed, baseline_generated, baseline_degenerate):
    """L57's exact per-arm eval: generate+score real & random across ALPHAS,
    paired-bootstrap real-vs-random per alpha, dose-response over SAFE_ALPHAS,
    residue-exclusion at best_alpha. `vectors` is the per-layer 'real' direction.
    """
    n_layers = model.config.num_hidden_layers

    def apply_hooks(vecs, alpha):
        return [model.esm.encoder.layer[l].register_forward_hook(MultiLayerSteeringHook(vecs[l], alpha))
                for l in range(n_layers)]

    def gen_and_score(vecs, alpha):
        handles = apply_hooks(vecs, alpha) if alpha != 0.0 else []
        try:
            generated = [mask_fill_generate(model, tokenizer, s, MASK_FRACTION, seed + i, device)
                         for i, s in enumerate(eval_sequences)]
        finally:
            for h in handles:
                h.remove()
        return generated, score_expression_yield(generated)

    def arm(vecs, alpha):
        g, s = gen_and_score(vecs, alpha)
        return g, s, np.array([is_degenerate_sequence(x) for x in g])

    real_by_alpha = {a: arm(vectors, a) for a in ALPHAS}
    random_by_alpha = {a: arm(random_vectors, a) for a in ALPHAS}

    rvr = {}
    for a in ALPHAS:
        _, rs, rd = real_by_alpha[a]
        _, ns, nd = random_by_alpha[a]
        keep = ~rd & ~nd & ~baseline_degenerate
        n_kept = int(keep.sum())
        if n_kept < MIN_NONDEGENERATE_PAIRS:
            rvr[a] = {"point_estimate": None, "significant_at_95pct": False, "n": n_kept}
            continue
        b = paired_bootstrap_mean_diff(ns[keep], rs[keep], n_boot=N_BOOT, seed=seed)
        b["pct_real_beats_random"] = float((rs[keep] > ns[keep]).mean())
        rvr[a] = b

    valid = [a for a in SAFE_ALPHAS if rvr[a]["point_estimate"] is not None]
    dose_ok = (dose_response_is_monotonic_then_collapsing(valid, [rvr[a]["point_estimate"] for a in valid])
               if len(valid) >= 3 else False)
    best_alpha = max((a for a in SAFE_ALPHAS if rvr[a].get("significant_at_95pct")),
                     key=lambda a: rvr[a]["point_estimate"], default=None)

    robustness = None
    if best_alpha is not None:
        real_gen, _, real_deg = real_by_alpha[best_alpha]
        rand_gen, _, rand_deg = random_by_alpha[best_alpha]
        counts = Counter()
        for seq, base in zip(real_gen, baseline_generated):
            for x, y in zip(seq, base):
                if x != y:
                    counts[x] += 1
        top = frozenset(r for r, _ in counts.most_common(2))
        keep = ~real_deg & ~rand_deg & ~baseline_degenerate
        re = np.array([expression_yield_proxy_excluding(s, top) for s in np.array(real_gen)[keep]])
        ne = np.array([expression_yield_proxy_excluding(s, top) for s in np.array(rand_gen)[keep]])
        eb = paired_bootstrap_mean_diff(ne, re, n_boot=N_BOOT, seed=seed)
        robustness = {"alpha": best_alpha, "excluded_residues": sorted(top),
                      "substitution_counts_top5": counts.most_common(5), "diff_with_exclusion": eb}

    crit1 = best_alpha is not None
    crit3 = robustness is not None and robustness["diff_with_exclusion"]["significant_at_95pct"]
    decision = ("KILL" if not crit1 else "AMBIGUOUS" if not crit3
                else "PASS" if dose_ok else "AMBIGUOUS")
    return {
        "criteria": {"1_beats_random": crit1, "2_dose_response": dose_ok, "3_residue_robust": crit3},
        "decision": decision, "best_alpha": best_alpha,
        "real_vs_random_by_alpha": rvr, "robustness_check": robustness,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"device: {device}", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME).to(device).eval()
    n_layers = model.config.num_hidden_layers
    print(f"model loaded: {MODEL_NAME}, {n_layers} layers", flush=True)

    # --- L57 direction (from its own low/high expression groups + eval set) ---
    low57, high57, eval_sequences = l57_groups_and_eval(SEED)
    print(f"L57: {len(low57)} low / {len(high57)} high vectors, {len(eval_sequences)} eval seqs", flush=True)
    low_act = mean_pooled_activation_all_layers(model, tokenizer, low57, device)
    high_act = mean_pooled_activation_all_layers(model, tokenizer, high57, device)
    v57 = np.stack([difference_of_means_vector(low_act[l], high_act[l]) for l in range(n_layers)], axis=0)

    # --- L55 disorder direction (exact l55/l58 group logic) ---
    low55, high55 = l55_groups()
    print(f"L55: {len(low55)} low / {len(high55)} high disorder vectors", flush=True)
    v55 = l58_build_vectors(model, tokenizer, device, n_layers, low55, high55, L55_MAX_SEQ_LEN)

    # --- orthogonalize L57 against L55, per layer ---
    resid = np.zeros_like(v57)
    frac_removed = []
    for l in range(n_layers):
        resid[l], fr = orthogonalize_residual(v57[l], v55[l])
        frac_removed.append(fr)
    deep_removed = [frac_removed[l] for l in DEEP_LAYERS]
    print(f"norm fraction of L57 removed by projecting out L55: "
          f"mean={np.mean(frac_removed):.3f}, deep layers {DEEP_LAYERS}={[round(x,3) for x in deep_removed]}",
          flush=True)

    def to_tensors(arr):
        return {l: torch.tensor(arr[l], dtype=torch.float32, device=device) for l in range(n_layers)}

    v57_t = to_tensors(v57)
    resid_t = to_tensors(resid)

    # one shared random control, matched to L57's original per-layer norms
    rng2 = np.random.RandomState(SEED + 1)
    random_t = {}
    for l in range(n_layers):
        rv = torch.tensor(rng2.normal(size=v57.shape[1]), dtype=torch.float32, device=device)
        random_t[l] = rv / rv.norm() * v57_t[l].norm()

    # baseline (alpha=0) once, shared across arms
    baseline_generated = [mask_fill_generate(model, tokenizer, s, MASK_FRACTION, SEED + i, device)
                          for i, s in enumerate(eval_sequences)]
    baseline_degenerate = np.array([is_degenerate_sequence(s) for s in baseline_generated])
    print(f"baseline degenerate: {baseline_degenerate.sum()}/{len(baseline_degenerate)}", flush=True)

    print("\n=== ARM A: l57_original (correctness check -- expect AMBIGUOUS, crit3 fail) ===", flush=True)
    arm_a = run_eval_arm(model, tokenizer, device, eval_sequences, v57_t, random_t, SEED,
                         baseline_generated, baseline_degenerate)
    print(json.dumps(arm_a["criteria"]), "best_alpha", arm_a["best_alpha"], "->", arm_a["decision"], flush=True)

    print("\n=== ARM B: l57_resid_l55 (L57 with disorder projected out -- the decisive test) ===", flush=True)
    arm_b = run_eval_arm(model, tokenizer, device, eval_sequences, resid_t, random_t, SEED,
                         baseline_generated, baseline_degenerate)
    print(json.dumps(arm_b["criteria"]), "best_alpha", arm_b["best_alpha"], "->", arm_b["decision"], flush=True)

    def eff_at(arm, a):
        r = arm["real_vs_random_by_alpha"].get(a)
        return (r["point_estimate"] if r and r["point_estimate"] is not None else None)

    # Two INDEPENDENT axes -- do not conflate them:
    #   (i) disorder-dependence: how much of arm A's effect survives removing the
    #       L55-parallel component? High retention => effect is NOT disorder's echo.
    #  (ii) artifact: does the (disorder-orthogonal) effect survive residue-exclusion?
    a_eff, b_eff = eff_at(arm_a, 0.5), eff_at(arm_b, 0.5)
    retention = (b_eff / a_eff) if (a_eff and b_eff is not None) else None
    disorder_independent = retention is not None and retention >= 0.80  # keeps >=80% of effect
    residue_robust = bool(arm_b["criteria"]["3_residue_robust"])

    conclusion = (
        f"disorder-INDEPENDENT: projecting out L55 (only {np.mean(frac_removed):.1%} of L57's "
        f"norm) retains {retention:.0%} of the effect ({b_eff:.4f} vs {a_eff:.4f} @0.5) -- "
        f"REFUTES the 'echo of disorder' reading. "
        if disorder_independent else
        f"disorder-DEPENDENT: removing L55 drops the effect to {retention:.0%} of arm A "
        f"({b_eff} vs {a_eff}) -- consistent with the 'echo of disorder' reading. "
    ) + (
        "It STILL fails residue-exclusion (collapses excluding its charge-proxy residues), "
        "so it remains AMBIGUOUS as a composition-collapse artifact -- but that failure is "
        "NOT due to disorder."
        if not residue_robust else
        "And it now SURVIVES residue-exclusion -- a clean disorder-orthogonal expression effect; "
        "L57's AMBIGUOUS verdict would need revisiting."
    )
    out = {
        "seed": SEED,
        "norm_fraction_removed_by_l55_projection": {
            "mean": float(np.mean(frac_removed)),
            "per_layer": [round(x, 4) for x in frac_removed],
            "deep_layers": {str(l): round(frac_removed[l], 4) for l in DEEP_LAYERS},
        },
        "arm_A_l57_original": arm_a,
        "arm_B_l57_resid_l55": arm_b,
        "effect_at_0.5": {"arm_A": a_eff, "arm_B": b_eff},
        "effect_retention_after_removing_disorder": retention,
        "disorder_independent": disorder_independent,
        "arm_B_residue_robust": residue_robust,
        "conclusion": conclusion,
    }
    with open(OUT_DIR / "results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\n=== L60 CONCLUSION ===", flush=True)
    print(conclusion, flush=True)
    print(f"arm A effect@0.5={eff_at(arm_a, 0.5)}, arm B effect@0.5={eff_at(arm_b, 0.5)}", flush=True)
    print(f"saved to {OUT_DIR / 'results.json'}", flush=True)


if __name__ == "__main__":
    main()
