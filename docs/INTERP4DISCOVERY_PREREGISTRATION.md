# Interp4Discovery Preregistration

Date drafted: 2026-08-13

Confirmatory core completion deadline: 2026-08-19

Submission go or no-go gate: 2026-08-20

Status: Draft accepted, not frozen, and not authorized for confirmation
execution. No confirmation-panel attention or ablation result may be computed
until every Section 16 lock key has a validated value, the values have been
reviewed, and the frozen manifest has been hashed.

## 1. Confirmatory question and claim

Research question:

Does contact enrichment on a discovery structure panel identify attention
heads whose outputs are necessary for masked-residue prediction on an
independent structure panel?

Primary hypothesis:

Discovery-panel contact enrichment predicts contact-specific ablation damage
on an independent confirmation panel.

The primary outcome is:

ablation damage on contact-bearing positions minus ablation damage on matched
non-contact positions within the same protein.

The study has one ordered decision path:

1. Test the positive 480-head association branch.
2. If that branch does not pass, test the top-five equivalence branch.
3. If neither branch passes, stop the Interp4Discovery submission.

A non-significant positive test is not evidence of equivalence. Grouped
ablation is exploratory and cannot rescue either confirmatory branch.

## 2. Freeze and leakage rules

This study has two pre-confirmation states.

1. The non-authorizing feasibility specification permits discovery-only
   benchmarking, candidate confirmation-cohort construction from structure
   and sequence metadata, matching-rule simulation without confirmation model
   outcomes, and branch-specific precision planning. It cannot authorize
   confirmation attention, baseline probability, matching, or ablation work.
2. The final immutable preregistration lock consumes the reviewed feasibility
   artifacts, all resolved lock values, owner assignments, and exact hashes.
   Only this final lock can authorize confirmation-panel processing.

The discovery panel may be used for pilot variance estimates, sample-size
planning, head ranking, head-control matching, matching-rule development,
mean-replacement estimation, and runtime benchmarking.

The confirmation panel may be used only after the preregistration lock is
complete. Before the lock, no worker may inspect confirmation-panel attention
enrichment, baseline masked-residue results, single-head ablation results, or
summary statistics.

Baseline true-residue probability is needed to construct position matches.
After the panel lock, a matching worker may compute baseline probabilities and
run the frozen matching code. That worker must not receive any ablation output.
The resulting matched sets are locked before any head ablation is summarized.

Confirmation-panel enrichment may test correlational replication. It may not
rerank heads, change the top-five set, choose controls, change matching
tolerances, or change an analysis threshold.

The following items must be part of the final preregistration lock:

- this document and its content hash;
- the source revision and environment lock;
- the reviewed `feasibility/discovery_manifest.json` and
  `feasibility/candidate_cohort_manifest.json` hashes;
- the position-matching specification;
- the selected top-five heads and their matched head controls;
- all numeric statistical, precision, replication, and calibration thresholds;
- the seed registry;
- the runtime projection and compute decision;
- the expected artifact list.

The `ROLE_HANDOFF` lock key records the discovery, cohort and matching,
ablation, analysis, and Interp paper-owner identities and their disjoint write
and read scopes. All five agent IDs must be distinct.
After actual matching closes, `matching/handoff.json` records the accepted
cohort, discovery, and matching stage hashes. The ablation command requires
that separate handoff artifact.

## 3. Structure panels

### 3.1 Discovery and pilot panel

The discovery panel is the original L48 panel:

- 1UBQ
- 1CRN
- 1LYZ
- 1MBN
- 2LZM
- 1PGA
- 1TEN
- 1SHG

This panel has already been inspected. It is not confirmatory evidence.
It is a fixed convenience panel, not a random sample from all proteins.
Resampling it measures sensitivity to its eight protein contributions and
does not support population-wide uncertainty.

For each of the 480 heads, discovery contact enrichment is the pooled fraction
of eligible attention mass placed on contacts divided by the pooled background
contact rate. This is the metric implemented in L48. Ranking uses this metric
in descending order.

`DECISION TO FREEZE`: Record the exact PDB file versions, checksums, chain IDs,
and any discovery exclusions used for the final ranking. Record whether the
existing L48 artifacts are reused or regenerated from a fixed model revision.

### 3.2 Independent confirmation panel

The confirmation panel must contain fixed PDB structures that have no
sequence-cluster overlap with the discovery panel under one frozen clustering
procedure. The same rule must also identify duplicate or near-duplicate chains
within the confirmation panel.

The target population is the finite set of confirmation chains that pass the
frozen PDB snapshot, clustering, diversity, chain, length, contact, and
matching rules. The primary claim is limited to this panel and the 480 fixed
model heads. Any generalization beyond that finite set is future work.

The required number of proteins is set by a precision calculation based on
discovery-panel protein-level variance and the frozen confidence-interval
targets. Proteins may not be added after any confirmation result is inspected.

`DECISION TO FREEZE`: Record all confirmation PDB IDs, chain IDs, PDB snapshot
or download date, file hashes, clustering software and version, sequence
identity threshold, coverage rule, panel diversity criteria, panel-selection
seed, required protein count, and maximum sequence length policy.

If the required protein count exceeds the compute budget, stop before opening
the confirmation panel.

## 4. Model, contacts, and statistical unit

The model family is `Rostlab/prot_bert_bfd`, with 30 layers and 16 heads per
layer. The confirmatory analysis includes all 480 heads.

`DECISION TO FREEZE`: Record the exact model and tokenizer revisions, local
artifact hashes, library versions, numerical precision, device type, and
determinism settings.

A contact is a pair of residues whose C-alpha distance is less than 8
angstroms and whose absolute sequence separation is at least 6. A position is
contact-bearing when it has at least one such contact. A position is
non-contact when it has none.

The independent sampling unit for damage estimation is the protein. Residues
are repeated observations within proteins. Heads are fixed model components,
not independent biological samples.

All primary summaries give each protein equal weight after matching. The
hierarchical bootstrap samples proteins first and matched position sets second.
No residue-pooled confidence interval may be reported as the primary
uncertainty estimate.

The bootstrap interval is a stability interval for the frozen panels. It
does not treat the 480 heads as random draws and does not claim uncertainty
over a population of possible heads.

## 5. Head selection without leakage

The top-five set is selected once by descending discovery-panel enrichment.
Selection occurs before any confirmation-panel output is computed.

`DECISION TO FREEZE`: Record the five layer and head IDs and the deterministic
rule for ties.

Each selected head receives at least two eligible control heads from the same
layer. Selected heads are not eligible as controls. Controls are matched using
only discovery-panel values for:

- attention entropy;
- single-head output norm;
- model-output displacement caused by single-head ablation.

The control set should include one low-enrichment head and one randomly
selected eligible head when the frozen matching set permits this. Random
selection uses only the registered head-control seed.

`DECISION TO FREEZE`: Define each matching feature, its aggregation over
proteins and positions, feature scaling, matching tolerances, the exact number
of controls per selected head, control reuse, low-enrichment eligibility,
random-control eligibility, tie handling, and the action when fewer than the
required controls exist. Freeze the resulting control IDs.

No confirmation-panel quantity may be used in head selection or head-control
matching.

## 6. Matched non-contact positions

Position matching is performed once and reused for every head and both
replacement variants. A contact-bearing position may be matched only to
non-contact positions in the same protein.

Matching is without replacement within each protein. One non-contact position
may serve only one retained contact position. If this rule leaves too little
common support under the frozen minimum, the study stops rather than reusing
controls.

Matching uses:

- residue identity when possible;
- distance from the nearest terminus;
- local sequence context;
- baseline log probability of the true residue.

For a matched contact position `i`, let its non-contact controls be `M(i)`.
The same matched set is used for baseline, zero replacement, and mean
replacement.

`DECISION TO FREEZE`: Define the local-context representation, exact-match
hierarchy for residue identity, distance metric, calipers, matching ratio,
deterministic tie rule, unmatched position handling, minimum matched positions
per protein, minimum panel common support, and the matching seed if any step is
random.

Balance is checked before ablation results are opened. Every matched covariate
must have an absolute standardized mean difference no greater than 0.1.
Failure of a frozen common-support or balance rule stops the confirmatory
analysis. The rule may not be relaxed after ablation output is seen.

Every bootstrap replicate samples proteins and then complete contact-position
matched sets. It recomputes outcomes for all heads and both replacement
methods jointly. Selected heads and any shared head controls remain linked
inside the same replicate. No head contrast or replacement method receives
an independent resample. A replicate that fails the frozen support rule is a
failed replicate and is handled by the frozen fail-closed rule in Section 8.

## 7. Intervention and outcomes

### 7.1 Masked-residue task

Mask one residue at a time. All other sequence residues remain visible. Record
the model probability assigned to the true residue.

The baseline prediction for each position is computed once and reused for all
head comparisons.

### 7.2 Ablation variants

The 480-head association uses zero replacement. The requested head slice is
set to zero at every token position while all other head slices are unchanged.

Mean replacement is required for the selected heads. For the equivalence
branch it is also required for every matched head control. Replacement values
must be estimated from the discovery panel only.

`DECISION TO FREEZE`: Define the mean-replacement tensor, its conditioning and
aggregation, and the exact discovery examples used to estimate it.

### 7.3 Continuous outcome

For protein `p`, head `h`, position `i`, and replacement variant `v`,
define ablation damage as:

`damage[h,p,i,v] = log p_baseline(true residue) - log p_ablated(true residue)`

Natural logarithms are used. Positive damage means that ablation reduced the
probability of the true residue.

Compute each log probability directly with `log_softmax` in at least
float32. Do not take the logarithm of a rounded probability. A non-finite
baseline or ablated log probability is a required-result failure. Retry only
under the frozen technical retry rule. If it remains non-finite, keep the
failure record and stop the affected confirmatory branch. Do not drop the
position or replace the value.

For each matched contact position, define:

`matched_damage[h,p,i,v] = damage[h,p,i,v] - mean(damage[h,p,j,v] for j in M(i))`

The protein-level contact interaction is the mean matched damage over retained
contact positions in that protein:

`D[h,p,v] = mean_i matched_damage[h,p,i,v]`

The head-level outcome is the equal-weight mean over retained proteins:

`D[h,v] = mean_p D[h,p,v]`

This is the primary outcome. Masked-residue accuracy and generic ablation
damage without the contact interaction are secondary outcomes.

## 8. Confirmatory analyses

### 8.1 Correlational replication gate

The prespecified top-five set must replicate contact enrichment as a group on
the confirmation panel under a frozen rule. This result is a gate, not a new
selection step. It does not establish that every selected head replicates.

`DECISION TO FREEZE`: Define the top-five aggregation, bootstrap interval,
confidence level, and numerical replication threshold. The current portfolio
plan suggests pooled enrichment above 1 with an interval excluding 1, but this
is not frozen until the exact calculation is recorded.

### 8.2 Positive 480-head association branch

For each head `h`:

- `E[h]` is discovery-panel contact enrichment;
- `D[h,zero]` is confirmation-panel contact-specific damage under zero
  replacement.

The primary association is a layer-adjusted finite-head rank correlation.
Within each layer, rank its 16 heads separately by `E[h]` and by
`D[h,zero]`, using average ranks for ties. Center both rank values within
layer, pool the 480 centered rank pairs, and compute their Pearson
correlation. Call this statistic `rho_layer`. A positive value means that
higher discovery enrichment is associated with greater confirmation-panel
damage among heads in the same layer.

The 480 heads are the complete finite set under study. There is no head-label
permutation test and no claim that heads are exchangeable random samples.

Stability is computed by independently resampling discovery proteins and
confirmation proteins. Discovery enrichment, confirmation damage, within-layer
ranks, and `rho_layer` are recomputed in every hierarchical bootstrap
replicate. Confirmation matched sets are resampled within sampled proteins
under the joint rule in Section 6. This interval describes sensitivity to the
two frozen panels, not a population of possible heads.

The positive branch passes only when all of these conditions hold:

1. the lower bound of the association stability interval is greater than the frozen
   minimum association;
2. the association interval width is no greater than twice the minimum
   association;
3. all 480 heads have valid zero-replacement outcomes;
4. correlational replication, matching, hook isolation, and perturbation
   calibration pass;
5. mean replacement on the top-five heads shows no multiplicity-adjusted,
   statistically clear sign reversal.

Mean replacement does not retest the 480-head association. For the sign check,
the five top-head contact interactions receive a familywise correction. A
clear sign reversal occurs when `D[s,mean]` and `D[s,zero]` have opposite
signs and the familywise-adjusted interval for `D[s,mean]` excludes zero. If
the mean-replacement interval is imprecise, the zero-replacement claim may
still pass, but the paper must call method sensitivity inconclusive. It may
not claim robustness across replacement methods.

`DECISION TO FREEZE`: Set the minimum association, total familywise alpha,
positive-branch alpha allocation, number of bootstrap replicates, interval
method, and the familywise interval method for the five mean-replacement sign
checks.

### 8.3 Top-five contrasts

For selected head `s`, let `C(s)` be its frozen matched head controls. For
replacement variant `v`, define:

`contrast[s,v] = D[s,v] - mean(D[c,v] for c in C(s))`

Positive values mean that the selected contact-enriched head causes more
contact-specific damage than its matched controls.

There are five zero-replacement contrasts and five mean-replacement contrasts.
Control heads are weighted equally within each selected-head contrast.

### 8.4 Equivalence branch

The equivalence branch is tested only if the positive branch does not pass.
It asks whether each selected head is practically equivalent to its matched
controls.

Let the symmetric equivalence interval be `[-delta, +delta]`. For each of the
ten selected-head by replacement-variant contrasts, test:

- lower null: `contrast <= -delta`;
- upper null: `contrast >= +delta`.

Use two one-sided tests. For each contrast, the equivalence p-value is the
larger of its two one-sided p-values. Apply Holm correction across all ten
contrasts at the equivalence-branch familywise alpha. Equivalence is declared
only if every corrected test passes and every corresponding
familywise-adjusted interval lies inside `[-delta, +delta]`.

The equivalence branch also requires every adjusted interval to have width no
greater than `2 * delta`. A pooled top-five average cannot replace the five
individual contrasts.

`DECISION TO FREEZE`: Set `delta`, the equivalence-branch alpha allocation,
the bootstrap test and adjusted-interval construction, and the rule for
bootstrap replicates with failed matching support.

### 8.5 Familywise error control

Let `alpha_family` be the total confirmatory familywise error rate. Freeze
positive and equivalence allocations such that:

`alpha_positive + alpha_equivalence <= alpha_family`

The positive branch uses one global 480-head stability interval. The study
does not run 480 head-specific significance tests. Holm correction covers the
ten equivalence contrasts. The five positive-branch mean-replacement sign
checks use their separately frozen familywise correction.

`DECISION TO FREEZE`: Set `alpha_family`, both branch allocations, and the
positive-branch sensitivity allocation. These values must be fixed before any
confirmation output is computed.

## 9. Association and equivalence margins

The minimum association and `delta` must be justified before confirmation
analysis.

The minimum association justification must:

- state the smallest discovery-to-damage rank association that would make
  contact enrichment useful for causal candidate selection;
- explain the expected change in head ranking or candidate quality;
- use discovery-panel precision without using confirmation outcomes;
- show that the planned panel can meet the interval-width rule.

The equivalence-bound justification must:

- state the largest selected-head versus control difference that is still
  practically unimportant;
- interpret `delta` on the true-residue log-probability scale and as the
  corresponding probability-odds multiplier;
- compare `delta` with discovery-panel protein-level variability and ordinary
  masked-residue variation;
- explain why an effect outside the bound would change the scientific
  conclusion;
- show that the planned panel can place all ten adjusted intervals inside the
  bound if practical equivalence is true;
- receive review from the independent statistical reviewer.

Neither margin may be chosen only because it produces a feasible sample size,
fits the old L48 confidence interval, or makes a desired conclusion easier.
If no defensible margin can be stated, stop the submission.

Before the confirmation panel opens, run a discovery-only precision
simulation that executes the complete frozen analysis pipeline for both
branches. It must vary or resample:

- discovery enrichment over discovery proteins;
- confirmation-like proteins held out from any head selection;
- position matching and common-support attrition;
- all 480 layer-adjusted head outcomes;
- all ten selected-head by replacement-method contrasts;
- shared head controls and complete matched sets;
- familywise interval adjustment;
- failed support under the frozen fail-closed rule.

The selected panel size must meet the positive-branch width rule and give a
prespecified probability that every equivalence interval can fit inside the
margin when the simulated effects are within that margin. Size for the more
demanding allowed branch controls. A generic protein-level variance
calculation is not enough. Save the simulation code, inputs, seeds, full
result distribution, and decision.

`DECISION TO FREEZE`: Record both numerical margins, their written
justifications, the branch-specific precision simulation, selected panel
size, target planning probability, and statistical-review approval.

## 10. Exclusions and missing results

Structure and chain exclusions are applied without access to attention or
ablation outcomes. Allowed reasons are:

- sequence-cluster overlap under the frozen rule;
- missing or unreadable structure data;
- no valid standard-amino-acid chain under the frozen chain rule;
- failure of the frozen length or tokenizer rule;
- no eligible contact-bearing or non-contact positions;
- failure of frozen matching common support or balance;
- a prespecified technical failure that remains after the allowed retries.

Position exclusions are limited to rules frozen before ablation:

- non-standard or un-tokenizable residue;
- missing C-alpha coordinate;
- invalid baseline true-residue probability;
- no match under the frozen matching rule;
- a logged model-evaluation failure after allowed retries.

No protein, position, head, or bootstrap replicate may be excluded as an
outlier because its effect is large, small, or unfavorable. No replacement
protein may be added after confirmation outcomes are opened.

All 480 zero-replacement head results are required. A missing head result stops
the positive branch. All five selected-head mean-replacement results are
required for the positive branch. All ten selected-head and matched-control
replacement results are required for the equivalence branch. A required
result that remains missing after frozen retries stops its branch and remains
in the artifact as a failure record. It is never dropped. If exclusions reduce
the panel below the frozen protein, common-support, or precision requirement,
both branches stop.

`DECISION TO FREEZE`: Set length limits, minimum retained proteins, minimum
matched positions, allowed retry count, technical failure definitions, and
whether a fully restarted run replaces or supplements a failed run. Also set
the maximum allowed failed-bootstrap proportion and the branch decision when
that limit is exceeded.

## 11. Seeds and reproducibility

Use separate seeds for separate purposes. At minimum, register:

- confirmation panel selection and any clustering tie;
- position sampling, if all eligible positions are not used;
- position-matching ties;
- random head-control selection;
- discovery protein bootstrap;
- confirmation protein bootstrap;
- within-protein matched-set bootstrap;
- branch-specific precision simulation;
- sensitivity analyses.

The L49 pilot seed of 0 does not automatically become a confirmation seed.
One integer must not control the whole experiment.

`DECISION TO FREEZE`: Record each integer seed, random-number generator,
library version, and exact purpose. Record deterministic operations explicitly
rather than assigning them an unused seed.

## 12. Runtime benchmark and compute rule

Before the full run, benchmark all 16 heads in one layer on 100 fixed eligible
positions using the target hardware, model revision, precision, hook code, and
output-writing path. Use discovery-panel or other non-confirmation outcomes
for the benchmark.

The benchmark record must include:

- wall-clock and accelerator time;
- warmup and model-load treatment;
- peak accelerator and host memory;
- baseline reuse;
- batch size and effective positions per second;
- software and hardware identifiers;
- output bytes per position and per head.

Project the 480-head zero-replacement run by scaling from one layer to 30
layers and from 100 positions to the frozen matched-position count. Add the
top-five and matched-control mean-replacement work, matching, resampling,
validation, artifact checks, and a 25 percent retry buffer.

`DECISION TO FREEZE`: Record the benchmark result, frozen position count,
projected hours for each core stage, available compute window, and maximum
compute budget.

ICBINB-BIO compute has priority. Cancel Interp4Discovery by 2026-08-14 if the
projected confirmatory core cannot finish by 2026-08-19.

By the end of 2026-08-19, all 480 zero-replacement results, required
mean-replacement results, matched controls, resampling outputs, validation
checks, and immutable artifacts must be complete. Grouped ablations are not
part of this completion requirement.

## 13. Artifact schema

The exact output root is:

`plm_steering/interp4discovery_out/$EXPERIMENT_ID/`

Before `feasibility-init`, the orchestrator selects one unique, nonempty
`EXPERIMENT_ID`. Feasibility commands use it as a provisional namespace. The
identifier becomes frozen only when the final preregistration lock records the
same value. The final lock command rejects a feasibility artifact or output
root with a different identifier. Selecting the identifier does not authorize
confirmation work. Every path below is relative to that root.

All artifacts include `schema_version`, `experiment_id`, `source_git_commit`,
`created_at_utc`, and the model revision. Feasibility artifacts also record
the hashes of the feasibility-draft preregistration and lock-values files.
Artifacts produced after the final lock record `preregistration_sha256` and
`preregistration_lock_sha256`. JSON files use `null` plus an explicit reason
for missing values. They must not contain unlabelled `NaN` or infinity values.

### 13.0 Feasibility artifacts

Before the final lock, discovery-only feasibility work writes:

- `feasibility/specification.json`
- `feasibility/runtime_benchmark.json`
- `feasibility/discovery_manifest.json`
- `feasibility/candidate_cohort_manifest.json`
- `feasibility/matching_simulation.json`
- `feasibility/precision_simulation.json`
- `feasibility/stage_lock.json`

These files contain no confirmation-panel attention, baseline probability,
matching, or ablation outcome. The final lock consumes their reviewed hashes.
The `discovery-manifest` command records the exact discovery panel, ranking
inputs, selected heads, control matching, and mean-replacement inputs. The
`candidate-cohort` command records structure and sequence metadata only. That
candidate manifest is an input to the final cohort stage and never becomes
the final cohort manifest by renaming or implicit copying.

### 13.1 `lock/preregistration_lock.json`

Required fields:

- hashes of this document, source revision, environment lock, and all input
  manifests;
- every resolved lock key from Section 16;
- freeze time and reviewer identity;
- expected artifact paths;
- confirmation-opening authorization.

### 13.2 `cohort/cohort_manifest.json`

One record per PDB chain:

- panel;
- PDB ID, chain ID, source version, and file hash;
- extracted sequence and sequence hash;
- sequence-cluster ID;
- residue count and eligible contact counts;
- inclusion status and exclusion reason;
- chain, distance, sequence-separation, and length rules.

The post-lock `build-cohort` command produces this file and
`cohort/stage_lock.json`. It consumes the final preregistration lock, the
accepted feasibility lock, and the candidate cohort manifest. It may apply
only the frozen metadata rules. It cannot compute confirmation attention,
baseline probabilities, matching, or ablation outcomes. The cohort stage lock
records the final lock, feasibility lock, candidate manifest hash, and every
final cohort artifact hash.

### 13.3 `discovery/head_selection.json`

One record per head:

- layer and head;
- discovery attention-on-contact fraction;
- discovery background rate and enrichment;
- attention entropy, output norm, and output displacement;
- enrichment rank and tie key;
- top-five flag;
- control eligibility;
- selected-head ID served, control role, and matching distances.

The post-lock `build-discovery` command produces this file and
`discovery/stage_lock.json`. It materializes the reviewed feasibility
discovery manifest under the final lock and verifies the frozen head ranking,
top-five set, controls, and replacement inputs. It cannot read confirmation
data. The discovery stage lock records the final lock, feasibility lock,
feasibility discovery-manifest hash, and every final discovery artifact hash.

### 13.4 `matching/position_matches.jsonl`

One record per contact-bearing position and its matched set:

- PDB ID, chain ID, protein cluster, and residue index;
- true residue, contact count, and contact-bearing flag;
- terminus distance, local-context fields, and baseline log probability;
- matched-set ID;
- matched non-contact residue indices and weights;
- all matching distances and caliper results;
- retained flag and exclusion reason.

Matching also writes `matching/balance.json`,
`matching/common_support.json`, `matching/stage_lock.json`, and
`matching/handoff.json`. The matching stage consumes the accepted cohort and
discovery stage locks. Its stage lock records both parent hashes. The handoff
is written only after the cohort and matching owner, discovery owner, ablation
owner, and orchestrator accept the cohort, discovery, and matching stage
hashes.

### 13.5 `ablation/ablation_records.jsonl`

One record per evaluated protein, position, head, and replacement variant:

- PDB ID, chain ID, position, layer, and head;
- replacement variant and replacement-artifact hash;
- baseline and ablated true-residue log probability;
- damage;
- baseline and ablated correctness;
- matched-set ID;
- run attempt, device, seed references, runtime, and failure reason.

Ablation also writes `ablation/hook_isolation.json`,
`ablation/perturbation_calibration.json`, and
`ablation/stage_lock.json`.

### 13.6 `analysis/head_outcomes.json`

One record per head and replacement variant:

- protein-level `D[h,p,v]` values;
- equal-weight `D[h,v]`;
- retained protein and matched-position counts;
- selected-head and control flags;
- selected-head control contrast when applicable;
- secondary accuracy summaries.

### 13.7 `analysis/confirmatory_statistics.json`

Required fields:

- correlational replication estimate and interval;
- 480-head `rho_layer` statistic, stability interval, and margin;
- all five zero-replacement contrasts;
- all five mean-replacement contrasts;
- raw and adjusted equivalence p-values and intervals;
- precision checks;
- bootstrap settings and failed-replicate counts;
- branch reached and pass or fail reasons.

Analysis also writes `analysis/stage_lock.json`.

### 13.8 `gate/gate_decision.json`

The accepted runtime benchmark is the stage-locked feasibility artifact.

The gate artifact stores every August 20 condition as a separate boolean with
supporting artifact hashes. It records `GO` only when every general condition
and one complete confirmatory branch pass. Otherwise it records `NO_GO` and
the exact failed conditions.

Each stage lock contains exact hashes for every artifact in that stage and
its accepted parent lock or parent-lock set. Cohort and discovery each depend
on the final and feasibility locks. Matching depends on the accepted cohort
and discovery locks. Ablation depends on the matching handoff, and analysis
depends on the discovery and ablation locks. Cohort, discovery, matching,
ablation, and analysis stages become append-only when their own stage lock is
written. A later correction, including one before the gate, requires a new
experiment ID and a linked amendment. The gate consumes only stage-locked
hashes.

### 13.9 `result_ledger.csv`

After the gate and independent statistical review, the orchestrator composes
one controlling row for each Interp claim from the accepted stage locks,
`gate/gate_decision.json`, and the review decision. Failed, stopped, excluded,
and negative analyses remain in the ledger. Artifact-list cells follow
`docs/RESULT_LEDGER_SCHEMA.md` and contain JSON arrays. The ledger is written
to the output root and becomes immutable when the submission evidence
allowlist records its SHA-256.

After `verify` passes, the orchestrator and the named Interp paper owner write
`handoff/paper_handoff.json`. It records all five distinct role IDs, the final
lock, gate, result-ledger, verification, and result-bundle hashes, and the
paper owner's acceptance. The paper owner receives no confirmation artifact
before this handoff exists.

### 13.10 Required commands

Run from the repository root in a clean worktree. These are target interfaces.
They must remain unavailable until strict argument parsing, safe output-path
checks, and focused tests are implemented. `EXPERIMENT_ID` must be selected
once before `feasibility-init`. Every command fails if it is unset or differs
from the identifier in its input artifact.

```bash
.venv/bin/python -m pytest -p no:cacheprovider \
  tests/test_l48_vig_contact_heads.py \
  tests/test_interp4discovery_contract.py \
  -q

.venv/bin/python -m plm_steering.interp4discovery feasibility-init \
  --preregistration docs/INTERP4DISCOVERY_PREREGISTRATION.md \
  --lock-values docs/INTERP4DISCOVERY_LOCK_VALUES.json \
  --output-root "plm_steering/interp4discovery_out/$EXPERIMENT_ID"

.venv/bin/python -m plm_steering.interp4discovery benchmark \
  --feasibility-spec "plm_steering/interp4discovery_out/$EXPERIMENT_ID/feasibility/specification.json"

.venv/bin/python -m plm_steering.interp4discovery discovery-manifest \
  --feasibility-spec "plm_steering/interp4discovery_out/$EXPERIMENT_ID/feasibility/specification.json"

.venv/bin/python -m plm_steering.interp4discovery candidate-cohort \
  --feasibility-spec "plm_steering/interp4discovery_out/$EXPERIMENT_ID/feasibility/specification.json"

.venv/bin/python -m plm_steering.interp4discovery matching-simulate \
  --feasibility-spec "plm_steering/interp4discovery_out/$EXPERIMENT_ID/feasibility/specification.json"

.venv/bin/python -m plm_steering.interp4discovery precision-plan \
  --feasibility-spec "plm_steering/interp4discovery_out/$EXPERIMENT_ID/feasibility/specification.json"

.venv/bin/python -m plm_steering.interp4discovery feasibility-lock \
  --feasibility-spec "plm_steering/interp4discovery_out/$EXPERIMENT_ID/feasibility/specification.json"

.venv/bin/python -m plm_steering.interp4discovery lock \
  --preregistration docs/INTERP4DISCOVERY_PREREGISTRATION.md \
  --lock-values docs/INTERP4DISCOVERY_LOCK_VALUES.json \
  --feasibility-lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/feasibility/stage_lock.json" \
  --output-root "plm_steering/interp4discovery_out/$EXPERIMENT_ID"

.venv/bin/python -m plm_steering.interp4discovery build-cohort \
  --lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/lock/preregistration_lock.json" \
  --feasibility-lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/feasibility/stage_lock.json" \
  --candidate-cohort "plm_steering/interp4discovery_out/$EXPERIMENT_ID/feasibility/candidate_cohort_manifest.json"

.venv/bin/python -m plm_steering.interp4discovery build-discovery \
  --lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/lock/preregistration_lock.json" \
  --feasibility-lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/feasibility/stage_lock.json" \
  --discovery-manifest "plm_steering/interp4discovery_out/$EXPERIMENT_ID/feasibility/discovery_manifest.json"

.venv/bin/python -m plm_steering.interp4discovery match \
  --lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/lock/preregistration_lock.json" \
  --cohort-lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/cohort/stage_lock.json" \
  --discovery-lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/discovery/stage_lock.json"

.venv/bin/python -m plm_steering.interp4discovery accept-matching \
  --lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/lock/preregistration_lock.json" \
  --cohort-lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/cohort/stage_lock.json" \
  --discovery-lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/discovery/stage_lock.json" \
  --matching-lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/matching/stage_lock.json"

.venv/bin/python -m plm_steering.interp4discovery ablate \
  --lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/lock/preregistration_lock.json" \
  --matching-handoff "plm_steering/interp4discovery_out/$EXPERIMENT_ID/matching/handoff.json"

.venv/bin/python -m plm_steering.interp4discovery analyze \
  --lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/lock/preregistration_lock.json" \
  --discovery-lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/discovery/stage_lock.json" \
  --ablation-lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/ablation/stage_lock.json"

.venv/bin/python -m plm_steering.interp4discovery gate \
  --lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/lock/preregistration_lock.json" \
  --cohort-lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/cohort/stage_lock.json" \
  --discovery-lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/discovery/stage_lock.json" \
  --analysis-lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/analysis/stage_lock.json"

.venv/bin/python -m plm_steering.interp4discovery verify \
  --lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/lock/preregistration_lock.json" \
  --gate "plm_steering/interp4discovery_out/$EXPERIMENT_ID/gate/gate_decision.json" \
  --ledger "plm_steering/interp4discovery_out/$EXPERIMENT_ID/result_ledger.csv"

.venv/bin/python -m plm_steering.interp4discovery accept-paper-handoff \
  --lock "plm_steering/interp4discovery_out/$EXPERIMENT_ID/lock/preregistration_lock.json" \
  --gate "plm_steering/interp4discovery_out/$EXPERIMENT_ID/gate/gate_decision.json" \
  --ledger "plm_steering/interp4discovery_out/$EXPERIMENT_ID/result_ledger.csv" \
  --verification "plm_steering/interp4discovery_out/$EXPERIMENT_ID/verification/verification.json" \
  --paper-owner "$INTERP_PAPER_OWNER_ID"
```

Every command rejects unknown arguments and existing output files. `verify`
returns nonzero for a missing lock key, field, hash, head, position, control,
replacement result, or gate condition.

The command order is fixed. Discovery-only work runs from
`feasibility-init` through `feasibility-lock`. The final `lock` command then
consumes the reviewed feasibility stage lock and all resolved lock values.
Only that final lock authorizes `build-cohort` and `build-discovery`. Those
two independent stages may run in either order. Both must close before
`match`, followed by `accept-matching`, `ablate`, `analyze`, and `gate`.
Independent review and result-ledger construction follow the gate, then
`verify` writes `verification/verification.json` and closes the artifact set.
`accept-paper-handoff` then authorizes the paper owner's read access. No
confirmation command can create an input required by the final lock.

## 14. Stopping rule

Before confirmation opens, stop if any of these conditions holds:

- any required Section 16 lock key is missing, null, unreviewed, or invalid;
- the independent panel or no-overlap rule is not complete;
- no defensible association or equivalence margin exists;
- the precision calculation requires more proteins than the compute budget;
- the runtime projection cannot finish the core by August 19;
- hook isolation or perturbation calibration fails.

After confirmation opens, there is no outcome-based early stopping. Do not
peek and add proteins, change controls, change margins, change seeds, or relax
matching. Technical retries follow only the frozen retry rule.

Grouped ablation of the top 1, 5, and 10 heads may run only after the
confirmatory core succeeds and only if compute remains. It uses size-matched
controls with frozen layer composition, aggregate output norm, and
model-output displacement. It is exploratory and cannot change the gate.

## 15. August 20 go or no-go gate

Record `GO` only if all conditions below pass:

1. The preregistration lock contains every numerical association,
   equivalence, precision, replication, and method-sensitivity threshold.
2. Correlational replication passes its frozen rule.
3. The continuous contact interaction and hierarchical analysis complete for
   all 480 heads.
4. Either the positive 480-head branch passes or all ten top-five equivalence
   tests pass under their familywise rule.
5. Every branch-specific interval meets its frozen precision rule.
6. Positive-branch mean replacement has no corrected clear sign reversal, or
   negative-branch equivalence passes under both zero and mean replacement.
7. Position matching passes common-support and balance rules.
8. Head-control matching follows the frozen discovery-only rule.
9. Hook-isolation and perturbation-calibration tests pass.
10. All required artifacts are complete, hashed, and linked to the frozen
    source and model revisions.
11. The result supports a five-page contact-attention paper without importing
    steering results.

If any condition fails on 2026-08-20, record `NO_GO`, stop the
Interp4Discovery submission, preserve the artifacts as future work, and move
the remaining workshop effort to ICBINB-BIO.

## 16. Decisions that remain to be frozen

The canonical value carrier is
`docs/INTERP4DISCOVERY_LOCK_VALUES.json`. Every key below must contain a
non-null value, a provenance note, an approving reviewer ID, and a validation
result in `lock/preregistration_lock.json`.

The carrier has two allowed pre-confirmation statuses.
`feasibility_draft` authorizes only the discovery-only feasibility commands
through `feasibility-lock`. `ready_for_final_lock` requires all 20 values,
provenance notes, reviewer approvals, and validations to be present. The
`lock` command accepts only `ready_for_final_lock`; the immutable lock artifact,
not another editable carrier status, records confirmation authorization.

| Lock key | Required content | Validation |
|---|---|---|
| `DISCOVERY_PANEL` | PDB versions, chains, hashes, exclusions, and ranking reuse decision | Every file and chain verifies |
| `CONFIRMATION_PANEL` | PDB snapshot, chains, hashes, clustering, diversity, panel size, and length rules | No prohibited cluster overlap; precision size met |
| `MODEL_RUNTIME` | Model and tokenizer revisions, local hashes, environment-lock hash, precision, hardware, and determinism | Immutable revisions and environment verify |
| `TOP_FIVE_HEADS` | Five head IDs and deterministic tie rule | Derived only from locked discovery data |
| `HEAD_CONTROLS` | Feature definitions, scaling, tolerances, control count, reuse rule, control IDs, and seed | Discovery-only matching passes |
| `POSITION_MATCHING` | Context representation, calipers, ratio, no-replacement rule, tie rule, support limits, and seed | Balance and support simulation passes |
| `MEAN_REPLACEMENT` | Tensor definition, conditioning, aggregation, and discovery examples | No confirmation data used |
| `REPLICATION_GATE` | Group statistic, interval method, confidence level, and threshold | Top-five group rule is executable |
| `POSITIVE_BRANCH` | `rho_layer` margin, interval method, bootstrap count, alpha allocation, and width rule | Full pipeline simulation passes |
| `EQUIVALENCE_BRANCH` | `delta`, TOST method, adjusted interval method, bootstrap count, alpha allocation, and failed-replicate rule | All ten contrasts covered |
| `FAMILYWISE_ERROR` | Total alpha and all branch and sensitivity allocations | Allocations do not exceed total |
| `PRECISION_PLAN` | Simulation inputs, planning probability, selected panel size, and full result artifact hash | Both branches meet precision target |
| `EXCLUSIONS_RETRIES` | Every technical exclusion, retry count, restart policy, and failed-bootstrap limit | Fail-closed behavior tested |
| `SEED_REGISTRY` | One integer, generator, library version, and purpose per random process | No silent seed reuse |
| `RUNTIME_BUDGET` | Benchmark, position count, stage hours, retry buffer, available window, and maximum budget | Core completes by 2026-08-19 |
| `HOOK_ISOLATION` | Numerical tolerance and required test result | Only the requested head changes |
| `PERTURBATION_CALIBRATION` | Zero and mean magnitude thresholds and required calibration result | Frozen thresholds pass |
| `METHOD_SENSITIVITY` | Positive-branch sign-reversal rule and any additional method threshold | Claim wording matches zero replacement |
| `ARTIFACT_PATHS` | Exact repository-relative output root and every expected file | No wildcard, absolute, or escaping path |
| `ROLE_HANDOFF` | Discovery, cohort and matching, ablation, analysis, and Interp paper-owner IDs with disjoint read and write scopes | All five owners are assigned, IDs are pairwise distinct, and the paper owner is blocked before final handoff |

Resolving every text marker is not enough. The experiment becomes frozen only
when all 20 keys pass validation, the feasibility stage lock verifies, the
statistical reviewer approves the margins and precision plan, and the final
preregistration lock authorizes opening the confirmation panel. The actual
matching stage hash is accepted later in `matching/handoff.json`, before
ablation.
