"""L60: activation-steering run for DNA-binding propensity (intrinsic,
the L42/L54 harness verbatim (same hook, same difference-of-means vector,
same matched-norm random control, same 6-criteria L50 verdict logic).

Only the target property, its loader, and its compositional proxy change.
Adds an explicit L54-derived compositional-separation gate (G1): the mean
per-residue AA-composition L2 distance between the low- and high-property
vector-building groups. L53 (binding) nulled with separation 0.0033; L54
(catalytic PASS) had 0.023-0.045. A run whose groups are compositionally
indistinguishable cannot produce a difference-of-means vector with signal,
regardless of proxy correlation, so this is asserted before any GPU work.

Run:  L60_SEED=0 python3 -m plm_steering.l59_run_repro   (seeds 0,1,2 for robustness)
"""
import json
import os
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from scipy.stats import pearsonr, spearmanr
from transformers import AutoModelForMaskedLM, AutoTokenizer

from plm_steering.l42_steering_repro import (
    difference_of_means_vector,
    dose_response_is_monotonic_then_collapsing,
    is_degenerate_sequence,
    paired_bootstrap_mean_diff,
)
from plm_steering.l60_binding_steering import (
    binding_proxy,
    binding_proxy_excluding,
)

MODEL_NAME = "facebook/esm2_t33_650M_UR50D"
DATA_PATH = Path(__file__).resolve().parent / "data_cache" / "binding" / "uniprot_dnabinding.json"
SEED = int(os.environ.get("L60_SEED", "0"))
OUT_DIR = Path(__file__).resolve().parent / ("l60_repro_out" if SEED == 0 else f"l60_repro_out_seed{SEED}")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_SEQ_LEN = 400
N_VECTOR_SEQS_PER_GROUP = 150
N_EVAL_SEQS = 150
ALPHAS = [0.1, 0.15, 0.2, 0.25, 0.5, 1.0, 2.0]
MASK_FRACTION = 0.3
N_BOOT = 10000
MIN_NONDEGENERATE_PAIRS = 30
TRAIN_FRACTION = 0.7
CANONICAL_RESIDUES = frozenset("ACDEFGHIKLMNPQRSTVWY")
SAFE_ALPHAS = (0.1, 0.15, 0.2, 0.25)  # fine grid strictly below the ~0.35 collapse boundary; per L52, alpha>=0.5 degenerates this eval
MIN_PROXY_ABS_R = 0.15
MIN_GROUP_SEPARATION = 0.015  # L54 gate: L53 null=0.0033, L54 PASS=0.023-0.045


class MultiLayerSteeringHook:
    def __init__(self, direction: torch.Tensor, alpha: float):
        self.direction = direction
        self.alpha = alpha

    def __call__(self, module, inputs, output):
        if self.alpha == 0.0:
            return output
        hidden = output[0] if isinstance(output, tuple) else output
        original_norm = hidden.norm(dim=-1, keepdim=True)
        perturbed = hidden + self.alpha * self.direction
        perturbed_norm = perturbed.norm(dim=-1, keepdim=True).clamp(min=1e-8)
        renormalized = perturbed * (original_norm / perturbed_norm)
        if isinstance(output, tuple):
            return (renormalized,) + output[1:]
        return renormalized


@torch.no_grad()
def mean_pooled_activation_all_layers(model, tokenizer, sequences, device, max_len=MAX_SEQ_LEN):
    n_layers = model.config.num_hidden_layers
    per_layer_activations = {layer: [] for layer in range(n_layers)}
    for seq in sequences:
        seq = seq[:max_len]
        enc = tokenizer(seq, return_tensors="pt", truncation=True, max_length=max_len + 2).to(device)
        out = model(**enc, output_hidden_states=True)
        for layer in range(n_layers):
            hidden = out.hidden_states[layer + 1].squeeze(0).float()
            per_layer_activations[layer].append(hidden.mean(dim=0).cpu().numpy())
    return {layer: np.stack(vals, axis=0) for layer, vals in per_layer_activations.items()}


@torch.no_grad()
def mask_fill_generate(model, tokenizer, sequence, mask_fraction, seed, device, max_len=MAX_SEQ_LEN):
    seq = sequence[:max_len]
    enc = tokenizer(seq, return_tensors="pt", truncation=True, max_length=max_len + 2)
    input_ids = enc["input_ids"][0].clone()
    rng = torch.Generator().manual_seed(seed)
    special_ids = set(tokenizer.all_special_ids)
    non_special_positions = torch.tensor([i for i, t in enumerate(input_ids.tolist()) if t not in special_ids])
    n_mask = max(1, int(len(non_special_positions) * mask_fraction))
    perm = torch.randperm(len(non_special_positions), generator=rng)
    mask_positions = non_special_positions[perm[:n_mask]]
    masked_ids = input_ids.clone()
    masked_ids[mask_positions] = tokenizer.mask_token_id
    masked_enc = {"input_ids": masked_ids.unsqueeze(0).to(device), "attention_mask": enc["attention_mask"].to(device)}
    out = model(**masked_enc)
    predicted_ids = out.logits.argmax(dim=-1).squeeze(0).cpu()
    filled_ids = masked_ids.clone()
    filled_ids[mask_positions] = predicted_ids[mask_positions]
    tokens_str = tokenizer.convert_ids_to_tokens(filled_ids.tolist())
    return "".join(t for t in tokens_str if t not in tokenizer.all_special_tokens)


def score_binding(sequences):
    return np.array([binding_proxy(seq) for seq in sequences])


def load_binding(path=DATA_PATH, max_len=MAX_SEQ_LEN):
    """UniProt records -> (sequences, dna_binding) deduplicated by sequence."""
    with open(path) as f:
        records = json.load(f)
    by_sequence = {}
    for rec in records:
        seq = rec["sequence"]
        if len(seq) > max_len or len(seq) == 0 or not set(seq) <= CANONICAL_RESIDUES:
            continue
        by_sequence[seq] = float(rec["dna_binding"])  # unique per accession already
    sequences = sorted(by_sequence)
    labels = np.array([by_sequence[s] for s in sequences])
    return sequences, labels


_AA_INDEX = {a: k for k, a in enumerate("ACDEFGHIKLMNPQRSTVWY")}


def _aa_composition(seq):
    v = np.zeros(20)
    for c in seq:
        if c in _AA_INDEX:
            v[_AA_INDEX[c]] += 1
    return v / max(1, len(seq))


def _group_separation(low_group, high_group):
    lo = np.mean([_aa_composition(s) for s in low_group], axis=0)
    hi = np.mean([_aa_composition(s) for s in high_group], axis=0)
    return float(np.linalg.norm(hi - lo))


def main():
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"device: {device}  SEED={SEED}  OUT_DIR={OUT_DIR.name}", flush=True)

    sequences, labels = load_binding()
    print(f"usable unique proteins (<={MAX_SEQ_LEN} aa, canonical): {len(sequences)} "
          f"(tm>0: {int((labels > 0).sum())}, tm=0: {int((labels == 0).sum())})", flush=True)

    rng = np.random.RandomState(SEED)
    order = rng.permutation(len(sequences))
    cut = int(TRAIN_FRACTION * len(sequences))
    train_idx, test_idx = order[:cut], order[cut:]
    train_seqs = [sequences[i] for i in train_idx]
    train_labels = labels[train_idx]
    test_seqs = [sequences[i] for i in test_idx]
    test_labels = labels[test_idx]
    print(f"train (vector pool): {len(train_seqs)}, test (eval pool): {len(test_seqs)}", flush=True)

    # === Criterion 4, enforced before any GPU work ===
    train_proxy = score_binding(train_seqs)
    test_proxy = score_binding(test_seqs)
    r_train, p_train = pearsonr(train_proxy, train_labels)
    r_test, p_test = pearsonr(test_proxy, test_labels)
    rho_test, _ = spearmanr(test_proxy, test_labels)
    proxy_validation = {
        "train": {"pearson_r": float(r_train), "p": float(p_train), "n": len(train_seqs)},
        "test": {"pearson_r": float(r_test), "p": float(p_test), "spearman_rho": float(rho_test), "n": len(test_seqs)},
        "min_abs_r_required": MIN_PROXY_ABS_R,
    }
    print(f"proxy vs real dna_binding: train r={r_train:+.4f} (p={p_train:.2e}), "
          f"test r={r_test:+.4f} (p={p_test:.2e}), test rho={rho_test:+.4f}", flush=True)
    assert abs(r_test) >= MIN_PROXY_ABS_R, (
        f"criterion 4 FAILED: proxy correlates only r={r_test:+.4f} with real held-out labels "
        f"(need |r| >= {MIN_PROXY_ABS_R})"
    )
    assert r_test > 0, "proxy sign is inverted relative to the real label"

    # vector-building groups: percentile split on the REAL label
    low_threshold = np.percentile(train_labels, 20.0)
    high_threshold = np.percentile(train_labels, 80.0)
    low_group = [s for s, y in zip(train_seqs, train_labels) if y <= low_threshold][:N_VECTOR_SEQS_PER_GROUP]
    high_group = [s for s, y in zip(train_seqs, train_labels) if y >= high_threshold][:N_VECTOR_SEQS_PER_GROUP]
    print(f"vector-building groups: {len(low_group)} low-binding (<= {low_threshold:.3f}), "
          f"{len(high_group)} high-binding (>= {high_threshold:.3f})", flush=True)
    assert len(low_group) == N_VECTOR_SEQS_PER_GROUP and len(high_group) == N_VECTOR_SEQS_PER_GROUP

    # === G1: compositional separation gate (L54 lesson) ===
    separation = _group_separation(low_group, high_group)
    proxy_validation["group_separation"] = separation
    proxy_validation["min_group_separation_required"] = MIN_GROUP_SEPARATION
    print(f"G1 compositional separation (AA-comp L2, low vs high): {separation:.4f} "
          f"[L53 null=0.0033, L54 PASS=0.023-0.045, require >= {MIN_GROUP_SEPARATION}]", flush=True)
    assert separation >= MIN_GROUP_SEPARATION, (
        f"G1 FAILED: group separation {separation:.4f} < {MIN_GROUP_SEPARATION}; "
        f"difference-of-means vector would have no compositional signal (the L53 failure mode)"
    )

    # eval sequences: LOW-tm held-out proteins -- steering should push them up
    test_median = np.percentile(test_labels, 50.0)
    eval_sequences = [s for s, y in zip(test_seqs, test_labels) if y <= test_median][:N_EVAL_SEQS]
    print(f"eval sequences (low-binding, held-out): {len(eval_sequences)}", flush=True)
    assert len(eval_sequences) == N_EVAL_SEQS, f"only {len(eval_sequences)} eval sequences, need {N_EVAL_SEQS}"

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME).to(device).eval()
    n_layers = model.config.num_hidden_layers
    print(f"model loaded: {MODEL_NAME}, {n_layers} layers", flush=True)

    print("\nembedding low-binding group...", flush=True)
    low_activations = mean_pooled_activation_all_layers(model, tokenizer, low_group, device)
    print("embedding high-binding group...", flush=True)
    high_activations = mean_pooled_activation_all_layers(model, tokenizer, high_group, device)

    steering_vectors = {}
    for layer in range(n_layers):
        vec = difference_of_means_vector(low_activations[layer], high_activations[layer])
        steering_vectors[layer] = torch.tensor(vec, dtype=torch.float32, device=device)
    print(f"built {len(steering_vectors)} per-layer difference-of-means steering vectors", flush=True)

    rng2 = np.random.RandomState(SEED + 1)
    random_vectors = {}
    for layer, vec in steering_vectors.items():
        rv = torch.tensor(rng2.normal(size=vec.shape[0]), dtype=torch.float32, device=device)
        random_vectors[layer] = rv / rv.norm() * vec.norm()

    def apply_hooks(vectors, alpha):
        handles = []
        for layer, vec in vectors.items():
            hook = MultiLayerSteeringHook(vec, alpha)
            handles.append(model.esm.encoder.layer[layer].register_forward_hook(hook))
        return handles

    def remove_hooks(handles):
        for h in handles:
            h.remove()

    def generate_then_score(vectors, alpha):
        generated = []
        handles = apply_hooks(vectors, alpha) if alpha != 0.0 else []
        try:
            for i, seq in enumerate(eval_sequences):
                generated.append(mask_fill_generate(model, tokenizer, seq, MASK_FRACTION, SEED + i, device))
        finally:
            remove_hooks(handles)
        return generated, score_binding(generated)

    def score_arm(vectors, alpha):
        generated, scores = generate_then_score(vectors, alpha)
        degenerate = np.array([is_degenerate_sequence(s) for s in generated])
        return generated, scores, degenerate

    results = {"proxy_validation": proxy_validation, "real_direction": {}, "random_control": {}}
    all_sequences = {"baseline": None, "real_direction": {}, "random_control": {}}

    print("\n=== baseline (alpha=0) ===", flush=True)
    baseline_generated, baseline_scores = generate_then_score(steering_vectors, 0.0)
    baseline_degenerate = np.array([is_degenerate_sequence(s) for s in baseline_generated])
    print(f"baseline mean score: {baseline_scores.mean():.4f}, "
          f"degenerate: {baseline_degenerate.sum()}/{len(baseline_degenerate)}", flush=True)
    results["baseline"] = {
        "mean": float(baseline_scores.mean()), "std": float(baseline_scores.std()),
        "n": len(baseline_scores), "n_degenerate": int(baseline_degenerate.sum()),
    }
    all_sequences["baseline"] = baseline_generated

    real_by_alpha = {}
    random_by_alpha = {}
    for alpha in ALPHAS:
        print(f"\n=== real_direction, alpha={alpha} ===", flush=True)
        generated, scores, degenerate = score_arm(steering_vectors, alpha)
        real_by_alpha[alpha] = (generated, scores, degenerate)
        all_sequences["real_direction"][alpha] = generated
        print(f"mean score: {scores.mean():.4f}, degenerate: {degenerate.sum()}/{len(degenerate)}", flush=True)

        print(f"=== random_control, alpha={alpha} ===", flush=True)
        generated, scores, degenerate = score_arm(random_vectors, alpha)
        random_by_alpha[alpha] = (generated, scores, degenerate)
        all_sequences["random_control"][alpha] = generated
        print(f"mean score: {scores.mean():.4f}, degenerate: {degenerate.sum()}/{len(degenerate)}", flush=True)

    real_vs_random_by_alpha = {}
    for alpha in ALPHAS:
        _, real_scores, real_degenerate = real_by_alpha[alpha]
        _, random_scores, random_degenerate = random_by_alpha[alpha]
        keep = ~real_degenerate & ~random_degenerate & ~baseline_degenerate
        n_kept = int(keep.sum())
        results["real_direction"][alpha] = {"mean": float(real_scores.mean()), "n_degenerate": int(real_degenerate.sum())}
        results["random_control"][alpha] = {"mean": float(random_scores.mean()), "n_degenerate": int(random_degenerate.sum())}
        if n_kept < MIN_NONDEGENERATE_PAIRS:
            real_vs_random_by_alpha[alpha] = {
                "point_estimate": None, "ci_lower": None, "ci_upper": None,
                "significant_at_95pct": False, "n": n_kept,
                "excluded_reason": f"only {n_kept} non-degenerate pairs",
            }
            print(f"\nalpha={alpha}: EXCLUDED -- only {n_kept} non-degenerate pairs", flush=True)
            continue
        bootstrap = paired_bootstrap_mean_diff(random_scores[keep], real_scores[keep], n_boot=N_BOOT, seed=SEED)
        bootstrap["pct_sequences_real_beats_random"] = float((real_scores[keep] > random_scores[keep]).mean())
        real_vs_random_by_alpha[alpha] = bootstrap
        print(f"\nalpha={alpha}: real-vs-random (n={n_kept}) diff={bootstrap['point_estimate']:.4f} "
              f"[{bootstrap['ci_lower']:.4f}, {bootstrap['ci_upper']:.4f}] sig={bootstrap['significant_at_95pct']} "
              f"pct_real_beats_random={bootstrap['pct_sequences_real_beats_random']:.3f}", flush=True)

    valid_alphas = [a for a in SAFE_ALPHAS if real_vs_random_by_alpha[a]["point_estimate"] is not None]
    dose_response_ok = (
        dose_response_is_monotonic_then_collapsing(
            list(valid_alphas), [real_vs_random_by_alpha[a]["point_estimate"] for a in valid_alphas]
        )
        if len(valid_alphas) >= 3 else False
    )

    best_alpha = max(
        (a for a in SAFE_ALPHAS if real_vs_random_by_alpha[a].get("significant_at_95pct")),
        key=lambda a: real_vs_random_by_alpha[a]["point_estimate"],
        default=None,
    )
    robustness_check = None
    if best_alpha is not None:
        real_generated, _, real_degenerate = real_by_alpha[best_alpha]
        random_generated, _, random_degenerate = random_by_alpha[best_alpha]
        counts = Counter()
        for seq, base in zip(real_generated, baseline_generated):
            for a, b in zip(seq, base):
                if a != b:
                    counts[a] += 1
        top_residues = frozenset(r for r, _ in counts.most_common(2))
        print(f"\ndominant substituted residues at alpha={best_alpha}: {counts.most_common(5)}", flush=True)

        keep = ~real_degenerate & ~random_degenerate & ~baseline_degenerate
        real_excl_scores = np.array([
            binding_proxy_excluding(s, top_residues) for s in np.array(real_generated)[keep]
        ])
        random_excl_scores = np.array([
            binding_proxy_excluding(s, top_residues) for s in np.array(random_generated)[keep]
        ])
        excl_bootstrap = paired_bootstrap_mean_diff(random_excl_scores, real_excl_scores, n_boot=N_BOOT, seed=SEED)
        robustness_check = {
            "alpha": best_alpha,
            "excluded_residues": sorted(top_residues),
            "diff_with_exclusion": excl_bootstrap,
        }
        print(f"robustness check (excluding {sorted(top_residues)}): diff={excl_bootstrap['point_estimate']:.4f} "
              f"[{excl_bootstrap['ci_lower']:.4f}, {excl_bootstrap['ci_upper']:.4f}] "
              f"sig={excl_bootstrap['significant_at_95pct']}", flush=True)

    crit1 = best_alpha is not None
    crit2 = dose_response_ok
    crit3 = robustness_check is not None and robustness_check["diff_with_exclusion"]["significant_at_95pct"]
    crit4 = bool(abs(r_test) >= MIN_PROXY_ABS_R)
    crit5 = None  # no prior binding-steering technique exists
    crit6 = len(eval_sequences) >= 150

    criteria = {
        "1_beats_random_control": crit1,
        "2_dose_response": crit2,
        "3_residue_robust": crit3,
        "4_proxy_pre_validated": crit4,
        "5_beats_existing_technique": crit5,
        "6_adequately_powered": crit6,
    }
    operative = [v for v in criteria.values() if v is not None]
    if all(operative):
        decision = "PASS"
    elif not crit1 or not crit3:
        decision = "KILL"
    elif sum(bool(v) for v in operative) >= 3:
        decision = "AMBIGUOUS"
    else:
        decision = "KILL"

    verdict = {
        "criteria": criteria,
        "decision": decision,
        "best_alpha": best_alpha,
        "seed": SEED,
        "proxy_validation": proxy_validation,
        "real_vs_random_by_alpha": real_vs_random_by_alpha,
        "robustness_check": robustness_check,
    }
    print("\n=== L60 VERDICT (DNA-binding propensity, degenerate-filtered, "
          "paired-bootstrapped, residue-exclusion-checked) ===", flush=True)
    print(json.dumps(verdict, indent=2, default=str), flush=True)

    results["verdict"] = verdict
    results["raw_scores"] = {
        "baseline": baseline_scores.tolist(),
        **{f"real__{a}": real_by_alpha[a][1].tolist() for a in ALPHAS},
        **{f"random__{a}": random_by_alpha[a][1].tolist() for a in ALPHAS},
    }
    results["eval_sequences"] = eval_sequences
    with open(OUT_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to {OUT_DIR / 'results.json'}", flush=True)


if __name__ == "__main__":
    main()
