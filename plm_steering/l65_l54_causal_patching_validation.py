"""L65 -- causal validation of L54 (catalytic-activity steering) by ACTIVATION
PATCHING, the same second, independent intervention L47 used to validate L42's
thermostability steering.

WHY THIS EXISTS
    L54 is the project's one clean new-property PASS, but all its evidence comes
    from ONE kind of intervention: ADD alpha*(high-low difference-of-means) to
    the residual stream (the steering hook) and beat a matched-norm random
    control. A skeptic can ask whether that is a genuine causal handle on
    catalytic-activity information or an idiosyncrasy of additive perturbation.
    L47 answered the same question for L42 with a DIFFERENT intervention that
    converged on the same conclusion -- activation PATCHING: SUBSTITUTE the mean
    high-Tm activation for a low-Tm sequence's own activation, at the masked
    positions, and check the prediction shifts toward the target property more
    than substituting the low-Tm mean.

    This ports L47's Task-B harness verbatim to catalytic activity: per layer,
    patch the mean HIGH-kcat activation vs the mean LOW-kcat activation into the
    masked positions of low-kcat eval enzymes, score the mask-fill output with
    L54's catalytic proxy, paired-bootstrap high-vs-low, and sign-test across
    layers. If high-kcat patching beats low-kcat patching at many layers
    (distinct intervention, same direction as L54's steering), L54's causal
    story is triangulated, not resting on the additive hook alone.

    Uses N_EVAL=60 (L47 Task-B's precedent) to bound cost; the question is
    causal direction across layers, not a new-property power claim.

WHY NOT reuse l47 directly: L47's code was pruned from this repo (it lives in
    biostat). The MaskedPositionPatchHook / masked-position generation below are
    reproduced verbatim from biostat src/l38/l47_task_b_patching_validation.py;
    L54's data pipeline, proxy, and primitives are imported from l54_run_repro.

RUNNABLE CHECK
    python3 -m plm_steering.l65_l54_causal_patching_validation
    Needs ESM2-650M; DLKcat data ships in-tree. ~15-20 min.
"""
import json
from pathlib import Path

import numpy as np
import torch
from scipy.stats import binomtest
from transformers import AutoModelForMaskedLM, AutoTokenizer

from plm_steering.l42_steering_repro import is_degenerate_sequence, paired_bootstrap_mean_diff
from plm_steering.l54_run_repro import (
    MASK_FRACTION,
    MAX_SEQ_LEN,
    MODEL_NAME,
    N_VECTOR_SEQS_PER_GROUP,
    SEED,
    TRAIN_FRACTION,
    load_dlkcat,
    mean_pooled_activation_all_layers,
    score_catalytic_activity,
)

OUT_DIR = Path(__file__).resolve().parent / "l65_l54_patching_out"
N_EVAL = 60          # L47 Task-B precedent; keeps 33-layer x 2-patch sweep tractable
N_BOOT = 10000
MIN_NONDEGENERATE_PAIRS = 30


class MaskedPositionPatchHook:
    """Verbatim from L47: replace a layer's residual output with a fixed vector
    ONLY at the masked positions (true substitution, not L54's additive hook)."""

    def __init__(self, patch_vector, mask_positions):
        self.patch_vector = patch_vector
        self.mask_positions = mask_positions

    def __call__(self, module, inputs, output):
        is_tuple = isinstance(output, tuple)
        current = output[0] if is_tuple else output
        patched = current.clone()
        patched[:, self.mask_positions, :] = self.patch_vector.to(current.device, current.dtype)
        return (patched,) + output[1:] if is_tuple else patched


def get_mask_positions(tokenizer, sequence, mask_fraction, seed, max_len):
    seq = sequence[:max_len]
    enc = tokenizer(seq, return_tensors="pt", truncation=True, max_length=max_len + 2)
    input_ids = enc["input_ids"][0].clone()
    rng = torch.Generator().manual_seed(seed)
    special_ids = set(tokenizer.all_special_ids)
    non_special = torch.tensor([i for i, t in enumerate(input_ids.tolist()) if t not in special_ids])
    n_mask = max(1, int(len(non_special) * mask_fraction))
    perm = torch.randperm(len(non_special), generator=rng)
    return input_ids, non_special[perm[:n_mask]], enc["attention_mask"][0]


@torch.no_grad()
def mask_fill_with_patch(model, tokenizer, sequence, seed, device, patch_vector=None, patch_layer=None):
    input_ids, mask_positions, attn = get_mask_positions(tokenizer, sequence, MASK_FRACTION, seed, MAX_SEQ_LEN)
    masked = input_ids.clone()
    masked[mask_positions] = tokenizer.mask_token_id
    handle = None
    if patch_vector is not None:
        handle = model.esm.encoder.layer[patch_layer].register_forward_hook(
            MaskedPositionPatchHook(patch_vector, mask_positions))
    try:
        out = model(input_ids=masked.unsqueeze(0).to(device), attention_mask=attn.unsqueeze(0).to(device))
    finally:
        if handle is not None:
            handle.remove()
    pred = out.logits.argmax(dim=-1).squeeze(0).cpu()
    filled = masked.clone()
    filled[mask_positions] = pred[mask_positions]
    toks = tokenizer.convert_ids_to_tokens(filled.tolist())
    return "".join(t for t in toks if t not in tokenizer.all_special_tokens)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"device: {device}", flush=True)

    # L54's exact data pipeline: dedup, train/test split, low/high-kcat groups,
    # low-kcat held-out eval enzymes.
    sequences, labels = load_dlkcat()
    rng = np.random.RandomState(SEED)
    order = rng.permutation(len(sequences))
    cut = int(TRAIN_FRACTION * len(sequences))
    train_seqs = [sequences[i] for i in order[:cut]]
    train_labels = labels[order[:cut]]
    test_seqs = [sequences[i] for i in order[cut:]]
    test_labels = labels[order[cut:]]
    low_t, high_t = np.percentile(train_labels, 20.0), np.percentile(train_labels, 80.0)
    low_group = [s for s, y in zip(train_seqs, train_labels) if y <= low_t][:N_VECTOR_SEQS_PER_GROUP]
    high_group = [s for s, y in zip(train_seqs, train_labels) if y >= high_t][:N_VECTOR_SEQS_PER_GROUP]
    test_median = np.percentile(test_labels, 50.0)
    eval_sequences = [s for s, y in zip(test_seqs, test_labels) if y <= test_median][:N_EVAL]
    print(f"{len(low_group)} low / {len(high_group)} high kcat vectors; {len(eval_sequences)} low-kcat eval enzymes",
          flush=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME).to(device).eval()
    n_layers = model.config.num_hidden_layers
    print(f"model loaded: {n_layers} layers", flush=True)

    low_act = mean_pooled_activation_all_layers(model, tokenizer, low_group, device)
    high_act = mean_pooled_activation_all_layers(model, tokenizer, high_group, device)
    high_patch = {l: torch.tensor(high_act[l].mean(axis=0), dtype=torch.float32, device=device) for l in range(n_layers)}
    low_patch = {l: torch.tensor(low_act[l].mean(axis=0), dtype=torch.float32, device=device) for l in range(n_layers)}

    def gen_patched(patch_vectors, layer):
        g = [mask_fill_with_patch(model, tokenizer, s, SEED + i, device, patch_vectors[layer], layer)
             for i, s in enumerate(eval_sequences)]
        return g, score_catalytic_activity(g)

    print("\n=== baseline (no patch) ===", flush=True)
    baseline_gen = [mask_fill_with_patch(model, tokenizer, s, SEED + i, device) for i, s in enumerate(eval_sequences)]
    baseline_deg = np.array([is_degenerate_sequence(s) for s in baseline_gen])
    print(f"baseline degenerate: {baseline_deg.sum()}/{len(baseline_deg)}", flush=True)

    by_layer = {}
    for layer in range(n_layers):
        hg, hs = gen_patched(high_patch, layer)
        lg, ls = gen_patched(low_patch, layer)
        hd = np.array([is_degenerate_sequence(s) for s in hg])
        ld = np.array([is_degenerate_sequence(s) for s in lg])
        keep = ~hd & ~ld & ~baseline_deg
        n = int(keep.sum())
        e = {"high_patch_mean": float(hs.mean()), "low_patch_mean": float(ls.mean()),
             "n_degenerate_high": int(hd.sum()), "n_degenerate_low": int(ld.sum())}
        if n < MIN_NONDEGENERATE_PAIRS:
            e.update({"point_estimate": None, "significant_at_95pct": False, "n": n})
        else:
            e.update(paired_bootstrap_mean_diff(ls[keep], hs[keep], n_boot=N_BOOT, seed=SEED))  # high - low
        by_layer[layer] = e
        mark = " <-- SIG (high>low)" if (e.get("point_estimate") or 0) > 0 and e["significant_at_95pct"] else \
               " <-- SIG (high<low)" if e["significant_at_95pct"] else ""
        print(f"layer {layer:2d}: high={e['high_patch_mean']:.4f} low={e['low_patch_mean']:.4f} "
              f"diff={e.get('point_estimate')} n={e['n']}{mark}", flush=True)

    valid = [e for e in by_layer.values() if e.get("point_estimate") is not None]
    n_high_gt_low = sum(1 for e in valid if e["point_estimate"] > 0)
    sig_high = [l for l, e in by_layer.items() if e.get("point_estimate", 0) and e["point_estimate"] > 0 and e["significant_at_95pct"]]
    sig_low = [l for l, e in by_layer.items() if e.get("point_estimate") is not None and e["point_estimate"] < 0 and e["significant_at_95pct"]]
    sign = binomtest(n_high_gt_low, len(valid), 0.5, alternative="two-sided") if valid else None
    sign_p = float(sign.pvalue) if sign is not None else None

    causal = (sign_p is not None and sign_p < 0.05 and n_high_gt_low > len(valid) / 2 and len(sig_high) >= 1)
    summary = {
        "intervention": "activation PATCHING (substitute high- vs low-kcat mean at masked positions) -- "
                        "distinct from L54's additive steering hook",
        "n_eval": len(eval_sequences), "n_layers_valid": len(valid),
        "n_layers_high_beats_low": n_high_gt_low,
        "sign_test_p": sign_p,
        "layers_high_sig_beats_low": sig_high,
        "layers_low_sig_beats_high": sig_low,
        "baseline_mean": float(score_catalytic_activity(baseline_gen).mean()),
        "conclusion": (
            f"CAUSALLY CONFIRMED via a 2nd intervention: high-kcat patching beats low-kcat patching at "
            f"{n_high_gt_low}/{len(valid)} layers (sign-test p={sign_p:.2g}), significant at "
            f"{len(sig_high)} layer(s). Patching (substitution) converges with L54's steering (addition) "
            f"-- the catalytic direction is a real causal handle, not an additive-hook artifact."
            if causal else
            f"NOT confirmed by patching: high beats low at only {n_high_gt_low}/{len(valid)} layers "
            f"(sign-test p={sign_p}); the additive steering result does not clearly reproduce under "
            f"substitution. L54's PASS still stands on its own evidence, but this triangulation is inconclusive."),
    }
    with open(OUT_DIR / "results.json", "w") as f:
        json.dump({"by_layer": by_layer, "summary": summary}, f, indent=2, default=str)
    print("\n=== L65 CONCLUSION ===", flush=True)
    print(summary["conclusion"], flush=True)
    print(f"saved to {OUT_DIR / 'results.json'}", flush=True)


if __name__ == "__main__":
    main()
