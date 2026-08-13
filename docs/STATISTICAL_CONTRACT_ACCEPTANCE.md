# Statistical Contract Acceptance

Date: 2026-08-13

Reviewer role: Independent statistical contract reviewer

Scope: Resolution of M1 from
`docs/STATISTICAL_CONTRACT_FINAL_REVIEW.md` only

## Reviewed State

Git HEAD:

`3c7c27cd805e0b5baae9685f0e6c4b272a8fa3db`

The worktree was dirty when the review inputs were captured. It had 6 modified
tracked files and 23 untracked files before this report was created. HEAD does
not identify the reviewed contract text. The hashes below identify the exact
inputs.

## Exact Inputs

- `docs/STATISTICAL_CONTRACT_FINAL_REVIEW.md`
  SHA-256:
  `135f69938ebac620f3e8d0d6bc3556cd2d860392d209af9c32c0238449b6ef7d`
- `docs/PAPER_PORTFOLIO_PLAN.md`
  SHA-256:
  `085f558db973e8115600f020b3a9bd8fe79537f50297a43eb098f65525300b12`
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`
  SHA-256:
  `2097e7374cb389e9090c7b69c215a383c98c6236bb43586a23c6430d55ca3322`
- `docs/CLAIM_REGISTRY.md`
  SHA-256:
  `be0e3a2bf238a5dadd15bce49d53ca2249d8c8a40d34632caa06c3f6a71a3017`

## Decision

M1 resolution: Accepted

Remaining Critical contract findings: 0

Remaining Major contract findings: 0

## M1 Verification

The prior finding was that the plan and manifest said the audit detected
confounding, while ICB-03 supported only a performance pattern consistent with
confounding.

The current plan corrects all relevant paper-level L56 wording:

- Section 7.1, `Product contract`, separates detected endpoint mismatch from a
  performance pattern consistent with source-organism confounding.
- Section 7.3 calls L56 an endpoint-mismatch and grouped-validation sensitivity
  case.
- Section 7.4 calls the mechanism endpoint mismatch and grouped-validation
  sensitivity. Its lesson says grouped-validation changes are evidence
  consistent with confounding, not proof of its cause.
- Section 7.6 limits the minimum package to endpoint mismatch and a
  grouped-validation pattern consistent with source-organism confounding.

The current manifest makes the same correction:

- Section 1 describes the L56 mechanism as endpoint mismatch and a
  grouped-validation pattern consistent with source-organism confounding.
- Section 2 keeps ICB-02 as weaker validation performance for measured T-cell
  response.
- Section 2 keeps ICB-03 as a performance fall under organism-grouped
  evaluation that is consistent with source-organism confounding.
- Section 2 limits the paper-level claim to a performance pattern consistent
  with source-organism confounding.
- Section 3 calls L56 an endpoint-mismatch and grouped-validation sensitivity
  case.
- Section 6 is titled `L56 endpoint-mismatch and grouped-validation
  sensitivity study`.
- Sections 6.1 through 6.3 retain the H2b boundary that a performance fall is
  consistent with confounding but does not identify confounding as the sole
  cause.

These statements remain consistent with `docs/CLAIM_REGISTRY.md`, Sections
`ICB-02` and `ICB-03`. ICB-02 supports the endpoint-performance comparison.
ICB-03 supports the grouped-validation sensitivity result and its limited
confounding interpretation. The correction does not change either estimand,
statistical unit, provenance label, required analysis, or acceptance rule.

The phrase `decisive confound analysis` in manifest Section 6.2 names the
registered grouping analysis. It does not expand the paper claim because H2b,
the paper-level claim, and the acceptance rule all retain the
consistent-with-confounding limit.

## Source Plan Hash

Current `docs/PAPER_PORTFOLIO_PLAN.md` SHA-256:

`085f558db973e8115600f020b3a9bd8fe79537f50297a43eb098f65525300b12`

Recorded in `docs/ICBINB_EXPERIMENT_MANIFEST.md`, opening metadata:

`085f558db973e8115600f020b3a9bd8fe79537f50297a43eb098f65525300b12`

The hashes match exactly.

## New Issue Check

The correction narrows claim wording without changing the statistical
contract. It does not alter the L56 units, endpoint definitions, estimands,
clustered uncertainty, provenance, missingness rules, acceptance conditions,
or fail-closed implementation gates.

No new Critical or Major statistical contract issue was introduced.

## Checks Run

- Compared the prior M1 text with every current L56 paper-level statement in
  the plan and manifest.
- Compared all corrected statements with registry claims ICB-02 and ICB-03.
- Searched both files for direct claims that the audit detects or proves
  endpoint or source-organism confounding. The only broad-form match was inside
  the explicit prohibition against claiming that confounding is proven as the
  only cause.
- Recomputed the plan, manifest, registry, and prior-review SHA-256 values.
- Compared the current plan SHA-256 with the value recorded in the manifest.
- Ran `git diff --check`.
- Ran trailing-whitespace, ASCII, and prohibited-dash scans on the reviewed
  files.

## Commit-Gate Recommendation

Pass the statistical contract commit gate. Commit the complete contract
baseline from the reviewed worktree, then run the required exact-commit
consistency review. This acceptance does not authorize experiment execution.
The existing implementation and artifact gates remain in force.
