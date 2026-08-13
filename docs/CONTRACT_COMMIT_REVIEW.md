# Contract Commit Review

Date reviewed: 2026-08-13

Branch reviewed: `master`

Commit reviewed:
`14baabb2435835b345946b065f5268f067cc0d3b`

Tree reviewed:
`4b2bfabd6d72e343be607c5b4f61ea8cf7bbaeae`

Gate decision: HOLD

Finding counts:

- Critical: 0
- Major: 3
- Minor: 1
- Submission blockers: 3

## Exact Commit Boundary

The boundary was verified before repository content was read.

- `HEAD` resolved to the requested full commit.
- Short commit `14baabb` resolved to the same full commit.
- The current branch was `master`.
- `origin/master` and `origin/HEAD` resolved to the same commit.
- The requested tree and `HEAD` tree both resolved to
  `4b2bfabd6d72e343be607c5b4f61ea8cf7bbaeae`.
- The worktree and index were clean.
- Tracked files had no difference from the requested commit.

The review therefore covers the committed tree, not an ambient modified
worktree.

## Critical Findings

None.

## Major Findings

### M-01: The statistical acceptance does not identify the committed plan and manifest

The status boards call the plan and ICBINB manifest statistically accepted.
See `docs/PAPER_PORTFOLIO_PLAN.md`, Section 15, `Current execution board`, and
`docs/EXECUTION_LEDGER.md`, Sections `Current work` and `Completed work`.

The cited acceptance report has a narrower and older review boundary. See
`docs/STATISTICAL_CONTRACT_ACCEPTANCE.md`, Sections `Scope`, `Exact Inputs`,
`Decision`, and `Source Plan Hash`.

It records:

- plan SHA-256
  `085f558db973e8115600f020b3a9bd8fe79537f50297a43eb098f65525300b12`;
- manifest SHA-256
  `2097e7374cb389e9090c7b69c215a383c98c6236bb43586a23c6430d55ca3322`.

The committed files reviewed here have:

- plan SHA-256
  `4e380703696476e03381c91400f8983d15b4b8f2a91d958f84f6e378d76be3dc`;
- manifest SHA-256
  `9f4acfd8748a09259b1f327a9b74b350d85d811e8c7b3f6b0daa4c142b1f5fca`.

The claim registry hash still matches the acceptance report. The plan and
manifest do not. The committed manifest correctly records the committed plan
hash, but that does not extend the earlier reviewer's approval to new bytes.

Impact: The exact committed statistical contract has no matching independent
statistical acceptance record. This can change whether the contract-freeze
gate is allowed to close.

Required resolution: Obtain a statistical acceptance that names the full
commit or the current plan and manifest hashes. Otherwise narrow the status
boards so they do not claim that these exact files are statistically accepted.

### M-02: The ownership checker does not enforce the full prohibited evidence boundary

The active claim contracts are clear. ICBINB must contain no L54 result, and
Interp must contain no steering result. See:

- `docs/PAPER_PORTFOLIO_PLAN.md`, Sections 4, 7.9, 8.2, 8.6, and 14.2;
- `docs/RESULT_LEDGER_SCHEMA.md`, Section `Validation`;
- `docs/CONTRACT_REVIEW_RESOLUTION.md`, Section `Consistency review`, M-02.

`plm_steering/submission_ownership.py`, constant `PROHIBITED`, does not reject
literal `L54` references or `l54_` artifact paths for ICBINB. For Interp, it
rejects several phrases such as `activation steering`, `steering direction`,
and `steering vector`, but it does not reject generic steering or steered-result
claims. It inspects text only in Markdown and TeX files. For other files, it
rejects only three fixed historical PDF names.

The focused tests in `tests/test_submission_ownership.py` cover only selected
phrases and the three historical figure names. Adversarial checks returned no
violation for all of these prohibited examples:

- `The L54 result supports the paper.`
- `The l54_repro_out result supports the paper.`
- `Steering improves the measured score.`
- `The steered sequence changed the result.`

A renamed PDF containing a steering result would also pass the filename check.

The checker does reject both current historical packages. That resolves their
current status, but it does not prove that a future package is clean.

Impact: A package can pass the required ownership command while carrying a
prohibited L54 claim or a steering claim. This can change submission scope and
readiness.

Required resolution: Enforce exact forbidden study and artifact identifiers,
cover generic steering result language for Interp, and validate every packaged
figure or other evidence file through an allowlist tied to the locked result
ledger. Add focused bypass tests.

### M-03: The Interp target commands do not close the cohort and discovery stage contract

The preregistration correctly places discovery-only feasibility work before
the final lock. It also correctly places confirmation work after the final
lock. See `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Sections 2, 13.0, 13.9,
14, and 16.

The stage details remain incomplete:

- Section 2 requires the final lock to include a complete discovery manifest
  and metadata-only confirmation cohort manifest.
- Section 13.0 creates only a
  `feasibility/candidate_cohort_manifest.json` before final lock.
- Sections 13.2 and 13.3 require `cohort/cohort_manifest.json` and
  `discovery/head_selection.json`.
- Section 13.8 says cohort and discovery each become append-only when their own
  stage lock is written.
- Section 13.9 runs `build-cohort` only after final lock. It names no command
  that creates or accepts `discovery/head_selection.json`,
  `cohort/stage_lock.json`, or `discovery/stage_lock.json`.
- The later `match` command names only the preregistration lock. The contract
  does not state how it consumes accepted cohort and discovery parent locks.

This also leaves the discovery artifact without a clear owner in
`docs/PAPER_PORTFOLIO_PLAN.md`, Section 11.2, `Agent roles`.

Impact: Implementers can make different decisions about which pre-lock
manifest is final, which command creates discovery selection, and which parent
locks must verify. That weakens the declared append-only chain and exact
command contract.

Required resolution: Define the candidate-to-final cohort transition, name the
producer and owner of every cohort and discovery artifact, give both stages
exact lock paths, and make each later command consume the accepted parent lock.
Keep all confirmation-derived work after the final preregistration lock.

## Minor Findings

### N-01: The committed status boards still describe a pre-commit state

`docs/EXECUTION_LEDGER.md`, Section `Contract-freeze gate`, leaves `Contract
artifacts are committed and pushed` unchecked. The same file calls the program
`BASELINE COMMIT READY`.

`docs/PAPER_PORTFOLIO_PLAN.md`, Section 15, says the next step is to commit a
baseline. `docs/PAPER_PORTFOLIO_REVIEW.md`, Section `Active contract workers`,
still calls the ICBINB manifest review in progress, while the execution ledger
calls it statistically accepted with exact-commit review pending.

Commit `14baabb` exists on `master` and `origin/master`. These stale statements
are conservative because they do not authorize execution, but they make the
current gate state unclear.

Required resolution: Update the boards after the blocking findings are
resolved and record the accepted commit explicitly.

## Required Ownership Verification

### ICBINB and L54

The active ICBINB claim set contains no L54 claim.

- `docs/CLAIM_REGISTRY.md`, Sections `ICBINB-BIO claims` and `Rejected and
  deferred claims`, assigns active claims only to L52, L55, L56, L57, and the
  L55 versus L57 part of L58.
- ICB-06 names exact L55 and L57 vector paths and a paper-specific derived
  geometry path. It has no wildcard and no L54 input.
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 3, 9.2, 13.5, and 15, excludes
  L54 and requires verification to reject it.
- `docs/RESULT_LEDGER_SCHEMA.md`, Section `Validation`, requires the future
  ledger verifier to reject L54 evidence.

The current ICBINB manuscript does contain prohibited L54 material, but
`docs/submissions/STATUS.md` explicitly marks it historical and not an active
input. The package checker returns nonzero for that directory.

Result: No L54 claim is in the active ICBINB contract. The current historical
package is rejected. Mechanical protection for a future package is incomplete
under M-02.

### Interp and steering

The active Interp claim set contains no steering claim.

- `docs/CLAIM_REGISTRY.md`, Section `Interp4Discovery claims`, limits INT-01
  through INT-03 to contact enrichment, ablation damage, matched controls, and
  correlational replication.
- `docs/PAPER_PORTFOLIO_PLAN.md`, Sections 8.1, 8.2, and 8.6, states that this
  is not an activation-steering paper and requires all steering results,
  protocol, and figures to be removed.
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Sections 1 and 15, defines only
  contact-attention claims and bars imported steering results.
- `docs/RESULT_LEDGER_SCHEMA.md`, Section `Validation`, requires rejection of
  Interp evidence from steering experiments.

The current Interp manuscript does contain steering claims and figures, but
`docs/submissions/STATUS.md` explicitly marks it historical and not an active
input. The package checker returns nonzero for that directory.

Result: No steering claim is in the active Interp contract. The current
historical package is rejected. Mechanical protection for a future package is
incomplete under M-02.

## Prior Finding Disposition

All findings in `docs/CONTRACT_CONSISTENCY_REVIEW.md` and
`docs/CONTRACT_REVIEW_RESOLUTION.md` were rechecked.

### Statistical review findings

| Prior finding | Exact-commit result |
|---|---|
| C1, L57 absence claim | Resolved in registry ICB-05 and manifest Sections 2 and 8.3. |
| C2, L56 absence and confounding claims | Contract resolved in registry ICB-02 and ICB-03 and manifest Section 6. Required row-level work remains correctly blocked. |
| M1, generation estimands | Resolved in manifest Sections 4.1 through 4.4. |
| M2, L52 pairing | Contract resolved in manifest Sections 5.2 and 5.4. Mapping implementation remains correctly blocked. |
| M3, low-complexity threshold | Resolved in manifest Sections 4.2 through 4.4. |
| M4, provenance conflicts | Resolved in registry ICB-04 and ICB-05 and manifest Section 2. |
| M5, Interp head estimand | Resolved in preregistration Sections 4 and 8.2. |
| M6, Interp claim breadth | Resolved in registry INT-01 and INT-03 and preregistration Sections 8.1 and 8.2. |
| M7, Interp precision | Contract states the required simulation in preregistration Sections 9 and 16. Implementation is correctly blocked. |
| M8, Interp dependence and missingness | Resolved in preregistration Sections 6, 7, 8, and 10. |
| N1, L58 units | Resolved in manifest Section 9.2. |
| N2, interval method | Resolved in manifest Sections 4.1 and 4.4. |
| N3, width rule | Retained as an explicit auditable rule. |

The substantive corrections are present. M-01 in this report concerns the
review provenance for the exact committed plan and manifest bytes.

### Consistency review findings

| Prior finding | Exact-commit result |
|---|---|
| C-01, fail-open legacy runners | Immediate risk resolved. Five entry points abort before evidence access. The audited interfaces remain correctly blocked. |
| M-01, broad L58 paths | Resolved. Registry ICB-06 uses exact L55, L57, and derived output paths. |
| M-02, mixed submission packages | Historical status and current-directory rejection are resolved. Full checker enforcement remains open under M-02 in this report. |
| M-03, claim ID mismatch | Resolved. The manifest preserves ICB-01 through ICB-06, and the result schema requires one row per registry claim. |
| M-04, L55 consequence | Resolved. Manifest Sections 7.3 and 15 make L55 mandatory. |
| M-05, freeze artifact mismatch | Resolved. The three pre-run schemas exist and populated ledgers remain post-run. |
| M-06, controlling revision | Commit and source-plan hash are resolved. Exact statistical review provenance and board state remain open under M-01 and N-01 in this report. |
| M-07, incomplete Interp freeze marker | Resolved. Section 16 and the JSON contain the same 20 null keys. Confirmation is blocked. |
| M-08, missing Interp command contract | Partly resolved. Commands and paths now exist, but cohort and discovery stage production remains open under M-03 in this report. |
| M-09, late immutability | Stage-level immutability is stated. Its cohort and discovery command chain remains open under M-03 in this report. |
| M-10, matching information barrier | Role separation and handoff semantics are resolved. Owner assignment remains correctly blocked by the null `ROLE_HANDOFF` key. |
| N-01, cutoff precision | Resolved as `2026-08-15 23:59 Anywhere on Earth`. |
| N-02, evidence and narrative fields | Resolved in the claim registry. |
| N-03, orchestrator ID | Resolved in both status boards. |
| N-04, Interp acceptance wording | Resolved. The draft is accepted for feasibility, not frozen, and not authorized for confirmation. |

## Correctly Blocked Implementation

The following are implementation blockers, not additional contract defects:

- `plm_steering.icbinb_audit` does not exist.
- The audited L52, L55, L56, and L57 command interfaces do not exist.
- L52 source mapping is not verified.
- L55 seed bundles do not yet carry explicit seed metadata.
- L56 row-level predictions and fold artifacts do not exist.
- Model and tokenizer revisions are not pinned for the historical outputs.
- `plm_steering.interp4discovery` and its focused contract test do not exist.
- All 20 Interp lock values, provenance notes, approvals, and validations are
  null.
- Interp cohort, matching, ablation, analysis, and gate artifacts do not exist.
- Clean active manuscript packages and locked result ledgers do not exist.

The ICBINB manifest, Sections 13, 15, and 16, blocks affected execution and
claim confirmation. The Interp preregistration, Sections 13.9, 14, and 16,
blocks final lock and confirmation. These blocks are working as intended.

## Checks Run

- Verified branch, full commit, tree, remote refs, clean index, and clean
  worktree before reading.
- Ran `.venv/bin/python -m pytest -p no:cacheprovider -q`.
  Result: 123 passed in 3.52 seconds.
- Ran Python bytecode compilation for `plm_steering` and `tests` with the cache
  outside the repository. Result: passed.
- Ran all five guarded legacy module commands with target-style arguments.
  All returned nonzero, all five evidence hashes were unchanged, and no
  requested output path was created.
- Ran both historical package ownership commands. Both returned 1 and listed
  prohibited text or figures.
- Ran four adversarial ownership checks. All four prohibited examples passed
  undetected, confirming M-02.
- Parsed `docs/INTERP4DISCOVERY_LOCK_VALUES.json` with `jq`.
- Compared the 20 JSON keys with the 20 Section 16 keys. They matched exactly.
- Verified status `feasibility_draft` and null value, provenance, approval, and
  validation fields for all 20 keys.
- Recomputed the source-plan SHA-256. It exactly matched the hash in the ICBINB
  manifest.
- Verified all ten explicit current input hashes recorded for L52, L55, L56,
  L57, and L58. All matched.
- Inspected the Interp feasibility, final-lock, confirmation, handoff, stage,
  and gate ordering.
- Compared claim IDs, evidence ownership, dates, deadlines, roles, schemas,
  freeze states, and prior finding resolutions across the committed files.
- Ran ASCII, prohibited-dash, trailing-whitespace, JSON, and Git diff checks.
  They passed.
- Ran `git show --check` and confirmed that the committed tree remained
  unchanged throughout the review.

## Gate Decision

HOLD the contract-freeze gate.

Do not create experiment worktrees or authorize paper execution from this
commit. Resolve M-01 through M-03, update the conservative status boards, and
run the affected focused checks on the new exact commit. The current
implementation and evidence blockers remain in force after the contract
findings are corrected.
