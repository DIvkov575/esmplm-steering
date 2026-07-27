#!/usr/bin/env bash
# Downloads the real datasets used by L42 (thermostability) and L43
# (solubility). Both are public HuggingFace datasets, fetched via direct
# HTTP -- no auth, no exotic client library.
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p plm_steering/data_cache/meltome
curl -sL "https://huggingface.co/datasets/hazemessam/meltome/resolve/main/mixed_split.csv" \
  -o plm_steering/data_cache/meltome/mixed_split.csv

mkdir -p plm_steering/data_cache/solubility
curl -sL "https://huggingface.co/datasets/hazemessam/solubility/resolve/main/train.csv" \
  -o plm_steering/data_cache/solubility/train.csv
curl -sL "https://huggingface.co/datasets/hazemessam/solubility/resolve/main/test.csv" \
  -o plm_steering/data_cache/solubility/test.csv

echo "Done. meltome: $(wc -l < plm_steering/data_cache/meltome/mixed_split.csv) lines, solubility train: $(wc -l < plm_steering/data_cache/solubility/train.csv) lines"
