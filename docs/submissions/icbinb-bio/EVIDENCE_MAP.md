# ICBINB-BIO Evidence Map

Updated: 2026-08-14

Status: Writing and review record

This map links the revised manuscript to completed experiment artifacts. It
does not authorize or require any experiment rerun, Python analysis, audit
tooling, or new result construction.

## Paper thesis

Across three completed steering studies and one pre-steering endpoint
analysis, endpoint mismatch, output low-complexity, composition sensitivity,
and whole-run variation changed the strength or meaning of score-based
steering conclusions. These retrospective cases motivate a staged reporting
sequence, but they do not show that it generalizes to other models or
properties or that steering established biological control.

## Result claims

| Claim | Existing evidence | Permitted wording | Required limitation |
|---|---|---|---|
| L52 low-complexity denominator loss | `plm_steering/l52_repro_out/results.json`; `docs/L52_LAYER_SUBSET_STEERING.md` | The all-layer arm retained 57 to 58 evaluable pairs in the shared low-strength range, but only 5 at alpha 1.0 and 0 at alpha 2.0 under the historical low-complexity filter. All outputs retained numerical scores. | The saved file omits exact source identifiers, source revision, model revision, and complete run metadata. The interpretation is retrospective. |
| L52 corrected comparison | Same L52 files | At alpha 0.5, the five-layer effect was 0.0236 and the all-layer effect was 0.0498 against their matched random controls. The five-layer intervention retained 43% to 59% of the all-layer effect over alpha 0.1 to 0.5. | This supports a smaller effect in the tested regime, not equivalence or a general layer-sufficiency claim. |
| L56 endpoint mismatch | `plm_steering/l56_immunogenicity_proxy_validation.py`; `plm_steering/data_cache/immunogenicity/l56_proxy_validation_summary.json`; `docs/L56_IMMUNOGENICITY_KILLED.md` | The source table contained 125,985 peptide-allele measurements, 15,362 unique peptides, and 72 HLA-II alleles. The analysis grouped by peptide and used the maximum normalized IC50 score across each peptide's assayed alleles. The fitted peptide-only composition score had held-out correlation 0.427 with that label and 0.100 with measured T-cell response. | The composition score did not use allele identity. The first result is an association with an allele-aggregated dataset label, not generic binding affinity or affinity for a specified peptide-allele pair. The cohorts also differ by endpoint and context. No steering intervention was run for L56. |
| L56 organism grouping | Same L56 files | In the full-length cohort, random-fold correlation was 0.379, organism-grouped correlation was -0.323, and mean within-organism correlation was 0.056. | The drop is consistent with source-organism confounding. It does not establish organism as the only cause. |
| L55 whole-run sensitivity | `plm_steering/l55_repro_out/results.json`; `plm_steering/l55_repro_out_seed1/results.json`; `plm_steering/l55_repro_out_seed2/results.json`; `docs/L55_DISORDER_STEERING.md` | At alpha 0.5, the contrasts were 0.0497, 0.0373, and 0.0435 over 116, 102, and 113 surviving pairs. The historical low-complexity counts were 34, 47, and 33 of 150 learned outputs and 7, 8, and 13 of 150 controls. The E/S-excluded interval was above zero in two configurations and included zero in one. | The result files do not store seed or configuration metadata. Several random processes changed together, so differences cannot be attributed to direction construction alone. |
| L57 composition sensitivity | `plm_steering/l57_repro_out/results.json`; `docs/L57_EXPRESSION_STEERING.md` | At alpha 0.5, the eSol soluble-fraction score contrast was 0.0125 with interval [0.0086, 0.0166]. After excluding E and L, it was 0.00035 with interval [-0.0028, 0.0035]. | The interval that includes zero is inconclusive. It does not prove that the remaining effect is exactly zero. The score is not general expression yield. |
| L55 and L57 geometry | `plm_steering/l58_vector_geometry_out/results.json` | The saved one-run directions had cosine 0.376 overall and 0.556 to 0.666 in layers 30 to 32. | Descriptive, one run, no control-vector distribution, and no causal interpretation. Supporting context only. |

## Excluded material

- L54 catalytic steering is reserved for a later paper.
- L48 and L49 attention-head results are reserved for the separate
  Interp4Discovery decision.
- L42 and L51 are not needed for the revised paper.
- L53 binding-affinity results do not contribute to the staged-audit thesis.
- The old five-target correlation figure and catalytic dose-response figure
  are not used.

## External source support

| Citation key | Supports | Verification |
|---|---|---|
| `lin2023esm` | ESM-2 model family and protein language model context | Crossref DOI metadata checked 2026-08-14 |
| `huang2025steering` | Prior activation steering method for protein language models | Official PMLR proceedings record checked 2026-08-14 |
| `campen2008topidp` | TOP-IDP amino-acid scale | Crossref DOI metadata checked 2026-08-14 |
| `quaglia2022disprot` | DisProt annotation resource | Crossref DOI metadata checked 2026-08-14 |
| `vita2019iedb` | IEDB data resource | Crossref DOI metadata checked 2026-08-14 |
| `niwa2009esol` | eSol protein-solubility measurements | Crossref DOI metadata checked 2026-08-14 |
| `wilkinson1991solubility` | Charge term used in a recombinant-protein solubility model | Crossref DOI metadata checked 2026-08-14 |

## Review checks

- [x] Every number in `paper.tex` appears in this map.
- [x] Every cited source supports the sentence that cites it.
- [x] No catalytic or attention-head claim remains.
- [x] No sentence presents a sequence score as a biological measurement.
- [x] No sentence attributes L55 differences to one random factor.
- [x] The anonymous source and PDF contain no author identifiers.
- [x] The final PDF has been inspected page by page.
