# Statistical Contract Review

Date: 2026-08-13

Reviewer role: Independent statistical contract reviewer

## Scope

This review covers:

- `docs/PAPER_PORTFOLIO_PLAN.md`
- `docs/CLAIM_REGISTRY.md`
- `docs/ARTIFACT_INVENTORY.md`
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`

This is a contract review. It does not verify the saved numeric results or
certify either manuscript.

## Decision

Both submissions are blocked under the severity rule in Paper Portfolio Plan
Section 11.3, "Agent output contract."

Submission blocker count: 10

- Critical: 2
- Major: 8
- Minor: 3, not counted as submission blockers

No active claim should move from Conditional to Confirmed until the affected
blockers are resolved or the claim is narrowed or removed.

## Submission Blockers

### Critical

#### C1. L57 uses non-significance to claim that an effect was removed

References:

- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 2, "Fixed claims," claim C3
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 8.3, "H4 acceptance and
  failure," lines 490 through 504
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 11.3, "Multiplicity and
  interpretation," lines 653 through 656
- `docs/CLAIM_REGISTRY.md`, Section "ICB-05"
- `docs/CLAIM_REGISTRY.md`, Section "Rejected and deferred claims," EXC-05
- `docs/PAPER_PORTFOLIO_PLAN.md`, Section 3, "Terms and evidence boundaries"

H4 passes when the unexcluded confidence interval is above zero and the
E/L-excluded interval includes zero. An interval that includes zero does not
show that the effect was removed. It shows that the excluded analysis is
inconclusive at that precision. This conflicts with the manifest's own rule
that a non-significant interval is inconclusive and with EXC-05.

The current rule can support this narrower statement:

> The unexcluded analysis met its positive rule, while the E/L-excluded
> analysis did not.

It cannot support claim C3 or ICB-05 as currently worded.

To retain an "effect removed" claim, define a paired attenuation estimand and a
scientifically justified bound. Test either that the attenuation exceeds the
bound or that the remaining effect is equivalent to zero within a frozen
margin. Because E and L were identified from an already observed run, any new
threshold must be labeled retrospective unless it is tested on new independent
data.

This blocks the required composition mechanism.

#### C2. L56 acceptance rules do not support absence or confounding claims

References:

- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 2, "Fixed claims," claim C2
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 6.1 through 6.3, "L56
  endpoint-mismatch and confounding study"
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 11.2, "L56"
- `docs/CLAIM_REGISTRY.md`, Sections "ICB-02" and "ICB-03"
- `docs/ARTIFACT_INVENTORY.md`, Section "Saved research outputs," L56 row

H2 is accepted from point estimates crossing retrospective numerical
thresholds. The contract gives no uncertainty rule for:

- the maximum absolute Tier 3 correlation;
- the difference between random-fold and organism-grouped correlations;
- the mean within-organism correlation;
- variation across organisms, antigens, repeated assays, or folds.

The statement that scores "do not transfer" is an absence claim. A maximum
absolute point estimate below 0.15 is not enough. The contract needs a
precision rule showing that every relevant association is smaller than a
defensible bound.

The statement that source-organism confounding "explains" the apparent signal
is also stronger than the acceptance rule. Lower grouped-validation
performance can show poor transport to held-out organisms. By itself it does
not identify confounding as the cause. The unit, assay aggregation rule,
organism weighting, target population, and uncertainty for the performance
drop are not defined.

Either narrow the claim to the observed validation result, using language such
as "performance fell under organism-grouped validation, consistent with
source-organism confounding," or add a frozen confounding estimand and
clustered uncertainty analysis. The current artifact lacks row-level
predictions and fold assignments, so the stronger analysis cannot yet be
audited.

This blocks the required endpoint-mismatch and confounding mechanism.

### Major

#### M1. The ICBINB generation estimands are not fully specified

References:

- `docs/PAPER_PORTFOLIO_PLAN.md`, Section 6, "Statistical rules shared by all
  new experiments"
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 4.1 through 4.4, "Shared
  generation contract"
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 11.1, "Generation studies"

The source protein is correctly named as the independent unit. The two
reported quantities are also distinct:

1. failure risk over all attempts;
2. score difference among proteins for which both compared outputs are valid.

The contract does not state whether each quantity targets:

- the fixed saved evaluation cohort under the realized masks and control
  direction;
- repeated masks or directions on that cohort;
- a population of similar proteins;
- a population of complete runs.

One generated output per protein does not identify variability over masks or
control directions. A protein bootstrap supports population inference only if
the proteins can be treated as an exchangeable sample from a stated target
population. The current low-property held-out cohorts are not described that
way.

Part B is a joint-survivor estimand. It is valid as a conditional descriptive
contrast, but it is not an unconditional intervention effect and it can refer
to a different protein subset at each alpha and seed. The manuscript must name
that estimand directly.

Freeze the target population, sources of randomness, weighting, and
interpretation of each interval. If the target is only the fixed saved cohort,
report finite-cohort estimates and do not give bootstrap intervals a
superpopulation interpretation.

#### M2. L52 does not currently preserve auditable protein-level pairing

References:

- `docs/ARTIFACT_INVENTORY.md`, Section "Immediate blockers," items 2 and 9
- `docs/ARTIFACT_INVENTORY.md`, Section "Saved research outputs," L52 row
- `docs/ARTIFACT_INVENTORY.md`, Section "Required artifacts that are absent,"
  per-attempt failure flags row
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 4.1, "Statistical unit"
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 12.1, "Per-generation record"
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 15, "Stop rules"

The L52 result lacks original source identifiers and source evaluation
sequences. The analysis requires paired failure and score contrasts by source
protein. Array position may preserve pairing, but the current contract does
not define or verify that mapping. The stop rule also says that a missing
cohort identifier stops a case.

Before H1 can pass, either reconstruct and verify an immutable
`evaluation_index` to source-protein mapping from frozen inputs and runner
logic, or rerun L52 with source IDs and hashes. A synthetic ID that only labels
an unverified array row is not enough.

#### M3. The 25 percent single-residue failure threshold is not portable across cases

References:

- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 4.2, "Attempt and validity"
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 14, "Confounds and
  limitations"
- `docs/PAPER_PORTFOLIO_PLAN.md`, Section 6, rules 1 through 3

Condition 5 was calibrated on L42 and is then included in the primary failure
union for L52, L55, and L57. The manifest correctly notes that this rule can
reject real low-complexity disorder sequences. It is therefore not an
endpoint-neutral technical failure definition.

This matters because the rule changes both Part A and the proteins retained in
Part B. For L55, it can remove outputs related to the property being scored.

Keep conditions 1 through 4 as technical and scoring failures. Treat condition
5 as a separate degeneracy diagnostic unless a case-specific scientific
justification is frozen. At minimum, report the joint rule both with and
without condition 5 and state whether any claim changes.

#### M4. Provenance labels conflict across the registered contracts

References:

- `docs/CLAIM_REGISTRY.md`, Section "ICB-04," provenance row
- `docs/CLAIM_REGISTRY.md`, Section "ICB-05," provenance row
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 2, claims C3 and C4
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 8.3, H4 residue-selection rule
- `docs/PAPER_PORTFOLIO_PLAN.md`, Sections 5.1 and 7.3

ICB-05 is registered as a post-hoc sensitivity analysis, while manifest claim
C3 calls the L57 check prospective under L50. ICB-04 is registered as post-hoc,
while claim C4 calls seed 0 prospective and seeds 1 and 2 post-hoc.

The E/L and E/S identities and the alpha 0.5 rules are already known from the
saved outcomes. Reproducing them does not make their selection prospective.
The contracts need one chronology supported by dated commits or other locked
records. In the absence of such evidence, use the more conservative
retrospective or post-hoc label.

This is not only wording. The label controls whether thresholds can be treated
as confirmatory.

#### M5. The Interp head-level estimand and null model are not aligned

References:

- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 4, "Model, contacts, and
  statistical unit"
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 8.2, "Positive 480-head
  association branch"
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 9, "Association and
  equivalence margins"
- `docs/CLAIM_REGISTRY.md`, Section "INT-01"

The preregistration says that heads are fixed model components, not independent
biological samples. The primary statistic then correlates 480 fixed heads and
uses a within-layer permutation as a null distribution.

That permutation requires an exchangeability argument. Heads within a layer
are not randomized labels and can differ in output norm, entropy,
perturbation size, and other properties related to both enrichment and damage.
Preserving layer alone does not establish exchangeability.

Define the estimand as a finite-head association between expected enrichment
and expected damage over stated protein populations. Then choose an inference
method that matches that estimand. If the permutation test remains, state its
null and justify why enrichment labels are exchangeable within layer. A
layer-adjusted model or prespecified residual association may be more
defensible if important head-level covariates must be controlled.

The discovery panel contains eight already inspected proteins. Its bootstrap
cannot automatically be interpreted as sampling uncertainty for a broad
protein population. The target population and sampling basis must be stated.

#### M6. Interp acceptance rules are broader than the registered analyses

References:

- `docs/CLAIM_REGISTRY.md`, Sections "INT-01" and "INT-03"
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 8.1, "Correlational
  replication gate"
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 8.2, "Positive 480-head
  association branch"
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 15, "August 20 go or
  no-go gate"

INT-03 says that contact-enriched heads replicate their enrichment. The
planned gate is one top-five aggregate. That can support replication of the
prespecified set as a group. It cannot show that each of the five heads
replicates unless the rule requires each head to pass.

INT-01 does not name the replacement method. The 480-head association is
tested only under zero replacement. Mean replacement is checked only for the
top five, and the rule merely rejects a statistically clear sign reversal.
An imprecise negative mean-replacement estimate can pass this rule because its
interval includes zero.

Narrow INT-01 to zero replacement and describe mean replacement as a selected
head sensitivity analysis. Narrow INT-03 to group-level replication, or add
head-specific replication rules with appropriate multiplicity and precision.
Do not claim method robustness from failure to detect a sign reversal.

#### M7. The Interp precision gate has no valid completed planning calculation

References:

- `docs/PAPER_PORTFOLIO_PLAN.md`, Sections 8.3.A and 8.3.F
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 3.2, "Independent
  confirmation panel"
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Sections 8.2, 8.4, and 9
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 16, "Decisions that
  remain to be frozen"
- `docs/ARTIFACT_INVENTORY.md`, Section "Immediate blockers," items 4 and 5
- `docs/ARTIFACT_INVENTORY.md`, Section "Saved research outputs," L48 and L49
  rows

The required panel size is said to come from discovery-panel protein-level
variance. The positive gate, however, concerns a bootstrapped 480-head
Spearman correlation. The negative gate concerns ten jointly adjusted
equivalence intervals after matching. A generic variance calculation does not
cover either branch.

The saved pilot outputs discard the row-level continuous outcomes needed to
estimate matching attrition and protein-level variance for the planned
estimands. A new discovery-only pilot calculation is therefore needed.

The precision plan should simulate or resample the complete frozen pipeline
for both branches. It must include:

- uncertainty in discovery enrichment;
- confirmation protein sampling;
- position matching and attrition;
- layer dependence;
- all ten adjusted equivalence intervals;
- the chance that the required common support is not met.

The panel must be sized for the more demanding branch that the submission
intends to allow. The confirmation panel cannot open while this calculation or
any numerical margin remains unresolved.

#### M8. Interp missingness and matched-set dependence are unresolved

References:

- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 6, "Matched non-contact
  positions"
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 7.3, "Continuous
  outcome"
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Sections 8.2 and 8.4
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 10, "Exclusions and
  missing results"
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 13, "Artifact schema"

The contract correctly stops the positive branch when any of the 480
zero-replacement head results is missing. It also prohibits effect-based
outlier removal. Those are defensible rules.

Several details that affect uncertainty remain open:

- one non-contact position may appear in several matched sets;
- matching may use replacement;
- selected heads may share control heads;
- the bootstrap may encounter failed common support;
- an ablated true-residue probability may be numerically zero or non-finite;
- required mean-replacement results may fail after the zero-replacement sweep.

Resampling matched sets as if they were independent can understate uncertainty
when controls are shared. Freeze a joint resampling rule that preserves all
shared-position and shared-head dependence. Use stable log-probability
computation and define fail-closed handling for every required mean and zero
result. A failed required result must not become a dropped row.

## Minor Findings

### N1. L58 layers should not be called independent statistical units

References:

- `docs/CLAIM_REGISTRY.md`, Section "ICB-06," statistical-unit row
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 9, "L58 one-seed geometry
  diagnostic"

The 33 layers are components of one fixed direction pair, not independent
replicates. The manifest otherwise handles this correctly by making H5
descriptive and giving it no p-value or confidence interval. Call 33 the
number of paired layer vectors, not the statistical sample size.

### N2. The paired failure-risk interval method and sidedness are not frozen

References:

- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 4.3 and 4.4
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 11.1

The contract specifies a protein-level paired bootstrap but not the interval
method or whether the noninferiority bound uses a one-sided 95 percent limit or
a two-sided interval. A two-sided 95 percent interval is conservative for the
stated noninferiority decision and is defensible. Freeze the choice for exact
reproduction.

### N3. The Interp equivalence width rule is redundant but harmless

References:

- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 8.4, "Equivalence branch"

An adjusted interval that lies wholly inside `[-delta, +delta]` already has
width no greater than `2 * delta`. Keeping the explicit width check is harmless
and may make the gate easier to audit.

## Implementation Tasks

These tasks are separate from the findings. Completing a task closes a blocker
only after independent review confirms that the contract and artifacts agree.

1. Reconcile the claim registry and ICBINB manifest provenance labels. Record
   the evidence for the chronology of L50, L55, and L57.
2. Replace the L57 "interval includes zero" rule with either a narrowed
   decision-status claim or a valid attenuation or equivalence estimand.
3. Rebuild the L56 audit with row-level predictions, assay aggregation,
   organism and antigen identifiers, fold assignments, exclusion counts, and
   cluster-aware uncertainty. Narrow the causal confounding language unless
   the stronger estimand is implemented.
4. Recover and verify the L52 source-protein mapping or rerun L52 with source
   IDs, sequence hashes, arm pairing, separate seeds, and full provenance.
5. Add an ICBINB estimand table. For every contrast, state the target cohort or
   population, randomness averaged over, validity conditioning event, protein
   weighting, and interval interpretation.
6. Split technical generation failures from the 25 percent low-complexity
   diagnostic. Add the required sensitivity table and a rule for an empty
   sequence after residue exclusion.
7. Define the Interp finite-head estimand and justify or replace the within-layer
   permutation null. Align INT-01 and INT-03 wording with the zero-replacement
   and group-replication analyses.
8. Regenerate discovery-only row-level continuous outcomes and run a
   branch-specific precision calculation for both the association and all ten
   equivalence contrasts.
9. Freeze the Interp matching, missing-result, stable log-probability, retry,
   and joint bootstrap rules. Add tests for shared controls and failed support.
10. Resolve every `DECISION TO FREEZE`, hash the completed preregistration, and
    open the confirmation panel only after statistical review approves the
    margins and precision calculation.

## Rules Judged Defensible

The following rules should be retained.

1. Protein-level units. Both contracts correctly reject residue-pooled
   uncertainty. Equal protein weighting and protein-level clustering are
   appropriate once the target protein population is stated.
2. Two-part generation analysis. Separate failure risk over all attempts
   and score change among jointly valid pairs is the right minimum structure.
   It prevents invalid outputs from disappearing. Part B must remain labeled
   as conditional.
3. No numerical score for failed generation. This avoids an arbitrary
   utility assignment and keeps failure and score estimands distinct.
4. L55 seed interpretation. Calling seeds 0, 1, and 2 legacy whole-run
   seeds is accurate. The design can show sensitivity across those three fixed
   run configurations. It cannot estimate a seed distribution or attribute
   the change to direction construction alone.
5. L52 retrospective policy replay. The high-alpha thresholds are
   acceptable as reproduction checks for a known case because the manifest
   labels H1 retrospective. They must not be presented as prospectively
   calibrated operating characteristics.
6. Ordered Interp branches. Testing the positive branch first and allowing
   equivalence only under a frozen alpha allocation is defensible. Splitting
   branch alpha is conservative for two different possible claims.
7. Equivalence mechanics. TOST with a scientifically justified frozen
   margin, Holm control across all ten head-by-method contrasts, and a
   requirement that every adjusted interval lie within the margin can support
   INT-02. It supports equivalence to matched controls, not absence of an
   absolute head effect.
8. No 480 head-specific confirmatory tests. One global association avoids a
   large head-wise testing family. Exploratory individual-head results should
   retain false-discovery-rate control.
9. Fail-closed confirmation rules. Freezing the panel and matching before
   ablation, prohibiting outcome-based exclusions, requiring all 480 primary
   results, and forbidding post-opening sample additions are strong controls
   against selective missingness and leakage.
10. No familywise correction across C1 through C5. This is defensible only
    for the stated case-specific reproduction package, where the paper-level
    claim requires all required mechanisms and no best case is selected.
    Multiplicity within each case still needs the case-specific rules above.
