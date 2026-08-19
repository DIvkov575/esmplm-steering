"""L61 generic run: CAND=<name> L61_SEED=<n> python3 -m plm_steering.l61_run

Identical L42/L54/L59 harness (same hook, difference-of-means vector,
matched-norm random control, degeneracy filter, paired bootstrap,
residue-exclusion, L50 6-criteria verdict, G1 separation gate). Only the
target property and its compositional proxy vary, read from
l61_candidates.CANDIDATES.
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
from plm_steering.l61_candidates import CANDIDATES, PROXIES, proxy_excluding, CANON

CAND = os.environ["CAND"]
CFG = CANDIDATES[CAND]
PROXY = PROXIES[CFG["proxy"]]
PROXY_NAME = CFG["proxy"]

MODEL_NAME = "facebook/esm2_t33_650M_UR50D"
DATA_PATH = Path(__file__).resolve().parent / "data_cache" / f"l61_{CAND}" / "data.json"
SEED = int(os.environ.get("L61_SEED", "0"))
OUT_DIR = Path(__file__).resolve().parent / (f"l61_{CAND}_out" if SEED == 0 else f"l61_{CAND}_out_seed{SEED}")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_SEQ_LEN = 400
N_VECTOR_SEQS_PER_GROUP = 150
N_EVAL_SEQS = 150
ALPHAS = [0.1, 0.15, 0.2, 0.25, 0.5, 1.0, 2.0]
MASK_FRACTION = 0.3
N_BOOT = 10000
MIN_NONDEGENERATE_PAIRS = 30
TRAIN_FRACTION = 0.7
SAFE_ALPHAS = (0.1, 0.15, 0.2, 0.25)  # non-degenerate window (L52; confirmed in L59)
MIN_PROXY_ABS_R = 0.15
MIN_GROUP_SEPARATION = 0.015


class MultiLayerSteeringHook:
    def __init__(self, direction, alpha):
        self.direction = direction; self.alpha = alpha

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
    per_layer = {layer: [] for layer in range(n_layers)}
    for seq in sequences:
        seq = seq[:max_len]
        enc = tokenizer(seq, return_tensors="pt", truncation=True, max_length=max_len + 2).to(device)
        out = model(**enc, output_hidden_states=True)
        for layer in range(n_layers):
            per_layer[layer].append(out.hidden_states[layer + 1].squeeze(0).float().mean(dim=0).cpu().numpy())
    return {layer: np.stack(v, axis=0) for layer, v in per_layer.items()}


@torch.no_grad()
def mask_fill_generate(model, tokenizer, sequence, mask_fraction, seed, device, max_len=MAX_SEQ_LEN):
    seq = sequence[:max_len]
    enc = tokenizer(seq, return_tensors="pt", truncation=True, max_length=max_len + 2)
    input_ids = enc["input_ids"][0].clone()
    rng = torch.Generator().manual_seed(seed)
    special_ids = set(tokenizer.all_special_ids)
    non_special = torch.tensor([i for i, t in enumerate(input_ids.tolist()) if t not in special_ids])
    n_mask = max(1, int(len(non_special) * mask_fraction))
    perm = torch.randperm(len(non_special), generator=rng)
    mask_positions = non_special[perm[:n_mask]]
    masked_ids = input_ids.clone()
    masked_ids[mask_positions] = tokenizer.mask_token_id
    masked_enc = {"input_ids": masked_ids.unsqueeze(0).to(device), "attention_mask": enc["attention_mask"].to(device)}
    out = model(**masked_enc)
    predicted = out.logits.argmax(dim=-1).squeeze(0).cpu()
    filled = masked_ids.clone(); filled[mask_positions] = predicted[mask_positions]
    toks = tokenizer.convert_ids_to_tokens(filled.tolist())
    return "".join(t for t in toks if t not in tokenizer.all_special_tokens)


def score(sequences):
    return np.array([PROXY(s) for s in sequences])


def load_candidate():
    with open(DATA_PATH) as f:
        records = json.load(f)
    by_seq = {}
    for rec in records:
        seq = rec["sequence"]
        if len(seq) > MAX_SEQ_LEN or len(seq) == 0 or not set(seq) <= CANON:
            continue
        by_seq[seq] = float(rec["label"])
    seqs = sorted(by_seq)
    return seqs, np.array([by_seq[s] for s in seqs])


_IX = {a: k for k, a in enumerate("ACDEFGHIKLMNPQRSTVWY")}


def _comp(seq):
    v = np.zeros(20)
    for c in seq:
        if c in _IX:
            v[_IX[c]] += 1
    return v / max(1, len(seq))


def _separation(low, high):
    return float(np.linalg.norm(np.mean([_comp(s) for s in high], axis=0) - np.mean([_comp(s) for s in low], axis=0)))


def main():
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"CAND={CAND} proxy={PROXY_NAME} device={device} SEED={SEED}", flush=True)

    sequences, labels = load_candidate()
    print(f"usable unique: {len(sequences)} (pos={int((labels>0).sum())}, neg={int((labels==0).sum())})", flush=True)

    rng = np.random.RandomState(SEED)
    order = rng.permutation(len(sequences))
    cut = int(TRAIN_FRACTION * len(sequences))
    train_idx, test_idx = order[:cut], order[cut:]
    train_seqs = [sequences[i] for i in train_idx]; train_labels = labels[train_idx]
    test_seqs = [sequences[i] for i in test_idx]; test_labels = labels[test_idx]

    train_proxy = score(train_seqs); test_proxy = score(test_seqs)
    r_train, p_train = pearsonr(train_proxy, train_labels)
    r_test, p_test = pearsonr(test_proxy, test_labels)
    rho_test, _ = spearmanr(test_proxy, test_labels)
    proxy_validation = {
        "train": {"pearson_r": float(r_train), "p": float(p_train), "n": len(train_seqs)},
        "test": {"pearson_r": float(r_test), "p": float(p_test), "spearman_rho": float(rho_test), "n": len(test_seqs)},
        "min_abs_r_required": MIN_PROXY_ABS_R,
    }
    print(f"proxy vs real label: train r={r_train:+.4f}, test r={r_test:+.4f} (p={p_test:.2e}), rho={rho_test:+.4f}", flush=True)
    assert abs(r_test) >= MIN_PROXY_ABS_R, f"criterion 4 FAILED: proxy r={r_test:+.4f} < {MIN_PROXY_ABS_R}"
    assert r_test > 0, f"proxy sign inverted (r={r_test:+.4f}); flip the proxy in l61_candidates"

    low_threshold = np.percentile(train_labels, 20.0)
    high_threshold = np.percentile(train_labels, 80.0)
    low_group = [s for s, y in zip(train_seqs, train_labels) if y <= low_threshold][:N_VECTOR_SEQS_PER_GROUP]
    high_group = [s for s, y in zip(train_seqs, train_labels) if y >= high_threshold][:N_VECTOR_SEQS_PER_GROUP]
    assert len(low_group) == N_VECTOR_SEQS_PER_GROUP and len(high_group) == N_VECTOR_SEQS_PER_GROUP, \
        f"insufficient vector-group sequences ({len(low_group)}/{len(high_group)})"

    separation = _separation(low_group, high_group)
    proxy_validation["group_separation"] = separation
    proxy_validation["min_group_separation_required"] = MIN_GROUP_SEPARATION
    print(f"G1 separation: {separation:.4f} (require >= {MIN_GROUP_SEPARATION})", flush=True)
    assert separation >= MIN_GROUP_SEPARATION, f"G1 FAILED: separation {separation:.4f} < {MIN_GROUP_SEPARATION}"

    test_median = np.percentile(test_labels, 50.0)
    eval_sequences = [s for s, y in zip(test_seqs, test_labels) if y <= test_median][:N_EVAL_SEQS]
    assert len(eval_sequences) == N_EVAL_SEQS, f"only {len(eval_sequences)} eval sequences"

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME).to(device).eval()
    n_layers = model.config.num_hidden_layers
    print(f"model loaded: {n_layers} layers", flush=True)

    low_act = mean_pooled_activation_all_layers(model, tokenizer, low_group, device)
    high_act = mean_pooled_activation_all_layers(model, tokenizer, high_group, device)
    steering_vectors = {l: torch.tensor(difference_of_means_vector(low_act[l], high_act[l]), dtype=torch.float32, device=device) for l in range(n_layers)}

    rng2 = np.random.RandomState(SEED + 1)
    random_vectors = {}
    for l, vec in steering_vectors.items():
        rv = torch.tensor(rng2.normal(size=vec.shape[0]), dtype=torch.float32, device=device)
        random_vectors[l] = rv / rv.norm() * vec.norm()

    def apply_hooks(vectors, alpha):
        return [model.esm.encoder.layer[l].register_forward_hook(MultiLayerSteeringHook(v, alpha)) for l, v in vectors.items()]

    def gen_then_score(vectors, alpha):
        generated = []
        handles = apply_hooks(vectors, alpha) if alpha != 0.0 else []
        try:
            for i, seq in enumerate(eval_sequences):
                generated.append(mask_fill_generate(model, tokenizer, seq, MASK_FRACTION, SEED + i, device))
        finally:
            for h in handles:
                h.remove()
        return generated, score(generated)

    def score_arm(vectors, alpha):
        g, s = gen_then_score(vectors, alpha)
        return g, s, np.array([is_degenerate_sequence(x) for x in g])

    results = {"candidate": CAND, "proxy": PROXY_NAME, "proxy_validation": proxy_validation,
               "real_direction": {}, "random_control": {}}

    baseline_generated, baseline_scores = gen_then_score(steering_vectors, 0.0)
    baseline_degenerate = np.array([is_degenerate_sequence(s) for s in baseline_generated])
    results["baseline"] = {"mean": float(baseline_scores.mean()), "std": float(baseline_scores.std()),
                           "n": len(baseline_scores), "n_degenerate": int(baseline_degenerate.sum())}
    print(f"baseline mean {baseline_scores.mean():+.4f} degen {baseline_degenerate.sum()}/{len(baseline_degenerate)}", flush=True)

    real_by_alpha, random_by_alpha = {}, {}
    for alpha in ALPHAS:
        real_by_alpha[alpha] = score_arm(steering_vectors, alpha)
        random_by_alpha[alpha] = score_arm(random_vectors, alpha)
        print(f"alpha={alpha}: real {real_by_alpha[alpha][1].mean():+.4f} rand {random_by_alpha[alpha][1].mean():+.4f}", flush=True)

    rvr = {}
    for alpha in ALPHAS:
        _, real_scores, real_deg = real_by_alpha[alpha]
        _, random_scores, random_deg = random_by_alpha[alpha]
        keep = ~real_deg & ~random_deg & ~baseline_degenerate
        n_kept = int(keep.sum())
        results["real_direction"][alpha] = {"mean": float(real_scores.mean()), "n_degenerate": int(real_deg.sum())}
        results["random_control"][alpha] = {"mean": float(random_scores.mean()), "n_degenerate": int(random_deg.sum())}
        if n_kept < MIN_NONDEGENERATE_PAIRS:
            rvr[alpha] = {"point_estimate": None, "ci_lower": None, "ci_upper": None,
                          "significant_at_95pct": False, "n": n_kept, "excluded_reason": f"{n_kept} pairs"}
            continue
        b = paired_bootstrap_mean_diff(random_scores[keep], real_scores[keep], n_boot=N_BOOT, seed=SEED)
        b["pct_sequences_real_beats_random"] = float((real_scores[keep] > random_scores[keep]).mean())
        rvr[alpha] = b
        print(f"  alpha={alpha}: diff={b['point_estimate']:+.4f} [{b['ci_lower']:+.4f},{b['ci_upper']:+.4f}] sig={b['significant_at_95pct']}", flush=True)

    valid = [a for a in SAFE_ALPHAS if rvr[a]["point_estimate"] is not None]
    dose_ok = dose_response_is_monotonic_then_collapsing(list(valid), [rvr[a]["point_estimate"] for a in valid]) if len(valid) >= 3 else False
    best_alpha = max((a for a in SAFE_ALPHAS if rvr[a].get("significant_at_95pct")),
                     key=lambda a: rvr[a]["point_estimate"], default=None)

    robustness = None
    if best_alpha is not None:
        real_gen, _, real_deg = real_by_alpha[best_alpha]
        random_gen, _, random_deg = random_by_alpha[best_alpha]
        counts = Counter()
        for seq, base in zip(real_gen, baseline_generated):
            for a, b_ in zip(seq, base):
                if a != b_:
                    counts[a] += 1
        top = frozenset(r for r, _ in counts.most_common(2))
        keep = ~real_deg & ~random_deg & ~baseline_degenerate
        try:
            re_s = np.array([proxy_excluding(PROXY_NAME, s, top) for s in np.array(real_gen)[keep]])
            ra_s = np.array([proxy_excluding(PROXY_NAME, s, top) for s in np.array(random_gen)[keep]])
            eb = paired_bootstrap_mean_diff(ra_s, re_s, n_boot=N_BOOT, seed=SEED)
            robustness = {"alpha": best_alpha, "excluded_residues": sorted(top), "diff_with_exclusion": eb}
            print(f"robustness excl {sorted(top)}: diff={eb['point_estimate']:+.4f} sig={eb['significant_at_95pct']}", flush=True)
        except ValueError as e:
            robustness = {"alpha": best_alpha, "excluded_residues": sorted(top), "error": str(e)}

    crit1 = best_alpha is not None
    crit2 = dose_ok
    crit3 = robustness is not None and robustness.get("diff_with_exclusion", {}).get("significant_at_95pct", False)
    crit4 = bool(abs(r_test) >= MIN_PROXY_ABS_R)
    crit5 = None
    crit6 = len(eval_sequences) >= 150
    criteria = {"1_beats_random_control": crit1, "2_dose_response": crit2, "3_residue_robust": crit3,
                "4_proxy_pre_validated": crit4, "5_beats_existing_technique": crit5, "6_adequately_powered": crit6}
    operative = [v for v in criteria.values() if v is not None]
    if all(operative):
        decision = "PASS"
    elif not crit1 or not crit3:
        decision = "KILL"
    elif sum(bool(v) for v in operative) >= 3:
        decision = "AMBIGUOUS"
    else:
        decision = "KILL"

    verdict = {"candidate": CAND, "proxy": PROXY_NAME, "criteria": criteria, "decision": decision,
               "best_alpha": best_alpha, "seed": SEED, "proxy_validation": proxy_validation,
               "real_vs_random_by_alpha": rvr, "robustness_check": robustness}
    print(f"\n=== L61 VERDICT [{CAND}] ===", flush=True)
    print(json.dumps(verdict, indent=2, default=str), flush=True)
    results["verdict"] = verdict
    results["raw_scores"] = {"baseline": baseline_scores.tolist(),
                             **{f"real__{a}": real_by_alpha[a][1].tolist() for a in ALPHAS},
                             **{f"random__{a}": random_by_alpha[a][1].tolist() for a in ALPHAS}}
    results["eval_sequences"] = eval_sequences
    with open(OUT_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Saved {OUT_DIR / 'results.json'}", flush=True)


if __name__ == "__main__":
    main()
