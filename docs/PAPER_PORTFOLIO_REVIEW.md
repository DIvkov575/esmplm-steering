# Paper Portfolio Review Log

Date: 2026-08-13

Reviewed file: `docs/PAPER_PORTFOLIO_PLAN.md`

## Independent reviewers

| Reviewer | Agent ID | Scope | Status |
|---|---|---|---|
| Locke | `019ffd08-69d5-7420-9efa-a84e11d63bba` | ICBINB-BIO strategy | Complete |
| Dewey | `019ffd08-71b2-7381-9dbb-1f20571bf212` | Interp4Discovery strategy | Complete, two passes |
| Bernoulli | `019ffd08-741e-7f60-81f3-5840a3b7943f` | Catalytic and disorder follow-up papers | Complete |
| Erdos | `019ffd08-8ccd-72f0-aef6-ecb35843b227` | Program structure, ownership, and critical path | Complete, two passes |

The reviewers read the first complete plan independently. They did not edit
the repository.

The Interp and program reviewers completed a second blocker-only pass after
the first revisions. They reported no remaining critical blocker. Their
remaining major findings are included in the resolution table below.

## Findings integrated into the plan

| Finding | Resolution |
|---|---|
| Invalid generations had no executable continuous outcome | Replaced the vague rule with a two-part analysis of failure risk and conditional score change |
| ICBINB depended on missing L42, L43, and L51 artifacts | Added a tracked artifact inventory, removed L43 and L54, added an August 15 rerun cutoff, and defined a minimum package that does not depend on missing bundles |
| Case selection and temporal provenance were unclear | Defined the eligible corpus and required prospective, retrospective, or post-hoc sensitivity labels |
| L51's saved verdict conflicts with its documented interpretation | Required an immutable derived audit bundle that records original and corrected policies |
| ICBINB risked becoming another property catalog | Reduced the main paper to three failure mechanisms and moved L53 to a boundary case |
| Interp allowed the result to choose the thesis | Replaced the thesis menu with one primary hypothesis and an ordered positive-then-equivalence test |
| Interp measured generic prediction damage instead of contact-specific damage | Defined the primary outcome as an ablation-by-contact interaction within proteins |
| Interp sample size and runtime had no basis | Added a pilot precision calculation, fixed cohort, runtime benchmark, retry buffer, and August 14 early cancellation rule |
| Interp controls and grouped ablation were underspecified | Added discovery-only matching, intervention calibration, matched group burden, and comparison with summed individual effects |
| Predictor architecture alone was treated as independence | Required training provenance, cluster-level overlap checks, and external experimental calibration |
| Catalytic and disorder gates did not bind every control | Added mandatory random, label-shuffled, reverse, composition, and regression checks to the decision rules |
| Boltz settings could bias structural comparisons | Required frozen inputs and sampling policy, no forced constraints in the primary analysis, and blinded arm review |
| Liability screens could be read as safety validation | Defined them as computational warning signals and separated beneficial-design claims from possible tradeoff analyses |
| Worktree ownership and reviewer authority were incomplete | Required committed contracts before worktree creation, named agent IDs, prohibited role combinations, handoff acceptance, and reviewer blocking authority |
| Definitions of done allowed unresolved review findings | Added clean-worktree reproduction, environment and model records, zero unresolved critical or major findings, and orchestrator sign-off |
| The ICBINB fallback was not an immutable submission artifact | Required the minimum source and reviewed PDF to be tagged before optional expansion |
| L55 seed provenance was not reproducible | Added a pre-August-15 task to parameterize the runner, record seeds, and reproduce all three runs |
| Final technical and packaging roles were referenced but undefined | Added both roles and required an accountable agent ID before work starts |
| Major findings did not block a submission | Defined review severities and made critical and major findings submission-blocking |
| Mean replacement could not repeat the 480-head positive test | Limited it to a prespecified top-five sensitivity analysis that can veto a contradictory positive branch |
| A pooled top-five equivalence result could hide one important head | Required head-by-head equivalence with familywise correction |
| Contact-position matching lacked balance and support checks | Added frozen calipers, unmatched-position handling, common-support rules, baseline-difficulty matching, and a balance threshold |
| The Interp completion gate omitted required August 20 checks | Required an explicit recorded pass for replication, matching, calibration, and branch-specific intervention checks |

## Open gates before execution

1. Author approves the portfolio plan.
2. Official venue policies and deadlines are verified and recorded.
3. The approved plan and initial paper contracts are committed.
4. The ICBINB claim registry and artifact manifest are frozen.
5. The Interp hypothesis, numerical margins, power target, and compute budget
   are frozen.
6. Fresh owner agents are assigned. The four planning reviewers above do not
   serve as final reviewers of their own future implementation work.

This review validates the planning revision only. It does not certify any
experiment, manuscript, or submission as complete.

## Active contract workers

| Worker | Agent ID | Scope | Status |
|---|---|---|---|
| Codex orchestrator | `019ffc96-17fe-70b0-b7ed-c8d499598db5` | Program controls, integration, and gates | In progress |
| Turing | `019ffd1c-1ea6-7763-9237-cdb0b291111d` | Official ICBINB-BIO and Interp4Discovery venue policy | Complete and accepted |
| Leibniz | `019ffd1c-24a4-7460-a6ff-47348bfd1dc6` | Artifact provenance inventory | Complete and accepted |
| Pauli | `019ffd1c-2bc4-7412-8740-2ad6648f8fb1` | ICBINB experiment manifest | ICB-03 control correction in progress; exact re-review pending |
| Ramanujan | `019ffd1c-33df-75c1-94d8-ef3244927a5b` | Interp4Discovery preregistration | Role-barrier correction in progress; final lock remains blocked |
| Hume | `019ffd25-3a51-76a0-8fbe-f1fe825d4af7` | Independent statistical contract review | Exact review of `0a9ace0` held on 1 Major finding |
| Maxwell | `019ffd25-3fde-7bb2-9bd3-9e326bdd4131` | Independent cross-document contract review | Exact review of `0a9ace0` held on 3 Major findings |
| Huygens | `019ffd75-3142-74c3-8b51-1391723775e6` | Ownership checker correction and bypass tests | Complete; second correction extends semantic coverage |

These workers have separate file ownership. They may not serve as final
reviewers of the artifacts they create.
