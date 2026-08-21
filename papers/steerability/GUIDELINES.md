# Distilled submission guidelines — ICBINB-BIO (NeurIPS 2026 workshop)

Distilled from `esmplm-steering-icbinb/docs/VENUE_POLICY_2026.md` (verified
2026-08-13 against official sources) and `SUBMISSION_GUIDE.md`. Re-verify the
tentative fields before upload.

## Hard constraints (desk-reject risks)

- **Structure — four required elements** (full paper): **Problem**, **Proposed
  approach**, **Observed outcome**, **Reason for failure**. Names need not be
  literal headings, but we use them as headings so reviewers can locate each.
  → `paper.tex` §Problem / §Proposed Approach / §Observed Outcome / §Reason for
  Failure. ✅
- **Page limit — 8 content pages** (incl. figures) for a full paper (4 for a
  tiny paper). References and appendices do **not** count. Over the limit → not
  reviewed. → current build is **6 pages**. ✅
- **Abstract — one paragraph.** ✅
- **Double-blind.** No author names/affiliations/acknowledgments; self-cite in
  the third person; template uses `[dblblindworkshop]`. → author is `Anonymous
  Authors`; no self-identifying citations. ✅
- **LLM-use disclosure** — one short paragraph describing the role. ✅
  (`\section*{LLM usage disclosure}`).

## Recommended (evaluation criteria)

- **Quantitative evidence** with data and **seed details** — reproducibility is
  scored. → scoreboard table + per-target seeds + separation/dose grid;
  Reproducibility statement present. ✅
- **Ethics + reproducibility statements** — recommended end matter (not
  appendices). ✅
- **Template footer** ("Submitted to …") from `neurips_2026.sty` — leave it in
  the review PDF. ✅

## Logistics

- **Deadline:** 2026-08-30 11:59 UTC (= Aug 29, 11:59 pm AoE). Website labels
  the schedule *tentative* — recheck.
- **Non-archival**, appears on OpenReview; form requires **CC BY 4.0**.
- **Dual submission OK**, incl. work under NeurIPS 2026 main-track review; not
  eligible if already accepted in prior proceedings.
- **Preprints permitted** but a named public version with the same title/text
  breaks anonymity → do not post a named preprint before review completes.
- **One PDF field** on OpenReview; ZIP/supplement support unresolved. Main paper
  must stand alone.

## Anonymity pre-upload checklist (from SUBMISSION_GUIDE)

Search both source files and the compiled PDF for and remove:

```
Ivkov   divkov   DIvkov575   umich   University of Michigan   github.com
```

Also strip: Git metadata, remote URLs, local absolute paths, acknowledgments,
and PDF author metadata.

- Source + PDF string scan: **clean** (verified). ✅
- PDF `/Author`, `/Creator`, `/Keywords`: **empty** (verified). ✅
- Do **not** link the public `DIvkov575/esmplm-steering` repo from the
  anonymous submission or review materials.

## Build

```
cd papers/steerability
latexmk -pdf paper.tex      # -> paper.pdf (6 pp)
latexmk -C                  # clean aux artifacts
```
