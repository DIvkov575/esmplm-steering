# Claim Registry

Registry version: 0.1

Created: 2026-08-13

State: BASELINE CANDIDATE

This registry controls the two active workshop papers. A candidate entry may
guide artifact recovery and experiment design, but it may not be presented as
a confirmed manuscript claim. The registry becomes FROZEN only when the
reconciled contract commit passes independent review and that commit is
recorded in `docs/EXECUTION_LEDGER.md`.

## Status definitions

| Status | Meaning |
|---|---|
| Confirmed | The claim is supported by a locked result bundle and has passed independent review |
| Conditional | Existing evidence motivates the claim, but a required audit, rerun, or confirmatory analysis remains open |
| Rejected | The available evidence does not support the claim or the claim is outside the paper contract |
| Deferred | The claim belongs to a later paper and is not active before August 29 |

No active workshop claim is Confirmed at registry version 0.1.

## ICBINB-BIO claims

### ICB-01

Claim:

> Survivor-only score comparisons can make a steering method appear useful
> after low-complexity outputs have removed most or all of a comparison arm
> from the historical-filter denominator.

| Field | Contract |
|---|---|
| Owner | ICBINB-BIO |
| Empirical evidence | `plm_steering/l52_repro_out/results.json` |
| Narrative context | `docs/L52_LAYER_SUBSET_STEERING.md` |
| Statistical unit | Source protein |
| Control | Matched-norm random direction and the all-layer steering arm where both arms remain evaluable |
| Required analysis | Technical-failure and low-complexity risks over all attempts, plus conditional score change among jointly scoring-valid and historical-filter pairs |
| Main limitation | Low-complexity outputs can remain scoring-valid. The claim concerns the historical filter and does not call every low-complexity sequence invalid. |
| Provenance | Retrospective correction of an earlier decision rule |
| Status | Conditional |
| Gate to confirm | Derived audit bundle reproduces raw counts, failure risks, conditional effects, and corrected interpretations |

### ICB-02

Claim:

> In the saved L56 cohorts, sequence-composition scores that were associated
> with peptide MHC-II binding had weaker validation performance for observed
> T-cell response.

| Field | Contract |
|---|---|
| Owner | ICBINB-BIO |
| Empirical evidence | `plm_steering/data_cache/immunogenicity/l56_proxy_validation_summary.json` |
| Narrative context | `docs/L56_IMMUNOGENICITY_KILLED.md` |
| Statistical unit | Peptide or labeled sequence, according to the source cohort |
| Control | Evaluation against the biological endpoint rather than only the binding surrogate |
| Required analysis | Reproduce every reported endpoint comparison from the saved source data, with row-level predictions and peptide-level stability analysis over the fixed deduplicated cohorts |
| Main limitation | The available work evaluates the listed scores in fixed cohorts. It does not prove that sequence cannot predict T-cell response, and it does not run a steering intervention. |
| Provenance | Retrospective endpoint audit |
| Status | Conditional |
| Gate to confirm | Endpoint definitions, cohort construction, and reported validation statistics pass artifact and statistical review |

### ICB-03

Claim:

> In the saved full-length cohort, validation performance fell under
> organism-grouped evaluation, a pattern consistent with source-organism
> confounding.

| Field | Contract |
|---|---|
| Owner | ICBINB-BIO |
| Empirical evidence | `plm_steering/data_cache/immunogenicity/l56_proxy_validation_summary.json` |
| Narrative context | `docs/L56_IMMUNOGENICITY_KILLED.md` |
| Statistical unit | Sequence |
| Control | Identical random and organism-grouped folds for prespecified length-only, composition-only, and composition-plus-length models |
| Required analysis | Reproduce the historical estimate, then fit all three fixed models with organism-level weighting and paired organism-clustered uncertainty for each grouping difference |
| Main limitation | A performance drop under grouped validation is consistent with confounding but does not identify it as the sole cause |
| Provenance | Post-hoc grouping sensitivity analysis |
| Status | Conditional |
| Gate to confirm | The composition-only and composition-plus-length grouping differences are positive with 95 percent intervals above zero, and the bundle reports the length-only diagnostic |

### ICB-04

Claim:

> Across three legacy whole-run seeds, the conditional disorder-score
> contrast is positive, but the dominant-residue exclusion decision changes
> across those seeds.

| Field | Contract |
|---|---|
| Owner | ICBINB-BIO |
| Empirical evidence | `plm_steering/l55_repro_out/results.json`; `plm_steering/l55_repro_out_seed1/results.json`; `plm_steering/l55_repro_out_seed2/results.json` |
| Narrative context | `docs/L55_DISORDER_STEERING.md` |
| Statistical unit | Source protein, nested within legacy whole-run seed |
| Control | Matched-norm random direction and residue-exclusion sensitivity analysis |
| Required analysis | Reproduce seeds 0, 1, and 2 with explicit seed and output-directory arguments and saved seed metadata |
| Main limitation | Existing bundles do not record the seed, and the current runner hard-codes seed zero. The same integer controls the cohort split, masks, control direction, and bootstrap, so the result cannot be attributed to direction construction alone. |
| Provenance | Post-hoc sensitivity analysis |
| Status | Conditional |
| Gate to confirm | Parameterized clean-worktree reruns reproduce the three seed-specific interpretations by 2026-08-15 23:59 Anywhere on Earth |

### ICB-05

Claim:

> The saved L57 analysis met its positive rule before dominant E and L
> substitutions were excluded, but the E/L-excluded analysis did not meet
> that rule.

| Field | Contract |
|---|---|
| Owner | ICBINB-BIO |
| Empirical evidence | `plm_steering/l57_repro_out/results.json` |
| Narrative context | `docs/L57_EXPRESSION_STEERING.md` |
| Statistical unit | Source protein |
| Control | Matched-norm random direction and E/L residue-exclusion analysis |
| Required analysis | Recompute the primary, technical-failure, low-complexity, and residue-exclusion results from saved raw sequences and scores |
| Main limitation | An interval that includes zero is inconclusive. It does not prove that the remaining effect is zero. One direction build also cannot establish general seed sensitivity. |
| Provenance | Post-hoc sensitivity analysis |
| Status | Conditional |
| Gate to confirm | Locked audit bundle verifies the raw sequences, exclusions, uncertainty, and corrected interpretation |

### ICB-06

Claim:

> In the saved one-seed analysis, the L55 and L57 steering directions have
> positive cosine overlap overall and in layers 30 through 32.

| Field | Contract |
|---|---|
| Owner | ICBINB-BIO, supporting diagnostic only |
| Required audit evidence | `plm_steering/icbinb_audit_out/cases/l58/l55_l57_geometry.json` |
| Exact source inputs | `plm_steering/l58_vector_geometry_out/l55_disorder_steering_vectors.npy`; `plm_steering/l58_vector_geometry_out/l57_expression_steering_vectors.npy` |
| Statistical unit | One fixed direction pair summarized over 33 paired layer vectors; layers are not independent replicates |
| Control | None. This is a descriptive pairwise diagnostic with no control-vector distribution. |
| Required analysis | Verify vector hashes, layer definitions, and pairwise statistics |
| Main limitation | One seed cannot support a robustness or causal claim |
| Provenance | Post-hoc supporting diagnostic |
| Status | Conditional |
| Gate to confirm | The manuscript labels the analysis as one-seed evidence and uses it only to interpret ICB-04 and ICB-05 |

## Interp4Discovery claims

### INT-01

Claim:

> Across the 480 fixed heads, contact enrichment measured on the discovery
> panel predicts greater contact-specific masked-residue damage under zero
> replacement on an independent structure panel.

| Field | Contract |
|---|---|
| Owner | Interp4Discovery |
| Supporting files | None yet; the existing L48 and L49 outputs are pilot and discovery evidence only |
| Statistical unit | Protein for outcome estimation; the 480 heads form one fixed finite set for the association |
| Control | Matched non-contact positions within protein and discovery-matched control heads |
| Primary outcome | Ablation damage on contact-bearing positions minus damage on matched non-contact positions |
| Required analysis | Prespecified layer-adjusted finite-head association across all 480 heads on an unopened independent panel |
| Main limitation | The independent cohort, association threshold, precision target, and analysis bundle do not yet exist |
| Provenance | Prospective confirmatory claim |
| Status | Conditional |
| Gate to confirm | The positive branch and every intervention, matching, precision, and replication check pass by August 20 |

### INT-02

Claim:

> Each of the five prespecified contact-enriched heads has a contact-specific
> ablation effect equivalent to its matched controls within a frozen margin.

| Field | Contract |
|---|---|
| Owner | Interp4Discovery negative branch |
| Supporting files | None yet |
| Statistical unit | Protein-level head-control contrast |
| Control | At least two same-layer controls matched on discovery-only measurements |
| Required analysis | Head-by-head equivalence under zero and mean replacement with familywise correction |
| Main limitation | Equivalence is not supported by a non-significant difference, and no margin is frozen yet |
| Provenance | Prospective fallback branch after the global association does not pass |
| Status | Conditional |
| Gate to confirm | Every adjusted confidence interval lies within the frozen equivalence margin under both replacement methods |

### INT-03

Claim:

> The prespecified top-five set replicates contact enrichment as a group on
> the independent structure panel.

| Field | Contract |
|---|---|
| Owner | Interp4Discovery, prerequisite rather than primary causal claim |
| Supporting files | None yet; `plm_steering/l48_replication_out.json` is discovery and pilot evidence |
| Statistical unit | Protein |
| Control | Frozen top-five set selected only from the discovery panel |
| Required analysis | Apply one frozen group-level replication rule without reranking heads on the independent panel |
| Main limitation | The group result does not establish that every selected head replicates, and correlational replication does not establish causal importance |
| Provenance | Prospective prerequisite |
| Status | Conditional |
| Gate to confirm | The independent-panel replication statistic and confidence interval pass the frozen rule |

## Rejected and deferred claims

| ID | Claim | Status | Reason |
|---|---|---|---|
| EXC-01 | Steering improves catalysis | Deferred | Requires a separate substrate-specific study and ultimately a controlled turnover assay |
| EXC-02 | Boltz validates catalytic activity, disorder, toxicity, immunogenicity, or safety | Rejected | These endpoints are outside what Boltz can establish |
| EXC-03 | The current disorder result is a validated positive biological result | Rejected for workshop use | Composition and seed sensitivity remain unresolved |
| EXC-04 | L43 supplies a workshop failure mechanism | Rejected | No tracked L43 document, script, or result bundle exists |
| EXC-05 | A non-significant ablation proves no causal effect | Rejected | Absence requires a prespecified equivalence test with defensible margins |
| EXC-06 | The attention-head study and steering audit form one workshop claim | Rejected | The two papers have separate questions, evidence, and ownership |

## Change control

Each change must record the claim ID, old text, new text, evidence added or
removed, reviewer, and date. A manuscript owner may narrow a claim without
approval. Expanding a claim requires an updated manifest, supporting locked
artifacts, and independent review.
