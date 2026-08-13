# Result Ledger Schema

Schema version: 1.0

State: PRE-RUN SCHEMA

The result ledger has exactly one controlling row per claim ID in
`docs/CLAIM_REGISTRY.md`. Negative, failed, stopped, and excluded analyses
remain in the ledger.

## File encoding

The ledger is a UTF-8 CSV file named `result_ledger.csv`. Its header must
include every required column below. The four artifact-list cells use JSON
array encoding inside the CSV cell:

- `raw_artifact_paths`
- `raw_artifact_sha256`
- `derived_artifact_paths`
- `derived_artifact_sha256`

For example, a two-file path cell is
`["results/a.json","results/b.csv"]`. An empty list is `[]`. Paths and hashes
match by array position. A plain string, delimiter-separated list, JSON
object, or `null` is invalid for these four columns.

The CSV has no editable top-level lock field. A submission package locks the
exact ledger bytes by recording the ledger SHA-256 in
`ownership_allowlist.json`.

## Required columns

| Column | Meaning |
|---|---|
| `claim_id` | Exact registry ID |
| `paper_id` | Owning paper |
| `claim_text_sha256` | Hash of the registered claim text |
| `claim_status` | `conditional`, `confirmed`, `rejected`, `deferred`, or `stopped` |
| `provenance` | `prospective`, `retrospective`, or `post_hoc_sensitivity` |
| `estimand` | Exact quantity and conditioning event |
| `statistical_unit` | Independent unit or `fixed_descriptive_object` |
| `control` | Frozen comparison |
| `cohort_manifest_path` | Repository-relative path |
| `cohort_manifest_sha256` | Frozen cohort hash |
| `experiment_manifest_path` | Repository-relative path |
| `experiment_manifest_sha256` | Frozen experiment hash |
| `raw_artifact_paths` | Exact repository-relative paths, with no wildcard |
| `raw_artifact_sha256` | Hash for every raw path |
| `derived_artifact_paths` | Exact repository-relative paths |
| `derived_artifact_sha256` | Hash for every derived path |
| `point_estimate` | Value or `null` with a reason |
| `interval` | Bounds, level, method, and interpretation |
| `denominator` | Attempted, retained, and conditioned counts |
| `gate_result` | `pass`, `fail`, `not_estimable`, or `not_run` |
| `limitation` | Required claim boundary |
| `review_status` | Reviewer ID, severity findings, and resolution |
| `source_git_commit` | Full source commit |

## Validation

The verifier must reject:

- a claim ID missing from the registry;
- two controlling rows for one claim;
- a wildcard or absolute artifact path;
- a favorable result without failed attempts and exclusions;
- a number without an immutable source artifact;
- a `confirmed` status with an unresolved critical or major finding;
- ICBINB evidence from L43, L48, L49, or L54;
- Interp evidence from steering experiments;
- a claim that is broader than the registered text.

For `claim_status = confirmed`, the verifier must also require:

- `gate_result = pass`;
- every required raw and derived artifact hash verifies;
- every required denominator, estimate, and interval is present;
- independent review is complete;
- no required analysis is `not_run` or `not_estimable`;
- no unresolved critical or major finding exists.

A negative or failure-focused claim still uses `gate_result = pass` when its
registered statement and acceptance rule are supported.

## Submission evidence allowlist

Each clean submission package that contains figures or other result artifacts
must include `ownership_allowlist.json`. The file has this structure:

```json
{
  "paper_id": "interp4discovery",
  "result_ledger_sha256": "64 hexadecimal characters",
  "artifacts": [
    {
      "path": "figures/contact_ablation.pdf",
      "sha256": "64 hexadecimal characters",
      "claim_id": "INT-01",
      "ledger_artifact_path": "plm_steering/interp4discovery_out/run-id/analysis/contact_ablation.pdf"
    }
  ]
}
```

`path` is relative to the submission package. `ledger_artifact_path` is the
exact repository-relative path in one raw or derived artifact array for the
same claim. Both files must exist and have the same SHA-256. Paths must use
POSIX separators and cannot be absolute, contain wildcards, or escape their
respective roots. Every packaged evidence file must have exactly one allowlist
entry.
