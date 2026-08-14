# Contract F0C6440 Review

Date reviewed: 2026-08-13

Branch reviewed: `master`

Commit reviewed:
`f0c6440263cf18de0138fb02302b4a8a1bf99832`

Tree reviewed:
`c6cfb57426c5ae1e2d84a6e4e40304dde5c253f8`

Decision: HOLD

Severity counts:

- Critical: 0
- Major: 3
- Minor: 1
- Blocking contract findings: 3

## Exact Review Boundary

The corrected boundary was verified before contract content was read.

- The object exists and has type `commit`.
- The object resolves to full commit
  `f0c6440263cf18de0138fb02302b4a8a1bf99832`.
- Its tree is
  `c6cfb57426c5ae1e2d84a6e4e40304dde5c253f8`.
- `HEAD`, `master`, `origin/master`, and `origin/HEAD` all resolved to that
  commit.
- `HEAD` had the same tree.
- The index and worktree were initially clean.

The committed tree was extracted with `git archive` to
`/private/tmp/esmplm-f0c6440-review.EbeOEW`. All repository reads, tests, PDF
checks, adversarial checks, and hash checks used that extracted tree. The
working checkout was used only to verify Git refs and create this report.

The committed `docs/STATISTICAL_CONTRACT_COMMIT_REVIEW.md` was excluded from
the evidence used here. An untracked
`docs/STATISTICAL_CONTRACT_F0C6440_REVIEW.md` appeared after the initial clean
boundary check. It was also excluded. No conclusion below relies on either
Hume report.

## Critical Findings

None.

## Major Findings

### M-01: The checker does not enforce the complete result-ledger semantics

`docs/RESULT_LEDGER_SCHEMA.md:7-9` requires exactly one controlling row per
claim and requires negative, failed, stopped, and excluded analyses to remain
in the ledger. Lines 101-108 require a confirmed row to contain all required
artifacts, denominators, estimates, intervals, completed analyses, and
independent review.

`plm_steering/submission_ownership.py:120-145` declares the required columns,
but `_ledger_artifacts` at lines 443-593 does not validate most of them. It
does not validate:

- provenance;
- estimand;
- statistical unit;
- control;
- cohort manifest path or hash;
- experiment manifest path or hash;
- point estimate;
- interval;
- denominator;
- limitation;
- source commit;
- completeness of the paper's controlling claim rows.

The existing valid-row helper leaves these fields empty at
`tests/test_submission_ownership.py:61-97`, and
`test_valid_allowlisted_package_passes` at lines 396-399 accepts that row.

The checker also applies `claim_status = confirmed` and `gate_result = pass`
to every ledger row at `plm_steering/submission_ownership.py:486-491`. That
conflicts with the schema requirement to retain stopped, rejected, failed, and
negative rows.

Adversarial results against the exact committed code:

```text
blank_semantics_and_hold_report []
```

This package used the full committed claim registry, only one INT row, blank
scientific fields, blank manifest bindings, and a blank source commit. It
passed with no violations.

A second adversarial ledger contained all three INT claims: INT-01 confirmed,
INT-02 stopped, and INT-03 rejected. The checker rejected the two required
nonconfirmed rows:

```text
result ledger row 3: claim_status must be 'confirmed'
result ledger row 3: gate_result must be 'pass'
result ledger row 4: claim_status must be 'confirmed'
result ledger row 4: gate_result must be 'pass'
```

Impact: The checker fails open for incomplete confirmed evidence and fails
closed for branch outcomes that the schema requires the ledger to preserve.
This can change claim readiness and can make a valid positive or negative
branch impossible to package.

Required correction: Validate all required confirmed-row fields and their
files and hashes. Require exactly one controlling row for every claim owned by
the paper. Preserve stopped, rejected, failed, and negative rows without
letting those rows authorize package evidence. Only confirmed and fully valid
rows should enter the artifact authorization map.

### M-02: Independent-review acceptance is self-reported

`docs/RESULT_LEDGER_SCHEMA.md:41-56` defines review metadata and requires a
verified independent review. Lines 101-108 make complete independent review a
condition for confirmation.

`plm_steering/submission_ownership.py:297-355` checks values inside the
ledger's `review_status` JSON and checks only that the referenced report file
has the stated hash. It does not check that the report itself:

- has an ACCEPT decision;
- has zero Critical and Major findings;
- identifies the reviewed claim and ledger row;
- identifies the reviewed commit, registry, manifests, or artifact hashes;
- was written by the stated reviewer;
- was written by an identity different from the experiment or paper owner.

The test at `tests/test_submission_ownership.py:551-560` covers report hash
changes, but no test covers a hash-valid report whose content contradicts the
ledger JSON.

The adversarial `blank_semantics_and_hold_report` case used a report whose
actual content said:

```text
Decision: HOLD
Major findings: 3
```

The ledger JSON claimed `decision = accepted`, zero findings, and
`reviewer_id = same-id-as-paper-owner`. The report hash was correct. The
checker returned no violations.

Impact: A package author can label any hash-matching file as an accepted
independent review. This removes the independent-review gate without changing
or forging the referenced file.

Required correction: Use a machine-readable review decision that binds the
claim ID, reviewed commit, registry hash, ledger hash or row hash, manifest
hashes, artifact hashes, reviewer ID, severity counts, and decision. Validate
that content rather than duplicating unverified values in the ledger. Bind the
reviewer ID to the assigned role record and reject owner-reviewer identity
conflicts.

### M-03: Renamed foreign result bytes bypass cross-paper ownership

The ownership contract applies to result bundles, not only text and filenames.
See `docs/PAPER_PORTFOLIO_PLAN.md:89-107`.
`docs/RESULT_LEDGER_SCHEMA.md:27-30` defines exact source-study ownership, and
lines 97-99 require rejection of ICBINB L54 evidence and Interp steering
evidence.

The checker hard-codes claim-to-study names at
`plm_steering/submission_ownership.py:79-89`. It then compares those names only
with the ledger's own `source_study_ids` value at lines 499-520. Artifact
ownership at lines 556-564 is a regular-expression check on the artifact path.
The checker does not bind artifact lineage to a validated experiment manifest,
stage lock, or known source artifact hash.

Two adversarial cases copied exact committed foreign result bytes to neutral
paths and supplied the source-study label expected by the target claim:

```text
renamed_l54_bytes_in_icbinb []
renamed_l55_bytes_in_interp []
```

The first case copied
`plm_steering/l54_repro_out/results.json`, SHA-256
`7b4dba5deb79101d688a40a40688879cc32503766bbb24e214a4876b361c3793`,
to `results/locked_result.json`. It labeled the row ICB-01 and reported L52.
The checker returned no violations.

The second case copied
`plm_steering/l55_repro_out/results.json`, SHA-256
`822402c49d2687bbae65b71c18815bcbe45c3dadf51ef7d16530bb46743a8d13`,
to the same neutral path. It labeled the row INT-01 and reported
`INTERP4DISCOVERY-CONFIRMATORY`. The checker returned no violations.

The source hashes and their true ownership are recorded at
`docs/ARTIFACT_INVENTORY.md:143-146`.

The focused tests at `tests/test_submission_ownership.py:507-536` reject only
paths that expose `l54`, `l55`, or `steering`. They do not test renamed bytes.

Impact: The package checker can pass exact L54 result bytes in ICBINB and exact
steering result bytes in Interp. This directly violates the cross-paper
evidence boundary.

Required correction: Bind every ledger artifact to a validated claim-owned
experiment manifest or stage lock that records its exact source path, source
hash, derivation, and parent hashes. Reject known foreign source hashes. Do not
use a row-provided study label or filename token as provenance.

## Minor Findings

### N-01: The status boards remain one commit behind

`docs/EXECUTION_LEDGER.md:7` says the second correction is in progress. Lines
27-30 describe correction work as in progress, and line 85 leaves corrected
artifacts committed and pushed unchecked. The completed-work table at lines
53-56 records only the first correction commit and a second correction
candidate.

`docs/PAPER_PORTFOLIO_PLAN.md:1051-1061` also calls this a second correction
candidate and says the next step is to commit the corrected baseline.
`docs/PAPER_PORTFOLIO_REVIEW.md:72-76` uses the same in-progress wording.

Commit `f0c6440263cf18de0138fb02302b4a8a1bf99832` already exists on `master`,
`origin/master`, and `origin/HEAD`. The statements are conservative and do not
authorize execution, so this is Minor.

Required correction: At the next correction commit, identify `f0c6440` as the
reviewed HOLD baseline and describe the new correction and exact re-review
state.

## Prior Finding Disposition

All findings in `docs/CONTRACT_CORRECTION_REVIEW.md` were rechecked.

| Prior finding | Exact-commit result |
|---|---|
| M-01, ledger semantic validation | Partly corrected. Exact claim membership, claim-text hash, status, gate, reported review metadata, source-study labels, and artifact hashes are checked. Complete row semantics, nonconfirmed-row handling, review binding, and artifact lineage remain open under current M-01 through M-03. |
| M-02, compiled manuscript PDF bypass | Resolved. Root PDF extraction and scanning fail closed. Focused and operational checks passed. |
| M-03, Interp role read barriers | Resolved at the contract level. Five distinct IDs and a post-verification paper handoff are explicit. Owner assignment and implementation remain correctly blocked. |
| N-01, status boards behind commit state | Not resolved for this exact commit. It recurs as current N-01. |

The new ICB-03 control contract was independently checked without using the
statistical report. `docs/CLAIM_REGISTRY.md:70-89` and
`docs/ICBINB_EXPERIMENT_MANIFEST.md:364-443` agree on length-only,
composition-only, and composition-plus-length models, common folds, organism
weighting, paired organism-clustered uncertainty, and the two required
composition-model pass conditions. No cross-document regression was found in
that correction.

## PDF Correction Result

Prior M-02 is closed.

- `plm_steering/submission_ownership.py:358-378` invokes `pdftotext`, requires
  successful UTF-8 text extraction, and rejects empty extraction.
- Lines 759-768 scan every root PDF and record extraction failure as a
  violation.
- `tests/test_submission_ownership.py:324-393` covers clean text, prohibited
  ICBINB text, prohibited Interp text, and extraction failure.
- Operational checks used Poppler `pdftotext` 26.04.0.
- A clean source paired with the historical ICBINB PDF produced 17 prohibited
  PDF-text violations and no extraction failure.
- A clean source paired with the historical Interp PDF produced 61 prohibited
  PDF-text violations and no extraction failure.
- A malformed root PDF produced a `cannot extract compiled PDF text`
  violation.

Both historical submission directories returned code 1 under the exact
documented package commands. They remain explicitly historical under
`docs/submissions/STATUS.md:5-21` and are not required to be upload-ready.

## Cross-Paper Claim Result

The active claim text remains separated correctly.

- `docs/PAPER_PORTFOLIO_PLAN.md:95-107` assigns catalytic and contact-attention
  claims to different papers.
- Lines 276-286 exclude L54 from ICBINB.
- `docs/ICBINB_EXPERIMENT_MANIFEST.md:75-89` excludes L54, L48, and L49.
- `docs/PAPER_PORTFOLIO_PLAN.md:428-466` defines Interp as a contact-ablation
  paper and removes steering material.
- Its Interp completion gate at lines 632-648 requires no steering results.
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md:14-39` defines only
  contact-attention claims, and lines 880-904 prohibit imported steering
  results at the gate.

Result: No L54 claim is in the active ICBINB contract, and no steering claim is
in the active Interp contract. The historical packages are rejected. The
future mechanical evidence boundary still fails under current M-03 because
renamed foreign bytes pass.

## Interp Roles, Handoff, and Lock Order

Prior M-03 is closed at the contract level.

- `docs/PAPER_PORTFOLIO_PLAN.md:843-883` defines all five Interp roles,
  prohibits any shared identity among them, and blocks paper-owner access
  until final verification and paper handoff.
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md:85-90` puts all five IDs and their
  read and write scopes in `ROLE_HANDOFF`.
- Lines 737-751 define `handoff/paper_handoff.json` and bind it to the final
  lock, gate, ledger, verification, result bundle, and paper-owner acceptance.
- Lines 753-858 define the exact command order. Feasibility closes before the
  final lock. Cohort and discovery close before matching. Matching acceptance
  precedes ablation. Analysis and gate precede independent review and ledger
  construction. Verification precedes paper handoff.
- Section 16 at lines 906-947 requires pairwise distinct IDs and blocks paper
  access before the final handoff.

The lock carrier is valid JSON. Its 20 keys exactly match Section 16. Status is
`feasibility_draft`, and every value, provenance note, approval, and validation
is null. The final lock therefore remains correctly blocked.

## Source Plan and Artifact Hashes

The exact SHA-256 of committed `docs/PAPER_PORTFOLIO_PLAN.md` is:

`9a43ed00b7ac5143209fc2a8383c2e53eb906415a88a6cf2939d6cfa2153fa31`

It exactly matches `docs/ICBINB_EXPERIMENT_MANIFEST.md:11-14`.

All nine explicit tracked current-input hashes in the ICBINB manifest matched
the archived committed bytes. The ignored Meltome file
`plm_steering/data_cache/meltome/mixed_split.csv` is not in the committed
archive. Its mapping and availability remain an explicit implementation and
evidence blocker under `docs/ICBINB_EXPERIMENT_MANIFEST.md:253-260`, not a new
contract defect.

## Legacy Runner Result

Legacy blocking remains effective.

- `plm_steering/legacy_runner_guard.py:4-9` exits before legacy work.
- The five guarded `main` functions call it before experiment logic.
- `tests/test_legacy_runner_guard.py:10-22` checks all five entry points.
- The focused guard suite passed, 5 tests.
- Direct target-style commands for L51, L52, L55, L56, and L57 all returned
  code 1.
- All five protected evidence hashes were unchanged.
- None of the five requested output paths was created.

## Correctly Blocked Implementation

These are implementation or evidence blockers, not additional contract
defects:

- The claim registry remains `BASELINE CANDIDATE`, and no active workshop
  claim is confirmed. See `docs/CLAIM_REGISTRY.md:7-24`.
- Exact acceptance of this correction commit remains pending in the committed
  status boards.
- `plm_steering.icbinb_audit` and its audited command interfaces are absent.
- L52 source mapping, L55 explicit seed metadata, L56 row-level outputs, and
  historical model revision pins remain unresolved.
- The ignored Meltome input is not part of the committed archive.
- `plm_steering.interp4discovery` and
  `tests/test_interp4discovery_contract.py` are absent.
- All 20 Interp final-lock values, provenance notes, approvals, and validations
  are null.
- Interp confirmation artifacts and clean active submission packages do not
  exist.

The legacy guards and null Interp lock prevent these missing implementations
from starting or overwriting evidence. Those blocks work as intended.

## Checks Run

- Verified the corrected full commit, tree, local branch, remote refs, clean
  index, and initially clean worktree before content review.
- Extracted the exact commit with `git archive` and confirmed Python imported
  `plm_steering` from the archive.
- Ran
  `/Users/divkov/workplace/repos/esmplm-steering/.venv/bin/python -m pytest -p no:cacheprovider -q`.
  Result: 165 passed in 3.78 seconds.
- Ran focused `tests/test_submission_ownership.py`.
  Result: 47 passed in 0.46 seconds.
- Ran focused `tests/test_legacy_runner_guard.py`.
  Result: 5 passed in 4.81 seconds.
- Compiled all archived Python files. Result: passed.
- Ran three semantic and cross-paper adversarial package checks. All returned
  empty violation lists, confirming M-01 through M-03.
- Ran the full-branch stopped and rejected ledger check. It failed on the
  required nonconfirmed rows, confirming M-01.
- Ran real `pdftotext` scans on both historical root PDFs and a malformed PDF.
  Prohibited text was rejected and extraction failure failed closed.
- Ran both documented historical package commands. Both returned code 1.
- Ran all five legacy target-style commands and checked protected hashes and
  output paths. All guards passed.
- Recomputed the source-plan hash and nine tracked manifest input hashes. All
  matched.
- Parsed the Interp lock carrier and compared all keys and null fields with
  Section 16. They matched.
- Inspected the exact feasibility, final-lock, cohort, discovery, matching,
  handoff, ablation, analysis, gate, review, ledger, verification, and paper
  handoff order.
- Confirmed the target ICBINB and Interp implementation modules and focused
  Interp contract test remain absent.
- Ran ASCII, prohibited-dash, trailing-whitespace, JSON, Python compilation,
  `git show --check`, and commit-diff checks. They passed.

## Gate Decision

HOLD the contract-freeze gate.

Zero Critical and Major findings are required for ACCEPT. This commit has
three Major findings. Do not start experiment worktrees or paper execution
from this commit. Correct M-01 through M-03, refresh the status boards, commit
one new exact tree, and rerun independent statistical and contract reviews.
