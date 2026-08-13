# Paper Portfolio Execution Ledger

Ledger version: 0.1

Updated: 2026-08-13

Program state: BASELINE COMMIT READY

## Active scope

| Paper | Decision | Current gate |
|---|---|---|
| ICBINB-BIO | Protected primary submission | Freeze claims, artifact inventory, and minimum experiment manifest |
| Interp4Discovery | Conditional submission | Freeze preregistration and verify compute feasibility |
| Catalytic steering | Deferred until after August 29 | Not active |
| Disorder steering | Deferred until after August 29 | Not active |
| arXiv | Out of scope for this program | Do not work |
| XAI4Science | Out of scope for this program | Do not work |

## Current work

| Work item | Owner | Agent ID | Status | Expected artifact |
|---|---|---|---|---|
| Program orchestration and claim registry | Codex main session | `019ffc96-17fe-70b0-b7ed-c8d499598db5` | In progress | `docs/CLAIM_REGISTRY.md`, this ledger |
| Official venue-policy verification | Turing | `019ffd1c-1ea6-7763-9237-cdb0b291111d` | Complete and accepted | `docs/VENUE_POLICY_2026.md` |
| Artifact provenance inventory | Leibniz | `019ffd1c-24a4-7460-a6ff-47348bfd1dc6` | Complete and accepted | `docs/ARTIFACT_INVENTORY.md` |
| ICBINB experiment manifest | Pauli | `019ffd1c-2bc4-7412-8740-2ad6648f8fb1` | Statistically accepted; exact-commit review pending | `docs/ICBINB_EXPERIMENT_MANIFEST.md` |
| Interp preregistration | Ramanujan | `019ffd1c-33df-75c1-94d8-ef3244927a5b` | Reconciled for feasibility; final lock remains blocked | `docs/INTERP4DISCOVERY_PREREGISTRATION.md` |
| Statistical contract review | Hume | `019ffd25-3a51-76a0-8fbe-f1fe825d4af7` | Complete; 0 Critical and 0 Major findings remain | `docs/STATISTICAL_CONTRACT_ACCEPTANCE.md` |
| Cross-document contract review | Maxwell | `019ffd25-3fde-7bb2-9bd3-9e326bdd4131` | First pass complete; exact-commit re-review pending | `docs/CONTRACT_CONSISTENCY_REVIEW.md` |

These agents are contract workers or independent reviewers. They are not final
reviewers of their own outputs.

## Completed work

| Work item | Evidence | Status |
|---|---|---|
| Portfolio strategy | `docs/PAPER_PORTFOLIO_PLAN.md` | Author directed execution on 2026-08-13 |
| ICBINB planning review | Locke, `019ffd08-69d5-7420-9efa-a84e11d63bba` | Complete |
| Interp planning review | Dewey, `019ffd08-71b2-7381-9dbb-1f20571bf212` | Complete, two passes |
| Later-paper planning review | Bernoulli, `019ffd08-741e-7f60-81f3-5840a3b7943f` | Complete |
| Program planning review | Erdos, `019ffd08-8ccd-72f0-aef6-ecb35843b227` | Complete, two passes |
| Repository test baseline | `.venv/bin/python -m pytest -p no:cacheprovider -q` | 123 passed on 2026-08-13 |
| Legacy runner overwrite check | Five direct module commands plus evidence-file hashes | All commands failed closed; all five hashes were unchanged; no requested output path was created |
| Historical package ownership check | `plm_steering.submission_ownership` for both papers | Both packages rejected as expected; neither is a submission input |
| Contract static checks | JSON, ASCII, em dash, formatting, and `git diff --check` scans | Passed for the active contract set |
| Final statistical contract review | `docs/STATISTICAL_CONTRACT_ACCEPTANCE.md` | Accepted with 0 Critical and 0 Major findings |

## Environment baseline

| Field | Value |
|---|---|
| Environment path | `.venv`, ignored by git |
| Python | CPython 3.11.15 |
| Dependency source | `requirements.txt`; exact tested versions in `requirements-lock.txt` |
| Installation command | `uv pip install --python .venv/bin/python -r requirements.txt` |
| Test command | `.venv/bin/python -m pytest -p no:cacheprovider -q` |
| Test result | 123 passed in 4.13 seconds |

The default Homebrew Python 3.14 environment cannot collect the suite because
it lacks `torch` and `scikit-learn`. Use the Python 3.11 environment for
repository work.

## Contract-freeze gate

- [x] Author directed execution of the portfolio plan.
- [x] Paper ownership and prohibited claims are recorded.
- [x] Initial sentence-level claim registry exists.
- [x] Cohort, result-ledger, and citation-ledger schemas exist.
- [x] Official venue policies are verified from current official sources.
- [x] Artifact inventory is complete and hashes are recorded.
- [x] ICBINB experiment manifest is reviewed against the claim registry.
- [x] Interp preregistration contains an explicit complete lock-key set and
  unresolved values remain null.
- [x] Active contract artifacts pass prose and static checks.
- [ ] Contract artifacts are committed and pushed.
- [ ] Sibling worktrees start from the exact contract commit.

No experiment owner or paper owner starts before this gate closes.

## Next execution gate

After the contract commit:

1. Create `research/shared-audit`, `paper/icbinb`, and
   `paper/interp4discovery` from the exact same commit.
2. Assign fresh implementation owners with disjoint write scopes.
3. Patch and reproduce L55 seeds 0, 1, and 2.
4. Recover L42 or L51 only if a complete raw audit bundle can be produced by
   the cutoff.
5. Benchmark the Interp confirmatory core before spending the protected
   ICBINB compute allocation.
6. Lock the minimum ICBINB audit bundle before manuscript restructuring.

## Blocking rules

- Missing raw evidence removes a case; narrative text does not replace data.
- Failed and negative runs remain in the result ledger.
- A claim cannot exceed `docs/CLAIM_REGISTRY.md`.
- Critical and major review findings block the affected paper.
- Interp stops if its confirmatory core cannot finish by the gate date.
- Catalytic and disorder work cannot consume workshop-critical time.
- No manuscript rewrite starts before its result bundle is locked.

## Handoff log

| Date | From | To | Artifact | Acceptance |
|---|---|---|---|---|
| 2026-08-13 | Planning reviewers | Orchestrator | `docs/PAPER_PORTFOLIO_PLAN.md`, `docs/PAPER_PORTFOLIO_REVIEW.md` | Accepted for contract implementation |
| 2026-08-13 | Ramanujan | Orchestrator | `docs/INTERP4DISCOVERY_PREREGISTRATION.md` | Draft accepted; freeze blocked on listed numerical, cohort, and compute decisions |
| 2026-08-13 | Turing | Orchestrator | `docs/VENUE_POLICY_2026.md` | Accepted; earlier Interp OpenReview deadline is operational until resolved |
| 2026-08-13 | Leibniz | Orchestrator | `docs/ARTIFACT_INVENTORY.md` | Accepted after registry conflicts were corrected |
| 2026-08-13 | Hume | Orchestrator | `docs/STATISTICAL_CONTRACT_REVIEW.md` | First pass accepted; blockers require correction and re-review |
| 2026-08-13 | Hume | Orchestrator | `docs/STATISTICAL_CONTRACT_REREVIEW.md` | Rereview found five Major contract findings; corrections applied; final blocker-only review pending |
| 2026-08-13 | Hume | Orchestrator | `docs/STATISTICAL_CONTRACT_ACCEPTANCE.md` | Statistical contract accepted; 0 Critical and 0 Major findings remain |
| 2026-08-13 | Maxwell | Orchestrator | `docs/CONTRACT_CONSISTENCY_REVIEW.md` | First pass accepted; blockers require correction and committed-revision re-review |

Future handoffs must list inputs, changed files, supported and unsupported
claims, checks run, unresolved blockers, and the recommended gate decision.
