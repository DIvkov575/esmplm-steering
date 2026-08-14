# Statistical Contract Review for f0c6440

Review date: 2026-08-13

## Decision

ACCEPT

Severity counts:

- Critical: 0
- Major: 0
- Minor: 0

The contract at the reviewed commit has no remaining Critical or Major
statistical finding. The prior Major finding for ICB-03 is resolved. The
remaining work listed below is implementation work that the contracts
correctly block before experiment execution.

## Exact review boundary

- Commit:
  `f0c6440263cf18de0138fb02302b4a8a1bf99832`
- Tree:
  `c6cfb57426c5ae1e2d84a6e4e40304dde5c253f8`
- Parent:
  `0a9ace04d7e718723aa3fb69aba6320b02eb2f55`
- Object type: commit
- Initial worktree state: clean

The full commit and tree were verified before review. The earlier incorrect
hash expansion was not used. Committed bytes were exported to the isolated
snapshot `/private/tmp/esmplm-steering-f0c6440`. Contract review, data checks,
hashing, and tests used that snapshot. Concurrent or later worktree report
files could not affect the review.

Maxwell's new report was not read or used. The prior statistical report was
used only to identify the finding that this review had to recheck.

## Inputs reviewed

SHA-256 values are for the exact committed bytes.

| Input | SHA-256 |
|---|---|
| `docs/PAPER_PORTFOLIO_PLAN.md` | `9a43ed00b7ac5143209fc2a8383c2e53eb906415a88a6cf2939d6cfa2153fa31` |
| `docs/CLAIM_REGISTRY.md` | `bc1fdfe8dc5cb52d13032fbb7efad305bde6ee5b46179d011b1b495901288c7b` |
| `docs/ICBINB_EXPERIMENT_MANIFEST.md` | `2f71554b4d72909bd8648bdcf85947e1cc7e28dbc624b64a40adbaf074aec4a4` |
| `docs/INTERP4DISCOVERY_PREREGISTRATION.md` | `d86b2d836d70fe8e6a90cec3a46d7ac2aca508ee1e52d881bf35e86250da8c83` |
| `docs/INTERP4DISCOVERY_LOCK_VALUES.json` | `25341829e7341bd71a72f3c808bb0a5527ee56209c0e493023a6ff40758ab94d` |
| `docs/RESULT_LEDGER_SCHEMA.md` | `adc424d9f0494bfa0440bbd8085b936bc790ccf7bb53f04c391ca341e47d30e5` |
| `docs/COHORT_MANIFEST_SCHEMA.md` | `aad50a3e321309cef49680bbc41222310bf34b4d57a15a69c65603572fe42b9b` |
| `docs/CITATION_LEDGER_SCHEMA.md` | `a2c300d2ebe997e75892c92b6abece6184439d6d3b949b71b4c68f9e294714e6` |
| `docs/CONTRACT_REVIEW_RESOLUTION.md` | `2d0130f20e1fad9018d9640f893f7dcb89ee42b72699dec2682178c252b6d0af` |
| `docs/EXECUTION_LEDGER.md` | `b5049f16a2a1a7ac162cbc0f47f5ec53daf88b0dce8834fd9c4563aaf9420479` |
| `docs/PAPER_PORTFOLIO_REVIEW.md` | `7dfb3612e3429cb131a6440626753f42938f5ab0de0f2eb93ab5814341260540` |
| `docs/STATISTICAL_CONTRACT_COMMIT_REVIEW.md` | `adc8f1dd99625e772a857b51cbd76adcf52fbfecb0cbfebf6950ed7aa0803e85` |

Relevant committed source, tests, cached inputs, and historical result bundles
were also inspected where needed to test whether the specified analyses are
executable.

## Prior Major finding disposition

Status: RESOLVED

The prior finding was that ICB-03 required a grouped-validation interpretation
without a fixed analysis that separated sequence composition from sequence
length.

The corrected contract now fixes:

- length-only, composition-only, and composition-plus-length models;
- identical random and organism-grouped fold assignments across models;
- equal total weight for each organism;
- training-fold-only scaling for log sequence length;
- a fixed weighted least-squares implementation;
- paired organism-clustered bootstrap uncertainty;
- a positive grouping difference with a 95 percent interval above zero for
  both composition models;
- mandatory reporting of the length-only diagnostic without a directional
  pass rule.

Evidence:

- `docs/CLAIM_REGISTRY.md`, ICB-03, lines 70-89.
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 6.2, lines 342-411.
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 6.3, lines 416-443.
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 11.2, lines 762-773.

The fixed source data can support this design. The committed cohort has 1,024
usable full-length antigens from 160 organisms. Sequence lengths range from 61
to 400. The residue-composition matrix has shape 1,024 by 20. Composition and
log-length values are finite, and each composition row sums to 1. The fixed
minimum-norm least-squares rule handles the intercept and composition
collinearity without making predictions ambiguous.

The historical summary was also readable and internally coherent:

- random-fold correlation: `0.37912861081700555`;
- organism-grouped correlation: `-0.3225885143129409`;
- mean within-organism correlation: `0.05615293134265087`.

These historical values do not pass the new claim by themselves. The contract
requires the corrected weighted models, row-level predictions, and paired
clustered intervals before ICB-03 can be confirmed.

## Complete statistical contract assessment

No Critical, Major, or Minor contract defect was found in the following areas.

### Statistical units, dependence, and weighting

Generation studies use source protein as the independent unit, preserve
within-protein arm pairing, and do not treat residues as independent
observations. L56 gives each organism equal total weight and uses organisms as
bootstrap clusters for grouping differences. ICB-06 is limited to one fixed
direction pair and does not treat layers as independent replication.

Evidence:

- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 4.1, lines 96-114.
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 6.2, lines 344-411.
- `docs/CLAIM_REGISTRY.md`, ICB-06, lines 133-149.

### Estimands, missingness, and two-part generation analysis

The generation contract separates failure risk over all attempted generations
from conditional score change among scoring-valid paired outputs. Technical
failures receive no property score but remain in the attempted denominator.
Low-complexity status is recorded separately. This prevents complete-case
filtering from hiding failed generations.

Evidence:

- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 1, lines 35-38.
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 4.2 through 4.5, lines
  115-203.
- `docs/PAPER_PORTFOLIO_PLAN.md`, Section 7.5, lines 312-330.

### Thresholds, uncertainty, equivalence, and multiplicity

Retrospective and post-hoc analyses are labeled as such. Fixed thresholds are
not presented as prospective evidence. Stability intervals have stated units
and resampling rules. ICBINB does not turn an interval containing zero into an
equivalence claim. Interp equivalence, familywise error, precision, and failed
replicate rules must be fixed and validated before final lock.

Evidence:

- `docs/PAPER_PORTFOLIO_PLAN.md`, Section 7.3, lines 288-294.
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 11.1 through 11.3, lines
  734-791.
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Sections 14 through 16, lines
  860-948.

### Seed interpretation

The ICBINB seed registry gives each random purpose a named role. It explicitly
states that the L55 legacy seed changes several parts of a run together and
cannot isolate direction-build sensitivity. The claim registry and prohibited
claims use the same limitation.

Evidence:

- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 10, lines 703-732.
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 2, lines 61-73.
- `docs/CLAIM_REGISTRY.md`, ICB-04, lines 91-110.

### Interp lock ordering and decision gates

`feasibility_draft` authorizes discovery-only feasibility work.
`ready_for_final_lock` requires all 20 values and their provenance, approval,
and validation. The final lock consumes the reviewed feasibility lock and is
the first artifact that can authorize confirmation work. The explicit command
order prevents confirmation outputs from creating final-lock inputs.

The final GO rule requires both inferential and precision conditions. It also
requires complete artifacts and frozen source and model revisions.

Evidence:

- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 13.10, lines 753-858.
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 15, lines 880-904.
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Section 16, lines 906-948.

### Ledger encoding and provenance

The result ledger has one controlling row per claim. It preserves failed,
stopped, and excluded analyses, uses positional JSON arrays for paths and
hashes, fixes source-study ownership, records exact estimands and denominators,
and prevents confirmation when required estimates, intervals, artifacts, or
independent review are missing.

ICB-06 correctly names L55 and L57 as source studies because they own the
source vectors. L58 is the derived geometry diagnostic, not an independent
source experiment.

Evidence:

- `docs/RESULT_LEDGER_SCHEMA.md`, File encoding, lines 7-56.
- `docs/RESULT_LEDGER_SCHEMA.md`, Required columns and Validation, lines
  58-111.
- `docs/RESULT_LEDGER_SCHEMA.md`, Submission evidence allowlist, lines
  113-151.
- `docs/COHORT_MANIFEST_SCHEMA.md`, lines 7-65.

### Claim and source-plan binding

The ICBINB manifest records this source-plan SHA-256:

`9a43ed00b7ac5143209fc2a8383c2e53eb906415a88a6cf2939d6cfa2153fa31`

The independently computed SHA-256 of the committed
`docs/PAPER_PORTFOLIO_PLAN.md` is identical. The paper-level L56 wording,
ICB-02, ICB-03, and the manifest gates consistently limit the inference to
fixed cohorts, observed validation performance, and a pattern consistent with
confounding. They do not claim that confounding is proven or that sequence
cannot predict immune endpoints.

Evidence:

- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, lines 11-14 and 45-73.
- `docs/PAPER_PORTFOLIO_PLAN.md`, Sections 7.1 through 7.6, lines 245-361.
- `docs/CLAIM_REGISTRY.md`, ICB-02 and ICB-03, lines 49-89.

## Checks run

- Verified the object type, full commit, tree, and parent.
- Exported and reviewed only the exact committed snapshot.
- Ran the full committed test suite: 165 passed in 4.34 seconds.
- Ran the focused contract ownership suite: 47 passed in 0.37 seconds.
- Parsed `docs/INTERP4DISCOVERY_LOCK_VALUES.json` with `jq empty`.
- Verified that the carrier status is `feasibility_draft`.
- Verified that all 20 required lock keys exist and currently have null value,
  provenance, approval, and validation fields.
- Verified that the JSON key set exactly matches preregistration Section 16.
- Recomputed the source-plan SHA-256 and matched it to the manifest binding.
- Ran `git diff-tree --check` against the parent commit.
- Checked the reviewed contract inputs for non-ASCII bytes and trailing
  whitespace.
- Loaded the committed L56 source data and checked cohort size, organism count,
  lengths, composition shape, finite values, and row sums.

## Remaining implementation blockers

These are not contract defects. The contracts identify them and fail closed
before experiment execution:

1. `plm_steering.icbinb_audit` is not implemented.
2. The required L52, L55, L56, and L57 audited runner interfaces and metadata
   writers are not implemented.
3. L52 source mapping still needs identifier-level verification or a compliant
   rerun.
4. L55 seed bundles need explicit seed metadata and clean reproduction.
5. L56 still needs the three-model row-level predictions, frozen folds,
   weights, scalers, exclusions, clustered bootstrap output, and full
   provenance required by the corrected contract.
6. All 20 Interp lock values remain unresolved.
7. Interp margin selection, precision simulation, owner assignments,
   confirmation commands, result ledger, verification, and paper handoff are
   not implemented.
8. Focused tests for the new audit interfaces and fail-closed verification
   remain required.

Evidence:

- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Sections 13.2 through 13.5, lines
  887-1013.
- `docs/ICBINB_EXPERIMENT_MANIFEST.md`, Section 16, lines 1091-1114.
- `docs/INTERP4DISCOVERY_PREREGISTRATION.md`, Sections 13.10 through 16, lines
  753-948.
- `docs/EXECUTION_LEDGER.md`, Contract-freeze gate, lines 73-88.

## Gate recommendation

Accept the statistical contract at
`f0c6440263cf18de0138fb02302b4a8a1bf99832`. Record this acceptance against
that exact commit. Keep the experiment-execution gate closed until every
contract-freeze item and the implementation blockers above are resolved and
verified. Do not treat this contract acceptance as authorization to run the
blocked experiments or confirm any registered claim.
