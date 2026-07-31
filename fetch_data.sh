#!/usr/bin/env bash
# Downloads the real datasets used by L42 (thermostability) and L43
# (solubility). Both are public HuggingFace datasets, fetched via direct
# HTTP -- no auth, no exotic client library. The L48 PDB structures are
# already committed under plm_steering/data_cache/pdb_structures/ (small,
# 808K total) -- this function only exists to regenerate them if deleted.
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

mkdir -p plm_steering/data_cache/pdb_structures
for pdb in 1UBQ 1CRN 1LYZ 1MBN 2LZM 1PGA 1TEN 1SHG; do
  curl -sL "https://files.rcsb.org/download/${pdb}.pdb" -o "plm_steering/data_cache/pdb_structures/${pdb}.pdb"
done

echo "Done. meltome: $(wc -l < plm_steering/data_cache/meltome/mixed_split.csv) lines, solubility train: $(wc -l < plm_steering/data_cache/solubility/train.csv) lines, pdb_structures: $(ls plm_steering/data_cache/pdb_structures/*.pdb | wc -l) files"
