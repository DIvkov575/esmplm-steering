# Cohort Manifest Schema

Schema version: 1.0

State: PRE-RUN SCHEMA

Each experiment creates a paper-specific cohort manifest before evaluating
the cohort. JSON is the canonical machine-readable form.

## Root fields

| Field | Requirement |
|---|---|
| `schema_version` | Must equal `1.0` |
| `paper_id` | `icbinb-bio` or `interp4discovery` |
| `experiment_id` | Unique immutable identifier |
| `source_git_commit` | Full commit hash |
| `experiment_manifest_path` | Repository-relative path |
| `experiment_manifest_sha256` | Hash of the frozen manifest |
| `status` | `draft`, `frozen`, or `superseded` |
| `frozen_at_utc` | Required when status is `frozen` |
| `frozen_by` | Stable agent or reviewer ID |
| `source_datasets` | Nonempty list defined below |
| `records` | One row per source protein, peptide, antigen, or PDB chain |
| `exclusion_summary` | Count for every allowed exclusion reason |
| `seed_registry` | One named seed per random purpose |

## Source dataset fields

Each source dataset records:

- repository-relative path or stable official URL;
- source name, release, version, and access date;
- byte size, row count, and SHA-256;
- license when known;
- whether it is tracked, ignored, downloaded, or generated;
- any parent artifact and its hash.

## Record fields

Each record contains:

- stable source identifier;
- sequence or record hash;
- source dataset identifier;
- inclusion status and one frozen exclusion reason when excluded;
- cluster identifier and clustering rule;
- train, development, discovery, confirmation, or evaluation split;
- labels and substrate identifiers when applicable;
- source organism when applicable;
- chain and structure identifiers when applicable;
- every seed that affected selection or assignment.

## Validation

A validator must fail when:

- a required field is missing;
- a path is absolute or outside the repository;
- a hash differs;
- one record appears in prohibited splits or sequence clusters;
- an exclusion reason is not in the frozen manifest;
- one integer silently fills more than one seed role;
- the cohort changed after `frozen_at_utc` without a new experiment ID and
  linked amendment.
