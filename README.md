# Mechanistic Interpretability & Causal Steering on Protein LMs

Sixteen linked experiments spanning activation steering, unsupervised
feature discovery, and causal ablation on protein language models. The
throughline that survives all sixteen: **correlation with a real
biological signal does not predict causal effect** — shown first at the
level of individual model components (an attention head's correlation
with real contacts vs. its actual ablation effect, L48/L49), then at the
level of entire target properties (a scoring proxy's correlation with
real experimental labels vs. whether steering toward it actually works,
L53 vs. L54). The two clean new-property capability gains found here
(L54 catalytic activity, L55 intrinsic disorder) came from a systematic
5-target sweep run under one pre-registered protocol (L50) that caught
two of its own near-misses in real time — a spurious PASS from
comparing arms at an unsafe alpha (L52), and a seed-sensitive artifact
check that only 2 of 3 seeds actually clear (L55) — before either could
be reported as a clean result.

A workshop paper draft synthesizing the L48/L49 component-level finding
and the L50-L57 property-level sweep into one submission is at
[`docs/workshop_paper/paper.tex`](docs/workshop_paper/paper.tex)
([PDF](docs/workshop_paper/paper.pdf)).

**Headline findings:**

- **L41 — kinase-activity steering on ESM-C, using a raw SAE decoder
  direction: a real, expected null.** After finding and fixing a genuine
  bug (missing Z-score normalization of SAE inputs, which changed the
  winning feature), the corrected result was a weak, inconsistent signal
  (0.12–1.08 baseline SE, not independently significant). A dedicated
  literature check afterward found this exact combination — small model +
  discrete function class + raw SAE feature — has never been shown to work
  by anyone in this field, and predicted failure for reasons independent of
  this project's execution. See [`docs/L41_PROTOCOL.md`](docs/L41_PROTOCOL.md)
  and [`docs/L41_PAPER_ANALYSIS.md`](docs/L41_PAPER_ANALYSIS.md).
- **L42 — reproducing Huang et al.'s thermostability steering
  (arXiv:2509.07983) on ESM2-650M: real effect, confirmed after catching a
  false positive.** A difference-of-means steering vector correctly
  encodes real thermostability biology (IVYWREL enrichment, the classic
  Arg-for-Lys salt-bridge swap) — but naive single-shot generation collapses
  into a poly-leucine artifact at higher steering strength, which fooled two
  different scoring metrics in turn before being caught by direct inspection
  of the generated sequences. After filtering degenerate output and
  rescoring with an independent compositional marker, the real steering
  direction significantly beats a matched-norm random control at low alpha
  (0.1–0.5), with a clean monotonic dose-response on 57–58 of 60 held-out
  sequences. See [`docs/L42_STEERING_REPRO.md`](docs/L42_STEERING_REPRO.md).
- **L43 — does the L42 reproduction generalize to a second target
  (solubility)? AMBIGUOUS — a second artifact, caught before being reported
  as a win.** Same validated recipe (model, vector construction, degeneracy
  filter, significance test), new dataset (real soluble/insoluble labels)
  and scoring function (GRAVY hydropathy) only. Run on Apple Silicon via
  PyTorch MPS after AWS credentials for the original GPU host expired
  (verified MPS reproduces L42's result bit-for-bit first). The one alpha
  that cleared statistical significance did so in the *wrong direction* and
  the effect vanished entirely once the dominant substituted residues
  (alanine/glycine) were excluded from scoring — the same category of
  compositional artifact as L42's leucine collapse, this time correctly
  identified rather than reported as a pass. See
  [`docs/L43_SOLUBILITY_STEERING.md`](docs/L43_SOLUBILITY_STEERING.md) for
  the full pre-registered protocol and the residue-exclusion diagnostic.
- **L44 — is the over-steering collapse residue predictable in advance
  from the steering vector itself (logit-lens style)? Falsified.** Neither
  L42's leucine collapse nor L43's alanine/glycine collapse shows up as the
  dominant single-layer projection of its steering vector, even after
  fixing two real bugs in the check (wrong projection path; outlier
  embedding norms on non-standard residue tokens fooling raw dot product).
  Real negative result: collapse looks like a decoding-dynamics effect
  (compounding across layers during iterative generation), not something
  visible in a static per-layer projection. See
  [`docs/L44_LOGIT_LENS_DIAGNOSTIC.md`](docs/L44_LOGIT_LENS_DIAGNOSTIC.md).
- **L45 — which layers are actually doing the causal work in L42's
  validated steering vector? Distributed but depth-weighted.** Steered
  each of ESM2-650M's 33 layers individually (not all-at-once, as L42
  does) at the same eval sequences/alpha/scorer. 30 of 33 layers show a
  positive real-vs-random effect direction (binomial sign test
  p=0.000001 against a 50/50 null) — not concentrated in 2-3 special
  layers, but effect size triples from early to late layers, with layer
  31 standing out at ~7x the mean of the others. Checked directly against
  a vector-norm-renormalization confound (relative perturbation strength
  is flat across layers, NOT correlated with effect size) before trusting
  the depth trend. See [`docs/L45_LAYER_SWEEP.md`](docs/L45_LAYER_SWEEP.md).
- **L46 — unsupervised feature discovery: no target property specified at
  all, until characterization afterward.** Everything above requires
  picking a property before running anything. This uses InterPLM's
  published pretrained sparse autoencoders (real HuggingFace checkpoints,
  not vendored — reimplemented the ~15-line architecture from the actual
  checkpoint's tensor shapes) to decompose ESM2-650M activations into
  10,240 individually-interpretable directions with zero label involved.
  Ranked by a label-free selectivity score; only checked top features
  against real Tm labels AFTER discovery (2 weak, not-Bonferroni-
  significant hits — a lead, not a finding). See
  [`docs/L46_SAE_FEATURE_DISCOVERY.md`](docs/L46_SAE_FEATURE_DISCOVERY.md).
- **L47 — activation PATCHING (substitution), not steering (addition):
  Task B validates the method, converges with L45's independent finding.**
  Feasibility confirmed directly (head-level slicing recoverable from
  ESM2's merged attention output). Found and fixed a real destructive-
  patching bug first (broadcasting to every token position collapsed
  100% of generations at every layer). Fixed version: 27/31 layers show a
  positive effect (sign test p=0.000034), effect size ~13x larger in
  layers 22-30 — a genuinely different causal method (substitution, not
  addition) converging with L45's steering-based depth-weighting finding.
  See [`docs/L47_ACTIVATION_PATCHING.md`](docs/L47_ACTIVATION_PATCHING.md).
- **L48 — Task A: redo a 5-year-old correlational finding as a real causal
  test.** Vig et al. 2021 found attention heads in protein LMs that
  strongly align with real 3D contacts, but stated explicitly this was
  "purely associative" — never tested causally, and (confirmed via
  dedicated literature search) nobody has since. Replicated the
  correlation cleanly on 8 real PDB structures (layer 5 head 13: 12.9x
  enrichment over background). Then ablated that head and measured real
  masked-residue prediction accuracy at contact-bearing positions: **no
  significant causal effect**, statistically indistinguishable from
  ablating a genuine low-enrichment control head. A second, independent
  data point (different model family, different technique) for this
  repo's recurring lesson: correlation with a real biological signal
  does not imply causal necessity. See
  [`docs/L48_VIG_CAUSAL_TEST.md`](docs/L48_VIG_CAUSAL_TEST.md).
- **L49 — unsupervised causal candidate generation: ablate all 480 heads,
  rank by actual effect, zero correlation involved. The rankings invert.**
  Answers the open question after L48 (was Vig's pick just unlucky?) by
  skipping correlation-based candidate selection entirely — ablate every
  head in ProtBert-BFD, score each directly by causal effect on the same
  task. Vig's correlational #1 pick (12.9x contact enrichment) ranks
  **313th of 480** by real causal effect; L48's "least important"
  correlational control ranks **80th of 480** — genuinely more causally
  important than the head correlation says matters most. Also found real
  redundancy (166/480 heads show exactly zero ablation effect). Third
  independent instance of this repo's core lesson, and the most thorough
  one — a full 480-head sweep, not one hand-picked test. See
  [`docs/L49_UNSUPERVISED_CAUSAL_SWEEP.md`](docs/L49_UNSUPERVISED_CAUSAL_SWEEP.md).
- **L50 — a pre-registered 6-criterion protocol for calling a capability
  gain real, locked before any of L51-L57 ran.** Every prior new-target
  attempt (L41 kinase, L43 solubility) either failed cleanly or fooled a
  naive check first — this writes down in advance what would count as a
  real PASS (beats a matched-norm random control with a real CI;
  dose-response across >=3 alphas; survives residue-exclusion; proxy
  validated against real labels BEFORE the run; beats the best known
  technique where one exists; n>=150 for a new property) so the next 7
  results are judged against a rule fixed before they were seen, not
  after. See [`docs/L50_CAPABILITY_GAIN_PROTOCOL.md`](docs/L50_CAPABILITY_GAIN_PROTOCOL.md).
- **L51 — aggregation resistance: the script's own "PASS" is wrong; the
  real verdict is KILL.** Net-charge proxy validated at r=+0.20. Only
  alpha=1.0 clears significance, and that's exactly the alpha where 1/3
  of the eval set has already collapsed into degenerate output — no
  dose-response across the safe range, the same "one lucky unsafe alpha"
  shape that later produced (and got caught fixing) L52's bug. See
  [`docs/L51_AGGREGATION_STEERING.md`](docs/L51_AGGREGATION_STEERING.md).
- **L52 — does the 5 layers L45 found causally necessary for
  thermostability steering preserve the full-33-layer effect on their
  own? AMBIGUOUS, and a self-caught bug on the way to that answer.** A
  first draft's alpha-selection logic let `best_alpha` range into the
  harness's known-unsafe alpha>=1.0 regime and produced a spurious PASS,
  purely because the two arms being compared collapsed into degenerate
  output at different rates, not from any real advantage — caught,
  fixed, and rerun end to end rather than patched post hoc. The corrected
  result: the 5-layer subset genuinely steers (passes 5 of 6 criteria)
  but retains only ~43-59% of the full 33-layer effect size at every
  alpha where both are trustworthy — real, not equivalent. See
  [`docs/L52_LAYER_SUBSET_STEERING.md`](docs/L52_LAYER_SUBSET_STEERING.md).
- **L53 — binding affinity: the single sharpest data point in this repo
  for "proxy validity does not predict causal steerability."** The most
  rigorously validated proxy of any target ever attempted here (r=0.80-0.81
  held-out, confirmed with a weight-shuffle null control, held-out-position
  generalization, and mutational-load extrapolation — a memorization
  candidate that scored even higher, r=0.85, was explicitly rejected for
  not generalizing). The steering effect is a flat, unambiguous null at
  every alpha. A follow-up compositional-distance check found this
  target's vector-building low/high groups (single-backbone DMS point
  mutants) differ 10x less in raw amino-acid composition than the
  cross-protein datasets L54/L55/L57 use — a plausible mechanistic reason,
  not just an anticlimax. See [`docs/L53_BINDING_STEERING.md`](docs/L53_BINDING_STEERING.md).
- **L54 — catalytic activity (kcat): the first genuinely new-property
  capability gain in this whole arc, replicated on 3/3 independent
  seeds.** Glycine-minus-arginine compositional proxy (r=+0.22, the
  WEAKEST of the four runnable targets in this batch) produces a clean,
  monotonic, residue-exclusion-robust steering effect — significant at
  every safe alpha, on every one of 3 seeds tried. Directly falsifies
  "just use the best-validated proxy": L53's proxy is 4x stronger and
  steers nothing. See [`docs/L54_CATALYTIC_STEERING.md`](docs/L54_CATALYTIC_STEERING.md).
- **L55 — intrinsic disorder: a real, directionally-robust effect whose
  artifact-robustness check is itself seed-sensitive (2 of 3).** TOP-IDP
  proxy (r=+0.449, strongest of any target attempted) produces a
  significant, dose-responsive effect on all 3 independent seeds — but
  the residue-exclusion check that rules out pure compositional collapse
  passes on 2 of 3 (36-42% of magnitude retained) and fails on the third
  (10% retained, CI crosses zero). A concrete demonstration that
  different criteria in the same protocol can have different
  seed-sensitivity, not something a single run would ever reveal. See
  [`docs/L55_DISORDER_STEERING.md`](docs/L55_DISORDER_STEERING.md).
- **L56 — immunogenicity: killed at the proxy gate, by design, before any
  model run.** Four evaluation tiers (peptide binding affinity -> mass-spec
  presentation -> real T-cell response -> full-length antigens) show
  proxies that look strong on the binding-affinity surrogate (r=+0.37)
  collapse to near-chance on the REAL endpoint (T-cell response, r=+0.10)
  and flip sign on full-length antigens once a source-organism confound
  (58% of the apparent signal) is held out of cross-validation. No
  `l56_*_steering.py` exists — the intended outcome, not missing work.
  See [`docs/L56_IMMUNOGENICITY_KILLED.md`](docs/L56_IMMUNOGENICITY_KILLED.md).
- **L57 — expression yield: AMBIGUOUS, explained (not just observed) as a
  geometric echo of L55's real disorder direction.** Absolute-charge-average
  proxy (r=+0.31-0.34, a genuinely distinct dataset from L43's earlier
  solubility target, verified uncorrelated on their 441 overlapping
  sequences) produces a significant, dose-responsive effect that
  completely evaporates under residue-exclusion. Rather than leaving that
  as an unexplained artifact, a steering-vector cosine-similarity check
  against every other target found +0.30 overall similarity to L55's
  vector (rising to +0.40-0.50 at the deepest layers) — this result is
  best read as disorder's already-real effect leaking through a weaker,
  more collapse-prone proxy, not independent evidence of a 6th steerable
  property. See [`docs/L57_EXPRESSION_STEERING.md`](docs/L57_EXPRESSION_STEERING.md).

## Why this repo exists

Every result here was gated by running the actual pipeline on real data,
not by planning or literature review alone — but literature review before
and after each run is what caught the real bugs (SAE normalization in L41;
decoding collapse in L42; a destructive patching design in L47) that would
otherwise have produced confidently-wrong conclusions, and what surfaced
the specific, real, unclaimed gaps this repo goes after (L46's checkpoint
reuse, L48's causal redo of a 2021 finding).

Three patterns run through all sixteen experiments:
1. **Correlation with a real biological signal does not imply causal
   necessity, at the level of individual model components.** L41 (SAE
   feature ↔ kinase activity), L48 (attention head ↔ contact map, one
   head) and L49 (all 480 heads, ranked purely causally — Vig's
   correlational #1 pick ranks 313th of 480 by actual effect) all found
   real, strong correlations that did NOT translate into causal
   control/necessity when actually tested.
2. **Continuous, compositionally-grounded properties steered via
   difference-of-means work; this does not generalize freely** — real for
   thermostability (L42) and, in the L50-L57 batch, catalytic activity
   (L54) and (with a caveat) intrinsic disorder (L55); an artifact for
   solubility (L43), aggregation (L51), and expression yield (L57); a
   clean null for binding affinity (L53); killed before any run for
   immunogenicity (L56) — **and the underlying mechanism is
   depth-weighted, not localized**, confirmed by two independent causal
   methods (L45's additive steering, L47's substitutive patching)
   converging on the same conclusion.
3. **Correlation strength does not predict causal steerability, at the
   level of an entire target property — not even weakly.** L53's proxy
   (r=0.80, the strongest validated in this repo) steers nothing; L54's
   proxy (r=0.22, the weakest of the four runnable targets in that batch)
   produces a clean, 3-seed-replicated effect. This is the same lesson as
   (1), one level up: a component-level or property-level correlation is
   evidence about the model's REPRESENTATIONS, not about what happens
   when you actually intervene.

## Repo layout

```
plm_steering/
  l41_steering.py            pure-math: Cohen's d feature search, SAE encode/decode,
                              Z-score normalization, Gate-1 decision rule
  l41_run_gate1.py            ESM-C + SAE feature search (kinase vs. non-kinase)
  l41_run_gate2.py            steering + generation under the winning feature
  l41_run_gate3.py            independent classifier eval of steered output
  l42_steering_repro.py       pure-math: difference-of-means vectors, degeneracy
                              filter, IVYWREL/instability-index scorers, paired
                              bootstrap significance test
  l42_run_repro.py             ESM2-650M steering + generation + verdict (thermostability)
  l43_solubility_steering.py  pure-math: GRAVY hydropathy solubility proxy
  l43_run_repro.py             ESM2-650M steering + generation + verdict (solubility)
  l43_repro_results.json       full L43 run output (real, GRAVY-based, AMBIGUOUS result)
  l42_repro_results.json       full L42 run output (real, IVYWREL-based, PASS result)
  l44_logit_lens_diagnostic.py cosine-similarity projection of a steering vector onto
                                the model's own embedding matrix, restricted to standard AAs
  l44_logit_lens_out.json      full L44 output (falsified: collapse residue not predictable)
  l45_layer_sweep.py            single-layer causal-sufficiency sweep, reuses L42's vectors/data
  l45_layer_sweep_out.json      full L45 output (30/33 layers positive, depth-weighted effect)
  l46_sae_feature_discovery.py  minimal ReLUSAE reimplementation + InterPLM checkpoint loader
  l46_run_discovery.py           unsupervised discovery on 100 real sequences, layer 24
  l46_discovery_out.json         top-15 selective features + post-hoc Tm-correlation check
  l47_activation_patching.py    generic patching harness: PatchTarget, cache/patch hooks,
                                 head-level slicing (verified against ESM2's merged attention)
  l47_task_b_patching_validation.py  masked-position patching, validated against L42
  l47_task_b_out.json            full Task B output (27/31 layers positive, sign test p=0.000034)
  l48_vig_contact_heads.py      pure-math: PDB contact-map extraction, head-enrichment scoring
  l48_run_replication.py        Stage 1: replicate Vig et al.'s correlation on 8 real structures
  l48_run_causal_ablation.py    Stage 2: real causal ablation test (paired bootstrap)
  l48_replication_out.json       full head-enrichment matrix, all 30 layers x 16 heads
  l48_causal_ablation_out.json   full causal-ablation results, per-structure + pooled
  l49_unsupervised_causal_sweep.py  ablate ALL 480 heads, rank by real causal effect
  l49_causal_sweep_out.json      full 480-head ranking + Vig-pick vs. control cross-check
  l51_aggregation_steering.py   pure-math: net-charge aggregation-resistance proxy
  l51_run_repro.py                ESM2-650M steering run (aggregation) -- KILL, script's own "PASS" is wrong
  l52_layer_subset_causal_steering.py  layer-subset (18/23/25/30/31) vs all-33-layer head-to-head
  l53_binding_affinity_steering.py  pure-math: mutational-sensitivity-weighted wildtype preservation
  l53_run_repro.py                 ESM2-650M steering run (binding) -- KILL despite r=0.80 proxy
  l54_catalytic_activity_steering.py  pure-math: glycine-minus-arginine proxy
  l54_run_repro.py                  ESM2-650M steering run (catalytic activity) -- PASS, 3/3 seeds
  l55_disorder_steering.py         pure-math: TOP-IDP disorder-propensity proxy
  l55_run_repro.py                   ESM2-650M steering run (disorder) -- PASS 2/3 seeds on robustness
  l56_immunogenicity_proxy_validation.py  4-tier proxy validation -- KILL before any model run
  l57_expression_yield_steering.py  pure-math: absolute-charge-average proxy
  l57_run_repro.py                   ESM2-650M steering run (expression yield) -- AMBIGUOUS
  l57_validate_proxy.py              eSol fetch + proxy pre-validation, standalone from the run script
  phage_data.py                shared FASTA parsing / train-eval split utility
  data_cache/pdb_structures/    8 real PDB structures used by L48/L49 (committed, 808K total)
  data_cache/{aggregation,binding,catalytic,disorder,expression}/  real datasets for L51/L53-L55/L57
                                (committed, ~19M total -- see each dataset's source in its doc)
  data_cache/immunogenicity/    L56's real IEDB/DisProt-scale data, ~15M committed (the one large
                                file, iedb_tcell_mhcii.json, is gzip-compressed 53M->3M; loaded
                                transparently by load_tcell_records())
docs/
  L41_PROTOCOL.md              full L41 gate-by-gate protocol + results
  L41_PAPER_ANALYSIS.md        direct reading of the ESM-C source paper vs. what L41 tested
  L42_STEERING_REPRO.md        full L42 protocol, the false-positive catch, final results
  L43_SOLUBILITY_STEERING.md   full L43 protocol, run on Apple Silicon MPS, AMBIGUOUS result
  L44_LOGIT_LENS_DIAGNOSTIC.md full L44 method (incl. 2 bugs found/fixed) + falsification
  L45_LAYER_SWEEP.md            full L45 method, results, and the norm-confound check
  L46_SAE_FEATURE_DISCOVERY.md  full L46 method, checkpoint verification, discovery results
  L47_ACTIVATION_PATCHING.md    full L47 plan, Phase 0 feasibility, Task B validation
  L48_VIG_CAUSAL_TEST.md        full L48 Stage 1 replication + Stage 2 causal test
  L49_UNSUPERVISED_CAUSAL_SWEEP.md  full L49 method, results, and the rank cross-check
  L50_CAPABILITY_GAIN_PROTOCOL.md   the pre-registered 6-criterion protocol L51-L57 are judged against
  L51_AGGREGATION_STEERING.md       full L51 method + why the script's own "PASS" is wrong
  L52_LAYER_SUBSET_STEERING.md      full L52 method, the caught alpha-selection bug, AMBIGUOUS result
  L53_BINDING_STEERING.md           full L53 method, proxy validation, and the compositional-distance hypothesis
  L54_CATALYTIC_STEERING.md         full L54 method, results, and the 3-seed replication table
  L55_DISORDER_STEERING.md          full L55 method, results, and the seed-sensitive robustness table
  L56_IMMUNOGENICITY_KILLED.md      full L56 4-tier proxy validation and the organism-confound catch
  L57_EXPRESSION_STEERING.md        full L57 method and the vector-geometry explanation via L55
tests/                         unit tests for every pure-math module (145 tests, no GPU needed)
fetch_data.sh                  downloads real meltome/solubility/PDB data used by L42/L43/L48/L49
```

## Running it

```bash
pip install -r requirements.txt
pytest tests/ -q                 # 145 tests, pure-math only, no GPU/model download needed
./fetch_data.sh                  # pulls real meltome + solubility CSVs + PDB structures
python -m plm_steering.l42_run_repro   # ESM2-650M steering; picks CUDA > MPS > CPU automatically
python -m plm_steering.l43_run_repro   # same, solubility target
python -m plm_steering.l46_run_discovery         # unsupervised SAE discovery, no GPU-free download needed
python -m plm_steering.l47_task_b_patching_validation  # patching validation vs. L42
python -m plm_steering.l48_run_replication       # Vig et al. correlation, real PDB structures
python -m plm_steering.l49_unsupervised_causal_sweep  # ablate all 480 heads, ~30min on Apple Silicon
python -m plm_steering.l48_run_causal_ablation   # the actual causal test

# L50-L57 (requires ./fetch_data.sh first for L52's meltome dependency; all
# other L51-L57 data is committed directly, no fetch needed)
python -m plm_steering.l51_run_repro   # aggregation resistance -- KILL (script's decision field is wrong, see doc)
python -m plm_steering.l52_layer_subset_causal_steering  # layer-subset vs all-33-layer, thermostability
python -m plm_steering.l53_run_repro   # binding affinity -- KILL despite r=0.80 proxy
python -m plm_steering.l54_run_repro   # catalytic activity -- PASS
python -m plm_steering.l55_run_repro   # intrinsic disorder -- PASS (2/3 seeds on residue-robustness)
python -m plm_steering.l56_immunogenicity_proxy_validation  # proxy-only, no steering run -- KILL, by design
python -m plm_steering.l57_run_repro   # expression yield -- AMBIGUOUS
```

Both run scripts auto-select `cuda`, falling back to Apple Silicon `mps`,
falling back to plain `cpu`. The committed results in this repo were
produced on an A10G (L42's original run) and on an M3 Pro via MPS (L42's
rerun + L43) — the MPS rerun of L42 reproduced the A10G numbers exactly,
confirming MPS is a valid substitute for this workload.

**Important: do not trust the `"decision"` field inside any
`*_repro_out/results.json` at face value.** L43's and L51's naive
`"decision"` fields only check "did any alpha clear statistical
significance," which does NOT run the residue-exclusion robustness check
that would have caught both false positives (L43's alpha=2.0, L51's
alpha=1.0 — both outside the harness's known-safe range). L52-L57's
scripts compute a more complete `verdict.criteria` block that DOES check
residue-exclusion, but even that only reports what it was told to check —
it can still miss a seed-sensitivity issue like L55's (see that doc).
Always read the doc's own stated verdict, not any JSON `decision`/`verdict`
key in isolation, for the actual conclusion.

L41's scripts additionally require `esm` (EvolutionaryScale's ESM-C client)
and the kinase-positive/negative FASTA files referenced in
`docs/L41_PROTOCOL.md` (not included here — see that doc for the exact
UniProt query used to regenerate them).

## What this is NOT

Not a claim that activation steering is a solved technique for protein
design. Not a claim about biological causality — every "causal" result
here is causal about the MODEL's activation space (a real intervention on
the forward pass, with matched-norm random-direction controls and
residue-exclusion checks), not verified against a real wet-lab assay that
a generated, steered sequence actually has the intended property. Not a
claim that any single result here should be trusted from one run alone —
L52 and L55 are direct, documented demonstrations of why (a caught
alpha-selection bug and a seed-sensitive criterion, respectively). Read
each doc's own "what this is / is not" section before citing a number
from it.
