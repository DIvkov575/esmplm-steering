"""L59: fetch a CROSS-PROTEIN transmembrane dataset from UniProt.

Target property: transmembrane-residue fraction (fraction of a protein's
residues that fall inside annotated TRANSMEM segments). This is intrinsic to
the single sequence (passes L56's intrinsic-property gate trivially, unlike
binding/immunogenicity), and it varies ACROSS proteins (soluble .. multipass
membrane), which is the cross-protein regime L54 showed is required for the
difference-of-means construction to have any compositional signal at all.

Two reviewed (Swiss-Prot) pools, length 50-400 aa, canonical residues:
  - membrane pool: keyword KW-0812 (Transmembrane) WITH ft_transmem ranges;
    label = sum(TRANSMEM segment lengths) / length  (continuous, >0)
  - soluble pool: cytoplasm-localized (SL-0091), NOT transmembrane; label = 0

Writes data_cache/transmembrane/uniprot_tm.json:
  [{acc, sequence, length, tm_residues, tm_fraction}, ...]
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "data_cache" / "transmembrane"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUT_DIR / "uniprot_tm.json"

BASE = "https://rest.uniprot.org/uniprotkb/search"
TRANSMEM_RE = re.compile(r"TRANSMEM (\d+)\.\.(\d+)")

MEMBRANE_QUERY = "(keyword:KW-0812) AND (reviewed:true) AND (length:[50 TO 400])"
SOLUBLE_QUERY = "(cc_scl_term:SL-0091) AND (reviewed:true) AND (length:[50 TO 400]) NOT (keyword:KW-0812)"

MEMBRANE_PAGES = 8   # 500/page -> up to 4000 membrane proteins
SOLUBLE_PAGES = 6    # up to 3000 soluble proteins


def _fetch_pages(query: str, fields: str, max_pages: int):
    params = urllib.parse.urlencode(
        {"query": query, "fields": fields, "format": "tsv", "size": "500"}
    )
    url = f"{BASE}?{params}"
    rows, page = [], 0
    while url and page < max_pages:
        req = urllib.request.Request(url, headers={"User-Agent": "esmplm-steering-l59/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            text = resp.read().decode("utf-8")
            link = resp.headers.get("Link", "")
        lines = text.splitlines()
        if page == 0:
            header = lines[0].split("\t")
        rows.extend(dict(zip(header, ln.split("\t"))) for ln in lines[1:] if ln.strip())
        m = re.search(r'<([^>]+)>; rel="next"', link)
        url = m.group(1) if m else None
        page += 1
        print(f"  page {page}: +{len(lines) - 1} rows (total {len(rows)})", flush=True)
        time.sleep(0.2)
    return rows


def _tm_residues(ft_transmem: str) -> int:
    total = 0
    for a, b in TRANSMEM_RE.findall(ft_transmem or ""):
        total += int(b) - int(a) + 1
    return total


def main():
    print(f"fetching membrane pool: {MEMBRANE_QUERY}", flush=True)
    membrane = _fetch_pages(
        MEMBRANE_QUERY, "accession,length,ft_transmem,sequence", MEMBRANE_PAGES
    )
    print(f"fetching soluble pool: {SOLUBLE_QUERY}", flush=True)
    soluble = _fetch_pages(SOLUBLE_QUERY, "accession,length,sequence", SOLUBLE_PAGES)

    records, seen_seq = [], set()
    n_membrane_kept = 0
    for r in membrane:
        seq = (r.get("Sequence") or "").strip().upper()
        if not seq or seq in seen_seq:
            continue
        tm = _tm_residues(r.get("Transmembrane") or "")
        if tm == 0:  # keyword present but no parseable range -> drop, ambiguous label
            continue
        seen_seq.add(seq)
        records.append({
            "acc": r.get("Entry"), "sequence": seq, "length": len(seq),
            "tm_residues": tm, "tm_fraction": tm / len(seq),
        })
        n_membrane_kept += 1
    for r in soluble:
        seq = (r.get("Sequence") or "").strip().upper()
        if not seq or seq in seen_seq:
            continue
        seen_seq.add(seq)
        records.append({
            "acc": r.get("Entry"), "sequence": seq, "length": len(seq),
            "tm_residues": 0, "tm_fraction": 0.0,
        })

    with open(OUT_PATH, "w") as f:
        json.dump(records, f)
    fr = [x["tm_fraction"] for x in records]
    print(f"\nwrote {len(records)} records to {OUT_PATH}", flush=True)
    print(f"  membrane (tm>0): {n_membrane_kept}, soluble (tm=0): {len(records) - n_membrane_kept}", flush=True)
    print(f"  tm_fraction: min={min(fr):.3f} median={sorted(fr)[len(fr)//2]:.3f} max={max(fr):.3f}", flush=True)


if __name__ == "__main__":
    main()
