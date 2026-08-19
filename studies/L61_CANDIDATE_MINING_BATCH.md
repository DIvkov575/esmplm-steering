# L61 — Candidate mining batch: 5 new targets, config-driven rig

Status: **1 PASS (glycoprotein, 3/3 seeds), 1 weak PASS (disulfide, 2/3),
3 KILL (signal peptide, zinc finger, calcium).** Two mechanistic findings that
sharpen the whole arc.

## Rig

`plm_steering/l61_candidates.py` (proxy registry + candidate table),
`l61_fetch.py` (`CAND=<name>` → `data_cache/l61_<name>/data.json`), and
`l61_run.py` (`CAND=<name> L61_SEED=<n>`) run the identical L42/L54/L59 harness
— same hook, difference-of-means vector, matched-norm random control,
degeneracy filter, paired bootstrap, residue-exclusion, L50 6-criteria verdict,
and the G1 compositional-separation pre-gate. Adding a candidate is now a few
lines, not a hand-cloned file triple. All fine-grid (SAFE_ALPHAS
{0.1,0.15,0.2,0.25}, per the L59 non-degenerate-window lesson).

Candidates were pre-screened offline (no GPU): fetch + proxy correlation +
group separation. Only candidates clearing |r|>=0.15 and separation>=0.02 were
run.

## Seed-0 results (all 5)

| candidate | property | proxy | proxy_r | separation | verdict | failing criterion |
|---|---|---|---|---|---|---|
| glycoprotein | N-X-S/T glycosylation | sequon density | +0.41 | 0.039 | **PASS** | — |
| disulfide | disulfide bonds | Cys fraction | +0.17 | 0.026 | AMBIGUOUS→PASS | crit2 (seed 0 only) |
| signal_pep | N-terminal signal peptide | N-term(30aa) hydropathy | **+0.74** | 0.035 | **KILL** | crit3 |
| zinc_finger | zinc-finger domain | Cys+His | +0.29 | 0.028 | **KILL** | crit1 (anti-correlated) + crit3 |
| calcium | calcium-binding (EF-hand) | Asp+Glu | +0.16 | 0.038 | **KILL** | crit1 (no significant alpha) |

Replicated (seeds 0/1/2):
- **glycoprotein: PASS / PASS / PASS.** Dose monotonic on every seed
  (~0.0005→0.004), residue-exclusion (excl L,S) significant every seed
  (diff 0.0023–0.0032). A genuine, seed-robust capability — but the effect is
  tiny (~0.003 in sequon density), comparable to L60 binding, far below L59
  transmembrane.
- **disulfide: AMBIGUOUS / PASS / PASS.** Seed 0's AMBIGUOUS was crit2 (dose
  hovering at the noise floor, non-monotonic); seeds 1/2 clean. Effect
  ~0.002, at the practical detection limit.

## Finding 1 — separation is NECESSARY but NOT SUFFICIENT

L53–L60 established that near-zero separation guarantees a null. This batch
shows the converse fails: **calcium (separation 0.038, as high as L60 binding)
and signal_pep (0.035) both KILLed.** Separation screens out the L53 failure
mode; it does not predict a pass. Two distinct ways a well-separated candidate
still dies:
- **calcium — crit1:** the acidic (D/E) direction produced no significant
  steering at any safe alpha. A compositionally distinct group whose direction
  the model's residual stream does not act on.
- **signal_pep — crit3:** see Finding 2.

## Finding 2 — the harness steers COMPOSITION, not POSITION

signal_pep is the sharpest result in the batch. It has the **best proxy of any
candidate ever tried** (test r=+0.74) and a textbook-clean dose-response
(0.059→0.100→0.152→0.251 across the safe grid). Yet it **KILLs on criterion 3**:
excluding the top-2 substituted residues (L,S) the effect collapses to
non-significant (diff 0.028, CI crosses 0). The steering vector raises the
N-terminal-window hydropathy purely by dumping bulk hydrophobic residues — it
cannot concentrate them at the N-terminus, which is what actually defines a
signal peptide.

Contrast glycoprotein, which PASSes: its proxy is sequon *density* summed over
the whole sequence, a genuinely aggregate/compositional quantity, and the
mean-pooled steering vector can nudge it.

Conclusion: this activation-steering harness (mean-pooled per-layer
difference-of-means, added uniformly to every position) can only move
**aggregate compositional** properties — transmembrane fraction, catalytic
proxy, DNA-binding charge, glycosylation density. It structurally **cannot
install positionally-localized features** (a signal peptide, and by extension
active-site geometry, domain boundaries, termini-specific motifs). Steering
those would require position-aware injection, not uniform addition — a concrete
methodological next step, not a property-selection problem.

## Standing scoreboard (effect as % of natural low→high gap)

| target | separation | verdict | effect size |
|---|---|---|---|
| L59 transmembrane | 0.086 | PASS 3/3 | 72% (large) |
| L54 catalytic | 0.023–0.045 | PASS 3/3 | (moderate) |
| L60 DNA-binding | 0.039 | PASS 2/3 | 25% (weak) |
| L61 glycoprotein | 0.039 | PASS 3/3 | tiny (~motif density +0.003) |
| L61 disulfide | 0.026 | PASS 2/3 | tiny |
| L61 signal_pep | 0.035 | KILL | positional, not compositional |
| L61 zinc_finger | 0.028 | KILL | direction anti-correlated |
| L61 calcium | 0.038 | KILL | model ignores the direction |
| L53 binding (single-backbone) | 0.0033 | KILL | null (no separation) |

## Reproduce

```
source .venv/bin/activate
CAND=glycoprotein python3 -m plm_steering.l61_fetch
CAND=glycoprotein L61_SEED=0 python3 -m plm_steering.l61_run   # + SEED=1,2
# same for signal_pep, zinc_finger, disulfide, calcium
```
