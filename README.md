# PLM Activation Steering: What Works, What Doesn't, and Why

Three linked experiments on causally steering protein language models via
inference-time activation addition (no retraining) — one honest failure,
one reproduction that initially looked like a false positive and wasn't,
and one generalization check that found a second, different false positive
and correctly did not report it as a win.

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

## Why this repo exists

Every result here was gated by running the actual pipeline on real data,
not by planning or literature review alone — but literature review before
and after each run is what caught the two real bugs (SAE normalization in
L41; decoding collapse in L42) that would otherwise have produced
confidently-wrong conclusions. The clearest pattern across L41-L43:
**continuous, compositionally-grounded target properties on a mid-size
model, steered with a difference-of-means vector, are the one recipe that
reliably works** — discrete functional classes and raw SAE decoder
directions are not, and this does NOT generalize to every continuous
property either (L43). L44-L45 dig one level deeper into WHY and WHERE the
working case (L42) actually works mechanistically, rather than treating it
as a black box that either does or doesn't fire.

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
  phage_data.py                shared FASTA parsing / train-eval split utility
docs/
  L41_PROTOCOL.md              full L41 gate-by-gate protocol + results
  L41_PAPER_ANALYSIS.md        direct reading of the ESM-C source paper vs. what L41 tested
  L42_STEERING_REPRO.md        full L42 protocol, the false-positive catch, final results
  L43_SOLUBILITY_STEERING.md   full L43 protocol, run on Apple Silicon MPS, AMBIGUOUS result
  L44_LOGIT_LENS_DIAGNOSTIC.md full L44 method (incl. 2 bugs found/fixed) + falsification
  L45_LAYER_SWEEP.md            full L45 method, results, and the norm-confound check
tests/                         unit tests for every pure-math module (56 tests, no GPU needed)
fetch_data.sh                  downloads the real meltome/solubility datasets used by L42/L43
```

## Running it

```bash
pip install -r requirements.txt
pytest tests/ -q                 # 52 tests, pure-math only, no GPU/model download needed
./fetch_data.sh                  # pulls real meltome + solubility CSVs (~35MB total)
python -m plm_steering.l42_run_repro   # ESM2-650M steering; picks CUDA > MPS > CPU automatically
python -m plm_steering.l43_run_repro   # same, solubility target
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
