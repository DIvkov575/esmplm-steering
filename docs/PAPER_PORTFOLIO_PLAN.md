# Paper Portfolio Plan

Date: 2026-08-13

ICBINB-BIO deadline: 2026-08-29 at 11:59 p.m. Anywhere on Earth

Interp4Discovery operational deadline: 2026-08-30 at 01:00 UTC. The workshop
website states 2026-08-29 at 11:59 p.m. Anywhere on Earth, but the current
OpenReview portal closes 10 hours and 59 minutes earlier. Use the portal time
until the venue resolves the conflict.

## 1. Program decision

This project has one protected primary workshop submission, one conditional
workshop submission, and up to two follow-up papers after the workshop
deadline.

| Paper | Decision | Core subject | Current priority |
|---|---|---|---|
| ICBINB-BIO | Submit if the minimum evidence gate in Section 7.9 is met | How protein language model steering evaluations produce false or unstable successes | Protected primary workshop paper |
| Interp4Discovery | Submit only if the new causal analysis passes its evidence gate | Whether contact-enriched attention heads causally support masked-residue prediction | Conditional workshop paper |
| Catalytic steering | Develop after August 29 | Predicted enzyme-substrate turnover under steering, with structural and liability checks | Deferred |
| Disorder steering | Develop only if stronger composition controls pass | Independently predicted intrinsic disorder under steering | Deferred and conditional |

We will not work on the arXiv or XAI4Science versions during this program.
The catalytic and disorder papers must not delay either workshop paper.

The current deadline, page limits, anonymity rules, required headings,
supplement policy, dual-submission policy, preprint policy, and AI-disclosure
policy must be checked against the official calls and submission portals on
Day 0. The local README is a planning source, not final policy authority. Save
the official URLs, access date, and a short policy summary before creating
submission branches.

## 2. Research identity and narrative

We are not presenting the work as a sweep over unrelated protein properties.
The research program has one coherent purpose:

> Determine when internal signals in protein language models support reliable
> interventions, and identify the checks that separate a real intervention
> effect from an evaluation artifact.

Each paper answers a different part of that question.

- ICBINB-BIO asks why steering evaluations can produce a false or unstable
  success.
- Interp4Discovery asks whether attention patterns associated with protein
  contacts identify model components that are causally important.
- The catalytic paper asks whether the strongest positive steering result
  survives independent functional, structural, and safety-related checks.
- The disorder paper asks whether an apparent steering effect remains after
  amino-acid composition is controlled directly.

The author position is that of a careful investigator who found weaknesses in
the original evaluation, exposed them, and designed stronger tests. We should
not claim that a changed sequence score establishes a changed biological
property. We should also avoid describing an inconclusive result as a success.

## 3. Terms and evidence boundaries

The manuscripts should use the following terms consistently.

| Term | Meaning |
|---|---|
| Property label | An experimental or curated measurement, such as measured turnover or a DisProt annotation |
| Scoring surrogate | A sequence-derived score that correlates with the property label |
| Steering endpoint | The quantity measured after the model intervention |
| Independent validator | A model or assay with documented training provenance, no prohibited cohort overlap, and performance established on a separate experimental benchmark |
| Causal outcome | The change caused by an intervention relative to a defined control |
| Technical or scoring failure | An empty, malformed, length-mismatched, or unscorable generated sequence |
| Low-complexity diagnostic | A separate flag for a scoreable output that exceeds a frozen composition threshold |

The word "proxy" should not carry several meanings in one paper. When it is
used, the manuscript must identify whether it means a scoring surrogate,
biological endpoint, or control measurement.

The following claims are prohibited unless the required evidence is added.

| Prohibited claim | Evidence required before it becomes permissible |
|---|---|
| Steering improves catalysis | A controlled wet-lab turnover assay for the generated enzyme and fixed substrate |
| Steering improves safety | A defined safety endpoint and an appropriate experimental evaluation |
| Boltz validates catalytic activity | Not permissible. Boltz can assess structure, complexes, and possibly binding affinity, not turnover |
| Low Boltz confidence proves disorder | Not permissible. Low structural confidence is not a disorder assay |
| A non-significant ablation has no effect | A prespecified equivalence test with a defensible smallest effect of interest |
| A scoring surrogate change proves property control | An independent property validator or experiment |

## 4. Claim ownership

The papers need separate claim contracts. This prevents duplicate papers and
keeps each submission easy to understand. Claim ownership also applies to
figures, tables, and result bundles, not only manuscript sentences.

| Claim | Owning paper | Excluded from |
|---|---|---|
| A staged audit catches distinct steering evaluation failures | ICBINB-BIO | Interp4Discovery |
| Post-generation filtering can change a steering verdict | ICBINB-BIO | Positive-result papers, except as a cited method correction |
| Composition and seed choice can make an apparent effect unstable | ICBINB-BIO | Disorder paper as a final result |
| Contact enrichment does or does not identify causally important attention heads | Interp4Discovery | ICBINB-BIO |
| Steering improves independently predicted enzyme-substrate turnover while preserving plausibility | Catalytic paper | Both workshop papers |
| Steering increases consensus predicted disorder beyond composition changes | Disorder paper | Both workshop papers |

The current catalytic result may not be presented as a validated biological
success in ICBINB-BIO. The current disorder result may be used in ICBINB-BIO
only as evidence that an artifact check changes across seeds. A later disorder
paper requires new evidence and must answer a different question.

## 5. Shared research controls

Before any new experiment, the orchestrator freezes the claim registry, the
machine-readable submission contract and artifact-ownership catalog, the
shared cohort, role-assignment, result-ledger, and citation-ledger schemas, and
the paper-specific experiment manifest. Each actual role assignment and cohort
manifest is frozen before the work that uses it. The result and citation
ledgers are populated after results and sources exist, then locked before
manuscript drafting. ICBINB-BIO does not wait for an Interp manifest, and
neither workshop paper waits for later catalytic or disorder contracts.

The shared schema files are:

- `docs/COHORT_MANIFEST_SCHEMA.md`
- `docs/ROLE_ASSIGNMENT_SCHEMA.md`
- `docs/RESULT_LEDGER_SCHEMA.md`
- `docs/CITATION_LEDGER_SCHEMA.md`
- `docs/SUBMISSION_CONTRACT.json`
- `docs/ARTIFACT_OWNERSHIP.json`

### 5.1 Claim registry

For every planned claim, record:

- the exact sentence-level claim;
- the owning paper;
- the supporting result files;
- the statistical unit;
- the control condition;
- the important limitation;
- whether the analysis was prospective, retrospective, or a post-hoc
  sensitivity analysis;
- whether the claim is confirmed, conditional, or rejected.

No manuscript owner may expand a claim beyond this registry without an
explicit review.

The machine-readable submission contract fixes the complete claim set and the
exact provenance, estimand, unit, control, limitation, source-study ownership,
and typed result requirements for each claim. The artifact-ownership catalog
records known result hashes and their permitted papers and claims. Both files
are hash-locked before execution.

### 5.2 Cohort manifest

Each experiment must save:

- source data and version;
- inclusion and exclusion rules;
- sequence-clustering method;
- train, development, and test identifiers;
- property labels and substrate identifiers when applicable;
- all random seeds and their separate purposes;
- hashes for frozen input files.

Dataset split seeds, direction seeds, mask seeds, control-direction seeds, and
bootstrap seeds must be separate. One integer must not silently control the
whole experiment.

### 5.3 Experiment manifest

Each run must declare before execution:

- primary and secondary outcomes;
- generation settings;
- intervention strengths;
- control directions;
- invalid-output policy;
- statistical model;
- multiplicity policy;
- go or stop criteria;
- expected output files.

### 5.4 Result ledger

The pre-run result-ledger schema is frozen before execution. The populated
result ledger will contain one row per registry claim and link it to immutable
outputs. It will record negative and failed runs as well as favorable runs.
Manuscript text must be generated from the populated ledger, not from memory.

### 5.5 Citation ledger

The citation-ledger schema is frozen before execution. During drafting, every
external claim will receive a verified source, DOI or stable URL when
available, and a note explaining what the source supports. Novelty claims will
include the search date and nearest related work. The citation reviewer must
check the final text against the populated ledger.

## 6. Statistical rules shared by all new experiments

1. Use a two-part primary analysis for generation experiments.
   - Part A estimates technical-failure and low-complexity risks over all
     attempted generations.
   - Part B estimates the property-score change among jointly scoring-valid
     generations.
   - A favorable property-score change cannot support a success claim when
     the learned arm has an unacceptable failure-risk increase.
2. Do not assign an arbitrary numerical property score to an unscorable
   sequence. Each experiment manifest must define the failure event, the risk
   contrast, the conditional score contrast, and the joint decision rule.
3. A complete-case score estimate is Part B of the two-part analysis. It must
   be reported with Part A and must not be presented as the unconditional
   intervention effect.
4. Match controls by intervention burden. At minimum, compare edit count,
   Hamming distance from the source, and output-logit displacement.
5. Use a fixed evaluation cohort across direction builds and mask seeds.
6. Treat proteins, not individual residues, as the independent sampling unit.
   Residue-level outcomes require hierarchical analysis or clustered
   uncertainty.
7. Report effect sizes and confidence intervals. A significance flag alone is
   not sufficient.
8. Freeze the smallest effect of interest before running an equivalence test.
9. Keep model selection, threshold selection, and final evaluation on separate
   data.
10. Report every tested control direction or define a prespecified summary over
    them. Do not select a convenient random control after the run.
11. Save generated sequences, scores, failure flags, and exact configuration
    for every arm.
12. For historical runs with one output per source protein, target the fixed
    saved evaluation cohort under the realized masks and control direction.
    Do not generalize the interval to repeated masks, repeated directions, or
    a broader protein population.
13. Name the Part B estimand as the score difference among jointly
    scoring-valid outputs. It is conditional on an event that may select a
    different protein subset for each arm and strength.
14. Separate technical generation failures from low-complexity diagnostics.
    Report the 25 percent single-residue rule separately unless a
    case-specific reason makes it part of the primary validity definition.

## 7. ICBINB-BIO strategy

### 7.1 Product contract

Working title:

> When Protein Language Model Steering Appears to Work: A Staged Audit of
> Evaluation Failures

Research question:

> Which evaluation failures can make activation steering appear successful,
> and which checks detect them before a biological claim is made?

Thesis:

> Steering should be evaluated as a sequence of validity checks. In the
> current experiments, different checks detect decoder instability and
> endpoint mismatch. They also identify a performance pattern consistent with
> source-organism confounding and conclusions that depend on composition or
> complete run configuration.

This framing fits a failure-focused venue because the contribution is not a
catalog of attempted targets. It is an analysis of failure mechanisms and
reusable diagnostic checks.

### 7.2 Material to remove from the current paper

- Remove the attention-head method and results.
- Remove the five-property steering catalog as the organizing structure.
- Remove the four-point correlation-versus-effect scatter plot.
- Remove any claim that catalytic steering is a validated property gain.
- Remove text that treats a scoring-surrogate change as biological control.
- Remove abrupt statements that name a result without explaining why it
  matters to the failure analysis.

### 7.3 Eligible evidence corpus and artifact inventory

The eligible corpus is every tracked steering evaluation from L42 and
L51-L58. L48 and L49 belong only to Interp4Discovery. L43 is not eligible
because this repository contains no tracked L43 document, script, or result
bundle.

Case inclusion is determined before manuscript drafting. A case enters the
main text only when it contributes a distinct failure mechanism and has a
reproducible audit bundle. Other eligible cases go into the audit table or are
listed as excluded with a reason.

| Case | Current artifact state | ICBINB use |
|---|---|---|
| L42 | Narrative document, but no committed raw result bundle | Include only if a raw audit bundle is regenerated by the end of August 15 |
| L51 | Summary JSON lacks raw sequences and scores, and its saved `PASS` conflicts with the documented corrected interpretation | Include only after a derived audit bundle records both the original and corrected policies |
| L52 | Raw scores and generated sequences are committed | Primary decoder-instability case |
| L53 | Raw scores and generated sequences are committed | Brief boundary case, not a required apparent-success mechanism |
| L54 | Multi-seed raw outputs are committed | Exclude and reserve for the catalytic paper |
| L55 | Multi-seed raw outputs are committed, but the files do not record the seed and the runner hard-codes seed zero | Seed-sensitive artifact-check case only after parameterized reproduction |
| L56 | Reproducible validation summary is committed | Primary endpoint-mismatch and grouped-validation sensitivity case |
| L57 | Raw scores and generated sequences are committed | Composition-shortcut case |
| L58 | One-seed direction geometry is committed | Supporting diagnostic only, labeled as one-seed evidence |

Every included case receives one provenance label:

- prospective, when the decision rule was frozen before that experiment;
- retrospective, when an earlier result motivated a later rule;
- post-hoc sensitivity, when the analysis was added after the result was seen.

The paper must not imply that the L50 protocol preceded L42 or L51.

### 7.4 Evidence to retain and reorganize

Use three primary failure mechanisms. This gives each mechanism enough space
for the method, evidence, correction, and lesson.

| Failure mechanism | Primary evidence | Lesson |
|---|---|---|
| Decoder instability and survivor-only interpretation | L52, plus L42 or L51 only if their bundles are recovered | Report failure risk and conditional score change together; compare methods only where both arms remain evaluable |
| Endpoint mismatch and grouped-validation sensitivity | L56 | Validate the exact biological endpoint before steering, and treat grouped-validation changes as evidence consistent with confounding rather than proof of its cause |
| Composition-sensitive and seed-sensitive interpretation | L55 and L57, with L58 as a one-seed diagnostic | Repeat artifact checks across complete run configurations and test composition directly |

L53 may appear in a short boundary paragraph. It shows that a strong
sequence-score association can coexist with no measured steering effect. It
does not establish one unique failure mechanism, so the manuscript must not
present the proposed dataset-intervention mismatch as proven.

### 7.5 Required new analysis

The minimum paper can be produced from tracked artifacts, but the analysis
must create new immutable audit bundles.

1. For each included case, save the original decision policy, corrected
   policy, provenance label, raw input paths, and derived statistics.
2. Estimate generation-failure risk over every attempted generation.
3. Estimate the property-score contrast among valid generations and report it
   jointly with failure risk.
4. Compute Hamming distance and edit count where raw source or baseline arms
   permit it. Output-logit displacement is required only for a rerun that
   actually saves logits.
5. Show whether the original and corrected policies lead to different
   interpretations.
6. Build a failure-stage table that identifies which audit check catches each
   case.
7. Verify every manuscript number against the derived audit bundle, not a
   stale verdict field.

### 7.6 Rerun cutoff and fallback package

The end of August 15 is the cutoff for recovering L42 or L51. A rerun must use
a patched script that saves raw sequences, scores, failure flags,
configuration, seeds, and source revision. If the rerun misses the cutoff, the
case is removed.

By the same cutoff, parameterize the L55 runner with explicit `--seed` and
`--out-dir` arguments, save the seed in each result bundle, and reproduce
seeds 0, 1, and 2 from a clean worktree. If this task fails, the required
composition-sensitive and seed-sensitive mechanism fails and ICBINB-BIO does
not pass its submission gate.

The minimum viable ICBINB paper uses:

- L52 for decoder instability;
- L56 for endpoint mismatch and a grouped-validation pattern consistent with
  source-organism confounding;
- L55 and L57 for composition-sensitive and seed-sensitive interpretation;
- L58 only as a clearly labeled one-seed diagnostic.

This minimum package does not depend on L42, L51, L53, L54, or any Interp
experiment. If one of the three primary mechanisms cannot be reproduced from
the tracked artifacts, narrow the claim and request an immediate statistical
review. If fewer than three mechanisms remain defensible, do not submit an
unsupported paper.

Calling ICBINB the protected primary submission means that its compute,
review, and writing time take priority. It does not override the evidence
gate.

Build the minimum manuscript first. Commit its source and reviewed PDF on an
immutable fallback tag before adding any recovered L42, L51, or L53 material.
Optional expansion must not overwrite or replace this fallback package.

### 7.7 Paper structure

The official call requires four content elements but does not explicitly
require their names as literal headings. Use them as clear sections in the
current draft so reviewers can locate each required element. Recheck the
template before submission.

1. Problem
   - Define the difference between a changed score and reliable property
     control.
   - Explain why a single successful-looking run is insufficient.
2. Proposed Approach
   - Present the staged audit.
   - Define endpoint, intervention, generation, robustness, and independence
     checks.
3. Observed Outcome
   - Present the failure mechanisms in the order in which the audit detects
     them.
   - Use one compact example per mechanism.
4. Reason for Failure
   - Explain why each original inference was too strong.
   - State the corrected analysis and practical rule.
5. Limitations and conclusion
   - Restrict claims to ESM2-650M, the tested generation method, and the saved
     datasets.

### 7.8 Figures and tables

- Figure 1: the staged audit, with each check and the claim it protects.
- Figure 2: generation-failure risk and valid-output score estimates for the
  decoder-instability cases.
- Table 1: failure mechanism, original interpretation, failed check, corrected
  interpretation, and recommended practice.

Composition and seed sensitivity may be a compact panel in Figure 2 or part of
Table 1. No figure should exist only to list all targets.

### 7.9 ICBINB-BIO completion gate

The paper is ready for submission only when:

- three distinct failure mechanisms are supported by reproducible audit
  bundles;
- the two-part analysis reports every attempted generation through the
  failure-risk component;
- every numeric claim maps to the result ledger;
- the paper contains no attention-head results;
- L54 results do not appear;
- L58 is described as a one-seed diagnostic;
- every case is labeled prospective, retrospective, or post-hoc sensitivity;
- the conclusion does not claim improved biological properties;
- an independent reviewer can state the paper's thesis in one sentence;
- the statistical reviewer has no unresolved submission-blocking critical or
  major finding;
- the anonymous PDF passes the identity scan and fits within eight pages.

ICBINB-BIO remains the protected primary submission even if all other work
stops.

## 8. Interp4Discovery strategy

### 8.1 Product contract

Working title:

> Do Contact-Enriched Attention Heads Causally Support Protein Prediction?

Research question:

> Does attention to known three-dimensional contacts identify heads whose
> outputs are necessary for masked-residue prediction?

Primary confirmatory hypothesis:

> Contact enrichment measured on the discovery panel predicts greater
> contact-specific masked-residue damage under ablation on an independent
> structure panel.

Use one ordered decision path.

1. Test the primary enrichment-effect association.
2. If the positive association is not supported, test whether the
   prespecified top contact heads are equivalent to matched controls within a
   frozen margin.
3. If neither test supports its branch, do not submit.

Grouped ablation is a mechanistic extension. It cannot rescue an inconclusive
primary result. An imprecise null result is not a thesis.

This framing fits Interp4Discovery because it evaluates whether an
interpretable biological pattern supports causal model understanding. The
paper is about a scientific use of interpretability, not activation steering.

### 8.2 Material to remove from the current paper

- Remove all five-property steering results.
- Remove catalytic, disorder, immunogenicity, binding, and expression claims.
- Remove the steering protocol and its figures.
- Remove broad statements about property control that are not tested by the
  attention experiment.

### 8.3 Required experimental design

#### A. Independent structure panel

- Keep the original eight PDB structures as the discovery and pilot panel.
- Construct a separate test panel with no sequence-cluster overlap.
- Use the pilot panel to estimate protein-level variance and run a
  precision-based sample-size calculation.
- Freeze a fixed, diverse protein list with a size determined by the
  prespecified confidence-interval target. Do not add proteins after seeing
  test results.
- If the required protein count exceeds the compute budget, stop the
  submission before evaluating the test panel.
- Freeze chain selection, contact threshold, and sequence-separation rule.
- Save the PDB identifiers and processing exclusions in a cohort manifest.

#### B. Continuous causal outcome

For each masked position, measure the change in log probability assigned to
the true residue under ablation relative to the unablated model.

The primary head-level outcome is the contact interaction:

> ablation damage on contact-bearing positions minus ablation damage on
> matched non-contact positions within the same protein.

This difference separates contact-specific damage from a generic loss in
language-model performance. The matching rule for non-contact positions must
be frozen and include protein, residue identity when possible, distance from
the termini, local sequence context, and baseline true-residue probability.
The manifest must define matching calipers, unmatched-position handling,
minimum common support, and balance diagnostics. No matched covariate should
have an absolute standardized mean difference above 0.1. The sample-size
calculation uses the proteins and positions that remain after matching.
Accuracy is a secondary outcome
because the current 104-position sweep produces only eight distinct effect
values and large tied ranks.

#### C. Full head analysis

- Measure contact enrichment for all 480 heads on the discovery panel.
- Measure the causal outcome for all 480 heads on the independent test panel.
- Use one prespecified global association between discovery-panel enrichment
  and test-panel contact-specific damage.
- Bootstrap proteins in both panels and recompute the full enrichment and
  damage estimates.
- Use the frozen layer-adjusted finite-head association. Do not treat heads as
  exchangeable random samples.
- Do not run 480 confirmatory tests. If individual exploratory head claims are
  reported, control their false-discovery rate.

#### D. Matched controls

Select the top five contact-enriched heads from the discovery panel before
opening the test panel. Give each head at least two controls from the same
layer. Match on discovery-panel attention entropy, output norm, and
single-head output displacement. Freeze matching tolerances, the number of
controls, and deterministic tie handling. Include one low-enrichment and one
randomly selected eligible control when the matching set permits it.

Independent-panel contact enrichment may be used to test correlational
replication. It may not be used to rerank heads, change groups, choose
controls, or alter matching.

#### E. Ablation variants

- Zero replacement for the all-head sweep.
- Mean replacement for the primary selected heads, using replacement values
  estimated only from the discovery panel.
- If the confirmatory core succeeds and compute remains, grouped ablation for
  the top 1, 5, and 10 contact-enriched heads.
- Any grouped analysis uses size-matched controls with the same layer
  composition and comparable aggregate output norm and model-output
  displacement.

Compare grouped effects with the sum of the corresponding individual effects.
A larger grouped effect is consistent with redundancy only if it is
contact-specific and exceeds matched generic perturbations. It does not prove
redundancy by itself.

#### F. Statistics

- Use a hierarchical bootstrap that samples proteins and then positions.
- Make the global enrichment-effect association the first confirmatory test.
- If that test does not pass, compare the prespecified top five heads with
  matched controls using the contact interaction.
- The negative branch requires equivalence for each of the five head-control
  contrasts under a familywise multiplicity correction. It does not use a
  pooled average that can hide one important head.
- Define a numerical minimum association and equivalence margin from the pilot
  and scientific interpretation before the independent panel is evaluated.
- Use an ordered testing procedure or alpha allocation recorded in the
  manifest.
- If no defensible margin can be stated, do not claim absence of an effect.
- Run sensitivity analyses by contact distance, sequence separation, and
  protein length.

#### G. Intervention and resource validation

- Unit-test that every hook changes only the requested head.
- Confirm that zero and mean replacement have calibrated perturbation
  magnitudes.
- Benchmark one layer on 100 positions, project the full runtime, and add a
  25 percent retry buffer.
- Reserve compute first for any required ICBINB rerun.
- Cancel Interp by August 14 if the projected confirmatory core cannot finish
  by August 19.

### 8.4 Interp4Discovery gate on 2026-08-20

Continue to submission only if all of the following are true:

1. The manifest contains numerical thresholds for the primary association,
   equivalence, precision, method sensitivity, and correlational replication.
2. Correlational replication passes its frozen rule. A suitable default is
   pooled enrichment above one with a 95 percent confidence interval excluding
   one for the prespecified top-five set, but the exact rule must be fixed
   before opening the panel.
3. The continuous outcome and hierarchical analysis run successfully for all
   480 heads.
4. The primary association passes its frozen positive threshold, or every one
   of the five head-control contrasts places its familywise-adjusted
   confidence interval inside the frozen equivalence margin.
5. The positive-branch confidence interval is no wider than twice its
   association margin. For the negative branch, every adjusted confidence
   interval is no wider than twice the equivalence margin.
6. For the positive branch, mean replacement is a sensitivity analysis on the
   prespecified top five heads. Stop if any of the five estimates has the
   opposite sign with a multiplicity-adjusted confidence interval excluding
   zero. It does not re-test the 480-head association.
7. For the negative branch, every top-five head-control contrast meets the
   equivalence rule under both zero and mean replacement.
8. Matching meets the frozen common-support and balance rules.
9. Hook-isolation and perturbation-calibration tests pass.
10. The result fits a five-page paper without importing the steering study.

If any of these conditions fails by August 20, stop the submission. Preserve
the analysis as future work and move all effort to ICBINB-BIO.

### 8.5 Paper structure

1. Introduction
   - Associative attention patterns are biologically interpretable.
   - Causal usefulness requires an intervention test.
2. Related work
   - Contact-enriched protein attention.
   - Attention as explanation and known limits of attention weights.
3. Methods
   - Discovery and independent structure panels.
   - Continuous masked-residue outcome.
   - Single-head ablations, plus grouped ablations only if used for a
     redundancy analysis.
   - Matched controls and hierarchical statistics.
4. Results
   - Correlational replication.
   - Full 480-head causal relation.
   - Selected-head tests and, if run, grouped-ablation tests.
5. Discussion
   - What the result establishes about necessity, redundancy, or candidate
     selection.
6. Limitations
   - One model family, masked-residue task, intervention definition, and
     structure-panel scope.

### 8.6 Interp4Discovery completion gate

- One independent test panel is frozen and documented.
- The primary outcome is continuous.
- The primary outcome is contact-specific rather than a generic prediction
  loss.
- All 480 heads are evaluated.
- Controls are matched and prespecified.
- Zero and mean replacement are reported for the primary selected heads.
- Grouped ablations are required only if the manuscript makes a redundancy
  claim.
- The main claim follows the frozen ordered testing rule and passes its
  precision or equivalence requirement.
- The recorded August 20 gate shows that correlational replication, matching,
  intervention calibration, and the branch-specific zero/mean checks passed.
- No steering results remain in the manuscript.
- The anonymous PDF passes the identity scan and fits within five pages.

## 9. Catalytic steering paper

### 9.1 Status and claim

This paper begins only after the workshop packages are frozen.

Provisional claim:

> At low editing burdens, a turnover-derived steering direction increases
> independent predictions for a fixed enzyme-substrate pair while preserving
> annotated active sites and structural plausibility.

Until wet-lab testing exists, the title, abstract, and conclusion must say
"predicted turnover" rather than "catalytic activity."

### 9.2 First feasibility gate

The current L54 analysis takes the median turnover across substrates for each
enzyme. About forty percent of the evaluation enzymes have multiple
substrates. A sequence-only model cannot support a substrate-specific claim if
the substrate identity has been averaged away.

Before a new generation run:

1. Reconstruct enzyme-substrate records with sequence, substrate, SMILES, EC
   class, organism, units, and available conditions.
2. Choose one fixed source substrate for each evaluation enzyme using a
   written rule.
3. Prevent the same sequence, close homolog, or substrate family from crossing
   construction and evaluation splits.
4. Exclude records with conflicting or incomparable conditions unless they
   can be normalized defensibly.
5. Build the steering direction from normalized enzyme-substrate records. Do
   not reuse the current sequence-level median direction for a
   substrate-specific claim.
6. Decide whether the data support a substrate-specific claim or only a
   sequence-level turnover-tendency claim.

If this gate cannot be resolved, do not run the positive paper.

### 9.3 Required experiments

| Work package | Required design |
|---|---|
| Direction builds | Five sequence-cluster-disjoint construction splits |
| Generation | Fixed evaluation cohort, five mask seeds, mask fractions 0.05, 0.10, 0.20, and 0.30 |
| Controls | Unsteered, at least 20 random directions, label-shuffled directions, reverse steering, and direct G/R composition editing |
| Burden matching | Match Hamming distance, edit count, and output-logit displacement |
| Independent prediction | Two enzyme-substrate turnover predictors with different architectures, documented training provenance, cluster-level overlap exclusion, and calibration on an external experimental benchmark |
| Functional preservation | Protect catalytic, cofactor-binding, and required motif residues; verify domain and EC-family consistency |
| Structural analysis | Compare source, unsteered, learned, and burden-matched controls with Boltz |
| Liabilities | Aggregation, solubility, HLA-presentation liability, toxin homology, sequence complexity, diversity, and training-set similarity |
| Statistics | Hierarchical analysis over direction build, source enzyme, and mask seed |

Boltz may provide fold confidence, pocket geometry, complex confidence, ligand
pose, and possibly affinity estimates. A plausible complex is not evidence of
turnover. Boltz must not be used to make toxicity, immunogenicity, disorder,
or general safety claims.

The Boltz manifest must freeze template and MSA policy, ligand protonation and
stereochemistry, cofactors, oligomer state, and sampling count. The primary
analysis must not use forced pocket or contact constraints. Pair selection and
result review should be blinded to steering arm. The paper should call these
outputs predicted poses and predicted structural preservation.

If predictor training provenance or overlap cannot be established, the result
is agreement between predictors, not independent validation.

### 9.4 Catalytic go or stop criteria

Proceed to a paper only if:

- both independent turnover predictors improve against unsteered and
  edit-matched controls in at least four of five direction builds;
- the learned direction exceeds the prespecified percentile of the full
  random-direction distribution;
- label-shuffled directions do not reproduce the gain;
- reverse steering changes the outcome in the prespecified opposite direction;
- the effect remains after matching G/R composition and editing burden;
- the gain appears at low editing burdens, not only after extensive sequence
  rewriting;
- protected active-site residues remain unchanged;
- structure and pocket checks meet prespecified noninferiority margins;
- every liability and diversity measure stays within its prespecified
  threshold.

Before final evaluation, the manifest must assign numerical values to low
editing burden, minimum predictor gain, noninferiority margins, maximum
generation-failure increase, random-direction percentile, and every liability
threshold. "Four of five direction builds agree" means that four builds meet
the complete joint decision rule, not merely that their point estimates are
positive.

Liability models report computational warning signals, not toxicity,
immunogenicity, or safety. An adverse signal blocks a beneficial-design claim
but may support a separate tradeoff analysis.

If only the G/R score changes, cancel the positive paper and describe the
result as compositional steering. A claim of actual catalytic improvement
requires purified-protein turnover measurements under controlled substrate,
temperature, and pH conditions.

## 10. Disorder steering paper

### 10.1 Status and claim

This paper is conditional. The current effect is directionally stable, but the
E/S-excluded result fails in one of three seeds and degeneration is substantial
at alpha 0.5.

Provisional claim:

> Low-strength steering increases consensus predicted intrinsic disorder and
> creates contiguous disordered regions beyond amino-acid composition changes,
> while preserving ordered domains.

### 10.2 Required experiments

| Work package | Required design |
|---|---|
| Data split | Deduplicate and sequence-cluster DisProt before construction and evaluation splits |
| Direction builds | Five independent construction splits with a fixed external evaluation cohort |
| Validators | IUPred3 and flDPnn as primary per-residue validators, with documented training provenance, homolog-overlap checks, and calibration on an external experimental benchmark; a third method only if provenance permits |
| Composition controls | E/S exclusion, regression on all 20 residue frequencies, composition-matched shuffles, label-shuffled directions, and composition-orthogonalized steering |
| Region outcomes | Disorder fraction, contiguous region count and length, terminal versus internal regions, changed versus unchanged positions |
| Generation | Five mask seeds and edit-matched controls; failed outputs remain failures |
| Structural analysis | Boltz only for preservation of ordered domains outside predicted disordered regions |
| Liabilities | Aggregation, solubility, immune liability, toxin homology, complexity, diversity, and novelty |
| Statistics | Hierarchical uncertainty over direction build, protein, and mask seed |

If predictor provenance or homolog overlap cannot be established, describe
the result as agreement between disorder predictors rather than independent
validation.

The Boltz manifest must freeze template and MSA policy, oligomer state, and
sampling count. Do not use forced structural constraints in the primary
analysis. Boltz outputs may support a claim of predicted ordered-domain
preservation only.

### 10.3 Disorder go or stop criteria

Proceed to a positive paper only if:

- IUPred3 and flDPnn agree on the direction and region-level effect;
- the hierarchical confidence interval excludes zero;
- at least four of five direction builds agree;
- E/S exclusion, composition matching, and orthogonalized steering retain a
  composition-adjusted effect above the prespecified minimum;
- regression on all 20 residue frequencies retains the effect;
- label-shuffled directions do not reproduce the effect;
- the generation-failure risk difference stays within its prespecified
  margin;
- ordered-domain preservation meets its prespecified noninferiority margin.

Before final evaluation, the manifest must assign numerical values to the
minimum region-level effect, composition-adjusted effect, maximum
generation-failure increase, ordered-domain noninferiority margin, and each
liability threshold. "Four of five direction builds agree" means that four
builds meet the complete joint rule.

Liability models report computational warning signals. They do not establish
toxicity, immunogenicity, or safety. An adverse signal blocks a
beneficial-design claim but may support a separate tradeoff analysis.

If the composition controls fail, cancel the positive paper. Keep the current
result in ICBINB-BIO as a compositional-confounding and seed-sensitivity case.
Experimental claims about disorder require an ensemble-sensitive method such
as NMR, SAXS, circular dichroism, or controlled proteolysis.

## 11. Parallel execution model

### 11.1 Worktrees and branches

Use isolated sibling worktrees so paper owners cannot overwrite one another.
Commit the approved plan, initial claim registry, and paper-specific contracts
to the integration branch before creating any worktree. Every worktree must
start from that exact commit.

| Worktree | Branch | Owner |
|---|---|---|
| `esmplm-steering-shared` | `research/shared-audit` | Shared methods owner |
| `esmplm-steering-icbinb` | `paper/icbinb` | ICBINB paper owner |
| `esmplm-steering-interp` | `paper/interp4discovery` | Interp paper owner |
| `esmplm-steering-catalytic` | `paper/catalytic` | Catalytic paper owner after August 29 |
| `esmplm-steering-disorder` | `paper/disorder` | Disorder paper owner after August 29 |

The main worktree remains the integration and review workspace.

The shared ICBINB audit bundle is merged and locked before the ICBINB paper
owner receives it. Interp experiment code and results remain on their own
branch until the Interp gate passes. Later-paper branches are not created
before August 29.

### 11.2 Agent roles

| Role | Responsibility | May edit |
|---|---|---|
| Orchestrator | Freeze contracts, assign work, merge accepted outputs, enforce gates | Program artifacts and integration branch |
| Shared methods owner | Manifests, invalid-output analysis, edit-burden metrics, shared statistics | Shared experiment code and locked result bundles |
| ICBINB paper owner | Rebuild the failure-audit paper from the ICBINB result bundle | ICBINB paper directory only |
| Interp discovery owner | Discovery panel manifest, head ranking, head controls, replacement inputs, and discovery stage lock | Interp discovery code and outputs only; confirmation artifacts are prohibited |
| Interp cohort and matching owner | Confirmation cohort materialization, baseline probabilities, position matching, and cohort and matching stage locks | Interp cohort and matching code and outputs only |
| Interp ablation owner | Hook isolation, perturbation calibration, zero and mean replacement runs | Interp ablation code and outputs; matching stage is read-only |
| Interp analysis owner | Locked head outcomes, resampling, branch tests, and gate artifact | Interp analysis outputs; cohort, matching, and ablation stages are read-only |
| Interp paper owner | Write only from the locked Interp result bundle | Interp paper directory only |
| Statistical reviewer | Audit units, missingness, uncertainty, multiplicity, and equivalence | Review report only |
| Citation reviewer | Verify literature and citation ledger | Citation report and bibliography corrections |
| Final technical reviewer | Reproduce the locked claims and audit the complete manuscript | Review report only |
| Submission-package owner | Build the anonymous source archive and upload-ready files | Submission package only |
| Anonymity reviewer | Search sources, archives, and PDF metadata for identity leaks | Submission package corrections |
| Cross-paper reviewer | Detect duplicate text, evidence overlap, and conflicting claims | Review report only |

Before work begins, record one named agent and agent ID for every active role
in `docs/PAPER_PORTFOLIO_REVIEW.md`. A role with no accountable owner is not
started.

The following role combinations are prohibited:

- experiment owner and statistical reviewer for the same paper;
- paper owner and final technical reviewer for the same paper;
- either paper owner and cross-paper reviewer;
- submission-package owner and final anonymity reviewer;
- any shared identity among the Interp discovery, cohort and matching,
  ablation, analysis, and paper-owner roles.

The Interp cohort and discovery stages are separately hashed before matching.
Matching consumes both accepted locks. The matching stage and its three-lock
handoff are accepted before ablation begins. The discovery owner cannot read
confirmation artifacts, and the matching owner cannot read ablation output.
The ablation owner receives only the preregistration lock and accepted
matching handoff and cannot edit either. Every later stage verifies its
accepted parent-lock set. The five Interp roles use five distinct agent IDs.
The paper owner receives no confirmation artifact until the final verification
passes and the orchestrator writes the accepted paper handoff.

The ICBINB and Interp paper owners work independently. They receive the shared
method manifest, the claim registry, and only their own result bundle. They do
not read each other's draft until the cross-paper review.

The later catalytic and disorder paper owners also work independently. They do
not start from the workshop prose. They receive their own frozen data,
experiment manifest, result bundle, and claim contract.

### 11.3 Agent output contract

Every agent returns:

- files changed;
- inputs used;
- claims supported;
- claims not supported;
- tests or checks run;
- unresolved blockers;
- recommended next gate decision.

An agent may not declare a paper ready for submission. Readiness is an
orchestrator decision after independent review.

The orchestrator accepts a handoff only when its required files exist, focused
checks pass, and no claim exceeds the claim registry. A statistical reviewer
or final technical reviewer may block a gate with a critical or major
finding. The gate remains blocked until the finding is resolved or the
affected claim is removed.

Review severity has three levels.

- Critical means the data, analysis, primary claim, anonymity, or research
  integrity is invalid.
- Major means the issue could change the interpretation, gate decision, or
  submission readiness.
- Minor means the issue improves clarity without changing the claim.

Every critical or major finding blocks submission until it is resolved or the
affected claim is removed. Minor findings are tracked but do not
automatically block a gate.

## 12. Dependencies and critical path

```text
Freeze the ICBINB claims, outcomes, and invalid-output policy
    |
    +--> Shared audit reanalysis --> ICBINB result lock --> ICBINB draft
    |                                                    --> review and submission
    |
    +--> Freeze Interp hypothesis and compute budget
             |
             +--> Independent PDB panel --> full causal analysis --> August 20 gate
                                                                    |
                                                                    +--> Interp draft
                                                                    +--> stop submission

After August 29:
    |
    +--> Catalytic data reconstruction --> validators and controls --> paper gate
    |
    +--> Disorder clustered split --> composition controls --> paper gate
```

The ICBINB reanalysis is the workshop critical path. The Interp experiment may
run in parallel but may not take the only available compute slot when the
ICBINB result lock is incomplete.

## 13. Workshop schedule

| Date | ICBINB-BIO | Interp4Discovery | Shared and review work |
|---|---|---|---|
| Aug 13 | Verify official venue policy and approve paper contract | Freeze primary hypothesis and ordered test | Inventory artifacts and commit approved contracts |
| Aug 14 | Patch L55 seed handling and benchmark any allowed L42/L51 rerun | Benchmark one layer, run precision calculation, and make early compute decision | Create isolated worktrees and reserve compute |
| Aug 15 | Reproduce L55 seeds, finish allowed reruns, or exclude unrecovered cases | Freeze independent PDB cohort and matching rules | Lock minimum ICBINB corpus |
| Aug 16-17 | Build audit bundles, build and tag the minimum fallback source and PDF | Run all-head independent-panel sweep | Statistical audit of both analyses |
| Aug 18-19 | Add only approved optional cases and revise the protected fallback | Run matched controls and replacement variants; run grouped ablations only after the confirmatory core succeeds | Citation and result-ledger checks |
| Aug 20 | Internal paper review | Make submit or stop decision | Protect remaining schedule |
| Aug 21-23 | Revise and build figures | Draft only if the gate passed | Cross-paper claim review |
| Aug 24-25 | Content freeze | Content freeze if active | Independent technical review |
| Aug 26-27 | Format, bibliography, anonymity, PDF checks | Same if active | Build anonymous supplement if needed |
| Aug 28 | Upload and verify package | Upload and verify package | Final checklist |
| Aug 29 | Buffer only | Buffer only, with upload complete before 2026-08-30 01:00 UTC | Submit before each portal deadline |

No new scientific claim enters a workshop paper after the August 25 content
freeze.

## 14. Definitions of done

### 14.1 Experiment done

- manifest frozen before final evaluation;
- cohort identifiers and seeds saved;
- controls completed;
- invalid outputs handled according to the primary policy;
- raw outputs and summary statistics committed;
- exact reproduction command recorded;
- dependency environment and model revision recorded;
- focused result reproduced from a clean worktree;
- focused tests pass;
- result ledger updated;
- complete claim set and typed ledger semantics pass the ownership verifier;
- every result artifact has a locked lineage manifest and accepted parent
  hashes;
- role assignments separate experiment, paper, and review identities;
- independent statistical review completed;
- the machine-readable review decision binds the exact row, manifests, and
  artifacts;
- zero unresolved critical or major findings;
- orchestrator sign-off recorded.

### 14.2 Draft done

- one research question and one main thesis;
- every section advances that thesis;
- every numeric claim points to a saved result;
- every external claim points to a verified citation;
- limitations distinguish measured outcomes from biological interpretation;
- prose uses simple technical English with enough explanation;
- no em dashes, excessive parentheticals, or decorative emphasis;
- no duplicated paragraphs or figures from another active paper.
- the ownership verifier passes for the paper source and figures.

### 14.3 Submission package done

- correct venue template and page limit;
- anonymous author block;
- no identifying repository link;
- source and PDF scanned for `Ivkov`, `divkov`, `DIvkov575`, `umich`,
  `University of Michigan`, `github.com`, and local absolute paths;
- PDF metadata checked;
- bibliography builds without missing references;
- figures are legible in grayscale and at final size;
- venue-specific disclosure, code, data, ethics, funding, conflict, and author
  contribution requirements checked;
- official venue-policy check recorded with URLs and access date;
- final PDF opened and inspected page by page;
- uploaded file downloaded from the submission system and compared with the
  local final PDF.

Run the ownership checks from the repository root:

```bash
.venv/bin/python -m plm_steering.submission_ownership \
  --paper icbinb-bio \
  --root docs/submissions/icbinb-bio \
  --ledger plm_steering/icbinb_audit_out/result_ledger.csv \
  --ledger-root . \
  --claim-registry docs/CLAIM_REGISTRY.md

.venv/bin/python -m plm_steering.submission_ownership \
  --paper interp4discovery \
  --root docs/submissions/interp4discovery \
  --ledger "plm_steering/interp4discovery_out/$EXPERIMENT_ID/result_ledger.csv" \
  --ledger-root . \
  --claim-registry docs/CLAIM_REGISTRY.md
```

For Interp4Discovery, `EXPERIMENT_ID` must equal the identifier in the final
preregistration lock. `pdftotext` must be installed because a missing or
unreadable root PDF scan fails closed.

## 15. Current execution board

| Item | Status |
|---|---|
| Independent ICBINB strategy review | Complete |
| Independent Interp4Discovery strategy review | Complete |
| Independent catalytic and disorder review | Complete |
| Independent program and schedule review | Complete |
| Portfolio plan | Approved for execution on 2026-08-13 |
| Subagent review record | Complete in `docs/PAPER_PORTFOLIO_REVIEW.md` |
| Official venue-policy record | Complete, with unresolved portal fields recorded |
| Claim registry and shared ledger schemas | Third correction `5c9e90c` committed; Hume accepted and Maxwell held; fourth correction in progress |
| ICBINB manifest | Exact statistical review of `5c9e90c` accepted; implementation remains blocked |
| Interp preregistration | Five-role barrier accepted at the contract level; final lock remains unresolved |
| Independent contract reviews | Hume accepted `5c9e90c`; Maxwell held it on 2 Major and 1 Minor findings; fourth correction awaits exact review |
| Shared audit reanalysis | Not started |
| Independent Interp experiment | Not started |
| Manuscript restructuring | Blocked on locked result bundles |

The next execution step is to close the prohibited-claim scanner and modified
text-evidence findings from the exact review of `5c9e90c`, commit the fourth
correction, and obtain statistical and consistency reviews of that same exact
commit. Isolated worktrees start only from the accepted contract commit.
Manuscript rewriting starts only after the relevant result bundle is locked.
