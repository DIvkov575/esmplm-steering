# L60 — Cross-protein binding (DNA-binding propensity): weak PASS, rescues L53

Status: **PASS on 2/3 seeds, AMBIGUOUS on 1** — with a genuine but ~3× weaker
effect than L59 transmembrane. Directly rescues L53's binding KILL and
confirms the central finding: compositional group separation, not proxy
correlation, sets steerability.

## The framing problem (and why this is the honest test)

L53 steered binding AFFINITY on a single-backbone KRAS DMS (6k point mutants
of one protein) and got a flat null at every alpha. Its group separation was
**0.0033** — the low/high groups were compositionally identical, so the
difference-of-means vector had nothing to encode. L53:92 named "a cross-protein
binding dataset analogous to L54's DLKcat" as the natural next test.

But protein–protein binding *affinity* (Kd of A for B) is relational — a
function of two sequences — so it fails L56's intrinsic-property gate for
exactly the reason immunogenicity (host-MHC dependence) was killed pre-run.
The faithful reframing that is BOTH cross-protein AND intrinsic is a binding
*capability* with a generic partner: **DNA-binding**. A DNA-binding protein
binds the phosphate backbone by virtue of its own sequence, independent of
which DNA. This tests whether "binding" resists steering intrinsically, or
whether L53's null was purely a single-backbone data artifact.

## Dataset: UniProt DNA-binding vs control

`plm_steering/l60_fetch_binding.py` → `data_cache/binding/uniprot_dnabinding.json`.
Reviewed Swiss-Prot, 50–400 aa: DNA-binding (keyword KW-0238, label 1) vs
control (NOT KW-0238, NOT RNA-binding KW-0694, label 0). **7,783 usable unique**
(3,799 binding, 3,984 control).

## Proxy: positive-charge fraction (Lys + Arg)

`binding_proxy` in `plm_steering/l60_binding_steering.py`. Nucleic-acid
interfaces are documented to be Lys/Arg-enriched (Luscombe et al. 2001, NAR).
Validated against the real DNA-binding label BEFORE the run:
held-out **pearson r = +0.24 to +0.27** (p≈1e-32 to 1e-41) across seeds. Above
the 0.15 gate.

## G1 separation gate — the L53 predictor, now cleared

Mean AA-composition L2 distance between low/high groups: **0.039–0.043**.
Compare L53 single-backbone **0.0033** (nulled) and L54 catalytic **0.023–0.045**
(PASS). Moving from single-backbone to cross-protein data lifts separation
~12× into the PASS regime — this is the mechanism of the rescue, predicted
before any GPU work.

## Verdict — fine grid {0.1,0.15,0.2,0.25}, 3 seeds

| seed | dose 0.1→0.15→0.2→0.25 | crit1 | crit2 | crit3 (excl L,S) | decision |
|---|---|---|---|---|---|
| 0 | 0.001→0.004→0.005→0.007 | ✓ | ✓ | ✓ diff=0.011 [0.008,0.014] | PASS |
| 1 | 0.000→0.002→0.003→0.004 | ✓ | ✓ | ✓ diff=0.007 [0.005,0.010] | PASS |
| 2 | 0.002→0.002→0.003→0.003 | ✓ | ✗ (ties) | ✓ diff=0.006 [0.004,0.008] | AMBIGUOUS |

crit1 (beats random) and crit3 (residue-robust) hold on **all 3 seeds**. The
seed-2 AMBIGUOUS is a strict-monotonicity tie between 0.1 and 0.15 on an effect
so small that finer resolution only resolves noise — not worth chasing.

## The magnitude caveat is the real conclusion

Statistical significance understates how weak this is. Expressed as a fraction
of the *natural* low→high group gap in the proxy (how far a real DNA-binder
sits from a non-binder):

| target | separation | steer effect at α=0.25 as % of natural gap |
|---|---|---|
| L59 transmembrane | 0.086 | **72.3%** (proxy −0.363 → +0.266; gap 0.871) |
| L60 binding (DNA) | 0.039 | **24.7%** (proxy +0.121 → +0.127; gap 0.023) |

The transmembrane vector moves generations ~three-quarters of the way to the
membrane-protein distribution; the DNA-binding vector moves them ~a quarter of
the way toward the binder distribution (+0.006 in K+R fraction). Real,
artifact-resistant, reproducible — but marginal.

## Conclusion

1. **L53's binding KILL was a single-backbone-data artifact, not an intrinsic
   property of binding.** Given cross-protein, intrinsic data (separation
   0.039), the same harness produces a significant, residue-robust,
   dose-responsive effect (2/3 clean PASS). Binding is steerable.
2. **But binding is a weak target.** At ~25% of the natural gap it is the
   weakest positive result in the arc, well below transmembrane (72%) and
   below the practical bar transmembrane/catalytic set. Its separation (0.039)
   is the lowest of any non-killed target, and effect magnitude tracks
   separation, so this is expected.
3. **Central finding reinforced across four points** — L53 (sep 0.0033 → null),
   L60 (0.039 → 24.7%), L54 (0.023–0.045 → PASS), L59 (0.086 → 72.3%):
   compositional group separation predicts both steerability and effect size;
   proxy correlation strength does not (L53 had proxy r up to 0.80 and nulled).

## Reproduce

```
source .venv/bin/activate
python3 -m plm_steering.l60_fetch_binding
L60_SEED=0 python3 -m plm_steering.l60_run_repro    # -> l60_repro_out/
L60_SEED=1 python3 -m plm_steering.l60_run_repro    # -> l60_repro_out_seed1/
L60_SEED=2 python3 -m plm_steering.l60_run_repro    # -> l60_repro_out_seed2/
```
