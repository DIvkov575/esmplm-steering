# Mechanistic Interpretability & Causal Steering on Protein LMs

Eight linked experiments spanning activation steering, unsupervised
feature discovery, and causal ablation on protein language models — one
honest failure, one reproduction that initially looked like a false
positive and wasn't, a caught generalization failure, a falsified
mechanistic hypothesis, a real depth-dependence finding confirmed by two
independent causal methods, unsupervised feature discovery with zero
target property specified, and a 5-year-old correlational finding from
the literature finally tested causally (and it didn't hold up).

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

## Why this repo exists

Every result here was gated by running the actual pipeline on real data,
not by planning or literature review alone — but literature review before
and after each run is what caught the real bugs (SAE normalization in L41;
decoding collapse in L42; a destructive patching design in L47) that would
otherwise have produced confidently-wrong conclusions, and what surfaced
the specific, real, unclaimed gaps this repo goes after (L46's checkpoint
reuse, L48's causal redo of a 2021 finding).

Two patterns run through all eight experiments:
1. **Correlation with a real biological signal does not imply causal
   necessity or steerability.** L41 (SAE feature ↔ kinase activity), L48
   (attention head ↔ contact map) both found real, strong correlations
   that did NOT translate into causal control/necessity when actually
   tested — on two different techniques, two different model families.
2. **Continuous, compositionally-grounded properties steered via
   difference-of-means work; this does not generalize freely** — real for
   thermostability (L42), an artifact for solubility (L43) — **and the
   underlying mechanism is depth-weighted, not localized**, confirmed by
   two independent causal methods (L45's additive steering, L47's
   substitutive patching) converging on the same conclusion.

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
  phage_data.py                shared FASTA parsing / train-eval split utility
  data_cache/pdb_structures/    8 real PDB structures used by L48 (committed, 808K total)
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
tests/                         unit tests for every pure-math module (73 tests, no GPU needed)
fetch_data.sh                  downloads real meltome/solubility/PDB data used by L42/L43/L48
```

## Running it

```bash
pip install -r requirements.txt
pytest tests/ -q                 # 73 tests, pure-math only, no GPU/model download needed
./fetch_data.sh                  # pulls real meltome + solubility CSVs + PDB structures
python -m plm_steering.l42_run_repro   # ESM2-650M steering; picks CUDA > MPS > CPU automatically
python -m plm_steering.l43_run_repro   # same, solubility target
python -m plm_steering.l46_run_discovery         # unsupervised SAE discovery, no GPU-free download needed
python -m plm_steering.l47_task_b_patching_validation  # patching validation vs. L42
python -m plm_steering.l48_run_replication       # Vig et al. correlation, real PDB structures
python -m plm_steering.l48_run_causal_ablation   # the actual causal test
```

Both run scripts auto-select `cuda`, falling back to Apple Silicon `mps`,
falling back to plain `cpu`. The committed results in this repo were
produced on an A10G (L42's original run) and on an M3 Pro via MPS (L42's
rerun + L43) — the MPS rerun of L42 reproduced the A10G numbers exactly,
confirming MPS is a valid substitute for this workload.

**Important: do not trust the `"decision"` field inside either
`*_repro_results.json` at face value.** That field only checks "did any
alpha clear statistical significance" — it does NOT run the residue-
exclusion robustness check that caught L43's false positive (see
`docs/L43_SOLUBILITY_STEERING.md`). Always read the doc's own stated
verdict, not the JSON's `decision` key, for the actual conclusion.

L41's scripts additionally require `esm` (EvolutionaryScale's ESM-C client)
and the kinase-positive/negative FASTA files referenced in
`docs/L41_PROTOCOL.md` (not included here — see that doc for the exact
UniProt query used to regenerate them).

## What this is NOT

Not a claim that activation steering is a solved technique for protein
design, and not a paper-ready result on its own — L42's reproduction
validates the harness, it doesn't establish a new scientific finding about
thermostability. Read each doc's own "what this is / is not" section before
citing a number from it.
