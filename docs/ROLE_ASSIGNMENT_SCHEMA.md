# Role Assignment Schema

Schema version: 1.0

State: PRE-RUN SCHEMA

Each paper creates one machine-readable `role_assignments.json` before any
result-producing work begins. The submission allowlist locks its exact
SHA-256.

## Required fields

```json
{
  "schema_version": "1.0",
  "paper_id": "icbinb-bio",
  "source_git_commit": "40 hexadecimal characters",
  "orchestrator_id": "stable agent ID",
  "paper_owner_id": "stable agent ID",
  "experiment_owner_ids": [
    "stable agent ID"
  ],
  "statistical_reviewer_id": "stable agent ID",
  "final_technical_reviewer_id": "stable agent ID"
}
```

Every ID uses the canonical ASCII form
`[A-Za-z0-9][A-Za-z0-9._:@/-]{0,127}`. Leading, trailing, and embedded
whitespace is invalid. `experiment_owner_ids` is nonempty and contains no
duplicate. The paper owner, every experiment owner, statistical reviewer, and
final technical reviewer are distinct for the affected paper. The
orchestrator may coordinate work but cannot replace a missing owner or
reviewer.

For Interp4Discovery, the experiment-owner list contains the distinct
discovery, cohort and matching, ablation, and analysis owners recorded in the
final `ROLE_HANDOFF` lock. The Interp paper owner remains separate from all
four.

## Validation

The ownership verifier checks the role file against the paper ID and full
source commit in every result-ledger row. An artifact-lineage manifest must
name one assigned experiment owner. A machine-readable result-review decision
must name either the assigned statistical reviewer or the assigned final
technical reviewer and must state the matching reviewer role.

This file binds stable identities and enforces role separation. It does not
cryptographically prove who created a file. Identity signatures or a trusted
execution service would be required for that stronger claim.
