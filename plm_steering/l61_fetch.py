"""L61 generic fetch: CAND=<name> python3 -m plm_steering.l61_fetch

Fetches the candidate's positive (has-property) and negative (control) pools
from UniProt and writes data_cache/l61_<name>/data.json:
  [{acc, sequence, length, label}, ...]  label 1=has-property, 0=control
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from plm_steering.l61_candidates import CANDIDATES, CANON

BASE = "https://rest.uniprot.org/uniprotkb/search"
CAND = os.environ["CAND"]
CFG = CANDIDATES[CAND]
OUT_DIR = Path(__file__).resolve().parent / "data_cache" / f"l61_{CAND}"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUT_DIR / "data.json"
POS_PAGES = 6
NEG_PAGES = 6


def fetch(query, pages):
    params = urllib.parse.urlencode(
        {"query": query, "fields": "accession,length,sequence", "format": "tsv", "size": "500"})
    url = f"{BASE}?{params}"
    rows, header, pg = [], None, 0
    while url and pg < pages:
        req = urllib.request.Request(url, headers={"User-Agent": "esmplm-l61/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode(); link = r.headers.get("Link", "")
        lines = txt.splitlines()
        if pg == 0:
            header = lines[0].split("\t")
        rows += [dict(zip(header, l.split("\t"))) for l in lines[1:] if l.strip()]
        m = re.search(r'<([^>]+)>; rel="next"', link); url = m.group(1) if m else None
        pg += 1; time.sleep(0.15)
        print(f"  {query[:40]}... page {pg}: total {len(rows)}", flush=True)
    return rows


def main():
    print(f"CAND={CAND}", flush=True)
    pos = fetch(CFG["pos"], POS_PAGES)
    neg = fetch(CFG["neg"], NEG_PAGES)
    records, seen = [], set()

    def add(rows, label):
        n = 0
        for r in rows:
            seq = (r.get("Sequence") or "").strip().upper()
            if not seq or seq in seen or not set(seq) <= CANON:
                continue
            seen.add(seq)
            records.append({"acc": r.get("Entry"), "sequence": seq, "length": len(seq), "label": label})
            n += 1
        return n

    n_pos = add(pos, 1.0)
    n_neg = add(neg, 0.0)
    with open(OUT_PATH, "w") as f:
        json.dump(records, f)
    print(f"\nwrote {len(records)} to {OUT_PATH}  (pos={n_pos}, neg={n_neg})", flush=True)


if __name__ == "__main__":
    main()
