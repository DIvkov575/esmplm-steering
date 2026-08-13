# Contract Consistency Review

Date reviewed: 2026-08-13

Decision: NOT READY TO FREEZE

Submission blockers: 11 total, consisting of 1 Critical finding and 10 Major
findings.

Minor findings: 4.

## Scope

This review covers:

- `docs/PAPER_PORTFOLIO_PLAN.md`
- `docs/PAPER_PORTFOLIO_REVIEW.md`
- `docs/CLAIM_REGISTRY.md`
- `docs/EXECUTION_LEDGER.md`
- `docs/ARTIFACT_INVENTORY.md`
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`

The review checks claim ownership, prohibited evidence, artifact paths,
commands, freeze rules, dates, roles, and cross-document contradictions.

The reviewed files were not committed. Git HEAD was
`3c7c27cd805e0b5baae9685f0e6c4b272a8fa3db`, and all seven contract files were
untracked. Several contract files changed while this review was in progress.
The findings were rechecked after the contract-relevant revisions, but this
report is not a freeze attestation. The cross-document review must run again
against the final committed contract revision.

## Required Boundary Verification

| Boundary | Contract claim check | Evidence and package check | Result |
|---|---|---|---|
| No L54 claim enters ICBINB-BIO | No active registry claim assigns L54 to ICBINB-BIO. The plan reserves L54 for the catalytic paper, and the ICBINB manifest excludes it. See `PAPER_PORTFOLIO_PLAN.md`, Section 4 and Section 7.3; `CLAIM_REGISTRY.md`, Sections "ICBINB-BIO claims" and "Rejected and deferred claims"; `ICBINB_EXPERIMENT_MANIFEST.md`, Section 3. | `ICB-06` points to a mixed L58 JSON and an `*.npy` wildcard that include L54 data. The current ICBINB manuscript and one current figure also contain L54 material. See `CLAIM_REGISTRY.md`, Section ICB-06; `ARTIFACT_INVENTORY.md`, Sections "Saved research outputs" and "ICBINB-BIO package." | Claim text passes. Evidence isolation and current package fail. |
| No steering claim enters Interp4Discovery | The active Interp registry claims and preregistration concern contact enrichment and head ablation only. No steering claim appears in that contract. See `CLAIM_REGISTRY.md`, Section "Interp4Discovery claims"; `INTERP4DISCOVERY_PREREGISTRATION.md`, Section 1. | The current Interp manuscript is mainly a steering paper, and all three current Interp figures are steering figures. See `ARTIFACT_INVENTORY.md`, Section "Interp4Discovery package." | Contract text passes. Current package fails. |

The required ownership boundaries therefore exist in the intended claims, but
neither boundary is clean at the artifact and package level.

## Critical Findings

### C-01: The required ICBINB runner commands fail open and can overwrite evidence

`ICBINB_EXPERIMENT_MANIFEST.md`, Section 13.3, says the new runner interfaces
are not implemented and must fail closed. Section 16 confirms that the L52,
L55, L56, and L57 runners do not implement the required output, revision, and
separate seed arguments. `ARTIFACT_INVENTORY.md`, Section "Research source
files," says these runners use hard-coded seeds and output paths.

A static interface check found no argument parser in those runners. Python
therefore does not reject the documented flags. It starts the old hard-coded
run. L52, L55, and L57 then target their existing `l*_repro_out/results.json`
paths. L56 targets
`plm_steering/data_cache/immunogenicity/l56_proxy_validation_summary.json`,
even though Section 13.3 says it must write outside the cache.

The test command in `ICBINB_EXPERIMENT_MANIFEST.md`, Section 13.2, also uses
the default `python3`. That is Python 3.14 in this workspace. The exact command
failed during collection because `torch` and `sklearn` were absent. The same
focused tests passed as 80 tests under `.venv/bin/python`. This matches
`EXECUTION_LEDGER.md`, Section "Environment baseline."

Impact: A worker following the manifest can ignore the frozen seed and output
contract, overwrite tracked source evidence, and record a misleading command.
This is a research-integrity failure mode.

Required resolution: Implement strict parsers that require every documented
argument, reject unknown arguments, refuse existing output paths unless an
explicit safe policy allows them, and write only to the audit output root.
Use `.venv/bin/python` in every command. Add command-interface tests before any
runner is allowed to execute.

## Major Findings

### M-01: ICB-06 admits prohibited L54 evidence through broad paths

`CLAIM_REGISTRY.md`, Section ICB-06, lists
`plm_steering/l58_vector_geometry_out/results.json` and
`plm_steering/l58_vector_geometry_out/*.npy` as supporting files. The wildcard
includes `l54_catalytic_steering_vectors.npy`, and the JSON includes pairwise
entries involving L54.

`ICBINB_EXPERIMENT_MANIFEST.md`, Sections 3 and 9.2, permits only the L55 versus
L57 entry and prohibits the L54 entries and vector. `ARTIFACT_INVENTORY.md`,
Sections "Case-level status" and "Saved research outputs," also classifies the
L58 bundle as mixed.

Impact: The registry and manifest define different evidence sets for the same
claim. The broad registry paths prevent a verifier from proving that no L54
evidence entered ICBINB-BIO.

Required resolution: Replace both broad references with exact L55 and L57
vector paths and the extracted
`plm_steering/icbinb_audit_out/cases/l58/l55_l57_geometry.json` artifact.

### M-02: Both current submission packages violate their ownership contracts

`ARTIFACT_INVENTORY.md`, Section "ICBINB-BIO package," states that the current
paper includes attention-head and L54 material. Its first figure contains L54.
The same inventory, Section "Interp4Discovery package," states that the current
paper is mainly a steering paper and that all three figures are steering
figures.

The required removals are explicit in `PAPER_PORTFOLIO_PLAN.md`, Sections 7.2,
7.9, 8.2, and 8.6. They are also stop conditions in
`ICBINB_EXPERIMENT_MANIFEST.md`, Section 15, and
`INTERP4DISCOVERY_PREREGISTRATION.md`, Section 15.

Impact: The current files cannot serve as fallback packages, draft inputs, or
submission evidence under the new contracts.

Required resolution: Mark the current packages as historical only. Build clean
paper directories from the locked result ledgers. Add a package check that
rejects L54 and attention-head evidence in ICBINB-BIO and rejects steering
claims, results, and figures in Interp4Discovery.

### M-03: The ICBINB fixed claims do not map one-to-one to the claim registry

`CLAIM_REGISTRY.md` has six active ICBINB claims, ICB-01 through ICB-06.
`ICBINB_EXPERIMENT_MANIFEST.md`, Section 2, replaces them with five IDs, C1
through C5. C2 combines ICB-02 and ICB-03. Section 12.3 then requires one
result-ledger row per manifest claim rather than one row per registry claim.
This conflicts with `PAPER_PORTFOLIO_PLAN.md`, Sections 5.1 and 5.4.

There are also content conflicts:

- Manifest C2 gives one combined claim a retrospective provenance label.
  `CLAIM_REGISTRY.md`, Section ICB-02, labels the endpoint gate prospective,
  while Section ICB-03 labels the grouping explanation retrospective.
- Manifest C4 adds that the positive conditional disorder-score direction
  repeats across all three seeds. `CLAIM_REGISTRY.md`, Section ICB-04, owns
  only the change in the residue-exclusion interpretation.
- Manifest C4 labels seed 0 a retrospective reconstruction and seeds 1 and 2
  post-hoc. The registry gives ICB-04 one post-hoc provenance label.

Impact: Change control, provenance labels, and result-ledger rows cannot be
traced to the controlling claim IDs. C2 and C4 may exceed or contradict the
registry.

Required resolution: Preserve ICB-01 through ICB-06 in the manifest and result
ledger. Split the L56 claims. Reconcile the exact L55 wording and L57
provenance before freeze.

### M-04: L55 failure has two different paper-level consequences

`PAPER_PORTFOLIO_PLAN.md`, Section 7.6, says that failed L55 reproduction
removes the multi-seed claim and triggers a review of whether L57 alone still
supports the composition mechanism.

`ICBINB_EXPERIMENT_MANIFEST.md`, Sections 7.3 and 15, first allows removal of
C4 and review, but its paper stop rule then requires both the L57 shortcut claim
and the L55 seed-sensitivity claim.

Impact: The same L55 outcome can either allow a narrowed paper or stop the
submission. The go or no-go decision is not deterministic.

Required resolution: Choose one rule. If L57 alone may preserve the third
mechanism, define the exact review gate. If L55 is mandatory, update the plan
and registry to say so.

### M-05: The pre-experiment freeze requires different artifacts in different documents

`PAPER_PORTFOLIO_PLAN.md`, Section 5, says five artifacts are frozen before any
new experiment: the claim registry, cohort manifest, experiment manifest,
result ledger, and citation ledger.

`EXECUTION_LEDGER.md`, Section "Contract-freeze gate," can close without a
cohort manifest, result ledger, or citation ledger. `ARTIFACT_INVENTORY.md`,
Section "Required artifacts that are absent," says all three are absent.

The plan is also unclear about how a result ledger that links immutable outputs
can be populated before those outputs exist.

Impact: Different workers can reach different decisions about whether
experiments are authorized.

Required resolution: Separate pre-run schema locks from post-run populated
ledgers. Put the same named pre-run artifacts in the plan, execution ledger,
and paper-specific freeze validators.

### M-06: There is no single reviewed baseline for the contract set

`ICBINB_EXPERIMENT_MANIFEST.md` records source plan SHA-256
`dcc2dc146be1a660651e706d7a505cbaeb92f10a8477b7528be561461f4bebf5`.
The reviewed plan bytes do not have that hash.

`ARTIFACT_INVENTORY.md`, Section "Narrative and planning files," contains
earlier hashes for the plan, registry, ledger, and ICBINB manifest. Its scope
notice allows later contract changes, but no later reconciliation record
identifies which version controls execution.

The status text also conflicts. `PAPER_PORTFOLIO_PLAN.md`, Section 15, says the
plan awaits approval and the registry and manifests are not started.
`EXECUTION_LEDGER.md`, Sections "Current work" and "Completed work," says the
author directed execution and the registry and manifests exist.

Impact: A commit could freeze a manifest derived from an older plan while the
execution board reports a different gate state.

Required resolution: Select one exact contract revision, update every source
hash and status board to that revision, commit it, and rerun this review on the
committed files.

### M-07: The Interp freeze marker does not cover every required decision

`INTERP4DISCOVERY_PREREGISTRATION.md`, opening status and Section 14, make
resolution of every `DECISION TO FREEZE` marker the condition for opening the
confirmation panel.

Section 16 also requires numerical hook-isolation,
perturbation-calibration, and method-sensitivity thresholds. These values have
no corresponding `DECISION TO FREEZE` marker in the body. Section 13.1 requires
expected artifact paths, but Sections 13.1 through 13.8 provide only
basenames, not exact repository-relative paths.

Impact: A mechanical check can resolve every marked field while required
thresholds and artifact paths remain unset.

Required resolution: Give every unresolved value a unique lock key, exact
value, review record, and validation rule. Make the opening authorization
depend on the complete key set, not a text search for markers.

### M-08: Interp has no runnable command or exact output-path contract

`PAPER_PORTFOLIO_PLAN.md`, Section 14.1, requires an exact reproduction command
for an experiment to be done. `INTERP4DISCOVERY_PREREGISTRATION.md`, Section
13, defines artifact schemas but names no runner module, command, output root,
focused test command, or verification command.

`ARTIFACT_INVENTORY.md`, Sections "Tests" and "Required artifacts that are
absent," confirms that the current code and tests do not implement the required
matching, continuous outcomes, mean replacement, persistence, or verification.

Impact: Two workers can implement different directory layouts and command
interfaces while both claim to follow the preregistration. Reproduction cannot
be checked from the contract.

Required resolution: Add exact repository-root commands, an exact output root,
all expected repository-relative paths, focused tests, and a verifier that
fails on missing fields, hashes, heads, positions, or gate conditions.

### M-09: Interp artifact immutability starts after the decision that consumes the artifacts

`INTERP4DISCOVERY_PREREGISTRATION.md`, Section 2, requires position matches to
be locked before ablation results are summarized. Section 13.8 says all raw and
derived artifacts become immutable only after the August 20 gate.

The gate in Section 15 consumes those raw and derived artifacts. The current
wording therefore permits changes before the gate without requiring a new
experiment ID or amendment.

Impact: The inputs to the gate decision do not have a complete immutability
boundary.

Required resolution: Make cohort, matching, intervention, raw-output, and
analysis artifacts append-only and hashed when each stage closes. Require a new
experiment ID and linked amendment for every later correction, including
corrections before the gate.

### M-10: The Interp matching information barrier has no matching role contract

`INTERP4DISCOVERY_PREREGISTRATION.md`, Section 2, requires a matching worker who
does not receive ablation output. `PAPER_PORTFOLIO_PLAN.md`, Section 11.2,
assigns the whole independent panel and causal analysis to one Interp
experiment owner. Neither `PAPER_PORTFOLIO_REVIEW.md`, Section "Active contract
workers," nor `EXECUTION_LEDGER.md`, Section "Current work," defines a matching
worker or an access boundary.

Impact: The stated leakage control is not enforceable through the recorded
roles and write scopes.

Required resolution: Assign separate matching and ablation owners, or define a
technical handoff that prevents the matching process from reading ablation
outputs. Record both owners, paths, hashes, and handoff acceptance before
opening the confirmation panel.

## Minor Findings

### N-01: The August 15 cutoff has inconsistent precision

`CLAIM_REGISTRY.md`, Section ICB-04, says "by August 15."
`PAPER_PORTFOLIO_PLAN.md`, Section 7.6, says "the end of August 15."
`ICBINB_EXPERIMENT_MANIFEST.md`, Sections 3 and 15, defines
`2026-08-15 23:59 Anywhere on Earth`.

Use the exact timestamp everywhere. The manifest value is the most precise.

### N-02: Registry supporting-file fields mix evidence with narrative

`CLAIM_REGISTRY.md`, Sections ICB-01 through ICB-05, lists narrative Markdown
documents in the same `Supporting files` field as numeric outputs.
`ARTIFACT_INVENTORY.md`, Sections "Scope and terms" and "Narrative and planning
files," states that narrative is not empirical evidence.

Use separate fields for empirical evidence, analysis code, and narrative
context.

### N-03: The active orchestrator has no stable recorded agent ID

`EXECUTION_LEDGER.md`, Section "Current work," identifies the orchestrator as
`Codex main session` with agent ID `current session`.
`PAPER_PORTFOLIO_PLAN.md`, Section 11.2, requires one named agent and agent ID
for every active role in `PAPER_PORTFOLIO_REVIEW.md`.

Record a stable identifier before the contract commit. No currently recorded
person holds a prohibited role combination.

### N-04: "Accepted" is ambiguous for the unresolved Interp draft

`PAPER_PORTFOLIO_REVIEW.md`, Section "Active contract workers," marks the
Interp preregistration draft as accepted. `EXECUTION_LEDGER.md`, Section
"Handoff log," clarifies that only the draft was accepted and freeze remains
blocked.

Use `draft accepted, not frozen, not authorized for execution` in both files.

## Consistent Contracts

The following points are consistent across the reviewed documents:

- L43 is excluded from both active workshop papers.
- L48 and L49 are Interp pilot or discovery evidence only.
- L54 belongs to the later catalytic paper, not an active workshop claim.
- ICBINB-BIO has priority over Interp compute.
- Interp confirmation must stop if the projected core cannot finish by
  2026-08-19.
- Interp can submit only after either the positive branch or the full
  equivalence branch passes.
- No active owner currently holds one of the explicitly prohibited role
  combinations in `PAPER_PORTFOLIO_PLAN.md`, Section 11.2.

## Required Gate Decision

Do not close the contract-freeze gate. Resolve C-01 and M-01 through M-10,
commit one reconciled contract revision, and rerun the cross-document review
against that exact commit. Minor findings should be corrected in the same
revision but do not independently block the gate.
