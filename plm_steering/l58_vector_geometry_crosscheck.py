"""L58: rebuild L54 (catalytic activity), L55 (intrinsic disorder), and L57
(expression yield)'s per-layer difference-of-means steering vectors from
scratch, using each target's exact SEED=0 vector-building split and group
logic, and compute pairwise cosine similarity between them.

Backs the specific numeric claim in docs/L57_EXPRESSION_STEERING.md and the
paper drafts ("+0.30 overall, rising to +0.40-0.50 at deep layers" between
L57 and L55's vectors) with a runnable, committed script -- that claim
previously had no computing code anywhere in this repo's history.

Saves both the raw per-layer vectors (as .npy, one file per target) and the
pairwise cosine-similarity results (as JSON) to l58_vector_geometry_out/,
so this cross-check is reproducible without rebuilding the vectors again.

    python3 -m plm_steering.l58_vector_geometry_crosscheck
"""
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

from plm_steering.l42_steering_repro import difference_of_means_vector
from plm_steering.l54_run_repro import MAX_SEQ_LEN as L54_MAX_SEQ_LEN
from plm_steering.l54_run_repro import N_VECTOR_SEQS_PER_GROUP as L54_N_VECTOR_SEQS_PER_GROUP
from plm_steering.l54_run_repro import SEED as L54_SEED
from plm_steering.l54_run_repro import TRAIN_FRACTION as L54_TRAIN_FRACTION
from plm_steering.l54_run_repro import load_dlkcat
from plm_steering.l55_run_repro import DATA_PATH as L55_DATA_PATH
from plm_steering.l55_run_repro import MAX_SEQ_LEN as L55_MAX_SEQ_LEN
from plm_steering.l55_run_repro import N_VECTOR_SEQS_PER_GROUP as L55_N_VECTOR_SEQS_PER_GROUP
from plm_steering.l55_run_repro import SEED as L55_SEED
from plm_steering.l55_run_repro import VECTOR_POOL_SIZE as L55_VECTOR_POOL_SIZE
from plm_steering.l57_run_repro import DATA_PATH as L57_DATA_PATH
from plm_steering.l57_run_repro import MAX_SEQ_LEN as L57_MAX_SEQ_LEN
from plm_steering.l57_run_repro import N_VECTOR_SEQS_PER_GROUP as L57_N_VECTOR_SEQS_PER_GROUP
from plm_steering.l57_run_repro import SEED as L57_SEED

import pandas as pd

MODEL_NAME = "facebook/esm2_t33_650M_UR50D"
OUT_DIR = Path(__file__).resolve().parent / "l58_vector_geometry_out"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DEEP_LAYERS = (30, 31, 32)  # matches the "deepest layers" claim in docs/L57_EXPRESSION_STEERING.md


@torch.no_grad()
def mean_pooled_activation_all_layers(model, tokenizer, sequences, device, max_len):
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


def build_vectors(model, tokenizer, device, n_layers, low_group, high_group, max_len):
    low_activations = mean_pooled_activation_all_layers(model, tokenizer, low_group, device, max_len)
    high_activations = mean_pooled_activation_all_layers(model, tokenizer, high_group, device, max_len)
    return np.stack(
        [difference_of_means_vector(low_activations[layer], high_activations[layer]) for layer in range(n_layers)],
        axis=0,
    )  # shape (n_layers, d_model)


def l54_groups():
    """Reproduces l54_run_repro.py's exact train split and low/high groups."""
    sequences, labels = load_dlkcat(max_len=L54_MAX_SEQ_LEN)
    rng = np.random.RandomState(L54_SEED)
    order = rng.permutation(len(sequences))
    cut = int(L54_TRAIN_FRACTION * len(sequences))
    train_idx = order[:cut]
    train_seqs = [sequences[i] for i in train_idx]
    train_labels = labels[train_idx]
    low_threshold = np.percentile(train_labels, 20.0)
    high_threshold = np.percentile(train_labels, 80.0)
    low_group = [s for s, y in zip(train_seqs, train_labels) if y <= low_threshold][:L54_N_VECTOR_SEQS_PER_GROUP]
    high_group = [s for s, y in zip(train_seqs, train_labels) if y >= high_threshold][:L54_N_VECTOR_SEQS_PER_GROUP]
    return low_group, high_group


def l55_groups():
    """Reproduces l55_run_repro.py's exact vector pool and low/high groups."""
    df = pd.read_csv(L55_DATA_PATH)
    df = df[df["sequence"].str.len() <= L55_MAX_SEQ_LEN].reset_index(drop=True)
    shuffled = df.sample(frac=1.0, random_state=L55_SEED).reset_index(drop=True)
    vector_pool = shuffled.iloc[:L55_VECTOR_POOL_SIZE]
    labels = vector_pool["disorder_fraction"].astype(float).values
    low_threshold = np.percentile(labels, 20.0)
    high_threshold = np.percentile(labels, 80.0)
    low_group = vector_pool[vector_pool["disorder_fraction"].astype(float) <= low_threshold]["sequence"].tolist()[
        :L55_N_VECTOR_SEQS_PER_GROUP
    ]
    high_group = vector_pool[vector_pool["disorder_fraction"].astype(float) >= high_threshold]["sequence"].tolist()[
        :L55_N_VECTOR_SEQS_PER_GROUP
    ]
    return low_group, high_group


def l57_groups():
    """Reproduces l57_run_repro.py's exact train split and low/high groups."""
    df = pd.read_csv(L57_DATA_PATH)
    df = df[df["sequence"].str.len() <= L57_MAX_SEQ_LEN].reset_index(drop=True)
    train_df = df[df["split"] == "train"].reset_index(drop=True)
    train_shuffled = train_df.sample(frac=1.0, random_state=L57_SEED).reset_index(drop=True)
    labels = train_shuffled["label"].astype(float).values
    low_threshold = np.percentile(labels, 20.0)
    high_threshold = np.percentile(labels, 80.0)
    low_group = train_shuffled[train_shuffled["label"].astype(float) <= low_threshold]["sequence"].tolist()[
        :L57_N_VECTOR_SEQS_PER_GROUP
    ]
    high_group = train_shuffled[train_shuffled["label"].astype(float) >= high_threshold]["sequence"].tolist()[
        :L57_N_VECTOR_SEQS_PER_GROUP
    ]
    return low_group, high_group


def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main():
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"device: {device}", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME).to(device).eval()
    n_layers = model.config.num_hidden_layers
    print(f"model loaded: {MODEL_NAME}, {n_layers} layers", flush=True)

    targets = {
        "l54_catalytic": (l54_groups, L54_MAX_SEQ_LEN),
        "l55_disorder": (l55_groups, L55_MAX_SEQ_LEN),
        "l57_expression": (l57_groups, L57_MAX_SEQ_LEN),
    }

    vectors = {}
    for name, (group_fn, max_len) in targets.items():
        low_group, high_group = group_fn()
        print(f"\n{name}: {len(low_group)} low, {len(high_group)} high -- embedding...", flush=True)
        vec = build_vectors(model, tokenizer, device, n_layers, low_group, high_group, max_len)
        vectors[name] = vec
        np.save(OUT_DIR / f"{name}_steering_vectors.npy", vec)
        print(f"{name}: built and saved ({vec.shape})", flush=True)

    names = list(vectors.keys())
    results = {"deep_layers": list(DEEP_LAYERS), "n_layers": n_layers, "pairwise": {}}
    print("\n=== pairwise cosine similarity ===", flush=True)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a_name, b_name = names[i], names[j]
            a_full = vectors[a_name].flatten()
            b_full = vectors[b_name].flatten()
            full_cos = cosine(a_full, b_full)
            deep_coss = [cosine(vectors[a_name][layer], vectors[b_name][layer]) for layer in DEEP_LAYERS]
            key = f"{a_name}_vs_{b_name}"
            results["pairwise"][key] = {
                "full_vector_cosine": full_cos,
                "deep_layer_cosines": {str(layer): c for layer, c in zip(DEEP_LAYERS, deep_coss)},
                "deep_layer_range": [min(deep_coss), max(deep_coss)],
            }
            print(f"{key}: full={full_cos:+.4f}, deep layers {DEEP_LAYERS}={['%+.4f' % c for c in deep_coss]}",
                  flush=True)

    with open(OUT_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nsaved vectors and results.json to {OUT_DIR}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
