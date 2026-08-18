# L57 — Expression Yield Steering: AMBIGUOUS, explained as a geometric echo of L55's disorder direction

**Pre-registered against `studies/L50_CAPABILITY_GAIN_PROTOCOL.md`'s 6
criteria.** One of 5 parallel new-target attempts. The naive real-vs-random
result looks like a clean PASS through criteria 1-2, but fails
residue-exclusion (criterion 3) — and a follow-up vector-geometry check
explains *why*: this target's steering vector is not independent of L55's
(disorder) validated real direction.

## Data and proxy

eSol (Niwa et al. 2009, PNAS — chaperone-free PURE cell-free translation of
the E. coli ORFeome), via HuggingFace `AI4Protein/eSOL`. 3101 distinct
E. coli proteins, continuous label in [0,1] = soluble fraction of expressed
protein; 2337 after length<=400 filtering. Verified genuinely distinct from
L43's cached solubility dataset (441 overlapping sequences, but the two
labels are uncorrelated on that overlap, point-biserial r=0.048, p=0.32) —
same word "solubility," statistically orthogonal measurement.

Proxy: absolute charge average, `|(K+R)-(D+E)| / length`. Validated at
r=+0.305 (full set, n=2337) / +0.337 (held-out test, n=228) — one of the two
terms in Wilkinson & Harrison's (1991) published recombinant-solubility
discriminant, not a formula invented for this project. Confirmed NOT
hydrophobicity in disguise (r=-0.17 against GRAVY, L43's disqualified
proxy) and near-orthogonal to L51's signed net-charge proxy (r=-0.001) —
this asks "how far from neutral," not "which way."

## Steering results

| alpha | real mean | random mean | diff | significant | n | degenerate (real) |
|---|---|---|---|---|---|---|
| 0.1 | 0.0324 | 0.0305 | +0.0018 | **yes** | 141 | 7/150 |
| 0.25 | 0.0350 | 0.0305 | +0.0039 | **yes** | 140 | 9/150 |
| 0.5 | 0.0426 | 0.0303 | +0.0125 | **yes** | 138 | 11/150 |
| 1.0 | 0.0767 | 0.0307 | +0.0414 | yes | 108 | 40/150 |
| 2.0 | 0.1011 | 0.0301 | +0.0911 | yes | 78 | 62/150 |
(baseline mean 0.0304, n=150, 7/150 degenerate)

Significant and monotonic across the entire safe range (+0.0018 -> +0.0039
-> +0.0125) — by criteria 1-2 alone, this looks identical in shape to
L54's clean PASS.

**Residue-exclusion robustness (criterion 3): FAILS.** Dominant substituted
residues at alpha=0.5 are E and L (E is literally one of the proxy's own
four terms — `|(K+R)-(D+E)|` — the same strictness level as L54's G-vs-A
check). Excluding both: effect collapses from +0.0125 to +0.0003, CI
[-0.0028, 0.0035] — crosses zero, not significant. Essentially all of the
apparent effect evaporates once its own defining residue is removed. This
is the same composition-collapse-artifact shape as L42 v1's poly-leucine
false positive and L51's alpha=1.0 spike, not a genuine broad steering
effect.

## Why: vector-geometry check against L55 (disorder)

Rather than leaving this as an unexplained artifact, rebuilt L54, L55, and
L57's SEED=0 steering vectors from scratch (`plm_steering/l58_vector_geometry_crosscheck.py`,
runnable, saves both the per-layer vectors and this table to
`plm_steering/l58_vector_geometry_out/`) and computed cosine similarity
between every pair, per-layer and on the full 33-layer concatenation:

| comparison | full-vector cosine | deep layers (30-32) |
|---|---|---|
| L57 (expression) vs. L54 (catalytic) | -0.127 | -0.26 to -0.38 (mildly opposed) |
| L57 (expression) vs. L55 (disorder) | **+0.376** | **+0.56 to +0.67** |
| L54 (catalytic) vs. L55 (disorder) | -0.315 | -0.51 to -0.70 (opposed) |

L57's direction is **not independent of L55's** — real, substantial overlap
concentrated in the deepest layers, and stronger than a first informal look
suggested. This makes biological sense: eSol's soluble-expression-yield
label and DisProt's intrinsic-disorder fraction are independently known to
be related in the literature (disordered regions commonly reduce
solubility/expression), so a shared component of direction is not a
coincidence. L55's disorder effect is directionally robust across 3 seeds
(`studies/L55_DISORDER_STEERING.md`) even though its own residue-exclusion
check is seed-sensitive (2 of 3 seeds pass); L57's result is best read as a
partial, noisier echo of that same real direction, filtered through a
proxy (charge-based) that happens to composition-collapse more easily than
TOP-IDP does.

## Verdict: AMBIGUOUS — real signal, not independent evidence of a 6th steerable property

| criterion | result |
|---|---|
| 1. beats random control, real CI | **PASS** |
| 2. dose-response | **PASS** |
| 3. residue-exclusion robust | **FAIL** — effect vanishes to ~0 excluding E, L |
| 4. proxy pre-validated | **PASS** (r=0.305-0.337) |
| 5. beats prior technique | N/A |
| 6. adequately powered | **PASS** (n=150) |

Not a clean KILL (there is a real, non-trivial vector-geometry relationship
to a confirmed-real effect elsewhere) and not a PASS (fails the artifact
check outright, unlike L55's partial 2/3 pass). The correct characterization
is: **this result is not independent evidence for expression yield as a
6th distinct steerable capability** — it is largely explained by disorder's
already-established effect leaking through a related, weaker, more
collapse-prone proxy.

> **SUPERSEDED (2026-08-17):** the "largely explained by disorder" claim in
> this paragraph was tested causally and REFUTED — see "Validation follow-up"
> at the end of this file. The effect is disorder-independent (99% survives
> projecting L55 out). It is instead an **E/L composition artifact**, now
> confirmed non-circularly on an independent hydropathy proxy (L63: the GRAVY
> soluble-direction effect reverses under E/L exclusion), so the verdict is
> AMBIGUOUS **trending KILL**, not an echo of disorder.

## Methodological takeaway

Before writing off (or accepting) an AMBIGUOUS steering result as pure
noise or a standalone finding, checking its steering vector's cosine
similarity against every OTHER validated target's vector is a cheap,
informative diagnostic — it turned an unexplained borderline case into an
explained one here. Worth applying by default whenever running more than
one target property in the same batch.

## Cost

Single script run, `plm_steering/l57_run_repro.py`, 5 alphas x 2 directions
x 150 eval sequences, Apple Silicon MPS, ~5 minutes. The vector-geometry
cross-check (`plm_steering/l58_vector_geometry_crosscheck.py`, rebuilding
L54/L55/L57's steering vectors and computing pairwise cosine similarity)
cost one additional ~2-minute embedding pass, not a full steering sweep.
Raw scores/sequences saved to `plm_steering/l57_repro_out/results.json`;
the rebuilt vectors and cosine-similarity table saved to
`plm_steering/l58_vector_geometry_out/`.

## Validation follow-up (2026-08-17): the "echo of disorder" reading is REFUTED; verdict stays AMBIGUOUS for a different reason

The cosine-only argument above ("largely explained by disorder's effect
leaking through") was tested causally and does not hold. Two experiments:

**1. Orthogonalize disorder out and re-steer**
(`plm_steering/l60_l57_orthogonalized_validation.py`,
`l60_l57_ortho_out/results.json`). L57's per-layer steering vector was
Gram-Schmidt-orthogonalized against L55's disorder vector, renormalized to
L57's original per-layer norm, and rerun through L57's exact eval.
  - The L55-parallel component is only **8.9% of L57's norm** on average
    (≤25% even in the deep layers 30-32, where the +0.67 cosine lives — norm
    fraction removed is `1-√(1-cos²)`, small for moderate cosine, so a high
    cosine is NOT high shared magnitude).
  - Removing it retains **99% of the steering effect** (+0.0124 vs. +0.0125 at
    α=0.5, still significant and dose-responsive). Arm A (unmodified) reproduces
    the committed AMBIGUOUS/crit3-fail verdict as a built-in correctness check.
  - **Therefore the effect is NOT carried by disorder overlap.** Calling L57 "a
    partial echo of L55" overstated a directional correlation as a causal
    dependence. The effect is disorder-INDEPENDENT.

**2. Test the artifact non-circularly on an independent, E-free proxy**
The residue-exclusion collapse on the charge proxy is partly circular (E is one
of its four terms `|(K+R)-(D+E)|`). So the effect was re-scored end-to-end with
GRAVY hydropathy — an E-free FORMULA that independently validates against eSol
labels (r=-0.29) — through the full L50 pipeline
(`plm_steering/l63_l57_gravy_endtoend_validation.py`, `l63_l57_gravy_out/`; CPU
re-analysis of the saved generations, which are proxy-independent because the
steering vector is built on real labels).
  - At fixed alpha the effect shows up on E-free-formula proxies too
    (`l61_l57_altproxy_validation.py`: GRAVY +0.0497, aromatic +0.0080, both
    significant at α=0.5) — which at first looks like "broader than E-insertion."
  - **But under residue-exclusion it does NOT survive — it REVERSES.** Excluding
    the inserted residues E and L, the GRAVY soluble-direction effect flips from
    **+0.0497 to −0.0391** (significant, opposite sign). GRAVY being an E-free
    formula does not make the effect E-independent: GRAVY is a function of E
    content (E is hydrophilic, so inserting it lowers GRAVY), so the whole
    soluble-direction shift was carried by the E/L insertion, exactly like the
    charge proxy. Once E/L are removed the rest of the composition moves the
    *wrong* way.
  - **This confirms the residue-exclusion failure is real, not a circularity
    of the charge proxy.** (Correcting an earlier draft of this section: the
    "broader than E-insertion / genuine compositional shift" reading was wrong —
    it came from the fixed-alpha L61 numbers before the L63 residue-exclusion.)

**Corrected verdict.** Two independent facts, don't conflate them:
  1. L57 is **disorder-INDEPENDENT** (L60: removing L55 keeps 99% of the effect)
     — the "echo of disorder" reading is refuted.
  2. L57 is a **composition artifact concentrated in E/L**, now confirmed on an
     independent hydropathy proxy (L63), not just its own charge proxy — the
     effect collapses/reverses under residue-exclusion regardless of proxy or of
     whether disorder is projected out.
So L57 is best read as **AMBIGUOUS trending KILL**: the raw magnitude is real
but it is the E/L insertion, not a broad, transferable solubility gain, and it
is not disorder in disguise either. It does not clear the L50 artifact gate. The
paper drafts' "geometric echo of L55" language is simply wrong and should be
replaced with "an E/L composition artifact, independent of disorder."
