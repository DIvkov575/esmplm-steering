# Result Ledger Schema

Schema version: 1.1

State: PRE-RUN SCHEMA

The result ledger has exactly one controlling row for every claim assigned to
the paper by `docs/SUBMISSION_CONTRACT.json`. Negative, failed, stopped,
deferred, and excluded analyses remain in the ledger. Only a fully validated
confirmed row may authorize an artifact in a submission package.

## Contract files

The package verifier uses four hash-locked authorities:

- `docs/CLAIM_REGISTRY.md` supplies the exact public claim text.
- `docs/SUBMISSION_CONTRACT.json` supplies the complete paper claim set and
  fixed per-claim semantics.
- `docs/ARTIFACT_OWNERSHIP.json` records known artifact hashes and their true
  paper and claim ownership.
- the paper-specific `role_assignments.json` binds result producers, the paper
  owner, and independent reviewers.

The reviewed verifier fixes the canonical paths and expected hashes for
`docs/SUBMISSION_CONTRACT.json` and `docs/ARTIFACT_OWNERSHIP.json`. It also
fixes the complete claim-ID set for each paper. A package cannot select a
replacement contract, catalog, or smaller claim set by supplying a new path or
coherent set of new hashes. Changing one of these authorities requires a source
change and review of the exact resulting commit.

The submission contract records the exact claim-registry and
artifact-ownership hashes. The package allowlist records the canonical
submission-contract path and hash, the artifact-ownership hash, and the
paper-specific role-file path and hash. Any mismatch fails closed.

## CSV encoding

The ledger is a UTF-8 CSV file named `result_ledger.csv`. Its header includes
every required column below. Artifact lists and `source_study_ids` use JSON
array encoding inside their CSV cells. Paths and hashes match by array
position. A plain string, delimiter-separated list, JSON object, or `null` is
invalid for an array field.

`claim_text_sha256` is the SHA-256 of the UTF-8 registered claim text. Form the
text by joining the nonempty block-quote lines under the claim's `Claim:`
field with one ASCII space.

## Required columns

| Column | Meaning |
|---|---|
| `claim_id` | Exact claim ID required for this paper by the submission contract |
| `paper_id` | Owning paper |
| `claim_text_sha256` | Hash of the registered claim text |
| `source_study_ids` | JSON array exactly equal to the contract study ownership |
| `claim_status` | `conditional`, `confirmed`, `rejected`, `deferred`, or `stopped` |
| `status_reason` | Required explanation for every nonconfirmed status |
| `provenance` | Exact contract value: `prospective`, `retrospective`, or `post_hoc_sensitivity` |
| `estimand` | Exact quantity and conditioning event fixed by the submission contract |
| `statistical_unit` | Exact independent unit fixed by the submission contract |
| `control` | Exact frozen comparison fixed by the submission contract |
| `cohort_manifest_path` | Repository-relative path to the frozen cohort manifest |
| `cohort_manifest_sha256` | Exact frozen cohort-manifest hash |
| `experiment_manifest_path` | Repository-relative path to the frozen experiment contract or final preregistration lock |
| `experiment_manifest_sha256` | Exact frozen experiment-manifest hash |
| `lineage_manifest_path` | Repository-relative path to the claim artifact-lineage manifest |
| `lineage_manifest_sha256` | Exact artifact-lineage manifest hash |
| `raw_artifact_paths` | Exact repository-relative paths, with no wildcard |
| `raw_artifact_sha256` | Hash for every raw path |
| `derived_artifact_paths` | Exact repository-relative paths |
| `derived_artifact_sha256` | Hash for every derived path |
| `point_estimate` | Typed JSON result object |
| `interval` | Typed JSON interval object |
| `denominator` | Typed JSON denominator object |
| `gate_result` | `pass`, `fail`, `not_estimable`, or `not_run` |
| `limitation` | Exact claim boundary fixed by the submission contract |
| `review_status` | Pointer to a machine-readable review decision, or an explicit non-review reason |
| `source_git_commit` | Full 40-character source commit |

## Typed result fields

When the submission contract marks a field `required`, a confirmed row uses
these forms:

```json
{"status":"reported","value":{"primary":0.12}}
```

```json
{
  "status": "reported",
  "level": 0.95,
  "method": "paired organism-clustered bootstrap",
  "bounds": {"lower":0.03,"upper":0.21},
  "interpretation": "The interval is above zero."
}
```

```json
{"status":"reported","counts":{"attempted":100,"retained":84}}
```

The point-estimate `value` is a finite number, a nonempty list of numeric
values, or a nonempty object whose leaves are numeric values. Strings,
booleans, `null`, `NaN`, and infinite values are invalid at every nesting
level.

Interval `bounds` is either a two-number `[lower, upper]` list or a nonempty
keyed object whose leaves are objects containing exactly `lower` and `upper`.
Every bound is finite and every lower bound is no greater than its upper bound.
The interval level is greater than zero and no greater than one. Method and
interpretation are nonempty.

Denominator `counts` is a nonempty object with nonempty keys and nonnegative
integer values. Use descriptive flat keys when a claim needs several
denominators.

When the contract marks a field `not_applicable`, use:

```json
{"status":"not_applicable","reason":"One fixed direction pair has no sampling interval."}
```

A nonconfirmed row whose analysis did not produce the field uses:

```json
{"status":"not_available","reason":"Stopped before estimation because the cohort lock failed."}
```

Blank cells and untyped prose are invalid.

## Status rules

- `confirmed` requires `gate_result = pass`, no status reason, complete
  manifests and artifacts, all contract-required typed results, and accepted
  independent review.
- `conditional` and `deferred` use `gate_result = not_run`.
- `rejected` uses `fail` or `not_estimable`.
- `stopped` uses `fail`, `not_estimable`, or `not_run`.
- Every nonconfirmed row has a nonempty status reason.
- Nonconfirmed rows remain valid ledger history but never enter the package
  artifact-authorization map.
- Every supplied path and hash is validated even when the row is not
  confirmed.

A negative or failure-focused registered claim still uses `confirmed` and
`gate_result = pass` when its own statement and acceptance rule are supported.

## Artifact lineage

Each confirmed row points to one UTF-8 JSON lineage manifest:

```json
{
  "schema_version": "1.0",
  "paper_id": "interp4discovery",
  "claim_id": "INT-01",
  "source_git_commit": "40 hexadecimal characters",
  "experiment_owner_id": "assigned experiment owner",
  "claim_registry_sha256": "64 hexadecimal characters",
  "submission_contract_sha256": "64 hexadecimal characters",
  "cohort_manifest_path": "path/to/cohort_manifest.json",
  "cohort_manifest_sha256": "64 hexadecimal characters",
  "experiment_manifest_path": "path/to/preregistration_lock.json",
  "experiment_manifest_sha256": "64 hexadecimal characters",
  "status": "locked",
  "parent_locks": [
    {
      "path": "path/to/accepted_stage_lock.json",
      "sha256": "64 hexadecimal characters"
    }
  ],
  "artifacts": [
    {
      "path": "path/to/confirmatory_statistics.json",
      "sha256": "64 hexadecimal characters",
      "kind": "derived",
      "source_study_id": "INTERP4DISCOVERY-CONFIRMATORY",
      "derivation": "Analysis command and fixed transformation that produced this artifact.",
      "parents": [
        {
          "path": "path/to/analysis_stage_lock.json",
          "sha256": "64 hexadecimal characters"
        }
      ]
    }
  ]
}
```

The producer must be an experiment owner in the locked role file. Every
artifact and parent has a safe path, existing file, and matching hash. Every
artifact has a nonempty derivation statement and at least one parent. The
manifest cannot contain a self-reference or cycle. Its artifact set must
exactly equal the row's raw and derived arrays, including kind, path, hash, and
source study.

The cohort and experiment manifests are validated as data, not only by file
hash. Each one records schema version `1.0`, paper ID, a nonempty experiment
ID, claim IDs that include the current claim, source commit, submission
contract hash, role-assignment hash, the contract's exact source-study list,
and an assigned experiment owner. A cohort manifest has status `frozen`. An
experiment manifest has status `frozen` or `locked`.

Each parent-lock file is also validated as data. It records schema version
`1.0`, paper ID, claim IDs that include the current claim, source commit,
submission-contract hash, role-assignment hash, an assigned experiment owner,
and status `accepted` or `locked`. Its nonempty artifact list contains exact
paths, hashes, and source-study IDs allowed by the claim contract.

Every lineage parent must be one of the following:

- another artifact node in the same acyclic lineage;
- the row's validated cohort or experiment manifest;
- an artifact declared by a validated parent lock; or
- a known catalog artifact permitted for the paper and claim.

An existing file and a matching self-reported hash are not enough.

If an artifact or lineage ancestor hash occurs in
`docs/ARTIFACT_OWNERSHIP.json`, that catalog entry must permit both the target
paper and claim. This check rejects renamed foreign bytes, including L54
outputs in ICBINB-BIO and steering outputs in Interp4Discovery. The package
scanner checks every file against known catalog hashes regardless of filename
extension. Renaming known result bytes to a text-source extension does not
remove the allowlist requirement.

The catalog may retain a known hash for a deleted historical artifact by
setting `canonical_present` to `false`. Such an entry must authorize no paper
or claim. This preserves the excluded byte identity without restoring the
historical result to the current tree.

## Independent review decision

A confirmed row's `review_status` contains only a decision pointer:

```json
{
  "decision_path": "reviews/ICB-01.review.json",
  "decision_sha256": "64 hexadecimal characters"
}
```

The referenced JSON decision contains:

- schema version, paper ID, and claim ID;
- assigned reviewer ID and `statistical_reviewer` or
  `final_technical_reviewer` role;
- decision and structured findings;
- source commit;
- claim-registry, submission-contract, and role-assignment hashes;
- canonical ledger-row payload hash;
- cohort, experiment, and lineage manifest paths and hashes;
- the exact raw and derived artifact set.

The canonical row payload excludes only `review_status`. Encode all other CSV
columns as a JSON object with sorted keys, compact separators, and UTF-8, then
take SHA-256. This avoids a circular hash while binding every scientific and
provenance field.

An accepted decision has `decision = accepted` and no unresolved Critical or
Major finding. Findings are structured objects with `severity` and `resolved`;
the verifier derives blocking status from those objects rather than trusting
duplicated counts in the ledger. The reviewer ID and role must match the role
file and differ from every paper and experiment owner.

A nonconfirmed row may use:

```json
{"status":"not_required","reason":"The claim was stopped before independent review."}
```

This identity binding is not a digital signature. It enforces the repository
role contract but does not prove physical authorship outside a trusted
execution system.

## Validation

The verifier rejects:

- a missing, extra, or duplicate controlling claim row;
- a row whose claim text or fixed semantics differ from the contract;
- an invalid status and gate combination;
- a blank or malformed typed result;
- a wildcard, absolute, escaping, missing, or hash-mismatched path;
- any package symlink, including a symlinked package root, a broken link, a
  link to a directory, or a metadata file beneath a symlinked directory;
- a symlinked repository metadata root;
- a repository-relative authority, manifest, lock, artifact, parent, or review
  path with any symlinked component;
- an incomplete confirmed row;
- a confirmed row with no artifact;
- a lineage producer outside the assigned experiment owners;
- a malformed or contract-mismatched cohort manifest, experiment manifest, or
  parent lock;
- a lineage artifact set that differs from the row;
- a missing, undeclared, self-referential, cyclic, or foreign parent;
- a review decision that is HOLD, stale, mismatched, self-reported only, or
  written under a prohibited owner-reviewer identity;
- ICBINB-BIO evidence owned by L43, L48, L49, or L54;
- Interp4Discovery evidence from any steering experiment;
- an exact registered claim sentence without a complete confirmed-row
  authorization.

Validation order is fixed: file shapes and paths, contract hash pins, complete
claim set and row semantics, role assignments, manifests and lineage, known
artifact ownership, review decision, confirmed-row authorization, and package
allowlist coverage.

## Submission evidence allowlist

Every clean submission package that contains figures or result artifacts
includes `ownership_allowlist.json`:

```json
{
  "paper_id": "interp4discovery",
  "claim_registry_sha256": "64 hexadecimal characters",
  "submission_contract_path": "docs/SUBMISSION_CONTRACT.json",
  "submission_contract_sha256": "64 hexadecimal characters",
  "role_assignments_path": "plm_steering/interp4discovery_out/run-id/role_assignments.json",
  "role_assignments_sha256": "64 hexadecimal characters",
  "artifact_ownership_sha256": "64 hexadecimal characters",
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

Package paths are relative to the submission package. Ledger, contract, role,
lineage, and catalog paths are relative to the repository root supplied as
`--ledger-root`. Every packaged evidence file has exactly one allowlist entry
and must match an artifact authorized by a confirmed row. The contract path and
hash and the artifact-ownership hash must equal the canonical trust anchors in
the reviewed verifier. The package cannot replace those authorities.

The root manuscript PDF is named `paper.pdf` and is not treated as a result
artifact. Every other PDF requires evidence authorization, including another
PDF at the package root. The verifier extracts text from root PDFs with
`pdftotext` and applies the prohibited-claim scan used for manuscript sources.
Missing extraction support, an unreadable PDF, or an extraction error fails
closed.

Only these root manuscript-source paths are exempt from evidence
authorization:

- `paper.tex`
- `reference.bib`
- `neurips_2026.sty`
- `paper.bbl`

The verifier applies both fixed token checks and the broader ICBINB
claim-boundary scan to all four exempt source paths and to `paper.pdf`. It
treats line breaks as sentence whitespace and uses a conservative lexical
policy. The allowlist consists of the exact six ICBINB claim sentences in
`docs/CLAIM_REGISTRY.md` only for claims whose complete ledger rows validate
as `confirmed`, the two paper-level audit sentences, and the six exact boundary
sentences in `docs/ICBINB_EXPERIMENT_MANIFEST.md`. Documented risky wording,
close registered-claim restatements, negations, and disclaimers are rejected.

The lexical guard cannot prove that arbitrary prose is not a semantic
paraphrase. A nonexact result claim is unauthorized even if the guard does not
flag it. Before upload, the assigned final technical reviewer must inspect the
complete source and rendered PDF, map every result claim to an exact registered
sentence, paper-level sentence, or boundary sentence, and block any mismatch.
A clean verifier result is necessary but does not by itself approve manuscript
prose.

Every other package file requires evidence authorization unless it is
recognized verifier metadata. A text-like suffix does not create an
exemption. In particular, renamed or modified evidence in `.txt`, `.md`,
`.py`, or another source format must be allowlisted like any other packaged
result.
