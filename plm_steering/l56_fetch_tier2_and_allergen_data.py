"""One-time fetch for L56's Tier-2 (mass-spec MHC-II presentation) and
allergen-cross-check datasets, neither of which was cached in this repo --
the module docstring in l56_immunogenicity_proxy_validation.py cited AUC
numbers for both (Tier 2: 0.560; allergen check: 0.430-0.541) with no
fetch or computation code backing them anywhere in this repo's history.

Run once: python3 -m plm_steering.l56_fetch_tier2_and_allergen_data

Writes:
  data_cache/immunogenicity/mhcii_el.csv        (peptide, score) deduped,
                                                 downsampled from the full
                                                 7.05M-row HuggingFace
                                                 O047/MHC-II_EL_Data release
  data_cache/immunogenicity/allergen.fasta      1,020 UniProt reviewed
                                                 allergens (keyword KW-0020)
  data_cache/immunogenicity/nonallergen.fasta   length-matched non-allergens,
                                                 reviewed UniProtKB entries
                                                 without KW-0020, length
                                                 50-400aa, 3x the allergen
                                                 count per length decile
"""
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data_cache" / "immunogenicity"
DATA_DIR.mkdir(parents=True, exist_ok=True)

EL_URL = "https://huggingface.co/datasets/O047/MHC-II_EL_Data/resolve/main/el_dataset.csv"
EL_TOTAL_ROWS = 7_053_694  # the full dataset's row count, for computing the sampling fraction
UNIPROT_SEARCH = "https://rest.uniprot.org/uniprotkb/search"
SEED = 0
CANONICAL = frozenset("ACDEFGHIKLMNPQRSTVWY")
NONALLERGEN_MULTIPLIER = 3  # matches the doc's ~3x allergen count (1,020 -> ~3,000+)
EL_SAMPLE_TARGET = 50_000  # rows to sample from the 7.05M-row source before dedup


def fetch_el_dataset(out_path=DATA_DIR / "mhcii_el.csv", chunksize=500_000):
    """Streams the full 7.05M-row EL dataset (~680MB, never written to disk
    in full -- too large for this repo's "commit the real evidence, not bulk
    data" convention) and keeps a fixed-seed random sample of EL_SAMPLE_TARGET
    rows, deduped by peptide (majority vote on score for the small fraction of
    peptides seen with conflicting labels across alleles/contexts). Written
    as a (peptide, score) CSV -- the same shape Tier 1/3's `is_usable`-filtered
    peptide sets use. This preserves the source's real class imbalance
    (presented peptides are a small minority), unlike a stratified sample.
    """
    if out_path.exists():
        print(f"{out_path} already exists, skipping fetch")
        return
    print(f"streaming {EL_URL} (~680MB, sampling ~{EL_SAMPLE_TARGET} rows, not saved in full)...", flush=True)
    sample_frac = EL_SAMPLE_TARGET / EL_TOTAL_ROWS * 1.5  # oversample before canonical-filter/dedup trim
    chunks = []
    t0 = time.time()
    n_rows = 0
    for chunk in pd.read_csv(EL_URL, usecols=["peptide", "score"], chunksize=chunksize):
        chunks.append(chunk.sample(frac=sample_frac, random_state=SEED))
        n_rows += len(chunk)
        print(f"  {n_rows} rows streamed ({time.time()-t0:.0f}s)", flush=True)

    df = pd.concat(chunks, ignore_index=True)
    df = df[df.peptide.apply(lambda s: isinstance(s, str) and set(s) <= CANONICAL)]
    dedup = df.groupby("peptide")["score"].mean().reset_index()
    dedup["score"] = (dedup["score"] >= 0.5).astype(float)
    dedup.to_csv(out_path, index=False)
    print(f"wrote {len(dedup)} unique canonical peptides "
          f"({int((dedup['score']==1.0).sum())} presented / "
          f"{int((dedup['score']==0.0).sum())} not) to {out_path}", flush=True)


def _fetch_uniprot_fasta(query, max_records=None):
    sequences = []
    url = f"{UNIPROT_SEARCH}?query={urllib.parse.quote(query)}&format=fasta&size=500"
    while url:
        req = urllib.request.Request(url, headers={"User-Agent": "python-urllib"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            link_header = resp.headers.get("Link", "")
        current_seq = []
        for line in body.splitlines():
            if line.startswith(">"):
                if current_seq:
                    sequences.append("".join(current_seq))
                current_seq = []
            else:
                current_seq.append(line.strip())
        if current_seq:
            sequences.append("".join(current_seq))
        url = None
        for part in link_header.split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().lstrip("<").rstrip(">")
        if max_records is not None and len(sequences) >= max_records:
            sequences = sequences[:max_records]
            break
        print(f"  fetched {len(sequences)} sequences so far...", flush=True)
    return sequences


def fetch_allergens(out_path=DATA_DIR / "allergen.fasta"):
    if out_path.exists():
        print(f"{out_path} already exists, skipping fetch")
        return
    print("fetching UniProt reviewed allergens (keyword KW-0020)...", flush=True)
    sequences = _fetch_uniprot_fasta("keyword:KW-0020 AND reviewed:true")
    sequences = [s for s in sequences if 50 <= len(s) <= 400 and set(s) <= CANONICAL]
    with open(out_path, "w") as f:
        for i, seq in enumerate(sequences):
            f.write(f">allergen_{i}\n{seq}\n")
    print(f"wrote {len(sequences)} length-filtered allergens to {out_path}", flush=True)


# NCBI/UniProt taxon IDs for the coarse lineage buckets allergen source
# organisms fall into. Matching non-allergens by BROAD lineage (not exact
# species) is necessary because most individual allergen-source species
# (obscure mites, wasps, molds) have almost no non-allergen reviewed
# sequences at all -- e.g. Olea europaea (olive, 102 allergens) has exactly
# 1 non-allergen reviewed protein in UniProt. Matching only by length while
# leaving the non-allergen query organism-unrestricted pulls a set that is
# ~100% Homo sapiens by UniProt's default relevance ranking, which turned
# out to inflate every proxy's apparent AUC via a species/taxonomic
# composition difference having nothing to do with allergenicity -- caught
# by checking the non-allergen fetch's actual organism composition before
# trusting the resulting AUC numbers.
LINEAGE_TAXON_IDS = {
    "plant": 3193,       # Viridiplantae
    "arthropod": 6656,   # Arthropoda
    "chordate": 7711,    # Chordata
    "fungi": 4751,       # Fungi
    "other_animal": 33208,  # Metazoa (catch-all for non-arthropod, non-chordate animals)
}


def _classify_lineage(lineage_names):
    s = set(lineage_names)
    if "Viridiplantae" in s:
        return "plant"
    if "Fungi" in s:
        return "fungi"
    if "Metazoa" in s:
        if "Arthropoda" in s:
            return "arthropod"
        if "Chordata" in s:
            return "chordate"
        return "other_animal"
    return "other"


def _fetch_lineage(taxon_id):
    url = f"https://rest.uniprot.org/taxonomy/{taxon_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "python-urllib"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        import json
        data = json.load(resp)
    return [entry.get("scientificName") for entry in data.get("lineage", [])]


def _allergen_organism_buckets(allergen_path=DATA_DIR / "allergen.fasta"):
    """Re-derives each allergen's source-organism lineage bucket by
    re-querying UniProt for the allergen set's organism IDs (the FASTA
    format alone doesn't carry organism_id, so this re-fetches metadata
    only, not sequences)."""
    ids_and_lengths = []
    url = ("https://rest.uniprot.org/uniprotkb/search?query="
           + urllib.parse.quote("keyword:KW-0020 AND reviewed:true")
           + "&format=tsv&fields=organism_id,length&size=500")
    while url:
        req = urllib.request.Request(url, headers={"User-Agent": "python-urllib"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            link = resp.headers.get("Link", "")
        lines = body.strip().split("\n")[1:]  # skip header
        for line in lines:
            tax_id, length = line.split("\t")
            ids_and_lengths.append((int(tax_id), int(length)))
        m = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = m.group(1) if m else None
    return ids_and_lengths


LENGTH_BIN_EDGES = list(range(50, 425, 25))  # 25aa bins from 50 to 400


def fetch_nonallergens(allergen_path=DATA_DIR / "allergen.fasta", out_path=DATA_DIR / "nonallergen.fasta"):
    """Length-AND-lineage-matched non-allergens: for each (coarse taxonomic
    bucket, 25aa length bin) an allergen falls into, fetch
    NONALLERGEN_MULTIPLIER times as many reviewed, non-allergen UniProtKB
    sequences from that SAME lineage bucket and length bin, so the AUC
    comparison isn't confounded by either broad taxonomic composition or
    length. Binning jointly (not lineage alone) matters: a first attempt
    matched only by lineage and length range 50-400 as a whole, and the
    resulting non-allergen set skewed much longer than the allergens within
    every bucket (mean 263aa vs 186aa) -- length alone then predicted the
    allergen/non-allergen label at r=-0.36, and a fitted composition model
    hit AUC=0.88 on pure length/composition confound, not allergenicity.
    """
    if out_path.exists():
        print(f"{out_path} already exists, skipping fetch")
        return

    ids_and_lengths = _allergen_organism_buckets(allergen_path)
    ids_and_lengths = [(t, l) for t, l in ids_and_lengths if 50 <= l <= 400]
    unique_taxa = sorted(set(t for t, _ in ids_and_lengths))
    print(f"resolving lineage for {len(unique_taxa)} distinct allergen source organisms...", flush=True)
    bucket_by_taxon = {}
    for taxon_id in unique_taxa:
        try:
            bucket_by_taxon[taxon_id] = _classify_lineage(_fetch_lineage(taxon_id))
        except Exception:
            bucket_by_taxon[taxon_id] = "other"

    df = pd.DataFrame(ids_and_lengths, columns=["taxon_id", "length"])
    df["bucket"] = df["taxon_id"].map(bucket_by_taxon)
    df = df[df.bucket != "other"]
    df["length_bin"] = pd.cut(df["length"], bins=LENGTH_BIN_EDGES, right=False)
    joint_counts = df.groupby(["bucket", "length_bin"], observed=True).size()
    print(f"allergen (bucket, length-bin) counts:\n{joint_counts}", flush=True)

    sequences = []
    for (bucket, length_bin), n_allergen in joint_counts.items():
        taxon_id = LINEAGE_TAXON_IDS[bucket]
        lo, hi = int(length_bin.left), int(length_bin.right)
        target_n = int(n_allergen) * NONALLERGEN_MULTIPLIER
        query = f"NOT keyword:KW-0020 AND reviewed:true AND taxonomy_id:{taxon_id} AND length:[{lo} TO {hi}]"
        print(f"  bucket={bucket} length=[{lo},{hi}): fetching {target_n} non-allergens...", flush=True)
        sequences.extend(_fetch_uniprot_fasta(query, max_records=target_n))

    sequences = [s for s in sequences if set(s) <= CANONICAL]
    with open(out_path, "w") as f:
        for i, seq in enumerate(sequences):
            f.write(f">nonallergen_{i}\n{seq}\n")
    print(f"wrote {len(sequences)} length-and-lineage-matched non-allergens to {out_path}", flush=True)


def main():
    fetch_el_dataset()
    fetch_allergens()
    fetch_nonallergens()
    return 0


if __name__ == "__main__":
    sys.exit(main())
