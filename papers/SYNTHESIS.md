# What Activation Steering Can and Cannot Do to a Protein Language Model

*A synthesis of the L42–L61 steering arc on ESM2-650M.*

## Abstract

Activation steering edits a protein language model's residual stream at
inference time and can change its generated sequences without retraining. We
attempted to steer nine sequence properties in ESM2-650M under one fixed
harness (mean-pooled per-layer difference-of-means vectors, added uniformly at
every position, evaluated by single-shot masked filling) and one
pre-registered six-criterion acceptance protocol. Across these targets a single
quantity — the mean amino-acid *compositional separation* between the low- and
high-label groups used to build the steering vector — predicts both whether a
target is steerable and how large the achievable effect is, while proxy-score
correlation with the true label does not. The clearest contrast: a
binding-affinity proxy validated at held-out *r*=0.80 steered nothing (group
separation 0.003), whereas a catalytic proxy at *r*=0.22 (separation 0.02–0.05)
passed on all three seeds. Effect size scales with separation from a flat null
(0.003) through 25% of the natural property gap (0.039) to 72% (0.086).
Separation is necessary but not sufficient: two well-separated targets
(separation 0.035–0.038) still failed — one because the model does not act on
the direction, one because the property is *positional*. The last case exposes
a structural limit: uniform-addition steering can move aggregate compositional
properties but cannot install positionally-localized features (a
signal peptide, and by extension active-site geometry or domain boundaries),
regardless of how well its proxy predicts the property. All endpoints are
computational; no wet-lab assay was run.

## 1. The question

Prior work steers protein language models toward higher-scoring sequences
[Huang et al. 2025]. But a higher score is not control of a biological
property, and the field lacks an *a priori* rule for which properties a given
steering method can move at all. We ask two questions of one fixed method:
**(i)** what predicts whether a target property is steerable, and **(ii)** what
class of properties is this method structurally unable to reach?

## 2. Method (held fixed across all targets)

- **Model / decoder.** ESM2-650M; generation by `mask_fill_generate` (single
  masked fill, `mask_fraction=0.3`, argmax).
- **Direction.** Per-layer difference of mean activations between 150 low-label
  and 150 high-label proteins, added to all 33 layers, uniformly across
  positions. Control: a matched-norm random direction.
- **Evaluation.** 150 held-out proteins; a target-specific *compositional
  proxy* scores each generation; effect = paired-bootstrap contrast
  (10,000 resamples) of real vs. random direction.
- **Acceptance protocol (pre-registered, L50).** A capability gain counts only
  if it clears all operative criteria: (1) beats the random-direction control
  with a real CI; (2) coherent dose-response over ≥3 points; (3) **survives
  residue exclusion** — recompute the score with the two dominant substituted
  residues removed; (4) proxy validated against real labels *before* the run
  (asserted in code, |r|≥0.15); (5) beats any prior technique; (6) n≥150.
  Failing (1)/(2)/(3)/(4) outright → **KILL**; passing most but failing (3) or
  a dose check → **AMBIGUOUS**.
- **Compositional-separation gate (G1).** Before any GPU work, measure the mean
  per-residue amino-acid-composition L2 distance between the low/high vector
  groups. This became the arc's single most predictive number.
- **Dose window.** The masked-fill eval collapses into degenerate
  low-complexity output at α≥0.35 (a limitation of the eval, not the
  direction); dose-response is measured on the non-degenerate grid
  {0.10, 0.15, 0.20, 0.25}.

## 3. Result 1 — Separation predicts steerability and effect size; proxy correlation does not

Nine targets span the full range from a flat null to a large, seed-robust,
artifact-resistant gain. Effect size tracks compositional separation
monotonically; the best-validated proxy in the entire project (binding, *r*=0.80)
produced the cleanest null.

| Target | Group separation | Proxy *r* (held-out) | Verdict (seeds) | Effect (% of natural low→high gap) |
|---|---|---|---|---|
| Binding affinity, single-backbone (L53) | **0.003** | **+0.80** | **KILL** | flat null at every α |
| Zinc-finger domain (L61) | 0.028 | +0.29 | **KILL** | direction anti-correlated (crit 1) |
| Calcium-binding / EF-hand (L61) | 0.038 | +0.16 | **KILL** | model does not act on direction (crit 1) |
| Signal peptide (L61) | 0.035 | **+0.74** | **KILL** | positional, not compositional (crit 3) |
| Disulfide (Cys fraction) (L61) | 0.026 | +0.17 | PASS (2/3) | tiny (~+0.002) |
| Glycosylation density (L61) | 0.039 | +0.41 | PASS (3/3) | tiny (~+0.003) |
| DNA-binding propensity (L60) | 0.039 | +0.24–0.27 | PASS (2/3) | **25%** |
| Catalytic turnover, kcat (L54) | 0.023–0.045 | +0.21 | PASS (3/3) | moderate |
| Transmembrane fraction (L59) | **0.086** | +0.79 | PASS (3/3) | **72%** |

Two anchoring comparisons:

- **Proxy strength ≠ steerability.** L53's binding proxy is validated far more
  rigorously than any other target (held-out *r*=0.80, position-generalization
  *r*=0.54, shuffle-null *r*=−0.001) yet steers nothing across all five α. L54's
  catalytic proxy (*r*=0.22, the weakest runnable target) passes on 3/3 seeds.
  Proxy-validation strength and steering effect are not even weakly
  monotonically related.
- **Separation ≠ dataset artifact.** L53's null was originally read as "binding
  is unsteerable." L60 reframes binding as an *intrinsic, cross-protein*
  capability (DNA-binding: a protein binds the phosphate backbone by its own
  sequence). Moving from a single 188-residue backbone (separation 0.003) to
  cross-protein data (0.039) lifts separation ~12× and recovers a significant,
  residue-robust, dose-responsive effect. **Binding is steerable; L53's KILL
  was a single-backbone data artifact, not a property of binding.** The
  mechanism was predicted from separation before any GPU run.

The calibration ladder — L53 (0.003 → null), L60 (0.039 → 25%), L54
(0.02–0.05 → moderate), L59 (0.086 → 72%) — is the arc's central quantitative
claim: **build the difference-of-means vector from cross-protein data with real
compositional separation, and effect size follows separation.**

## 4. Result 2 — Separation is necessary but not sufficient

Screening candidates by separation removes the L53 null mode but does not
guarantee a pass. Three well-separated targets (0.028–0.038, in or above the
passing band) still failed, by two distinct routes:

- **The model does not act on the direction.** Calcium-binding (separation
  0.038, as high as DNA-binding) shows no significant steering at any safe α.
  A compositionally distinct group whose direction the residual stream simply
  ignores. Zinc-finger's Cys+His direction is *anti-correlated* with the
  proxy after steering.
- **The property is positional (see Result 3).** Signal peptide.

So separation is a screen, not a predictor of success: it is necessary
(near-zero separation guarantees a null, L53) but a high value can still die on
criterion 1 (model inert to the direction) or criterion 3 (positional).

## 5. Result 3 — The harness steers composition, not position

The sharpest single result. The signal-peptide target has the best proxy of any
candidate ever tried (held-out *r*=0.742, verified in
`l61_signal_pep_out/results.json`) and a textbook-clean dose-response
(N-terminal hydropathy 0.059 → 0.100 → 0.152 → 0.251 across the safe grid). It
nonetheless **KILLs on criterion 3**: excluding the two dominant substituted
residues (L, S) collapses the effect to non-significance (CI crosses zero). The
steering vector raises *N-terminal-window* hydropathy purely by dumping bulk
hydrophobic residues across the whole sequence — it cannot **concentrate** them
at the N-terminus, which is what defines a signal peptide.

Contrast glycosylation, which passes: its proxy is sequon density *summed over
the whole sequence* — a genuinely aggregate quantity a mean-pooled vector can
nudge.

**Conclusion.** A steering vector that is mean-pooled over positions and added
uniformly to every position can move only **aggregate compositional**
properties — transmembrane fraction, catalytic composition, DNA-binding charge,
glycosylation density. It **structurally cannot install positionally-localized
features**: a signal peptide, and by the same argument active-site geometry,
domain boundaries, or termini-specific motifs. This is a property of the
injection geometry, not of target selection; reaching positional features would
require position-aware injection, a concrete methodological next step.

## 6. What the acceptance protocol catches (negative-result discipline)

The predictions above are trustworthy only because the protocol rejects
flattering numbers. Four completed studies show the specific inferences each
check protects, and each changed a conclusion:

- **Endpoint validity (L56, immunogenicity).** A peptide-composition score
  correlated *r*=0.427 with an allele-aggregated binding label but only
  *r*=0.100 with measured T-cell response, and its full-length correlation went
  from +0.379 under random folds to **−0.323** under organism-grouped folds —
  consistent with learning organism-associated composition. Killed *before*
  generation: the score did not measure the claimed endpoint.
- **Denominator loss (L52, layer-subset thermostability).** A five-layer
  intervention looked competitive at high strength only because the all-layer
  arm's outputs had collapsed under the low-complexity filter (5 and 0
  evaluable pairs at α=1.0, 2.0 vs. 57–58 for five-layer). Restricted to the
  shared valid range, five-layer retains just 43–59% of all-layer effect. A
  conditional score must sit beside its evaluable denominator.
- **Composition dependence (L57, expression).** An eSol soluble-fraction
  contrast of +0.0125 fell to +0.00035 (CI crossing zero) once the two dominant
  substituted residues were excluded. The positive decision did not survive its
  own scoring rule.
- **Whole-run stability (L55, disorder).** A positive TOP-IDP contrast repeated
  across three stored runs, but residue-exclusion passed in only two — so the
  headline effect is partly compositional collapse. (L59 transmembrane, by
  contrast, holds criterion 3 on all three seeds: excluding L, S drops the
  effect from ~0.54 to ~0.20 but keeps it significant everywhere — a real
  capability, not a hydrophobic-dumping artifact.)

These are the same guards that earlier caught false positives from poly-leucine
and A/G collapse, and that assert proxy validity in code before the model loads.

## 7. Limitations

- **All endpoints are computational.** No wet-lab assay establishes that any
  generated sequence has improved thermostability, turnover, transmembrane
  character, binding, or glycosylation. Every "effect" is a change in a
  compositional proxy, not a measured biological property.
- **One model, one decoder, one injection geometry.** ESM2-650M, single-shot
  masked filling, uniform difference-of-means addition. The composition-only
  boundary (Result 3) is specific to this geometry.
- **Narrow usable dose range.** The eval degenerates at α≥0.35, so PASSes are
  demonstrated at modest strength (α≤0.25), and achievable effect is capped by
  the eval, not necessarily by the direction.
- **Proxies are compositional and non-mechanistic.** A PASS shows the model can
  be pushed toward an amino-acid signature that *correlates* with the property;
  it is not evidence of mechanistic specificity (e.g. preserved active-site
  geometry).
- **Retrospective checks; modest multiplicity control.** Several validity
  checks were clarified after outcomes were seen; bootstrap intervals describe
  stability over the fixed eval proteins, not population guarantees; one matched
  random direction per run. Some legacy runs (L55) omit seed metadata.
- **AMBIGUOUS ≠ negative.** Seed-2 ties on tiny effects (L60, disulfide) are
  resolution limits, not evidence of no effect.

## 8. What this means

For this harness, steerability is **predictable before any GPU work** from the
compositional separation of the vector-building groups, and effect size scales
with it; proxy correlation does not. The method is genuinely useful for
aggregate compositional targets — transmembrane fraction is moved ~72% of the
way to the membrane-protein distribution — and genuinely blind to positional
ones. The productive next steps are therefore not "try more properties" but
(i) position-aware injection to test whether localized features become
reachable, and (ii) wet-lab or structural validation of at least the strongest
compositional gain (transmembrane) to close the gap between a proxy score and a
biological property.

---

### Provenance

Every number above is taken from a committed study record or its result
artifact:

| Claim | Source |
|---|---|
| Acceptance protocol (6 criteria) | `studies/L50_CAPABILITY_GAIN_PROTOCOL.md` |
| Binding null, separation 0.003, proxy *r*=0.80 | `studies/L53_BINDING_STEERING.md`, `plm_steering/l53_repro_out/results.json` |
| Catalytic PASS 3/3, proxy *r*=0.22 | `studies/L54_CATALYTIC_STEERING.md`, `plm_steering/l54_repro_out/` |
| Transmembrane PASS 3/3, 72%, sep 0.086 | `studies/L59_TRANSMEMBRANE_STEERING.md`, `plm_steering/l59_repro_out{,_seed1,_seed2}/` |
| DNA-binding PASS 2/3, 25%, sep 0.039 | `studies/L60_BINDING_XPROT_STEERING.md`, `plm_steering/l60_repro_out{,_seed1,_seed2}/` |
| L61 batch (glyco/disulfide PASS; signal_pep/zinc/calcium KILL) | `studies/L61_CANDIDATE_MINING_BATCH.md`, `plm_steering/l61_*_out/` |
| signal_pep proxy *r*=0.742, sep 0.035, KILL crit 3 | `plm_steering/l61_signal_pep_out/results.json` (verified) |
| Endpoint / denominator / composition / whole-run cases | `studies/L56`, `L52`, `L57`, `L55`; and `papers/icbinb-bio/paper.tex` |

**Relationship to the ICBINB-BIO submission.** The double-blind submission in
`papers/icbinb-bio/` covers the negative-result half (Section 6) as a
standalone failure-modes paper. This synthesis is the fuller arc: the same
validity discipline turned toward a *predictive* account of steerability and its
structural limit. It is a working internal document, not the anonymous
submission; do not link it from review materials.
