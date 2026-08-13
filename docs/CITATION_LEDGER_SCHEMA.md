# Citation Ledger Schema

Schema version: 1.0

State: PRE-DRAFT SCHEMA

The citation ledger is populated before manuscript text is finalized. One
source may support several external claims, but each claim-source relation
has its own row.

## Required columns

| Column | Meaning |
|---|---|
| `citation_id` | Stable local identifier |
| `paper_id` | Owning paper |
| `external_claim` | Exact claim supported by the source |
| `source_title` | Verified title |
| `authors` | Verified author list |
| `year` | Publication or release year |
| `venue` | Journal, conference, repository, or website |
| `doi` | DOI when available |
| `stable_url` | Official or archival URL |
| `accessed_on` | Access date for web sources |
| `source_type` | Primary research, review, documentation, policy, or dataset |
| `support_scope` | What the source supports and what it does not support |
| `verification_status` | `verified`, `partial`, `unavailable`, or `rejected` |
| `verified_by` | Independent reviewer ID |
| `nearest_related_work` | Required for a novelty claim |
| `search_date` | Required for a novelty claim |

## Validation

The citation reviewer must reject:

- a source that was not opened or otherwise verified;
- a DOI, title, author list, or venue that does not match the source;
- a citation used for a broader claim than its reported evidence;
- a novelty claim without a dated search and nearest related work;
- a manuscript citation that has no ledger row;
- an anonymous review artifact that reveals author identity.
