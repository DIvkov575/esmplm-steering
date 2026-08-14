# Contract Correction Review

Date reviewed: 2026-08-13

Branch reviewed: `master`

Commit reviewed:
`0a9ace04d7e718723aa3fb69aba6320b02eb2f55`

Tree reviewed:
`c53e0ca074aa7153b373b02ae2b816949d676611`

Gate decision: HOLD

Finding counts:

- Critical: 0
- Major: 3
- Minor: 1
- Blocking contract findings: 3

## Exact Commit Boundary

The boundary was verified before repository content was read.

- `HEAD` was the requested full commit.
- The current branch was `master`.
- `origin/master` and `origin/HEAD` were the same commit.
- The requested commit and `HEAD` both had tree
  `c53e0ca074aa7153b373b02ae2b816949d676611`.
- The index and worktree were clean.
- No repository `AGENTS.md` existed.

An untracked `docs/STATISTICAL_CONTRACT_COMMIT_REVIEW.md` appeared after the
initial boundary check. It is outside the reviewed commit. It was not read or
used. The committed tree remained at the requested commit and tree.

## Critical Findings

None.

## Major Findings

### M-01: The ownership checker trusts result-ledger rows that violate the ledger contract

`docs/RESULT_LEDGER_SCHEMA.md`, Sections `Required columns`, `Validation`, and
`Submission evidence allowlist`, require exact registry IDs, registered claim
text, valid confirmed status, a passing gate, complete independent review, no
unresolved Critical or Major finding, and paper-specific evidence ownership.
The same validation section explicitly prohibits L54 evidence in ICBINB and
steering evidence in Interp.

`plm_steering/submission_ownership.py`, functions `_load_csv`,
`_ledger_artifacts`, and `_validate_ownership_allowlist`, do not enforce those
requirements. `_load_csv` checks that column names exist. `_ledger_artifacts`
checks only the claim prefix, paper ID, path form, file existence, and artifact
hash. It does not validate:

- exact membership in `docs/CLAIM_REGISTRY.md`;
- `claim_text_sha256`;
- `claim_status = confirmed`;
- `gate_result = pass`;
- complete independent review;
- absence of unresolved Critical or Major findings;
- the ICBINB ban on L43, L48, L49, and L54 evidence;
- the Interp ban on steering evidence.

Adversarial temporary-package checks all returned an empty violation list:

```text
invented_claim []
stopped_failed_unreviewed []
icbinb_l54_ledger_artifact []
interp_steering_ledger_artifact []
```

The accepted rows included invented claim `INT-999`, a stopped and failed
`INT-01` row with an unresolved Major review, an ICBINB artifact at
`results/l54_catalytic_result.pdf`, and an Interp artifact at
`results/l55_disorder_steering_result.pdf`. Each synthetic package used matching
file and CSV hashes and a valid allowlist.

`tests/test_submission_ownership.py` verifies path, hash, prefix, and CSV-shape
failures, but it has no test for these semantic ledger failures.

Impact: A package can pass the required checker using evidence that the
controlling result-ledger schema rejects. This directly defeats the claim and
paper ownership gate.

Required correction: Bind the checker to the exact claim registry and validate
all controlling row semantics before any row can authorize an allowlist entry.
Add adversarial tests for invented, unconfirmed, failed, unreviewed, L54, and
steering rows.

### M-02: A compiled manuscript PDF can carry prohibited claims without inspection

`plm_steering/submission_ownership.py`, functions
`_is_compiled_manuscript`, `_package_evidence_paths`, and `find_violations`,
exclude a root PDF when a neighboring TeX or Typst source looks like a
manuscript. The PDF is neither text-scanned nor hash-bound to the source.

The existing test
`test_compiled_root_manuscript_is_not_an_evidence_file` makes this exclusion an
expected behavior. An adversarial package with clean `paper.tex` and a root
`paper.pdf` containing prohibited L54, catalytic, and steering text returned:

```text
compiled_pdf_only_prohibited_text []
```

This conflicts with `docs/submissions/STATUS.md`, list `Clean packages may be
built in these directories only after`, item 4, which requires a package
verifier to reject cross-paper claims and evidence. It also leaves a gap between
`docs/PAPER_PORTFOLIO_PLAN.md`, Sections 14.2 and 14.3: the ownership verifier
checks source and figures, but the final uploaded PDF can differ from that
source. Manual page inspection is a later control, but it does not make this
checker reject the prohibited package.

Impact: The actual upload artifact can pass the automated ownership gate while
containing a claim assigned to another paper.

Required correction: Text-scan the compiled PDF or verify a reproducible
source-to-PDF binding and scan the bound extracted text. Add a stale or
substituted PDF bypass test for each paper.

### M-03: Interp role combinations can bypass the stated read barriers

`docs/PAPER_PORTFOLIO_PLAN.md`, Section 11.2, says that the discovery owner
cannot read confirmation artifacts and that the cohort and matching owner
cannot read ablation output. It prohibits only these Interp combinations:

- discovery plus cohort and matching;
- discovery plus analysis;
- cohort and matching plus ablation.

It does not prohibit discovery plus ablation or discovery plus paper owner.
Both later roles receive confirmation artifacts. It also does not prohibit
cohort and matching plus analysis or cohort and matching plus paper owner. Both
later roles receive ablation results.

`docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Sections 2 and 16, records discovery,
cohort and matching, ablation, and analysis identities in `ROLE_HANDOFF`, but it
does not require unique identities for all read-barrier roles. It does not
record the Interp paper owner in that lock. Section 13.4 requires several of
these owners to accept the matching handoff, but acceptance does not detect an
identity holding two conflicting roles.

This also leaves the resolution statement in
`docs/CONTRACT_REVIEW_RESOLUTION.md`, Section `Consistency review`, M-10, only
partly implemented. The stage write scopes are separate, but the identity and
read scopes are not fully separated.

Impact: One agent ID can receive data through a second role that its first role
is explicitly forbidden to read. That breaks the information barrier before
the analysis and paper stages.

Required correction: Require distinct identities for discovery, cohort and
matching, ablation, analysis, and paper ownership, or enumerate every
read-conflicting pair. Include the paper owner in the validated handoff before
the paper receives the locked result bundle.

## Minor Findings

### N-01: The status boards still describe a pre-commit correction state

`docs/EXECUTION_LEDGER.md`, Section `Contract-freeze gate`, leaves
`Corrected contract artifacts are committed and pushed` unchecked. Its
`Current work` section still says the Interp stage correction is in progress.

`docs/PAPER_PORTFOLIO_PLAN.md`, Section 15, says the next step is to commit the
corrected baseline. Commit
`0a9ace04d7e718723aa3fb69aba6320b02eb2f55` already exists on `master` and
`origin/master`.

These statements are conservative and do not authorize work, so they are not a
Major finding. They should be refreshed at the next correction commit.

## Required Ownership Verification

### No L54 claim enters ICBINB

The active ICBINB contract contains no L54 claim.

- `docs/CLAIM_REGISTRY.md`, Section `ICBINB-BIO claims`, assigns active claims
  to L52, L55, L56, L57, and the L55 versus L57 part of L58.
- `docs/PAPER_PORTFOLIO_PLAN.md`, Sections 4 and 7.3, reserves L54 for the
  catalytic paper and excludes it from ICBINB.
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 3, 9.2, 13.5, and 15, excludes
  L54 from the ICBINB result bundle.
- The historical ICBINB directory is explicitly historical under
  `docs/submissions/STATUS.md`, and the package checker rejects it with return
  code 1.

Result: No L54 claim is in the active ICBINB contract. The historical package
is correctly rejected and is not required to be upload-ready. Future mechanical
enforcement fails because M-01 accepts a hash-valid L54 ledger artifact and
M-02 can ignore prohibited text in the compiled PDF.

### No steering claim enters Interp

The active Interp contract contains no steering claim.

- `docs/CLAIM_REGISTRY.md`, Section `Interp4Discovery claims`, limits INT-01
  through INT-03 to contact enrichment, ablation damage, matched controls, and
  correlational replication.
- `docs/PAPER_PORTFOLIO_PLAN.md`, Sections 8.1, 8.2, and 8.6, excludes steering
  claims, protocols, results, and figures.
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Sections 1 and 15, defines only
  contact-attention and ablation claims and bars imported steering results.
- The historical Interp directory is explicitly historical under
  `docs/submissions/STATUS.md`, and the package checker rejects it with return
  code 1.

Result: No steering claim is in the active Interp contract. The historical
package is correctly rejected and is not required to be upload-ready. Future
mechanical enforcement fails because M-01 accepts a hash-valid steering ledger
artifact and M-02 can ignore prohibited text in the compiled PDF.

## Exact Statistical Provenance

The committed `docs/STATISTICAL_CONTRACT_ACCEPTANCE.md`, Sections `Reviewed
State`, `Exact Inputs`, `Decision`, and `Source Plan Hash`, accepts an earlier
dirty-worktree candidate identified by exact file hashes:

- plan:
  `085f558db973e8115600f020b3a9bd8fe79537f50297a43eb098f65525300b12`;
- manifest:
  `2097e7374cb389e9090c7b69c215a383c98c6236bb43586a23c6430d55ca3322`.

At the reviewed correction commit, the exact hashes are:

- plan:
  `f8b06e8f2ebd1d6e7324ed5f56b9ba507d70aaf5e5583f9b2d089e2eb820986f`;
- manifest:
  `42e6193041d07fb4c3f9c81ea4d48b1b04744eaac693e107ffe7066f60e83476`.

The current plan hash exactly matches the source-plan hash recorded in the
opening metadata of `docs/ICBINB_EXPERIMENT_MANIFEST.md`. There is no committed
statistical acceptance for these exact correction-commit bytes.

The status boards now state that the earlier candidate passed and that exact
correction-commit review is pending. This corrects prior M-01 without claiming
new provenance. The pending exact statistical review is a working
contract-freeze block, not a new contract defect.

## Prior Finding Disposition

Every finding in `docs/CONTRACT_COMMIT_REVIEW.md` was rechecked.

| Prior finding | Correction-commit result |
|---|---|
| M-01, statistical acceptance did not name committed bytes | Corrected conservatively. The committed boards now say exact correction-commit review is pending. No committed acceptance covers the current bytes. |
| M-02, ownership checker boundary incomplete | Text and filename bypasses were corrected, and CSV and artifact hashes are bound. Semantic ledger bypasses remain under M-01, and the compiled PDF bypass remains under M-02 in this review. |
| M-03, Interp cohort and discovery stages incomplete | Corrected. Pre-lock producers, post-lock producers, exact stage locks, parent locks, handoff inputs, and command order are explicit. Implementation remains correctly blocked. |
| N-01, status boards described a pre-commit state | The old baseline state was corrected, but the boards are again one commit behind under N-01 in this review. |

The statistical and consistency findings summarized in
`docs/CONTRACT_REVIEW_RESOLUTION.md` were also checked for regression. Claim
wording, estimands, ICBINB exact paths, deadlines, freeze keys, command
interfaces, and source-plan binding remain corrected. Consistency finding M-10
is reopened in narrower form by M-03 because the role identities do not enforce
all stated read barriers.

## Interp Producers, Locks, and Ordering

The correction to the Interp production chain is complete at the contract
level.

- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 13.0, defines pre-lock
  `discovery-manifest` and `candidate-cohort` producers.
- Sections 13.2 and 13.3 define post-lock `build-cohort` and
  `build-discovery`, with exact stage lock contents and parent hashes.
- Section 13.4 makes matching consume accepted cohort and discovery stage
  locks and defines the three-lock handoff.
- Section 13.10 gives exact inputs for `match`, `accept-matching`, `ablate`,
  `analyze`, `gate`, and `verify`.
- The fixed order is feasibility work, final lock, cohort and discovery,
  matching acceptance, ablation, analysis, gate, independent review, ledger,
  and verification. No confirmation command creates a final-lock input.

The lock carrier is valid JSON with status `feasibility_draft`. Its 20 keys
exactly match Section 16. Every value, provenance note, approval, and validation
is null. This correctly prevents the final lock.

## Correctly Blocked Implementation

The following are implementation or evidence blockers, not added contract
findings:

- `plm_steering.icbinb_audit` is absent.
- The audited L52, L55, L56, and L57 command interfaces are absent.
- L52 mapping, L55 seed metadata, L56 row-level artifacts, and historical model
  revision pins remain unresolved.
- `plm_steering.interp4discovery` and
  `tests/test_interp4discovery_contract.py` are absent.
- All 20 Interp final-lock values and approvals are null.
- Interp confirmation artifacts and clean active manuscript packages do not
  exist.
- Exact correction-commit statistical acceptance is not committed.

The contracts prohibit execution through these states. Their absence is not
evidence that the target interfaces fail their contracts because the contracts
explicitly require the interfaces to remain unavailable until implemented and
tested.

## Checks Run

- Verified branch, full `HEAD`, remote refs, requested commit, requested tree,
  clean index, and initially clean worktree before reading.
- Ran `.venv/bin/python -m pytest -p no:cacheprovider -q`.
  Result: 152 passed in 3.52 seconds.
- Ran the focused ownership suite.
  Result: 34 passed in 0.18 seconds.
- Compiled `plm_steering` and `tests` with bytecode output outside the
  repository. Result: passed.
- Ran the checker on both historical submission directories. Both returned 1
  and were rejected as required.
- Rechecked the four prior prohibited-text bypasses. All are now rejected and
  covered by tests.
- Ran five semantic ownership and compiled-PDF adversarial cases. All returned
  empty violation lists, confirming M-01 and M-02.
- Ran all five guarded legacy module commands with target-style arguments. All
  returned 1, all evidence hashes were unchanged, and no requested output was
  created.
- Recomputed all ten explicit manifest input hashes. All matched.
- Recomputed the plan SHA-256 and compared it with the manifest source-plan
  hash. Both were
  `f8b06e8f2ebd1d6e7324ed5f56b9ba507d70aaf5e5583f9b2d089e2eb820986f`.
- Parsed the Interp lock carrier and compared its 20 keys and null fields with
  preregistration Section 16. They matched.
- Inspected feasibility, final-lock, cohort, discovery, matching, handoff,
  ablation, analysis, gate, review, ledger, and verification ordering.
- Confirmed that the intentionally blocked target modules and focused Interp
  test are absent.
- Ran JSON, ASCII, prohibited-dash, trailing-whitespace, Python compilation,
  Git diff, and `git show --check` checks. They passed.

## Gate Decision

HOLD the contract-freeze gate.

Zero Critical and Major findings are required for ACCEPT. This commit has three
Major findings. Do not start experiment worktrees or paper execution from this
commit. Correct M-01 through M-03, refresh the conservative status boards, and
run exact-commit statistical and contract reviews on the next committed tree.
