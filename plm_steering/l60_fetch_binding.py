"""L60: fetch a CROSS-PROTEIN, INTRINSIC binding dataset from UniProt.

Context: L53 tried to steer binding AFFINITY on a single-backbone KRAS DMS
(6k point mutants of one protein) and got a flat null at every alpha; its
group separation was 0.0033, i.e. the low/high groups were compositionally
indistinguishable, so the difference-of-means vector had no signal. L53:92
named "a cross-protein binding dataset analogous to L54's DLKcat" as the
natural next test.

But protein-protein binding AFFINITY (Kd of A for B) is relational -- a
function of two sequences, not one -- so it fails L56's intrinsic-property
gate for the same reason immunogenicity (host MHC dependence) did. The
faithful cross-protein AND intrinsic reframing is a binding CAPABILITY whose
partner is generic: DNA-binding. A DNA-binding protein binds the phosphate
backbone by virtue of its own sequence, independent of which DNA -- intrinsic,
cross-protein, abundant, and with a documented compositional signature
(Lys/Arg enrichment at nucleic-acid interfaces).

Two reviewed Swiss-Prot pools, length 50-400 aa, canonical residues:
  - DNA-binding pool: keyword KW-0238 (DNA-binding); label = 1
  - control pool: NOT DNA-binding and NOT RNA-binding (KW-0694); label = 0

Writes data_cache/binding/uniprot_dnabinding.json:
  [{acc, sequence, length, dna_binding}, ...]
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "data_cache" / "binding"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUT_DIR / "uniprot_dnabinding.json"

BASE = "https://rest.uniprot.org/uniprotkb/search"
BIND_QUERY = "(keyword:KW-0238) AND (reviewed:true) AND (length:[50 TO 400])"
CTRL_QUERY = "(reviewed:true) AND (length:[50 TO 400]) NOT (keyword:KW-0238) NOT (keyword:KW-0694)"
BIND_PAGES = 8   # up to 4000
CTRL_PAGES = 8   # up to 4000


def _fetch_pages(query: str, fields: str, max_pages: int):
    params = urllib.parse.urlencode(
        {"query": query, "fields": fields, "format": "tsv", "size": "500"}
    )
    url = f"{BASE}?{params}"
    rows, page, header = [], 0, None
    while url and page < max_pages:
        req = urllib.request.Request(url, headers={"User-Agent": "esmplm-steering-l60/1.0"})
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


def main():
    print(f"fetching DNA-binding pool: {BIND_QUERY}", flush=True)
    binders = _fetch_pages(BIND_QUERY, "accession,length,sequence", BIND_PAGES)
    print(f"fetching control pool: {CTRL_QUERY}", flush=True)
    controls = _fetch_pages(CTRL_QUERY, "accession,length,sequence", CTRL_PAGES)

    records, seen = [], set()

    def add(rows, label):
        n = 0
        for r in rows:
            seq = (r.get("Sequence") or "").strip().upper()
            if not seq or seq in seen:
                continue
            seen.add(seq)
            records.append({"acc": r.get("Entry"), "sequence": seq,
                            "length": len(seq), "dna_binding": label})
            n += 1
        return n

    n_bind = add(binders, 1.0)
    n_ctrl = add(controls, 0.0)
    with open(OUT_PATH, "w") as f:
        json.dump(records, f)
    print(f"\nwrote {len(records)} records to {OUT_PATH}", flush=True)
    print(f"  DNA-binding: {n_bind}, control: {n_ctrl}", flush=True)


if __name__ == "__main__":
    main()
