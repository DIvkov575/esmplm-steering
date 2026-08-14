# Statistical Contract Commit Review

Review date: 2026-08-13

Reviewer role: Independent statistical contract reviewer

Decision: HOLD

Critical findings: 0

Major findings: 1

Minor findings: 0

Submission blockers: 1

## Exact Commit Boundary

Requested commit:
`0a9ace04d7e718723aa3fb69aba6320b02eb2f55`

Resolved object type: `commit`

Resolved tree:
`c53e0ca074aa7153b373b02ae2b816949d676611`

The resolved commit and tree exactly match the requested values. HEAD was the
requested commit, and `git status --short` was empty before review. All reviewed
contract files were tracked at that commit. This report is a new untracked file
and does not change the reviewed commit.

Maxwell's review was not used as statistical evidence or as a source for the
findings below.

## Exact Inputs

SHA-256 values:

| Input | SHA-256 |
|---|---|
| `docs/PAPER_PORTFOLIO_PLAN.md` | `f8b06e8f2ebd1d6e7324ed5f56b9ba507d70aaf5e5583f9b2d089e2eb820986f` |
| `docs/CLAIM_REGISTRY.md` | `be0e3a2bf238a5dadd15bce49d53ca2249d8c8a40d34632caa06c3f6a71a3017` |
| `docs/ICBINB_EXPERIMENT_MANIFEST.md` | `42e6193041d07fb4c3f9c81ea4d48b1b04744eaac693e107ffe7066f60e83476` |
| `docs/INTERP4DISCOVERY_PREREGISTRATION.md` | `3f0385a944c2ff7ff910f9e4a374a7cb1c8894006f75e15aa119c46554dc2ad4` |
| `docs/INTERP4DISCOVERY_LOCK_VALUES.json` | `25341829e7341bd71a72f3c808bb0a5527ee56209c0e493023a6ff40758ab94d` |
| `docs/RESULT_LEDGER_SCHEMA.md` | `20fdbbf4f4aedc310b58b4d1f5b288343f9a82546c82716829a02f7760e4af08` |
| `docs/COHORT_MANIFEST_SCHEMA.md` | `aad50a3e321309cef49680bbc41222310bf34b4d57a15a69c65603572fe42b9b` |
| `docs/CITATION_LEDGER_SCHEMA.md` | `a2c300d2ebe997e75892c92b6abece6184439d6d3b949b71b4c68f9e294714e6` |
| `docs/CONTRACT_REVIEW_RESOLUTION.md` | `a66b9e8fad80de6ba6462028939a8613c555886b69a193df5de619c25a650b90` |
| `docs/EXECUTION_LEDGER.md` | `aa0f319df1c372c3debe2e38d45226ea1716c9e045ebb31048e8d0aeb87ce177` |
| `docs/PAPER_PORTFOLIO_REVIEW.md` | `0eed51d6348ade7a8d93c7c40212af0f2237b3694501790c1d78defc79623b51` |
| `docs/STATISTICAL_CONTRACT_REVIEW.md` | `1cebaff7961a07782755aba3f0e273832ef217c62b9f1d07f7da9cf9796a04b1` |
| `docs/STATISTICAL_CONTRACT_REREVIEW.md` | `aa4c1024d8d1bd3deda69b1c3c423c77e658324b2990d20755d6bc18b8c2d22b` |
| `docs/STATISTICAL_CONTRACT_FINAL_REVIEW.md` | `135f69938ebac620f3e8d0d6bc3556cd2d860392d209af9c32c0238449b6ef7d` |
| `docs/STATISTICAL_CONTRACT_ACCEPTANCE.md` | `47dae0f142f0e7fdd87b1e37d3b8dc349fb81fa11c235466b2cb0ea23439ceab` |

The ICBINB manifest records source-plan SHA-256
`f8b06e8f2ebd1d6e7324ed5f56b9ba507d70aaf5e5583f9b2d089e2eb820986f`.
It exactly matches the reviewed plan.

## Major Finding

### M1. ICB-03 has no defined length or composition confound analysis

Contract anchors:

- `docs/CLAIM_REGISTRY.md`, Section `ICB-03`, `Control` and `Gate to confirm`,
  lines 84 through 89.
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 6.2, `Fixed design and
  denominators`, lines 352 through 384.
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 6.3, `H2 acceptance and
  failure`, lines 389 through 411.
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 11.2, `L56`, lines 730 through
  739.

ICB-03 requires group-aware evaluation and explicit checks for species,
length, and composition. Its confirmation gate requires the audit bundle to
identify which estimate changes under each confound control.

The manifest defines the organism control well. It specifies paired
random-fold and organism-grouped predictions, equal organism weighting,
organism-clustered resampling, `delta_grouping`, and within-organism reporting.
It does not define a length control or a composition control for the
full-length ICB-03 estimate. It gives no estimand, adjustment or stratification
rule, uncertainty method, or decision rule for either control.

As written, H2 can pass when `delta_grouping` is positive even though the
length and composition parts of the registered ICB-03 gate were never run.
The acceptance rule therefore does not support the full registered gate.

Required correction: either define the full-length length and composition
controls before execution, including their estimands and reporting rules, or
narrow the ICB-03 `Control` and `Gate to confirm` fields to the organism-grouped
analysis that the manifest actually specifies. This needs a new reviewed
commit.

## Prior Statistical Findings

No prior Critical or Major issue reappears in the procedures that were
corrected. The following rules are defensible:

- The generation estimand is the fixed saved protein cohort under realized
  masks and controls. Protein-level paired resampling matches that estimand.
- The two-part generation analysis reports technical failure and low
  complexity over all attempts, then reports score change only among jointly
  scoring-valid pairs. It does not call the conditional estimate an
  unconditional effect.
- Low complexity is separate from technical or scoring failure.
- L52 pairing fails closed when source identity and array order cannot be
  verified.
- L55 seeds are described as whole-run joint perturbations, not isolated
  direction seeds.
- L57 uses failure of a positive rule and does not infer equivalence from a
  non-significant result.
- The Interp estimand treats proteins as sampling units and heads as one fixed
  finite set. Joint resampling preserves shared controls, methods, and matched
  sets.
- The Interp positive and equivalence branches have explicit multiplicity,
  missing-result, precision, and fail-closed rules.
- The result ledger uses one controlling row per claim and links that row to
  immutable detailed artifacts. This is adequate for multi-estimate claims
  because `analysis/confirmatory_statistics.json` must contain all ten Interp
  contrasts, adjusted intervals, p-values, precision checks, and branch
  reasons. Confirmation also requires every required estimate and interval,
  a passing gate, verified hashes, and independent review.

The ICB-03 mismatch in M1 is an independently identified issue. It is not a
failure of the organism-grouped estimator itself.

## Correctly Blocked Implementation

The following work is incomplete but is not an additional contract finding:

- L52 source mapping must verify or the study must rerun with identifiers.
- L55 seeds 0, 1, and 2 must be reproduced with explicit seed metadata.
- L56 row-level cohorts, predictions, folds, exclusions, and clustered
  summaries do not yet exist.
- All 20 Interp lock values are null under `feasibility_draft`.
- Interp confirmation commands and their focused contract test are not yet
  implemented.
- Interp margins, precision simulation, owners, final cohort, matching,
  ablations, analysis, gate, review, and populated result ledger do not yet
  exist.

The current contracts stop the affected experiment or claim before these
items can be used. They must remain blocked. Correcting M1 does not authorize
execution.

## Checks Run

- Verified the requested object type, full commit, tree, HEAD, and initial
  clean worktree.
- Recomputed SHA-256 for every input listed above.
- Compared the ICBINB recorded source-plan hash with the plan SHA-256. Exact
  match.
- Parsed `docs/INTERP4DISCOVERY_LOCK_VALUES.json` with `jq`.
- Compared all Section 16 lock-key names with the JSON keys. Both sets contain
  the same 20 keys.
- Verified status `feasibility_draft`, 20 lock entries, and 20 entries with all
  four required values null.
- Ran `.venv/bin/python -m pytest -p no:cacheprovider -q`: 152 passed.
- Ran `.venv/bin/python -m pytest -p no:cacheprovider
  tests/test_submission_ownership.py -q`: 34 passed.
- Ran `git diff --check`: passed before this report was created.
- Scanned the reviewed contract inputs for non-ASCII bytes and trailing
  whitespace: no matches.
- Cross-checked claim IDs, statistical units, estimands, denominators,
  missing-result rules, thresholds, multiplicity, equivalence, precision,
  seed interpretation, stage ordering, ledger requirements, and stop rules.

## Gate Recommendation

HOLD the contract-freeze and experiment-execution gate.

Zero Critical findings remain, but one Major contract finding remains.
Resolve M1 in a new commit and repeat an exact-commit statistical review.
