# Causal Steering of Protein Language Models

Workshop submission packages and backing research for "Causal Steering
of Protein Language Models: When Correlational Validation Fails, and How
to Catch It."

## Submissions (deadline: Aug 29, 2026, AoE)

Three venue-specific, compiled, anonymized packages ready for upload:

| Venue | Path | Pages | Template |
|---|---|---|---|
| **ICBINB-BIO** (Failure Modes of AI in Biology) | [`docs/submissions/icbinb-bio/`](docs/submissions/icbinb-bio/) | 6/8 | NeurIPS 2026 dblblindworkshop |
| **Interp4Discovery** (Interpretability for Discovery) | [`docs/submissions/interp4discovery/`](docs/submissions/interp4discovery/) | 4/5 | NeurIPS 2026 dblblindworkshop |
| **XAI4Science** (Knowledge Discovery and Trust) | [`docs/submissions/xai4science/`](docs/submissions/xai4science/) | 6/8 | NeurIPS 2026 dblblindworkshop |

All three are non-archival; acceptance does not prevent later archival
publication (e.g., ICML 2027).

## Backing research

The code, data, and results backing every number in the papers:

- **L42** — thermostability steering baseline (Huang et al. 2025 reproduction)
- **L48/L49** — component-level evidence (Vig et al. attention-head causal
  ablation, full 480-head sweep)
- **L50** — pre-registered 6-criterion protocol
- **L51–L57** — the 5-target sweep (binding affinity KILL, catalytic activity
  PASS, intrinsic disorder PASS*, immunogenicity KILL pre-run, expression
  yield AMBIGUOUS)
- **L58** — cross-target steering-vector geometry cross-check (explains L57's
  AMBIGUOUS result as a geometric echo of L55's validated disorder direction)

## Running

```bash
pip install -r requirements.txt
pytest tests/ -q    # 113 tests, pure-math only, no GPU needed
```

Run scripts require ESM2-650M (auto-selects CUDA > MPS > CPU):
```bash
python -m plm_steering.l54_run_repro   # catalytic activity (PASS)
python -m plm_steering.l55_run_repro   # intrinsic disorder (PASS*)
python -m plm_steering.l53_run_repro   # binding affinity (KILL)
python -m plm_steering.l57_run_repro   # expression yield (AMBIGUOUS)
python -m plm_steering.l56_immunogenicity_proxy_validation  # proxy-only (KILL)
python -m plm_steering.l58_vector_geometry_crosscheck  # cross-target cosine similarity
```

One-time data fetches (already run; outputs committed):
```bash
python -m plm_steering.l56_fetch_tier2_and_allergen_data  # Tier-2 + allergen-check data
```

## Source draft and figures

[`docs/workshop_paper/`](docs/workshop_paper/) — the generic-template draft
all three venue submissions derive from, with `make_figures.py` regenerating
every figure directly from the committed `results.json` files.
