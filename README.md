# PLM Activation Steering: What Works, What Doesn't, and Why

Three linked experiments on causally steering protein language models via
inference-time activation addition (no retraining) — one honest failure,
one reproduction that initially looked like a false positive and wasn't,
and one generalization check currently blocked on infrastructure, not on
methodology.

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
  (solubility)? Code complete, GPU run pending.** Same validated recipe
  (model, vector construction, degeneracy filter, significance test), new
  dataset and scoring function only. See
  [`docs/L43_SOLUBILITY_STEERING.md`](docs/L43_SOLUBILITY_STEERING.md) for
  the pre-registered protocol and current status.

## Why this repo exists

Every result here was gated by running the actual pipeline on real data,
not by planning or literature review alone — but literature review before
and after each run is what caught the two real bugs (SAE normalization in
L41; decoding collapse in L42) that would otherwise have produced
confidently-wrong conclusions. The pattern that emerges across all three:
**continuous, compositionally-grounded target properties on a mid-size
model, steered with a difference-of-means vector, are the one recipe that
reliably works** — discrete functional classes and raw SAE decoder
directions are not, independent of how carefully the rest of the pipeline
is built.

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
  phage_data.py                shared FASTA parsing / train-eval split utility
docs/
  L41_PROTOCOL.md              full L41 gate-by-gate protocol + results
  L41_PAPER_ANALYSIS.md        direct reading of the ESM-C source paper vs. what L41 tested
  L42_STEERING_REPRO.md        full L42 protocol, the false-positive catch, final results
  L43_SOLUBILITY_STEERING.md   pre-registered L43 protocol + current (blocked) status
tests/                         unit tests for every pure-math module (52 tests, no GPU needed)
fetch_data.sh                  downloads the real meltome/solubility datasets used by L42/L43
```

## Running it

```bash
pip install -r requirements.txt
pytest tests/ -q                 # 52 tests, pure-math only, no GPU/model download needed
./fetch_data.sh                  # pulls real meltome + solubility CSVs (~35MB total)
python -m plm_steering.l42_run_repro   # needs a CUDA GPU; ESM2-650M auto-downloads via transformers
python -m plm_steering.l43_run_repro   # same, solubility target
```

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
