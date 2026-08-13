# Statistical Contract Final Review

Date: 2026-08-13

Reviewer role: Independent statistical contract reviewer

Review type: Final blocker-only review of the current uncommitted worktree

## Reviewed State

Git HEAD:

`3c7c27cd805e0b5baae9685f0e6c4b272a8fa3db`

The worktree was dirty when the review inputs were captured. It had 6 modified
tracked files and 22 untracked files before this report was created. Most
controlling contract files were untracked, so HEAD alone does not identify the
reviewed contract state. The hashes below identify the exact reviewed inputs.
This review does not certify a committed revision.

## Exact Inputs Reviewed

| Input | SHA-256 |
|---|---|
| `docs/STATISTICAL_CONTRACT_REREVIEW.md` | `aa4c1024d8d1bd3deda69b1c3c423c77e658324b2990d20755d6bc18b8c2d22b` |
| `docs/CONTRACT_REVIEW_RESOLUTION.md` | `79e704e9f8c6ffe13a44997392d3536d07d4a3be2cb6851b4daf462ba1d60e1e` |
| `docs/PAPER_PORTFOLIO_PLAN.md` | `241a487226fcd906ae728c42371d40b83f9ab898e120bb7f33ccb6b5b93cd004` |
| `docs/CLAIM_REGISTRY.md` | `be0e3a2bf238a5dadd15bce49d53ca2249d8c8a40d34632caa06c3f6a71a3017` |
| `docs/COHORT_MANIFEST_SCHEMA.md` | `aad50a3e321309cef49680bbc41222310bf34b4d57a15a69c65603572fe42b9b` |
| `docs/RESULT_LEDGER_SCHEMA.md` | `85b997c78355489a764aa96a6b1421f3c5c605d9abc170ebc6083cd4faa80d20` |
| `docs/CITATION_LEDGER_SCHEMA.md` | `a2c300d2ebe997e75892c92b6abece6184439d6d3b949b71b4c68f9e294714e6` |
| `docs/ICBINB_EXPERIMENT_MANIFEST.md` | `72d621bc52ad5452ce019ad6a9c5e84d85b5ce1e112d30dfa778a7bfc944b279` |
| `docs/INTERP4DISCOVERY_PREREGISTRATION.md` | `bc4424263e8f0bd0902e60eaa8ffaa57afdcd8bbf2394529862be79501bdaf6f` |
| `docs/INTERP4DISCOVERY_LOCK_VALUES.json` | `25341829e7341bd71a72f3c808bb0a5527ee56209c0e493023a6ff40758ab94d` |
| `docs/EXECUTION_LEDGER.md` | `448c0041a50626a1f466196afdb910f042ac368c5ed422ee29ce6b6e73ad9d9d` |
| `docs/ARTIFACT_INVENTORY.md` | `aac90d40d7bfff2e4fbc1b560ce9f6d57d76dfd46d50e415745961ea52d63881` |

## Decision

Remaining Critical contract findings: 0

Remaining Major contract findings: 1

## Prior Major Verification

| Prior finding | Final result | Exact contract anchors |
|---|---|---|
| M1, ICB-01 low-complexity wording | Corrected. The claim names low-complexity outputs and the historical filter. It does not call every low-complexity output invalid. | `docs/CLAIM_REGISTRY.md`, Section `ICB-01`; `docs/PAPER_PORTFOLIO_PLAN.md`, Section 3; `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 4.2 through 4.4 |
| M2, L56 provenance | Corrected. ICB-02 is a retrospective endpoint audit and ICB-03 is a post-hoc grouping sensitivity analysis in both controlling files. | `docs/CLAIM_REGISTRY.md`, Sections `ICB-02` and `ICB-03`; `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 2 |
| M3, L56 H2a resampling unit | Corrected by narrowing the contract. H2a targets fixed deduplicated peptide cohorts, uses unique peptides as singleton units, and states that related-peptide dependence may be understated. This is defensible for the narrow fixed-cohort stability claim. It does not support a broader peptide-population claim. | `docs/CLAIM_REGISTRY.md`, Section `ICB-02`; `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 6.2; `docs/COHORT_MANIFEST_SCHEMA.md`, Sections `Record fields` and `Validation` |
| M4, confirmed result-ledger rows could fail open | Corrected. Confirmation requires a passing gate, verified artifacts, complete estimates and denominators, completed independent review, and no required `not_run` or `not_estimable` analysis. | `docs/RESULT_LEDGER_SCHEMA.md`, Section `Validation` |
| M5, Interp final-lock construction cycle | Corrected. The contract separates non-authorizing feasibility work from `ready_for_final_lock` and the immutable final lock. `ROLE_HANDOFF` contains owners and scopes, while the accepted matching hash is recorded later in `matching/handoff.json`. | `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Sections 2, 13.0, 13.4, 13.9, and 16 |

The Interp command order is now:

`feasibility-init -> benchmark -> candidate-cohort -> matching-simulate -> precision-plan -> feasibility-lock -> lock -> build-cohort -> match -> accept-matching -> ablate -> analyze -> gate -> verify`

The explicit gate command is present in
`docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 13.9, `Required commands`.
The 20 Section 16 keys exactly match the 20 JSON keys. The JSON status is
`feasibility_draft`, and all 20 values are null. This correctly prevents the
final lock and confirmation execution.

The source-plan hash in `docs/ICBINB_EXPERIMENT_MANIFEST.md`, opening metadata,
matches the current `docs/PAPER_PORTFOLIO_PLAN.md` hash:

`241a487226fcd906ae728c42371d40b83f9ab898e120bb7f33ccb6b5b93cd004`

## Major Finding

### M1. The paper-level ICBINB contract still overstates the confounding result

Exact anchors:

- `docs/PAPER_PORTFOLIO_PLAN.md`, Section 7.1, `Product contract`, thesis
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 2, `Fixed claims`,
  paper-level claim
- `docs/CLAIM_REGISTRY.md`, Section `ICB-03`, claim and main limitation
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 6.1 through 6.3, H2b and its
  acceptance rule

The plan says the checks detect endpoint confounding. The manifest paper-level
claim says the checks detect source-organism confounding. The registered claim
and H2b support only a fall in performance under organism-grouped evaluation,
which is a pattern consistent with source-organism confounding. They explicitly
do not identify confounding as the sole cause.

A grouped-validation performance drop can also reflect reduced effective
sample size, distribution shift, or model instability. The acceptance rule
therefore cannot support direct detection of confounding. The broader
paper-level wording could change the interpretation even when every H2 gate
passes.

Narrow both paper-level statements to say that the audit detects a performance
pattern consistent with source-organism confounding. Refresh the ICBINB
source-plan hash after changing the plan.

## Correctly Blocked Implementation

The missing ICBINB audit module, audited runner interfaces, verified L52 source
mapping, reproduced L55 seed bundles, and L56 row-level outputs are
implementation tasks. `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 13, 15,
and 16 block execution or claim confirmation until they exist and verify.

The Interp target commands and focused contract tests are not implemented, and
all lock values remain null. `docs/INTERP4DISCOVERY_PREREGISTRATION.md`,
Sections 13.9, 14, and 16 correctly block the final lock and confirmation work.
These are not additional contract findings.

## Checks Run

- `.venv/bin/python -m pytest -p no:cacheprovider -q`: 123 passed in 5.41
  seconds.
- `jq empty docs/INTERP4DISCOVERY_LOCK_VALUES.json`: passed.
- JSON key count, Section 16 row count, and exact key-name comparison: 20, 20,
  and exact match.
- Lock status and null-value check: `feasibility_draft` and 20 null values.
- ICBINB recorded source-plan hash versus current plan hash: exact match.
- Static inspection of the Interp state transition, command dependencies,
  matching handoff, explicit gate command, and fail-closed verifier: passed.
- Claim-registry, manifest, cohort-schema, result-ledger, and execution-ledger
  consistency checks: passed except for M1.
- `git diff --check`: passed for tracked changes. Because controlling files are
  untracked, separate trailing-whitespace, ASCII, and prohibited-dash scans
  were run over the active contract inputs and passed.

## Gate Recommendation

Hold the contract-freeze gate. Narrow the two confounding statements in M1,
refresh the source-plan hash, commit the complete contract baseline, and run
the exact-commit review. Experiment execution remains blocked by the stated
implementation gates until their required code, artifacts, values, and tests
exist.
