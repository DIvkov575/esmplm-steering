# Contract Review Resolution Log

Date: 2026-08-13

This log maps first-pass findings to contract changes. It does not waive a
finding. An item marked implementation blocked still prevents the affected
experiment or submission phase.

## Statistical review

| Finding | Resolution | State |
|---|---|---|
| C1, L57 absence claim | ICB-05 and H4 now say that the E/L-excluded analysis does not meet the positive rule. They explicitly state that an interval containing zero is inconclusive. | Contract corrected |
| C2, L56 absence and confounding claims | ICB-02 now compares observed validation performance. ICB-03 says the grouped-validation drop is consistent with confounding. H2 requires row-level predictions, organism-clustered uncertainty, and narrower wording. | Contract corrected; row-level audit blocked |
| M1, generation estimands | The ICBINB manifest now targets fixed saved cohorts under realized masks and controls, gives proteins equal weight, names the joint-survivor estimand, and treats bootstrap intervals as finite-cohort stability summaries. | Contract corrected |
| M2, L52 pairing | H1 now requires reconstruction and independent verification of source IDs, sequence hashes, and array ordering from the frozen Meltome input, or a rerun with identifiers. | Implementation blocked until mapping verifies |
| M3, low-complexity threshold | Technical failures are conditions 1 through 4. The 25 percent rule is a separate low-complexity diagnostic, with analyses reported both with and without the historical filter. | Contract corrected |
| M4, provenance conflicts | ICB-04 and ICB-05 are post-hoc sensitivity claims. The manifest uses the same conservative chronology. | Contract corrected |
| M5, Interp head estimand | The primary statistic is now a layer-adjusted rank association over the fixed 480 heads. The permutation test and head-exchangeability claim were removed. | Contract corrected |
| M6, Interp claim breadth | INT-01 is limited to zero replacement. INT-03 is group-level top-five replication. Mean replacement can veto a precise reversal but cannot establish method robustness when imprecise. | Contract corrected |
| M7, Interp precision | `PRECISION_PLAN` requires a discovery-only simulation of the complete positive and equivalence pipelines, including matching attrition and all ten intervals. | Implementation blocked; confirmation cannot open |
| M8, Interp dependence and missingness | Position matching is without replacement. Every bootstrap jointly recomputes all heads and methods. Stable log probabilities and fail-closed required-result handling are specified. | Contract corrected |
| N1, L58 units | L58 is one fixed direction pair represented by 33 layer vectors. Layers are not called independent units. | Corrected |
| N2, interval method | ICBINB uses two-sided 95 percent percentile bootstrap stability intervals and the upper endpoint for its conservative noninferiority check. | Corrected |
| N3, redundant width rule | Retained as an auditable explicit check. | Accepted |

## Consistency review

| Finding | Resolution | State |
|---|---|---|
| C-01, fail-open legacy runners | L51, L52, L55, L56, and L57 entry points now abort through `legacy_runner_guard`. Focused tests enforce the guard. Target audited interfaces use `.venv/bin/python` and remain unauthorized until implemented and tested. | Immediate overwrite risk closed; audited CLI implementation blocked |
| M-01, broad L58 paths | ICB-06 names only the exact L55 and L57 vector inputs and the paper-specific extracted geometry artifact. | Corrected |
| M-02, mixed submission packages | `docs/submissions/STATUS.md` marks both current packages historical. `submission_ownership` rejects their cross-paper evidence and historical figures. | Corrected; clean packages not yet built |
| M-03, claim ID mismatch | The manifest preserves ICB-01 through ICB-06 and splits the two L56 claims. The result-ledger schema requires one row per registry claim. | Corrected |
| M-04, L55 consequence | L55 reproduction is mandatory. Failure stops the ICBINB submission rather than allowing L57 to replace it. | Corrected |
| M-05, freeze artifact mismatch | The plan separates pre-run schemas from post-run populated ledgers. Cohort, result-ledger, and citation-ledger schema files now exist. | Corrected |
| M-06, controlling revision | Status boards and the ICBINB source-plan hash were refreshed for the reconciled baseline. The consistency review will rerun against the exact commit. | Open until committed re-review |
| M-07, incomplete Interp freeze marker | Section 16 defines 20 required lock keys. `INTERP4DISCOVERY_LOCK_VALUES.json` carries all keys as null until resolved and reviewed. | Corrected; confirmation blocked |
| M-08, missing Interp command contract | The preregistration defines one output root, exact stage paths, target commands, focused tests, and a fail-closed verifier contract. | Contract corrected; implementation blocked |
| M-09, late immutability | Cohort, discovery, matching, ablation, and analysis stages become append-only when each stage lock is written. Every correction needs a new experiment ID and amendment. | Corrected |
| M-10, matching information barrier | The plan separates matching, ablation, and analysis owners. The matching stage lock is read-only downstream, and `ROLE_HANDOFF` blocks confirmation until owners and hashes are accepted. | Corrected; owners not yet assigned |
| N-01, cutoff precision | ICB-04 now uses `2026-08-15 23:59 Anywhere on Earth`. | Corrected |
| N-02, evidence and narrative fields | Registry rows separate empirical evidence from narrative context. | Corrected |
| N-03, orchestrator ID | The current orchestrator is recorded as `019ffc96-17fe-70b0-b7ed-c8d499598db5`. | Corrected |
| N-04, ambiguous Interp acceptance | Both trackers say the draft is accepted, not frozen, and not authorized for confirmation execution. | Corrected |

## Required re-review

1. Run the full repository test suite and all static contract checks.
2. Refresh controlling hashes and commit one baseline revision.
3. Ask the statistical reviewer to verify corrected claim and estimand
   contracts.
4. Ask the consistency reviewer to review the exact committed revision.
5. Do not create experiment worktrees until no contract-freeze critical or
   major finding remains.

## Exact review of `14baabb`

| Finding | Resolution | State |
|---|---|---|
| M-01, statistical acceptance did not name committed bytes | Status boards now distinguish the earlier candidate review from the required exact correction-commit review. | Open until exact corrected-commit review |
| M-02, ownership checker boundary incomplete | The checker rejects exact study identifiers, generic steering results, and unlisted or hash-mismatched evidence files. Its allowlist is bound to the contracted CSV result ledger. | Corrected; focused bypass tests pass |
| M-03, Interp cohort and discovery stages incomplete | The preregistration now defines candidate-to-final cohort materialization, discovery materialization, exact stage locks, owners, parent-lock sets, and command inputs. | Contract corrected; implementation blocked |
| N-01, status boards described a pre-commit state | The boards record commit `14baabb`, its HOLD decision, and the correction state. | Corrected |

## Exact reviews of `0a9ace0`

| Finding | Resolution | State |
|---|---|---|
| Statistical M1, ICB-03 length and composition controls undefined | ICB-03 now prespecifies length-only, composition-only, and composition-plus-length models under identical folds, organism weighting, and paired clustered uncertainty. Both composition-model grouping differences must pass. | Contract corrected; exact re-review pending |
| Contract M-01, ledger rows lacked semantic validation | The ownership checker now binds the claim registry and validates exact claim membership, claim text, confirmed status, passing gate, accepted independent review, and paper-prohibited artifact paths. | Corrected; focused bypass tests pass |
| Contract M-02, compiled PDF bypass | The checker extracts and scans root PDF text with `pdftotext`. Missing or failed extraction is a violation. | Corrected; focused bypass tests pass |
| Contract M-03, Interp role read barriers incomplete | Discovery, cohort and matching, ablation, analysis, and paper ownership now require five distinct IDs. A verified paper handoff controls result-bundle access. | Contract corrected; owner assignment blocked |
| Contract N-01, status boards behind commit state | Boards now record the `0a9ace0` HOLD reviews and this second correction state. | Corrected |

## Exact reviews of `f0c6440`

| Finding | Resolution | State |
|---|---|---|
| Statistical review | The exact ICBINB statistical contract, including ICB-03, was accepted with no Critical, Major, or Minor finding. | Accepted at `f0c6440`; exact third-correction review pending |
| Contract M-01, incomplete ledger semantics | `docs/SUBMISSION_CONTRACT.json` fixes the complete claim set and exact per-claim semantics. Ledger schema 1.1 retains every nonconfirmed row, validates typed results and all supplied hashes, and limits evidence authorization to complete confirmed rows. | Corrected in candidate; 101 focused tests pass |
| Contract M-02, self-reported independent review | Confirmed rows point to machine-readable review decisions that bind assigned reviewer identity, canonical row payload, source commit, contract files, manifests, lineage, and exact artifacts. Blocking findings are derived from the decision file. | Corrected in candidate; adversarial review tests pass |
| Contract M-03, renamed foreign bytes | `docs/ARTIFACT_OWNERSHIP.json` records known result hashes and permitted ownership. Every artifact and lineage ancestor is checked by hash, and each claim has a locked parent-bound lineage manifest. | Corrected in candidate; renamed L43, L54, and L55 checks pass |
| Contract N-01, status boards behind commit state | Boards now record the `f0c6440` statistical ACCEPT, consistency HOLD, and third-correction state. | Corrected in candidate; exact re-review pending |

## Dirty-candidate correctness review

| Finding | Resolution | State |
|---|---|---|
| Major, historical L43 bytes were absent from the known-hash catalog | Added a nonauthorizing historical-only L43 hash and verified that the exact historical bytes are rejected after a text-file rename. | Corrected; re-review pending |
| Major, directory and broken symlinks were skipped | Prohibited every package symlink before any signature, hash, text, or PDF read. Added file, directory, and broken-link tests. | Corrected; re-review pending |
| Major, every root PDF was exempted as a manuscript | Limited the exemption to root `paper.pdf`. Every other PDF now requires evidence authorization. | Corrected; re-review pending |
| Minor, very large JSON integers could raise `ValueError` | JSON loaders now convert both decode errors and integer-limit errors into violations. | Corrected; re-review pending |
| Minor, several rejection paths lacked direct tests | Added tests for malformed hash-matched manifests, canonical contract path, catalog hash, and an existing undeclared lineage parent. | Corrected; re-review pending |
| Major, a default allowlist symlink was read before the later package scan | Default and explicit allowlist, ledger, and claim-registry symlinks are now rejected before metadata discovery or parsing. | Corrected after second pass; re-review pending |
| Minor, deeply nested JSON could raise `RecursionError` | All three JSON parsing boundaries now convert parser recursion failures into violations. | Corrected after second pass; re-review pending |
| Major, metadata beneath a symlinked directory was read before rejection | Metadata paths are now checked component by component. Package and repository metadata roots containing symlinks also fail before content reads. | Corrected after third pass; re-review pending |
| Minor, medium-depth numeric payloads could recurse after JSON decoding | Numeric payload, interval-bound, and lineage-cycle validation now use iterative traversal. | Corrected after third pass; re-review pending |
| Adjacent read-order case, an allowlisted artifact symlink could resolve before the package scan | Package-entry paths now receive the same component-wise symlink check before containment or hashing. | Corrected during final local audit; re-review pending |
| Major, repository-relative paths still followed symlink components | The shared contained-file resolver now rejects every symlink component before resolution. This covers authorities, roles, manifests, artifacts, parents, locks, and reviews. | Corrected after fourth pass; re-review pending |
| Minor, direct exact-byte L43 test was absent | Added a direct test that recovers the historical blob when Git history is available, verifies its hash, renames it to text, and requires allowlisting. | Corrected after fourth pass; re-review pending |
| Final ownership correctness re-review | Harvey found no Critical, Major, or Minor issue. Focused ownership and exact L43 checks passed. | Accepted; exact commit reviews pending |
