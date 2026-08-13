# Statistical Contract Rereview

Date: 2026-08-13

Reviewer role: Independent statistical contract reviewer

## Scope

This rereview covers:

- `docs/CONTRACT_REVIEW_RESOLUTION.md`
- `docs/PAPER_PORTFOLIO_PLAN.md`
- `docs/CLAIM_REGISTRY.md`
- `docs/COHORT_MANIFEST_SCHEMA.md`
- `docs/RESULT_LEDGER_SCHEMA.md`
- `docs/CITATION_LEDGER_SCHEMA.md`
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`
- `docs/INTERP4DISCOVERY_LOCK_VALUES.json`
- the prior findings in `docs/STATISTICAL_CONTRACT_REVIEW.md`

This is a contract rereview. It does not verify experiment outputs, runner
implementations, or manuscript claims.

## Decision

Remaining Critical contract findings: 0

Remaining Major contract findings: 5

The corrected contracts resolve most prior statistical findings. Several
experiments remain blocked because required code, data reconstruction,
precision planning, and lock values do not yet exist. Those blocked tasks are
not contract findings when the current contract prevents execution or claim
confirmation.

The five Major findings below must be corrected before the contract baseline
is frozen.

## Prior Finding Verification

| Prior finding | Rereview result | Controlling sections |
|---|---|---|
| C1, L57 used non-significance to claim removal | Corrected. ICB-05 and H4 now claim only that the E/L-excluded analysis does not meet the positive rule. They explicitly call an interval containing zero inconclusive. | `docs/CLAIM_REGISTRY.md`, "ICB-05"; `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 2 and 8.3 |
| C2, L56 absence and confounding claims | The claim wording is corrected. ICB-02 is limited to observed validation performance. ICB-03 says the grouped result is consistent with confounding. One Major resampling mismatch remains in M3 below. | `docs/CLAIM_REGISTRY.md`, "ICB-02" and "ICB-03"; `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 6.1 through 6.3 |
| M1, generation estimands were incomplete | Corrected. The target is the fixed saved cohort under realized masks and controls. Proteins receive equal weight. Part B is the jointly scoring-valid contrast. Bootstrap intervals are finite-cohort stability summaries. | `docs/PAPER_PORTFOLIO_PLAN.md`, Section 6, rules 12 through 14; `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 4.1 through 4.4 |
| M2, L52 pairing was not auditable | Contract corrected, implementation blocked. H1 now requires verified reconstruction of source IDs, sequence hashes, and array order, or a rerun with identifiers. H1 fails if the mapping does not verify. | `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 5.2 and 5.4 |
| M3, the low-complexity threshold was treated as a universal failure | The analysis contract is corrected. Conditions 1 through 4 are technical or scoring failures. Condition 5 is a separate historical low-complexity diagnostic. The registry wording remains inconsistent, as described in M1 below. | `docs/PAPER_PORTFOLIO_PLAN.md`, Section 6, rule 14; `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 4.2 through 4.4 |
| M4, provenance labels conflicted | ICB-04 and ICB-05 are corrected. L56 provenance still conflicts between the registry and manifest, as described in M2 below. | `docs/CLAIM_REGISTRY.md`, "ICB-02" through "ICB-05"; `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 2 |
| M5, Interp head estimand and permutation null were misaligned | Corrected. The contract now defines a layer-adjusted rank association over the fixed 480 heads and removes the head-label permutation test. Panel resampling is labeled as stability analysis. | `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Sections 4 and 8.2 |
| M6, Interp claims were broader than their analyses | Corrected in the controlling claim registry and preregistration. INT-01 names zero replacement. INT-03 is group-level top-five replication. Imprecise mean replacement cannot support method robustness. | `docs/CLAIM_REGISTRY.md`, "INT-01" and "INT-03"; `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Sections 8.1 and 8.2 |
| M7, Interp precision planning was incomplete | Contract corrected, implementation blocked. The preregistration requires simulation of both complete branches, matching attrition, shared controls, all 480 outcomes, and all ten equivalence intervals. The precision result must be approved before confirmation opens. The lock workflow still has a Major ordering defect, described in M5 below. | `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 9 and Section 16, `PRECISION_PLAN` |
| M8, Interp missingness and dependence were unresolved | Corrected. Position matching is without replacement. All heads and methods are recomputed jointly in each bootstrap. Non-finite required results and missing required outputs stop the affected branch. | `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Sections 6, 7.3, and 10 |

## Remaining Major Contract Findings

### M1. ICB-01 still calls low-complexity outputs invalid or unscorable

References:

- `docs/CLAIM_REGISTRY.md`, Section "ICB-01"
- `docs/PAPER_PORTFOLIO_PLAN.md`, Section 3, "Terms and evidence boundaries"
- `docs/PAPER_PORTFOLIO_PLAN.md`, Section 6, rule 14
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 2, 4.2, 5.1, and 5.4

The corrected manifest says that a condition-5 output is scoring-valid, keeps
its numerical score, and receives a low-complexity flag. H1 is accepted from
high-alpha low complexity and loss of the historical-filter denominator.

ICB-01 still says that the method began to produce "invalid or unscorable
sequences." That statement is broader than the acceptance rule. H1 can pass
without showing any technical or scoring failure.

Revise ICB-01 to name low-complexity outputs and the historical filter. For
example:

> Survivor-only score comparisons can make a steering method appear useful
> after low-complexity outputs have removed most or all of a comparison arm
> from the historical-filter denominator.

The plan definition of generation failure should also distinguish technical or
scoring failure from the separate low-complexity diagnostic.

### M2. L56 provenance remains inconsistent

References:

- `docs/CLAIM_REGISTRY.md`, Section "ICB-02," provenance row
- `docs/CLAIM_REGISTRY.md`, Section "ICB-03," provenance row
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 2, ICB-02 and ICB-03 rows
- `docs/RESULT_LEDGER_SCHEMA.md`, Section "Required columns," `provenance`

The registry labels ICB-02 as a prospective stop and ICB-03 as a retrospective
explanation. The manifest labels ICB-02 as a retrospective endpoint audit and
ICB-03 as a post-hoc grouping sensitivity analysis.

The result ledger permits only one provenance value per claim. The current
contracts therefore cannot populate one controlling row for either L56 claim
without choosing between conflicting labels.

Separate the chronology of the original stop decision from the provenance of
the current claim-supporting analysis. Use one controlling analysis label in
both files. If the current row-level reconstruction and grouped analysis were
defined after the saved results were seen, use `retrospective` for ICB-02 and
`post_hoc_sensitivity` for ICB-03.

### M3. The L56 H2a bootstrap does not satisfy the registered cluster-aware rule

References:

- `docs/CLAIM_REGISTRY.md`, Section "ICB-02," required-analysis row
- `docs/COHORT_MANIFEST_SCHEMA.md`, Sections "Record fields" and "Validation"
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 6.2, paragraphs defining H2a
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 6.3, H2 acceptance

ICB-02 requires cluster-aware stability analysis. The cohort schema requires a
cluster identifier and clustering rule. The manifest instead says to bootstrap
individual peptides within each endpoint cohort.

If related peptides occur in the same sequence cluster, peptide-level
resampling treats dependent records as independent and can narrow the H2a
stability interval. That interval controls whether the endpoint ordering
passes.

Define the peptide clustering rule before execution and resample complete
clusters, preserving any peptide that appears in more than one endpoint
cohort. If the intended unit is truly the unique peptide with no larger
dependence cluster, remove "cluster-aware" from the registry and justify that
choice in the cohort manifest.

### M4. The result-ledger schema can validate a confirmed claim whose gate did not pass

References:

- `docs/CLAIM_REGISTRY.md`, Section "Status definitions"
- `docs/RESULT_LEDGER_SCHEMA.md`, Section "Required columns," `claim_status`
  and `gate_result`
- `docs/RESULT_LEDGER_SCHEMA.md`, Section "Validation"
- `docs/PAPER_PORTFOLIO_PLAN.md`, Sections 5.4 and 14.1

The schema allows `claim_status = confirmed` and separately allows
`gate_result = fail`, `not_estimable`, or `not_run`. Its validation rules reject
a confirmed claim with an unresolved Critical or Major review finding, but
they do not reject a confirmed claim whose gate did not pass.

This is a fail-open status contract. A row can satisfy the listed validation
rules while claiming confirmation without the registered acceptance rule.

Require all of the following for `claim_status = confirmed`:

- `gate_result = pass`;
- all required raw and derived artifact hashes verify;
- required denominators and estimates are present;
- the independent review is complete;
- no required analysis is `not_run` or `not_estimable`.

Negative or failure-focused claims still use `gate_result = pass` when their
registered statement and acceptance rule are supported.

### M5. The Interp preregistration lock has a circular construction order

References:

- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 2, "Freeze and leakage
  rules"
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 9, precision simulation
  requirements
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 13.9, "Required commands"
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 16, `CONFIRMATION_PANEL`,
  `PRECISION_PLAN`, `RUNTIME_BUDGET`, and `ROLE_HANDOFF`
- `docs/INTERP4DISCOVERY_LOCK_VALUES.json`, `status` and all 20 keys

Section 16 requires the final preregistration lock to contain the benchmark,
precision simulation, panel information, and role handoff. `ROLE_HANDOFF`
also requires matching stage-lock hashes.

Section 13.9 creates the preregistration lock before `benchmark`,
`build-cohort`, and `match`. Those later commands require the preregistration
lock as input. A matching stage-lock hash cannot exist before `match`, but
`match` cannot run before the preregistration lock exists.

The same problem affects the precision artifact. It must exist and be approved
before confirmation opens, but the command contract does not define a prelock
feasibility or precision stage.

Define two different states:

1. A non-authorizing feasibility specification may run discovery-only
   benchmarking, candidate cohort construction, matching simulation, and
   precision planning.
2. A final immutable preregistration lock consumes those reviewed artifacts
   and authorizes confirmation-panel processing.

Move matching stage-lock hashes out of the preregistration `ROLE_HANDOFF` key.
Record owner identities and write scopes before the final lock. Record and
accept the actual matching stage hash in a separate post-matching handoff
artifact before ablation.

The current null lock-values file correctly blocks execution, but filling its
keys cannot resolve this ordering cycle without a contract change.

## Corrected Contracts Versus Blocked Implementation

The following items are implementation work, not additional statistical
contract findings.

### ICBINB implementation blockers

References:

- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 5.2, L52 mapping requirement
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 6.3, L56 fail-closed fields
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 13.3 and 13.5
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 15 and 16

The following work remains blocked before claim confirmation:

- reconstruct and independently verify the L52 source mapping, or rerun L52;
- implement the audited L52, L55, L56, and L57 command interfaces;
- reproduce all three L55 legacy whole-run seeds with explicit metadata;
- produce L56 row-level predictions, fold assignments, and exclusion counts;
- implement and test `plm_steering.icbinb_audit`;
- pin model and tokenizer revisions and complete run provenance.

The manifest states that the target interfaces are not implemented, makes the
legacy entry points fail closed, and stops a case when required identifiers,
rows, seeds, or artifacts are missing. These are valid implementation gates.

### Interp implementation blockers

References:

- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, status lines and Sections 14
  through 16
- `docs/INTERP4DISCOVERY_LOCK_VALUES.json`, `status` and `keys`

All 20 lock keys are present and null, and the file status is `draft`. The
preregistration says that null, unreviewed, or invalid keys stop confirmation.
The absent panel, margins, precision simulation, seeds, calibration thresholds,
runtime budget, owners, and artifacts are therefore explicit implementation
blockers. They are not evidence that the statistical rules failed.

After M5 is corrected, these values may be populated only from reviewed
feasibility artifacts. Confirmation remains unauthorized until every required
value validates and the final lock is approved.

## Gate Recommendation

Do not freeze the contract baseline yet.

Correct M1 through M5, refresh the controlling hashes, and rerun this
statistical contract review on the exact baseline revision. The blocked
experiment implementation may begin only after the corrected contracts are
committed and their fail-closed checks pass.
