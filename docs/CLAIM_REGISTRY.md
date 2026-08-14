# Claim Registry

Registry version: 0.2

Created: 2026-08-13

State: MANUSCRIPT EVIDENCE BOUNDARY

This registry controls manuscript wording for ICBINB-BIO. The experiments are
complete. Existing result files and study documents are the evidence base.
Nothing in this registry authorizes a rerun, a new analysis program, an audit
bundle, or result-lock construction. If an existing artifact does not support a
claim, narrow or remove the claim.

Interp4Discovery is not an active submission. Its proposed claims are retained
only to explain why the completed L48 and L49 evidence is insufficient.

## Status definitions

| Status | Meaning |
|---|---|
| Supported | The saved evidence directly supports the stated manuscript wording |
| Bounded | The saved evidence supports the claim only with the listed limitation |
| Rejected | The available evidence does not support the claim or the claim is outside the active paper |
| Deferred | The claim belongs to a later paper and is not active before August 29 |

These statuses describe manuscript use. They are not experiment gates.

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
| Manuscript check | Report the saved attempt counts, evaluable-pair denominators, and conditional score contrasts without treating unavailable comparisons as successes |
| Main limitation | Low-complexity outputs can remain scoring-valid. The claim concerns the historical filter and does not call every low-complexity sequence invalid. |
| Provenance | Retrospective correction of an earlier decision rule |
| Status | Bounded |
| Permitted use | Retrospective low-complexity and denominator-collapse case using the counts stored in the existing result file |

### ICB-02

Claim:

> In the saved L56 cohorts, a peptide-only composition score associated with
> each peptide's maximum normalized IC50 score across its assayed HLA-II
> alleles had weaker validation performance for observed T-cell response.

| Field | Contract |
|---|---|
| Owner | ICBINB-BIO |
| Empirical evidence | `plm_steering/l56_immunogenicity_proxy_validation.py`; `plm_steering/data_cache/immunogenicity/l56_proxy_validation_summary.json` |
| Narrative context | `docs/L56_IMMUNOGENICITY_KILLED.md` |
| Statistical unit | Peptide after taking the maximum normalized IC50 score across its assayed alleles, or labeled sequence according to the source cohort |
| Control | Evaluation against measured T-cell response rather than only the allele-aggregated binding-assay label |
| Manuscript check | Report only endpoint comparisons present in the saved summary and disclose the missing row-level predictions, fold assignments, source versions, and input hashes |
| Main limitation | The composition score does not use allele identity, and the label takes the maximum score over each peptide's assayed alleles. Its Tier 1 result is therefore an association with an allele-aggregated dataset label rather than affinity for a specified peptide-allele pair. The fixed cohorts also do not prove that sequence cannot predict T-cell response, and no steering intervention was run. |
| Provenance | Retrospective endpoint audit |
| Status | Bounded |
| Permitted use | Endpoint-selection case before steering, not a failed steering intervention |

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
| Manuscript check | Report the saved random-fold, organism-grouped, and within-organism statistics without claiming that organism identity caused the difference |
| Main limitation | A performance drop under grouped validation is consistent with confounding but does not identify it as the sole cause |
| Provenance | Post-hoc grouping sensitivity analysis |
| Status | Bounded |
| Permitted use | Pattern consistent with source-organism confounding, with no causal attribution |

### ICB-04

Claim:

> Across three saved whole-run configurations, the conditional disorder-score
> contrast is positive, but the dominant-residue exclusion decision changes
> across those configurations.

| Field | Contract |
|---|---|
| Owner | ICBINB-BIO |
| Empirical evidence | `plm_steering/l55_repro_out/results.json`; `plm_steering/l55_repro_out_seed1/results.json`; `plm_steering/l55_repro_out_seed2/results.json` |
| Narrative context | `docs/L55_DISORDER_STEERING.md` |
| Statistical unit | Source protein within each saved whole-run configuration |
| Control | Matched-norm random direction and residue-exclusion sensitivity analysis |
| Manuscript check | Compare the three saved result files directly and report the surviving-pair denominators with each conditional contrast |
| Main limitation | The files do not record seeds or configurations. Cohort construction, masks, control direction, and bootstrap sampling vary together, so the differences cannot be attributed to one component. |
| Provenance | Post-hoc sensitivity analysis |
| Status | Bounded |
| Permitted use | Three completed configurations show a positive conditional contrast, while the residue-exclusion decision is not consistent across all three |

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
| Manuscript check | Report the saved primary and E/L-excluded contrasts and intervals exactly |
| Main limitation | An interval that includes zero is inconclusive. It does not prove that the remaining effect is zero. One direction build also cannot establish general seed sensitivity. |
| Provenance | Post-hoc sensitivity analysis |
| Status | Bounded |
| Permitted use | Composition-sensitive decision case; the E/L-excluded interval is inconclusive rather than proof of zero |

### ICB-06

Claim:

> In the saved one-seed analysis, the L55 and L57 steering directions have
> positive cosine overlap overall and in layers 30 through 32.

| Field | Contract |
|---|---|
| Owner | ICBINB-BIO, supporting diagnostic only |
| Existing evidence | `plm_steering/l58_vector_geometry_out/results.json` |
| Source inputs | `plm_steering/l58_vector_geometry_out/l55_disorder_steering_vectors.npy`; `plm_steering/l58_vector_geometry_out/l57_expression_steering_vectors.npy` |
| Statistical unit | One fixed direction pair summarized over 33 paired layer vectors; layers are not independent replicates |
| Control | None. This is a descriptive pairwise diagnostic with no control-vector distribution. |
| Manuscript check | Use the values stored in the saved result file and label the comparison as descriptive |
| Main limitation | One seed cannot support a robustness or causal claim |
| Provenance | Post-hoc supporting diagnostic |
| Status | Bounded |
| Permitted use | Optional one-run context only; it cannot explain or validate ICB-04 or ICB-05 |

## Interp4Discovery claims

Submission decision: DO NOT SUBMIT from the completed evidence. L48 is a
one-head pilot. L49 does not estimate the proposed association between contact
enrichment and contact-specific causal effect. The missing independent panel,
row-level outcomes, protein-level uncertainty, and equivalence analysis are not
current tasks.

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
| Future evidence that would be needed | Prespecified layer-adjusted finite-head association across all 480 heads on an unopened independent panel |
| Main limitation | The independent cohort, association threshold, precision target, and analysis bundle do not yet exist |
| Provenance | Prospective confirmatory claim |
| Status | Rejected for the current submission |
| Current action | Do not run new work to rescue the paper |

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
| Future evidence that would be needed | Head-by-head equivalence under zero and mean replacement with familywise correction |
| Main limitation | Equivalence is not supported by a non-significant difference, and no margin is frozen yet |
| Provenance | Prospective fallback branch after the global association does not pass |
| Status | Rejected for the current submission |
| Current action | Do not run new work to rescue the paper |

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
| Future evidence that would be needed | Apply one frozen group-level replication rule without reranking heads on the independent panel |
| Main limitation | The group result does not establish that every selected head replicates, and correlational replication does not establish causal importance |
| Provenance | Prospective prerequisite |
| Status | Rejected for the current submission |
| Current action | Do not run new work to rescue the paper |

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
approval. Expanding a claim requires author approval, supporting evidence, and
independent review. It is not part of the current paper refactor.
