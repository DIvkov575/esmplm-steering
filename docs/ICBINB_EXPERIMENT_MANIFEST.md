# ICBINB Experiment Manifest

Date: 2026-08-13

Current-use note: revised 2026-08-14

Paper: ICBINB-BIO

Status: Historical experiment specification and evidence guide. The
experiments are complete. This file is not an active execution contract.

Do not rerun experiment scripts, implement the proposed audit module, build
new result locks, or execute the commands in Section 13. The manuscript must
use the existing result files and study documents. If those materials do not
support a claim, narrow or remove the claim. New experiment or analysis code
requires explicit author approval.

Source plan: `docs/PAPER_PORTFOLIO_PLAN.md`

Historical source plan SHA-256 for the former contract revision:
`454ba114ebd1bd65f0cff0794f8d08db9dfcb95f5f2fdd97d7e485de74eb6f8d`

## 1. Purpose and decision boundary

This manifest records the intended interpretation of the completed ICBINB
evidence. The paper asks which checks prevent an apparent protein language
model steering result from being interpreted as reliable biological property
control.

The minimum package has three required failure mechanisms:

1. Decoder instability and survivor-only interpretation, owned by L52.
2. Endpoint mismatch and a grouped-validation pattern consistent with
   source-organism confounding, owned by L56.
3. Composition and seed-sensitive interpretation, owned jointly by L55 and
   L57.

L58 is a one-seed supporting diagnostic for the third mechanism. It cannot
create a fourth mechanism, rescue a failed L55 or L57 result, or support a
mechanistic claim.

The audit is complete only when all attempted generations are represented in
the technical-failure and low-complexity analyses and all scoring-valid
generations are represented in the conditional-score analysis. Technical
failures must never disappear through complete-case filtering.

## 2. Fixed claims

These are the strongest claims the ICBINB paper may make from this package.
Meaning may not be expanded. A sentence that triggers the package checker's
fail-closed claim boundary must use the exact corresponding claim text from
`docs/CLAIM_REGISTRY.md`.

| ID | Fixed claim | Evidence owner | Provenance |
|---|---|---|---|
| ICB-01 | In L52, a survivor-only policy can favor a high-strength intervention even when decoder instability removes most or all all-33-layer generations from the historical-filter denominator. Reporting low-complexity risk with conditional score change changes the interpretation. | L52 | Retrospective audit of a documented mid-analysis correction |
| ICB-02 | In the saved L56 cohorts, sequence-composition scores associated with MHC-II binding have weaker validation performance for measured T-cell response. | L56 | Retrospective endpoint audit |
| ICB-03 | In the saved L56 full-length cohort, performance falls under organism-grouped evaluation, a pattern consistent with source-organism confounding. | L56 | Post-hoc grouping sensitivity analysis |
| ICB-04 | In L55, the conditional disorder-score contrast is positive across three legacy whole-run seeds, but the dominant-residue exclusion decision changes across those seeds. | L55 | Post-hoc sensitivity analysis |
| ICB-05 | In L57, the unexcluded analysis meets its positive scoring rule, while the E/L-excluded analysis does not meet that rule. This is evidence of composition sensitivity, not evidence that the remaining effect is zero. | L57 | Post-hoc sensitivity analysis |
| ICB-06 | In the committed one-seed L58 diagnostic, the L55 and L57 steering vectors have positive cosine overlap overall and in layers 30 through 32. This is supporting geometry, not independent evidence or a causal explanation. | L58 | Post-hoc sensitivity analysis, one seed |

The paper-level claim is:

> A staged audit catches distinct steering evaluation failures. In this
> package, the relevant checks detect decoder instability, endpoint mismatch,
> a performance pattern consistent with source-organism confounding,
> composition-sensitive conclusions, and a seed-sensitive robustness verdict.

The following claims are prohibited:

- Steering improves thermostability, disorder, expression yield,
  immunogenicity, catalysis, safety, or any other biological property.
- A scoring-surrogate change proves biological property control.
- L58 proves that L57 is caused by L55, that the directions are the same, or
  that either direction is independently validated.
- The three L55 runs isolate direction-build sensitivity. The legacy seed
  changes cohort construction, masking, control direction, and bootstrap
  sampling together.
- L56 shows that no immune endpoint can be predicted from sequence. It only
  evaluates the listed scores, cohorts, and endpoints.
- A non-significant result proves no effect.

The package checker is a deterministic lexical guard, not a semantic
classifier. When the manuscript must state one of these boundaries, use the
corresponding sentence exactly:

- The audit does not establish that steering improves a biological property.
- A scoring-surrogate change does not establish biological property control.
- L58 does not establish causation, direction identity, or independent
  validation.
- The L55 runs do not isolate direction-build sensitivity.
- This analysis does not support a universal claim about immune-endpoint
  predictability.
- A non-significant result does not establish no effect.

The six boundary sentences above are always allowlisted. An exact registered
ICBINB claim sentence is allowlisted only when its result-ledger row is
`confirmed` and the complete ownership and review contract validates. The
checker also rejects documented risky lexical variants and close
restatements. This is defense in depth, not proof that every semantic
paraphrase is detectable.

Any nonexact result claim remains unauthorized whether or not the lexical
guard flags it. Before a package can pass final technical review, the assigned
reviewer must inspect the complete manuscript source and rendered PDF and
verify that every result claim is an exact registered sentence, an exact
paper-level sentence above, or an exact boundary sentence. A clean lexical
scan alone cannot approve manuscript prose.

## 3. Study inventory and ownership

| Study | Minimum package status | Permitted use | Exclusion or admission rule |
|---|---|---|---|
| L42 | Excluded from the active paper plan | None unless existing tracked material already supports a bounded statement | Do not rerun or reconstruct it for this paper. |
| L43 | Excluded | None | No tracked L43 document, script, and result bundle form an auditable case in this repository. |
| L48 and L49 | Excluded | None | Owned by Interp4Discovery. |
| L51 | Excluded from the active paper plan | None unless the existing summary supports a carefully limited policy-history statement | Do not rerun or reconstruct it for this paper. |
| L52 | Required | Primary decoder-instability case | Use the saved results and documented policy correction. State the missing-provenance limits. |
| L53 | Excluded from the minimum package | Optional boundary case after the fallback package is locked | It cannot replace one of the three mechanisms. Do not claim that its proposed dataset-intervention mismatch is proven. |
| L54 | Excluded and reserved | None | Reserved for catalytic work. Do not copy L54 results, vectors, tables, or claims into the ICBINB bundle or manuscript. |
| L55 | Required | Completed run-level and composition-sensitive case | Use the existing seed 0, 1, and 2 result files. Do not rerun them. |
| L56 | Required | Primary endpoint-mismatch and grouped-validation sensitivity case | Use the existing validation summary and describe its evidence limits. |
| L57 | Required | Primary composition-sensitivity case | Use the saved generation and residue-exclusion results. Do not rerun it. |
| L58 | Supporting only | One-seed geometry diagnostic for L55 and L57 | Use only the L55 versus L57 entry. Do not expose L54 entries from the current L58 result file. |

The minimum package does not wait for L42, L51, L53, any new audit bundle, or
any Interp4Discovery work.

## 4. Shared generation contract

### 4.1 Statistical unit

The independent sampling unit is one source protein. A generated sequence is
paired to its source protein and to the corresponding output from each
comparison arm. Residues are not independent observations.

The historical generation analyses target the fixed saved evaluation cohort
under the realized cohort split, masks, and control direction. Each source
protein receives equal weight. They do not estimate variation over repeated
masks, repeated random directions, complete reruns, or a broader protein
population.

Every bootstrap interval in this manifest is a two-sided 95 percent
percentile stability interval from resampling source proteins with pairing
preserved. It describes sensitivity to the empirical protein composition of
the fixed cohort. It is not a superpopulation confidence interval. The
one-sided decision in Section 4.4 uses the upper endpoint of this same
two-sided interval.

### 4.2 Attempt and validity

One attempt is one source protein processed once under one arm, intervention
strength, and mask seed. The attempted denominator is fixed before generation.

A technical or scoring failure occurs if any of these conditions is true:

1. The output is empty.
2. The output contains a noncanonical amino-acid character.
3. The output length differs from the truncated source length.
4. The scoring function raises an error or returns a non-finite value.

A generation is scoring-valid only if none of conditions 1 through 4 holds.
A technical or scoring failure receives no numerical property score.

Low complexity is a separate diagnostic:

5. More than 25 percent of the output is one amino acid.

Condition 5 preserves the historical L42 degeneracy rule, but it is not an
endpoint-neutral technical failure. A scoring-valid output that meets
condition 5 retains its score and receives a low-complexity flag. The audit
reports results with and without the historical low-complexity exclusion.
For L55, condition 5 is never part of the primary scoring-valid definition.
For L52, it is the fixed decoder-degeneracy outcome used in the retrospective
policy replay.

### 4.3 Two-part primary analysis

Every generation study must report both parts below for every arm and alpha.

Part A, failure risk:

- Denominator: all attempted generations in that arm and alpha.
- Outcomes: technical or scoring failure under conditions 1 through 4, and
  low complexity under condition 5. Report each reason and each union
  separately.
- Report: attempted count, scoring-valid count, technical-failure count,
  low-complexity count, each risk, and a 95 percent Wilson score interval.
- Primary arm contrast: paired failure-risk difference, learned direction
  minus matched random direction, with a protein-level paired percentile
  bootstrap for each outcome.
- Secondary contrasts: learned direction minus unsteered baseline and, for
  L52, subset5 learned direction minus all33 learned direction.

Part B, conditional score change:

- Denominator: source proteins for which both arms in the stated contrast are
  scoring-valid.
- Outcome: paired scoring-surrogate difference.
- Report: the exact jointly scoring-valid pair count, arm means, paired mean
  difference, 95 percent bootstrap stability interval, and the fraction of
  paired proteins with a positive difference.
- Report the same quantities after the historical low-complexity exclusion
  as a policy sensitivity analysis.
- If either pair count is below 30, report its point estimate and interval as
  descriptive only. It cannot satisfy an acceptance rule.
- If either pair count is zero, report `not_estimable`. Do not report zero.

The Part A and Part B denominators must appear next to each other in every
table and machine-readable summary. Part B must be called the score contrast
among jointly scoring-valid outputs. It is not an unconditional intervention
effect.

### 4.4 Joint decision rule

The maximum acceptable increase in technical or scoring failure risk for any
favorable steering claim is 0.05 absolute risk. There is no universal
low-complexity margin across biological endpoints.

A contrast is score-favorable only if:

- at least 30 jointly scoring-valid pairs remain; and
- the 95 percent stability interval for the conditional score difference is
  wholly above zero.

A contrast is failure-noninferior only if the upper bound of the 95 percent
stability interval for the learned-minus-control technical-failure difference is
at most 0.05.

A contrast is jointly favorable only if it is both score-favorable and
failure-noninferior. Low-complexity risk and the low-complexity-excluded score
contrast must be reported beside that decision. ICBINB does not use a jointly
favorable contrast to claim a biological gain. It uses changes across these
policies to audit earlier interpretations.

### 4.5 Intervention burden

For every scoring-valid generation, save:

- source-to-output Hamming distance;
- source-to-output edit count;
- source-to-output edit fraction;
- baseline-to-output Hamming distance when a baseline output exists;
- output-logit displacement when logits were saved.

L52 does not contain the source evaluation sequences in its committed result
file. Its current audit may report baseline-to-output burden only. Label
source-relative burden as unavailable. Output-logit displacement is
unavailable for all current saved runs. Do not claim that this burden measure
was evaluated.

## 5. L52 decoder-instability study

### 5.1 Hypothesis

H1:

> Replaying the original unrestricted alpha-selection policy yields a
> favorable verdict, while the corrected policy rejects that verdict because
> all33 learned-direction generation becomes low-complexity at high alpha and
> no historical-filter head-to-head score denominator remains.

This is a retrospective reproducibility claim. Its thresholds describe the
documented case and are not a new confirmatory test.

### 5.2 Fixed design

| Field | Value |
|---|---|
| Model | `facebook/esm2_t33_650M_UR50D` |
| Source data | `plm_steering/data_cache/meltome/mixed_split.csv` |
| Direction construction | Per-layer high-minus-low difference of means |
| Layer scopes | all 33 layers; subset `{18, 23, 25, 30, 31}` |
| Direction arms | learned; matched-norm random |
| Baseline | unsteered, alpha 0 |
| Alphas | `0.1, 0.25, 0.5, 1.0, 2.0` |
| Corrected safe alphas | `0.1, 0.25, 0.5` |
| Mask fraction | 0.30 |
| Decoder | Single-shot argmax masked fill |
| Evaluation proteins | 60 low-Tm proteins held out from direction construction |
| Scoring surrogate | IVYWREL residue fraction |
| Bootstrap resamples | 10,000 |
| Minimum inferential scoring-valid pairs | 30 |

Independent variables are layer scope, direction arm, and alpha. The source
protein and mask positions are paired across arms.

The existing L52 source data path is
`plm_steering/data_cache/meltome/mixed_split.csv`, whose recorded SHA-256 is
`ea48dbb222a5e18de61fabf0e1550b50e7a22c3d0f59cf9b47c01d993104ea3e`.
The saved result does not provide an independently checked mapping from all 60
rows to source identifiers. State this provenance limitation. Do not rebuild
or rerun L52 for the current paper.

### 5.3 Policies to replay

Original policy:

1. Search all five alphas for the strongest significant subset5 versus random
   conditional score contrast.
2. Allow alpha 1.0 or 2.0 to become `best_alpha`.
3. Treat an unavailable subset5 versus all33 comparison as not significantly
   worse.

Corrected policy:

1. Report technical-failure and low-complexity risk over all 60 attempts for
   every arm and alpha.
2. Restrict dose-response and `best_alpha` decisions to alphas 0.1, 0.25, and
   0.5.
3. Require at least 30 jointly scoring-valid pairs for the primary score
   comparison and report the historical-filter comparison separately.
4. Treat an unavailable head-to-head comparison as unevaluable, not as
   noninferior.
5. Apply the joint decision rule in Section 4.4.

### 5.4 H1 acceptance and failure

H1 is accepted only if all conditions hold:

- The original-policy replay returns `PASS`.
- The corrected-policy replay returns a non-PASS result.
- At alpha 1.0, all33 learned-direction low-complexity risk is at least 0.80
  and fewer than 30 all33 learned versus random historical-filter pairs
  remain.
- At alpha 2.0, all33 learned-direction low-complexity risk is at least 0.95
  and fewer than 30 all33 learned versus subset5 learned historical-filter
  pairs remain.
- The random all33 arm has low-complexity risk at most 0.10 at both alpha 1.0
  and alpha 2.0.
- Part B is reported as descriptive at alpha 1.0 and as `not_estimable` when
  its denominator is zero.

H1 fails if any required raw arm or verified source mapping is missing, if the
policy replay does not change the verdict, or if high-alpha low complexity
does not reproduce. A failed H1 removes L52 as a primary mechanism and
triggers the paper-level stop rule.

### 5.5 Inputs and outputs

Current raw input:

- `plm_steering/l52_repro_out/results.json`
- SHA-256:
  `bb2de0ece5306ab40a4a8c875e42cb9a41028fdc7cf3c5ee2f744eefd84c99f4`

Required audit outputs:

- `plm_steering/icbinb_audit_out/cases/l52/generation_records.jsonl`
- `plm_steering/icbinb_audit_out/cases/l52/failure_risk.csv`
- `plm_steering/icbinb_audit_out/cases/l52/conditional_scores.csv`
- `plm_steering/icbinb_audit_out/cases/l52/intervention_burden.csv`
- `plm_steering/icbinb_audit_out/cases/l52/policy_replay.json`
- `plm_steering/icbinb_audit_out/cases/l52/run_metadata.json`
- `plm_steering/icbinb_audit_out/cases/l52/checksums.sha256`

## 6. L56 endpoint-mismatch and grouped-validation sensitivity study

### 6.1 Hypotheses

H2a:

> In the fixed saved cohorts, sequence-composition scores associated with
> MHC-II binding have weaker validation performance for measured T-cell
> response.

H2b:

> In the fixed full-length cohort, validation performance falls under
> organism-grouped evaluation, a pattern consistent with source-organism
> confounding.

No sequence generation or steering run is allowed for L56.

### 6.2 Fixed design and denominators

| Tier | Endpoint | Unit and validity denominator | Primary report |
|---|---|---|---|
| 1 | MHC-II binding affinity | Unique canonical 9 to 50 residue peptide after aggregation by maximum score | Held-out Pearson correlation for every fixed score and the train-fit composition model |
| 2 | MHC-II presentation | Unique canonical 9 to 50 residue peptide in the fixed sampled and deduplicated eluted-ligand file | Held-out AUC and full-sample point-biserial correlation |
| 3 | T-cell response | Unique canonical 9 to 50 residue peptide with at least two assays | Held-out Pearson correlation for every score |
| 4 | Full-length antigen response fraction | Canonical 50 to 400 residue antigen with a mapped sequence and at least eight tested peptides in the cached cohort | Random-fold and organism-grouped out-of-fold correlation |
| Secondary | Allergen cross-check | 800 cached allergens and 2,423 cached lineage-and-length-matched nonallergens | Descriptive held-out AUC only |

Independent variables are endpoint tier, scoring function, model
specification, and cross-validation split policy. The source organism is the
grouping variable in the decisive confound analysis.

The target of each estimate is its fixed cached cohort. Tier 1 through Tier 3
weight each unique peptide equally after the frozen assay-aggregation rule.
Tier 4 gives each organism equal total weight so that organisms with more
recorded antigens do not dominate the correlation. Before execution, recover
and freeze the exact rule that combines repeated assays into one peptide
label, the handling of conflicting assays, every split identifier, and every
model-fitting step. If these cannot be reconstructed, H2 is not auditable.

The Tier 4 confound analysis has three fixed linear model specifications:

1. `length_only`: training-fold-standardized log sequence length and an
   intercept;
2. `composition_only`: the historical 20 normalized residue frequencies and
   an intercept;
3. `composition_plus_length`: the same 20 residue frequencies,
   training-fold-standardized log sequence length, and an intercept.

Use `numpy.linalg.lstsq` with `rcond=None` for the historical minimum-norm
composition design. Estimate the length mean and standard deviation from the
training fold only, using its inverse organism-frequency weights. Implement
weighted least squares by multiplying each training row and outcome by the
square root of its weight before calling `lstsq`. Use the same random-fold
assignment and the same organism-group assignment for all three
specifications. Save the design columns, training-only scaling values,
coefficients, weights, and row-level predictions for every fold. The
historical unweighted composition estimate is reproduced for provenance. The
audited estimates use inverse organism-frequency weights in model fitting and
in the reported correlation, so each organism has equal total weight.

For H2a, the analysis unit is one unique peptide after the frozen
deduplication and assay-aggregation rule. Use one singleton cluster identifier
per unique peptide because the cached peptide cohorts do not provide a
defensible shared source-protein or homology grouping. Bootstrap these peptide
units within each endpoint cohort and recompute the maximum absolute Tier 3
association across all fixed scores in every replicate. Compare that value
with the Tier 1 train-fit composition association. The resulting interval is
an empirical stability summary for these fixed deduplicated cohorts, not an
absence or equivalence test. It may understate dependence among related
peptides and cannot support a broader peptide-population claim.

For H2b, save one out-of-fold prediction per antigen, model specification, and
split policy under both the frozen random-fold and organism-grouped pipelines.
Bootstrap organisms as clusters, retain all sampled antigens for each sampled
organism, preserve each row's frozen fold assignment, rebuild
inverse-frequency weights, refit all three models, and compute for each model
`m`:

`delta_grouping[m] = r_random_fold[m] - r_organism_grouped[m]`

The paired cluster bootstrap must preserve all six predictions for each
antigen. `length_only` is a required diagnostic with no directional pass rule.
The composition-only difference is the primary source-organism sensitivity
estimate. The joint model checks whether that difference remains after
including sequence length. A fall in performance under both composition
models is consistent with source-organism confounding but does not identify
confounding as the sole cause.

The allergen result is not an immunogenicity endpoint and cannot change the
L56 stop decision.

### 6.3 H2 acceptance and failure

H2 is accepted only if all conditions hold:

- Row-level recalculation reproduces every value retained from the current
  summary within a frozen numerical tolerance.
- The Tier 1 train-fit composition association exceeds the maximum absolute
  Tier 3 association, and the 95 percent bootstrap stability interval for
  that difference is wholly above zero.
- `delta_grouping["composition_only"]` and
  `delta_grouping["composition_plus_length"]` are positive, and both 95
  percent organism-clustered bootstrap stability intervals are wholly above
  zero.
- The length-only random-fold estimate, grouped estimate, grouping difference,
  and 95 percent interval are reported regardless of direction.
- Random-fold and organism-grouped point estimates, organism-level estimates,
  all three model specifications, fold assignments, row-level predictions,
  training-fold length scalers, cohort counts, and exclusion counts are all
  saved.
- The manuscript uses observed-performance language. It does not claim that
  sequence scores cannot predict T-cell response or that organism
  confounding is proven to be the only cause.

H2 fails if the endpoint performance ordering does not reproduce, if grouped
validation does not reduce both composition-model estimates, or if the assay
aggregation, organism identifiers, model specifications, split assignments,
or row-level predictions are missing. A failed H2 blocks the endpoint-mismatch
claim and triggers the paper-level stop rule.

### 6.4 Inputs and outputs

Required cached inputs:

- `plm_steering/data_cache/immunogenicity/mhcii_ba.csv`
- `plm_steering/data_cache/immunogenicity/mhcii_el.csv`
- `plm_steering/data_cache/immunogenicity/iedb_tcell_mhcii.json.gz`
- `plm_steering/data_cache/immunogenicity/antigen_posfrac_relaxed.csv`
- `plm_steering/data_cache/immunogenicity/antigen_seqs.json`
- `plm_steering/data_cache/immunogenicity/allergen.fasta`
- `plm_steering/data_cache/immunogenicity/nonallergen.fasta`

Current summary:

- `plm_steering/data_cache/immunogenicity/l56_proxy_validation_summary.json`
- SHA-256:
  `c1324feb7f174209ea5a605c24acc2eff2ecac1305ed3520af8d9399b0661a98`

Required audit outputs:

- `plm_steering/icbinb_audit_out/cases/l56/cohort_counts.json`
- `plm_steering/icbinb_audit_out/cases/l56/row_predictions.parquet`
- `plm_steering/icbinb_audit_out/cases/l56/fold_assignments.csv`
- `plm_steering/icbinb_audit_out/cases/l56/endpoint_results.csv`
- `plm_steering/icbinb_audit_out/cases/l56/confound_results.json`
- `plm_steering/icbinb_audit_out/cases/l56/run_metadata.json`
- `plm_steering/icbinb_audit_out/cases/l56/checksums.sha256`

## 7. L55 seed-sensitive composition study

### 7.1 Hypotheses

H3a:

> Across legacy whole-run seeds 0, 1, and 2, the learned direction has a
> positive conditional TOP-IDP score contrast against the matched random
> direction at each safe alpha, with a monotonic increase from alpha 0.1 to
> 0.5.

H3b:

> The E/S-excluded conditional score verdict changes across the three legacy
> whole-run seeds.

The phrase `legacy whole-run seed` is required because one integer currently
controls several random processes. The audit must not attribute H3b to the
direction build alone.

### 7.2 Fixed design

| Field | Value |
|---|---|
| Model | `facebook/esm2_t33_650M_UR50D` |
| Source data | `plm_steering/data_cache/disorder/disprot_clean.csv` |
| Cohort cleaning | Canonical sequences, length at most 400 |
| Direction construction | All-33-layer difference of means from low and high DisProt disorder fraction |
| Direction arms | learned; matched-norm random |
| Baseline | unsteered, alpha 0 |
| Alphas | `0.1, 0.25, 0.5, 1.0, 2.0` |
| Safe alphas | `0.1, 0.25, 0.5` |
| Primary artifact alpha | 0.5 |
| Mask fraction | 0.30 |
| Evaluation proteins | 150 ordered proteins held out within each legacy seed |
| Scoring surrogate | Mean TOP-IDP score |
| Composition check | Remove E and S from each generated sequence, then recompute the mean over the remaining residues |
| Legacy seeds | `0, 1, 2` |
| Bootstrap resamples | 10,000 |

Independent variables are legacy whole-run seed, direction arm, and alpha.
The primary score outcome is conditional TOP-IDP change. The primary
artifact outcome is conditional E/S-excluded score change at alpha 0.5.
Technical-failure risk and low-complexity risk are co-primary validity
outcomes and are reported separately.

### 7.3 H3 acceptance and failure

The manuscript may report H3 from the completed runs only if direct source
inspection supports all conditions below:

- The three existing result files correspond to legacy whole-run seeds 0, 1,
  and 2 as documented by the study record. Seed identity must not be presented
  as stronger provenance than the repository actually provides.
- For every seed, all three safe-alpha learned-versus-random conditional
  score point estimates are positive and monotonically increase with alpha.
- For every seed, the alpha 0.5 conditional score stability interval is wholly
  above zero with at least 30 jointly scoring-valid pairs.
- E and S are the two excluded residues at alpha 0.5 in all three runs.
- At least one E/S-excluded alpha 0.5 stability interval is wholly above zero
  and at least one includes zero.
- The paper reports the observed pass count as `two of three` only if the
  existing files and study document directly support that wording.
- Technical-failure risk, low-complexity risk, and conditional score change
  are reported together for every seed and alpha.
- If removing E and S leaves no scored residues in either arm, that pair is
  unavailable for the exclusion analysis and is counted explicitly. At least
  30 exclusion-analysis pairs must remain for each seed.

If the existing evidence cannot support the full H3 wording, narrow the claim
to the result that is directly documented or omit H3. Do not rerun L55 to
repair provenance or recover a preferred statement.

### 7.4 Inputs and outputs

Current inputs:

- `plm_steering/l55_repro_out/results.json`
- `plm_steering/l55_repro_out_seed1/results.json`
- `plm_steering/l55_repro_out_seed2/results.json`
- `plm_steering/data_cache/disorder/disprot_clean.csv`

Current SHA-256 values, in the same order:

- `822402c49d2687bbae65b71c18815bcbe45c3dadf51ef7d16530bb46743a8d13`
- `16506034e3c210ab604bb095f79fed462f8b23620cd3cc300fd848d2456b0f36`
- `e664fdf911fd4d05a8fd77736dd931fd85ab17be781a4acfd839b8f185c691e9`
- `eb7062c0b05e4a6172b82fd4936fffa7918e30f51d181ede26d12823ff90aaeb`

Previously proposed audit outputs, retained only as historical design notes:

- `plm_steering/icbinb_audit_out/cases/l55/seed_0/generation_records.jsonl`
- `plm_steering/icbinb_audit_out/cases/l55/seed_1/generation_records.jsonl`
- `plm_steering/icbinb_audit_out/cases/l55/seed_2/generation_records.jsonl`
- `plm_steering/icbinb_audit_out/cases/l55/failure_risk.csv`
- `plm_steering/icbinb_audit_out/cases/l55/conditional_scores.csv`
- `plm_steering/icbinb_audit_out/cases/l55/residue_exclusion.csv`
- `plm_steering/icbinb_audit_out/cases/l55/intervention_burden.csv`
- `plm_steering/icbinb_audit_out/cases/l55/run_metadata.json`
- `plm_steering/icbinb_audit_out/cases/l55/checksums.sha256`

## 8. L57 composition-sensitivity study

### 8.1 Hypothesis

H4:

> At alpha 0.5, the learned direction has a favorable conditional absolute
> charge score against the matched random direction. After the dominant
> substituted residues E and L are excluded, the analysis no longer meets
> that positive rule.

### 8.2 Fixed design

| Field | Value |
|---|---|
| Model | `facebook/esm2_t33_650M_UR50D` |
| Source data | `plm_steering/data_cache/expression/esol_clean.csv` |
| Direction construction | All-33-layer high-minus-low eSol label difference of means |
| Direction arms | learned; matched-norm random |
| Baseline | unsteered, alpha 0 |
| Alphas | `0.1, 0.25, 0.5, 1.0, 2.0` |
| Safe alphas | `0.1, 0.25, 0.5` |
| Primary artifact alpha | 0.5 |
| Mask fraction | 0.30 |
| Evaluation proteins | 150 low-yield proteins from the held-out valid and test splits |
| Scoring surrogate | Absolute charge average |
| Composition check | Remove E and L from each generated sequence, then recompute the score over the remaining residues |
| Bootstrap resamples | 10,000 |

Independent variables are direction arm and alpha. The primary score outcome
is conditional absolute-charge difference. The primary artifact outcome is
conditional E/L-excluded score difference. Technical-failure risk and
low-complexity risk are co-primary validity outcomes and are reported
separately.

### 8.3 H4 acceptance and failure

H4 is accepted only if all conditions hold:

- At alpha 0.5, at least 30 jointly scoring-valid learned-versus-random pairs
  remain.
- The unexcluded conditional score stability interval is wholly above zero.
- E and L are the two dominant substituted residues under the frozen counting
  rule.
- The E/L-excluded conditional score stability interval includes zero.
- If removing E and L leaves no scored residues in either arm, that pair is
  unavailable and counted explicitly. At least 30 exclusion-analysis pairs
  must remain.
- Technical-failure and low-complexity risks over all 150 attempts are
  reported separately for learned, random, and baseline arms.
- Source-relative and baseline-relative edit burden are reported.

H4 fails if the unexcluded score is not favorable, if the excluded interval
also remains wholly above zero, or if the excluded residues are selected
using any arm other than the learned alpha 0.5 arm compared with its paired
baseline.

H4 supports only a change in the fixed decision status under residue
exclusion. An interval that includes zero is inconclusive and does not show
that the remaining effect is zero.

### 8.4 Inputs and outputs

Current inputs:

- `plm_steering/l57_repro_out/results.json`
- `plm_steering/data_cache/expression/esol_clean.csv`

Current SHA-256 values:

- `5790e1a0bb38391597c58a5141eec56753223d31073249f368cf1fd0fe9f262b`
- `bd099c1c9d4cc85d1f41f49a6ee12ec2142a15d6baf0e78766754e1546db7525`

Required audit outputs:

- `plm_steering/icbinb_audit_out/cases/l57/generation_records.jsonl`
- `plm_steering/icbinb_audit_out/cases/l57/failure_risk.csv`
- `plm_steering/icbinb_audit_out/cases/l57/conditional_scores.csv`
- `plm_steering/icbinb_audit_out/cases/l57/residue_exclusion.csv`
- `plm_steering/icbinb_audit_out/cases/l57/intervention_burden.csv`
- `plm_steering/icbinb_audit_out/cases/l57/run_metadata.json`
- `plm_steering/icbinb_audit_out/cases/l57/checksums.sha256`

## 9. L58 one-seed geometry diagnostic

### 9.1 Hypothesis

H5:

> In the seed-0 vectors already committed, L55 and L57 have positive cosine
> similarity over the full 33-layer concatenation and separately at layers
> 30, 31, and 32.

H5 is descriptive. It has no p-value, confidence interval, or independent
replication.

### 9.2 Fixed design and acceptance

The only permitted source result is:

`pairwise.l55_disorder_vs_l57_expression`

from:

`plm_steering/l58_vector_geometry_out/results.json`

SHA-256:
`e09e2c3c3022f1baece780ccb7df0bcf0055656653fb5889deae971dbaf30935`

The object is one fixed direction pair represented by 33 paired layer
vectors. The layers are model components, not independent statistical units.
The full-vector cosine and the three deep-layer cosines must all be positive.
A deterministic rebuild, if performed, must match the committed values within
absolute tolerance `1e-5`.

Required audit outputs:

- `plm_steering/icbinb_audit_out/cases/l58/l55_l57_geometry.json`
- `plm_steering/icbinb_audit_out/cases/l58/run_metadata.json`
- `plm_steering/icbinb_audit_out/cases/l58/checksums.sha256`

Do not copy these current L58 entries into the ICBINB audit:

- `l54_catalytic_vs_l55_disorder`
- `l54_catalytic_vs_l57_expression`
- `l54_catalytic_steering_vectors.npy`

H5 failure removes only the supporting diagnostic. It cannot by itself stop
the paper, and H5 success cannot rescue H3 or H4.

## 10. Seed registry

Every seed must be stored as an integer under a named role. Directory names
are not seed records.

| Study | Seed role | Frozen value or rule |
|---|---|---|
| L52 | cohort and split seed | 0 |
| L52 | mask seed | `0 + evaluation_index` |
| L52 | random-direction seed | 1 |
| L52 | original bootstrap seed | 0 |
| L52 | audit failure-risk bootstrap seed | 52000 |
| L55 seed `s` | legacy cohort and split seed | `s`, for `s` in `{0,1,2}` |
| L55 seed `s` | legacy mask seed | `s + evaluation_index` |
| L55 seed `s` | legacy random-direction seed | `s + 1` |
| L55 seed `s` | legacy bootstrap seed | `s` |
| L55 seed `s` | audit failure-risk bootstrap seed | `55000 + s` |
| L56 | random train/test and CV seed | 0 |
| L57 | cohort and split seed | 0 |
| L57 | mask seed | `0 + evaluation_index` |
| L57 | random-direction seed | 1 |
| L57 | original bootstrap seed | 0 |
| L57 | audit failure-risk bootstrap seed | 57000 |
| L58 | direction-build seed | 0 |

The L55 seed design is intentionally recorded as a legacy joint perturbation.
It does not satisfy an isolated seed-factor design. A later isolated
direction-seed experiment would require one fixed evaluation cohort, fixed
mask seeds, fixed control-direction seeds, and separate direction-build
seeds. That later experiment is outside this minimum package.

## 11. Statistical reporting

### 11.1 Generation studies

For L52, L55, and L57, report one row per case, seed, layer scope, direction
arm, and alpha with:

- attempted, scoring-valid, and technical-failure counts;
- count for each technical-failure reason and the separate low-complexity
  diagnostic;
- technical-failure and low-complexity risks with 95 percent intervals;
- paired risk differences with 95 percent percentile bootstrap stability
  intervals;
- jointly scoring-valid and historical-filter pair counts;
- conditional arm means;
- paired conditional score difference and 95 percent interval;
- positive-pair fraction;
- source-relative and baseline-relative edit burden;
- decision under the original policy;
- decision under the corrected policy.

Use 10,000 protein-level bootstrap resamples. Resample protein indices, not
individual residues. Preserve arm pairing inside each resample.

The fixed primary artifact alpha is 0.5 for L55 and L57. Do not search alphas
again. L52 high-alpha low-complexity risk at 1.0 and 2.0 is the fixed decoder
diagnostic. Safe-alpha dose-response values are secondary.

### 11.2 L56

Report all fixed scoring functions at every tier. Do not report only the best
score. State train and test counts, grouping policy, exclusions, point
estimate, interval when available, and endpoint meaning.

Tier 3 uses the maximum absolute held-out correlation across all reported
scores as its gate statistic. This avoids selecting a convenient weak score.
The organism analysis must report random-fold, organism-grouped, and
within-organism results together. It must show the length-only,
composition-only, and composition-plus-length results in one table with their
paired grouping differences and organism-clustered intervals.

### 11.3 Multiplicity and interpretation

The hypotheses in this manifest are fixed case-reproduction gates. Their
stability intervals are not a license to search across unreported
alternatives and do not support superpopulation claims.

No familywise correction is required across ICB-01 through ICB-06 because the paper
does not claim one pooled positive intervention effect. Within each study,
all tested alphas, scores, and controls must be reported. No favorable
control direction may be selected after execution.

Effect sizes and intervals take priority over significance flags. A
non-significant interval is described as inconclusive unless it is part of
the fixed artifact-check rule. No equivalence claim is allowed because this
manifest defines no smallest effect of interest for equivalence.

## 12. Artifact and provenance contract

### 12.1 Per-generation record

Each JSONL generation record must contain:

- `case_id`
- `source_protein_id`
- `source_sequence_hash`
- `evaluation_index`
- `seed_role_values`
- `layer_scope`
- `direction_arm`
- `alpha`
- `mask_fraction`
- `attempted`
- `generated_sequence`
- `generated_sequence_hash`
- `technical_failure`
- `technical_failure_reasons`
- `low_complexity`
- `score_name`
- `score_value`, null only when a technical or scoring failure prevents a
  valid score
- `source_hamming_distance`, null when source is unavailable
- `baseline_hamming_distance`, null when baseline is unavailable
- `edit_count`
- `edit_fraction`
- `output_logit_displacement`, null when logits were not saved

The generated sequence may remain in the locked raw bundle. Tables and
manuscript-facing ledgers should use its hash and derived values.

### 12.2 Run metadata

Every `run_metadata.json` must contain:

- case and claim IDs;
- provenance label;
- UTC start and end timestamps;
- exact command and exit code;
- full source commit;
- dirty-worktree status;
- manifest commit and SHA-256;
- input paths, byte sizes, row counts, and SHA-256 values;
- parent result paths and SHA-256 values;
- code file paths and SHA-256 values;
- submission-contract, claim-registry, artifact-ownership, and role-assignment
  paths and SHA-256 values;
- model repository ID and immutable model revision;
- tokenizer repository ID and immutable revision;
- Python, operating system, torch, transformers, numpy, pandas, scipy, and
  scikit-learn versions as applicable;
- device type and device name;
- all named seeds;
- all fixed configuration values;
- expected and observed output paths;
- output SHA-256 values;
- warnings, exceptions, missing fields, and retry count;
- operator or agent ID;
- review status and reviewer ID.

A model name without an immutable revision is incomplete provenance.
Dependency lower bounds in `requirements.txt` are not an environment lock.

### 12.3 Portfolio-level outputs

The completed audit root must contain:

- `plm_steering/icbinb_audit_out/claim_registry.json`
- `plm_steering/icbinb_audit_out/role_assignments.json`
- `plm_steering/icbinb_audit_out/cohort_manifest.json`
- `plm_steering/icbinb_audit_out/failure_stage_table.csv`
- `plm_steering/icbinb_audit_out/result_ledger.csv`
- one locked
  `plm_steering/icbinb_audit_out/lineage/<claim-id>.json` per claim;
- one machine-readable
  `plm_steering/icbinb_audit_out/reviews/<claim-id>.review.json` per confirmed
  claim;
- `plm_steering/icbinb_audit_out/run_metadata.json`
- `plm_steering/icbinb_audit_out/checksums.sha256`

`result_ledger.csv` has one row per fixed claim and must link every numeric
field to a case summary path and source artifact hash. Negative and failed
runs remain in the ledger. Each row exactly follows
`docs/RESULT_LEDGER_SCHEMA.md`. A confirmed row must bind its complete typed
semantics, cohort and experiment manifests, artifact lineage, assigned
producer, and accepted independent review decision. Nonconfirmed rows remain
present but cannot authorize submission evidence.

## 13. Archived execution design

This section records the former execution plan. It is inactive. Do not run any
command below as part of the paper refactor.

The former plan called for the following repository checks in an isolated
worktree. They are preserved for provenance only.

### 13.1 Preflight

```bash
git status --short
git rev-parse HEAD
sha256sum docs/ICBINB_EXPERIMENT_MANIFEST.md
uv pip freeze --python .venv/bin/python
```

The former plan would have stopped on a dirty worktree, an uncommitted
manifest, an unexpected input hash, or a mutable model revision.

### 13.2 Archived focused tests

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -p no:cacheprovider \
  tests/test_l42_steering_repro.py \
  tests/test_l51_aggregation_steering.py \
  tests/test_l52_layer_subset_causal_steering.py \
  tests/test_l55_disorder_steering.py \
  tests/test_l56_immunogenicity_proxy_validation.py \
  tests/test_l57_expression_yield_steering.py \
  -q
```

The former plan also called for additional focused tests. They are not part of
the current paper work.

### 13.3 Archived runner interfaces

The following interfaces were proposed for rerunning model experiments. They
are not part of the active plan and must not be implemented or executed
without explicit author approval.

```bash
.venv/bin/python -m plm_steering.l52_layer_subset_causal_steering \
  --out-dir plm_steering/icbinb_audit_out/raw/l52 \
  --model-revision "$MODEL_REVISION" \
  --cohort-seed 0 \
  --mask-seed-base 0 \
  --control-direction-seed 1 \
  --bootstrap-seed 0
```

```bash
.venv/bin/python -m plm_steering.l55_run_repro \
  --out-dir plm_steering/icbinb_audit_out/raw/l55/seed_0 \
  --model-revision "$MODEL_REVISION" \
  --cohort-seed 0 \
  --mask-seed-base 0 \
  --control-direction-seed 1 \
  --bootstrap-seed 0

.venv/bin/python -m plm_steering.l55_run_repro \
  --out-dir plm_steering/icbinb_audit_out/raw/l55/seed_1 \
  --model-revision "$MODEL_REVISION" \
  --cohort-seed 1 \
  --mask-seed-base 1 \
  --control-direction-seed 2 \
  --bootstrap-seed 1

.venv/bin/python -m plm_steering.l55_run_repro \
  --out-dir plm_steering/icbinb_audit_out/raw/l55/seed_2 \
  --model-revision "$MODEL_REVISION" \
  --cohort-seed 2 \
  --mask-seed-base 2 \
  --control-direction-seed 3 \
  --bootstrap-seed 2
```

```bash
.venv/bin/python -m plm_steering.l57_run_repro \
  --out-dir plm_steering/icbinb_audit_out/raw/l57 \
  --model-revision "$MODEL_REVISION" \
  --cohort-seed 0 \
  --mask-seed-base 0 \
  --control-direction-seed 1 \
  --bootstrap-seed 0
```

L56 uses cached data and must write outside the cached input directory:

```bash
.venv/bin/python -m plm_steering.l56_immunogenicity_proxy_validation \
  --out plm_steering/icbinb_audit_out/raw/l56/proxy_validation_summary.json \
  --seed 0
```

Do not rerun L58 for the minimum package. Extract only the permitted L55
versus L57 entry from the committed result.

### 13.4 Canceled L42 and L51 recovery

These proposed commands are canceled for the current paper.

```bash
.venv/bin/python -m plm_steering.l42_run_repro \
  --out-dir plm_steering/icbinb_audit_out/optional/l42 \
  --model-revision "$MODEL_REVISION" \
  --cohort-seed 0 \
  --mask-seed-base 0 \
  --control-direction-seed 1 \
  --bootstrap-seed 0

.venv/bin/python -m plm_steering.l51_run_repro \
  --out-dir plm_steering/icbinb_audit_out/optional/l51 \
  --model-revision "$MODEL_REVISION" \
  --cohort-seed 0 \
  --mask-seed-base 0 \
  --control-direction-seed 1 \
  --bootstrap-seed 0
```

Each optional bundle must satisfy the shared two-part analysis and provenance
contract. The L51 bundle must replay its saved original `PASS` policy and the
documented corrected `KILL` policy. Failure or lateness excludes the optional
case without changing the minimum-package commands.

### 13.5 Canceled audit build and verification

The former plan proposed this audit module interface. Do not implement or run
it for the current refactor.

```bash
.venv/bin/python -m plm_steering.icbinb_audit build \
  --manifest docs/ICBINB_EXPERIMENT_MANIFEST.md \
  --output-root plm_steering/icbinb_audit_out

.venv/bin/python -m plm_steering.icbinb_audit verify \
  --manifest docs/ICBINB_EXPERIMENT_MANIFEST.md \
  --output-root plm_steering/icbinb_audit_out
```

`verify` must return nonzero if an expected row, denominator, seed, provenance
field, policy result, or checksum is missing. It must also reject any L54,
L43, L48, or L49 evidence in the ICBINB result ledger. It validates the exact
six-claim set, role separation, typed result objects, lineage parent hashes,
known artifact ownership, and machine-readable review bindings before a
confirmed row can authorize evidence.

## 14. Confounds and limitations

The result ledger and paper limitations must include:

- All generation studies use ESM2-650M and one single-shot argmax masked-fill
  decoder at mask fraction 0.30.
- The scoring endpoints are compositional surrogates. They are not biological
  assays or independent property validators.
- The 25 percent single-residue threshold was calibrated on L42. It is
  conservative against real low-complexity disorder sequences and is not a
  universal protein-validity rule.
- Conditioning Part B on jointly scoring-valid output can select different
  protein subsets across arms. Part A is required to expose that selection.
- The current studies use one matched random direction per seed, not a random
  direction distribution.
- The current runners use broad model names rather than immutable model and
  tokenizer revisions. The new package lock does not repair provenance for
  earlier result files.
- L52 lacks source evaluation sequences in its committed result file, so
  source-relative edit burden cannot be reconstructed from that file.
- L55 legacy seeds change several random processes and evaluation cohorts
  together. The result supports seed sensitivity in aggregate, not a causal
  attribution to direction construction.
- L56 labels differ by endpoint, host context, assay process, and source
  organism. Tier 1 and Tier 2 cannot stand in for Tier 3.
- L56 full-length labels are effort-normalized but remain observational and
  organism-imbalanced.
- L57's score directly depends on charged-residue composition. Its
  residue-exclusion result shows decision sensitivity but does not prove that
  the remaining effect is zero or identify a biological mechanism.
- L58 has one seed, no control-vector distribution, no uncertainty estimate,
  and no test file. Positive cosine similarity is descriptive.

## 15. Historical execution stop rules

These rules describe the superseded execution plan. They do not create current
rerun, coding, or lock-building tasks.

Stop a case immediately if:

- an expected raw arm, attempted generation, cohort identifier, or seed is
  missing;
- an input or parent artifact hash changes without a recorded review;
- a runner overwrites an input artifact or another case's output;
- fewer than 30 jointly scoring-valid pairs remain for an inferential
  conditional-score claim;
- a technical or scoring failure is assigned a numerical score;
- a requested rerun changes an alpha, seed, threshold, cohort, score, or
  control after outcomes are inspected;
- a critical or major statistical review finding remains unresolved.

Apply these case-specific stops:

- Exclude L42 and L51 if their complete recovery bundles are not locked by
  2026-08-15 23:59 Anywhere on Earth. Do not delay the minimum package.
- Stop ICBINB-BIO if L55 seeds 0, 1, and 2 are not reproduced with explicit
  metadata by that cutoff.
- Remove L58 if its permitted one-seed entry or checksum does not verify. Do
  not replace it with L54 geometry.
- Never start L56 steering from this manifest. A passing surrogate tier does
  not override the failed real-endpoint gate.

Stop the ICBINB submission if:

- any of the three required failure mechanisms lacks a reproducible audit
  bundle;
- the composition mechanism cannot support both the L57 sensitivity claim and
  the L55 seed-sensitivity claim after review;
- fewer than three distinct mechanisms remain defensible;
- any numeric manuscript claim lacks a result-ledger row and immutable source
  path;
- L54, L43, or attention-head results enter the paper;
- L58 is described without the one-seed limitation;
- the conclusion claims improved biological properties;
- the statistical reviewer has an unresolved critical or major finding.

Do not tune this manifest to recover a failed case. Narrow or remove the
claim, preserve the failed output, and record the stop decision.

## 16. Existing evidence limitations

These items explain limits in the saved evidence and former execution design.
They do not block manuscript restructuring and are not implementation tasks:

1. `plm_steering.icbinb_audit` does not exist.
2. The L52, L55, L56, and L57 runners do not implement the required output,
   model-revision, or separate seed-role arguments.
3. L55 result files do not record their seed or complete run configuration.
4. L52's Meltome CSV is locally present but ignored by git, and its committed
   result does not include source evaluation sequences, explicit failure
   flags, full configuration, or model revision.
5. L42 has no committed raw result bundle or tracked model runner. L51's
   committed JSON lacks raw sequences and scores.
6. L56's summary omits row-level predictions, complete cohort exclusion
   counts, source versions, and input hashes.
7. L58 has no focused test and its current script always computes and saves
   L54 artifacts alongside L55 and L57.
8. No current audit-interface test covers the two-part generation analysis,
   the 0.05 failure margin, policy replay, complete typed ledger semantics,
   role assignments, lineage parents, review decisions, or ownership
   exclusions.
9. `requirements-lock.txt` records the tested package versions, but the
   runtime platform, model revision, and tokenizer revision are not pinned.

Address each relevant limitation through careful wording, an explicit
limitation, or claim removal. Do not write code or rerun an experiment to
close these items without explicit author approval.
