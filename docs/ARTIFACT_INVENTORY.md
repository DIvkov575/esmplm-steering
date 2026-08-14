# Artifact Inventory

Date inspected: 2026-08-13

Repository revision: `3c7c27cd805e0b5baae9685f0e6c4b272a8fa3db`

## Scope and terms

This inventory covers the current evidence relevant to ICBINB-BIO and
Interp4Discovery. It includes L42, L43, and L48 through L58, plus the current
manuscript inputs and local build or test state.

State meanings:

- `Tracked` means the file is present in the current Git tree.
- `Untracked` means the file is present in the worktree but is not in Git.
- `Ignored` means the file is present locally and excluded by `.gitignore`.
- `Historical only` means the file exists in Git history but not in the
  current tree.
- `Absent` means no current file was found.

Evidence meanings:

- `Record data` contains source records such as sequences, labels, or
  structures.
- `Per-generation output` contains generated sequences and per-sequence
  scores.
- `Derived numeric output` contains computed summaries, matrices, vectors,
  or aggregate statistics.
- `Narrative only` contains interpretation or planning text. It is not
  empirical evidence.
- Source code and tests define or check procedures. They are not empirical
  evidence by themselves.

Sizes are in bytes. SHA-256 values are hashes of the file bytes at inspection
time unless the row says historical. Contract files can change during the
review that follows this inventory; their freeze hashes are recorded later.
Directory totals are not used as file hashes.

## Immediate blockers

1. A draft claim registry, program execution ledger, ICBINB experiment
   manifest, and Interp4Discovery preregistration now exist as untracked
   files. They are not frozen. No cohort manifest, empirical result ledger,
   or citation ledger exists in the current worktree.
2. No saved result bundle records a Git source revision, exact model revision,
   dependency environment, or complete separation of dataset, direction,
   mask, control, and bootstrap seeds.
3. L42 has no current runner or result bundle. L43 has no current document,
   source, test, or result bundle. Deleted versions remain available in Git
   history, but they are not current tracked evidence.
4. L48 and L49 outputs are aggregate summaries. They do not save the
   per-position predictions needed for the new continuous, protein-clustered,
   contact-specific analysis.
5. The Interp4Discovery preregistration still has unresolved `DECISION TO
   FREEZE` fields. The independent structure panel, cohort manifest, matching
   records, continuous all-head output, calibration checks, and zero-versus-
   mean replacement results are absent.
6. L51 stores only summaries. Its saved `PASS` conflicts with the corrected
   `KILL` narrative.
7. L54 and L55 seed-specific result files do not record their seed. Their
   runners hard-code `SEED = 0`, so the seed 1 and seed 2 files cannot be
   reproduced from the tracked runner as named.
8. L53 and L57 result files record absolute paths into another checkout.
   L57 points to a different copy of its dataset even though a copy is tracked
   here.
9. L42, L51, L52, L53, L54, L55, and L57 use complete-case filtering after
   generation. No immutable two-part audit bundle reports failure risk over
   all attempts together with the conditional score analysis.
10. No experiment run logs were found. The only current logs are ignored
    LaTeX build logs.
11. Historical result bundles do not identify an exact environment. The new
    `requirements-lock.txt` records the tested Python 3.11 package versions,
    but it does not repair missing provenance in earlier runs.
12. The current ICBINB-BIO manuscript includes attention-head and L54
    material that the portfolio plan excludes. The current
    Interp4Discovery manuscript includes steering material and its build log
    reports six pages against the planned five-page limit.
## Corrections made during inventory review

1. Registry claim `ICB-06` was narrowed to the L55 versus L57 cosine
   diagnostic. It no longer compares either direction with L54.
2. Registry claim `ICB-04` now calls the three L55 files legacy whole-run
   seeds. It does not attribute their differences to direction construction
   alone.

## Case-level status

| Case | Paper ownership | Current evidence | Evidentiary status | Required action |
|---|---|---|---|---|
| L42 | Optional ICBINB-BIO case | Tracked narrative, helper code, unit tests; ignored Meltome data; deleted runner and generated sequences in history | Blocked. No current immutable result bundle or current runner. The historical JSON has generated sequences but no explicit seed, source revision, raw score arrays, or run configuration. | Recover and audit the historical files or rerun with all attempts, scores, failure flags, seeds, configuration, model revision, and source revision saved. Exclude if the cutoff is missed. |
| L43 | None for current workshop corpus | Ignored solubility data and stale bytecode; deleted narrative, source, test, and result JSON in history | Absent from the current tracked tree. It is not eligible evidence under the portfolio plan. | Keep excluded. Historical recovery would require a new ownership decision and a full provenance audit. |
| L48 | Interp4Discovery pilot and historical basis | Eight tracked PDB files, replication matrix, causal aggregate output, code, test, narrative, and an untracked draft preregistration | Pilot evidence only. The output is aggregate and uses one discovery panel, binary accuracy, one selected head, one low-enrichment control, and position-level rather than protein-level uncertainty. The preregistration is not frozen. | Resolve every preregistration decision, hash the lock, build the frozen independent panel, and save row-level continuous outcomes, matching data, calibration, exclusions, and protein-clustered statistics. |
| L49 | Interp4Discovery pilot | Aggregate effects for all 480 heads on 104 sampled positions, code, and narrative | Coarse derived summary only. It has eight effect levels, no saved sampled-position identifiers or per-position predictions, and no contact-specific interaction. | Replace with the prespecified continuous all-head independent-panel analysis. |
| L50 | Shared historical method context | Narrative protocol only | Not empirical evidence. It was written after L42 and does not satisfy the new manifest or two-part analysis contract. | Use only as historical context. Freeze paper-specific manifests before new evaluation. |
| L51 | Optional ICBINB-BIO case | Tracked source data, source code, summary JSON, tests, and corrected narrative | Blocked. The JSON lacks generated sequences and raw scores and stores a conflicting `PASS`. | Rerun or create an immutable derived audit bundle that records original and corrected policies. Exclude if recovery misses the cutoff. |
| L52 | Primary ICBINB-BIO decoder-instability case | Per-generation scores and sequences for 20 arms plus baseline sequences | Usable retrospective raw output, but not yet a paper-ready audit bundle. Seed, source revision, model revision, attempted-generation failure table, and corrected two-part policy are not saved. | Derive and lock the two-part audit bundle from every attempted generation. Record provenance as retrospective or post-hoc as applicable. |
| L53 | Optional ICBINB-BIO boundary case | Per-generation scores and sequences for 11 arms; source data, code, tests, and narrative | Usable retrospective negative result. The result omits eval sequences as a separate field and embeds an absolute path to another checkout. It does not prove the proposed mechanism. | Normalize the dataset path, save split identifiers and full configuration, and use only as a boundary case if included. |
| L54 | Catalytic follow-up only | Three per-generation result files, data, code, tests, and narrative | Excluded from both workshop papers by claim ownership. Seed-specific files do not record seeds and the runner is fixed to seed zero. The outputs measure a scoring surrogate, not turnover. | Reserve for the catalytic paper. Parameterize and reproduce before any later claim. Do not include L54 results in ICBINB-BIO. |
| L55 | ICBINB-BIO composition and seed-sensitivity case; later disorder paper is separate | Three per-generation result files, data, code, tests, and narrative | Blocked for the multi-seed workshop claim. The files do not record seeds and the tracked runner cannot reproduce seed 1 or 2 as named. | Add explicit seed and output-directory parameters, save provenance, reproduce all three seeds from a clean revision, and create a locked audit bundle. |
| L56 | Primary ICBINB-BIO endpoint-mismatch case | Record-level source datasets, reproducible validation code, summary JSON, tests, and narrative | Strong source corpus for a retrospective confounding audit. The summary is derived only and does not save row-level predictions, fold assignments, or a source revision. No steering run exists, by design. | Create a locked derived audit bundle with exact cohorts, split assignments, endpoint definitions, row-level predictions, and confounding statistics. |
| L57 | Primary ICBINB-BIO composition-shortcut case | Per-generation scores and sequences, source data, code, tests, and narrative | Usable retrospective raw output. The result embeds an absolute path to another checkout and lacks source/model revision and explicit seed metadata. | Rebind provenance to the tracked dataset, derive the two-part audit, and lock composition and failure analyses. |
| L58 | Supporting ICBINB-BIO diagnostic, with L54 portions reserved | Three 33 by 1280 float32 vectors and pairwise cosine summaries | One-seed derived diagnostic only. The bundle mixes ICBINB-relevant L55/L57 geometry with excluded L54 material. No seed or source/model revision is stored in the outputs. | Use only the L55/L57 comparison, label it one-seed evidence, and keep L54 results out of ICBINB-BIO. Reproduce under a manifest if retained. |

## Narrative and planning files

These files do not constitute empirical evidence.

| Path | State | Type, size, SHA-256 | Ownership | Status and action |
|---|---|---|---|---|
| `docs/PAPER_PORTFOLIO_PLAN.md` | Untracked | Markdown, 47,533, `dcc2dc146be1a660651e706d7a505cbaeb92f10a8477b7528be561461f4bebf5` | Program | Planning authority for this inventory, but not frozen in Git. Approve and commit before creating paper worktrees. |
| `docs/PAPER_PORTFOLIO_REVIEW.md` | Untracked | Markdown, 6,086, `ae628f19d00cc130f90b1be95b69375e6f0f02bcbec65ef3a71440f436105dcf` | Program | Planning review only. It explicitly does not certify experiments or manuscripts. |
| `docs/CLAIM_REGISTRY.md` | Untracked | Markdown, 10,527, `6d93bdc5f1dec4ebbd8961a4966fbb18d9a5a2845bbdc34110aeecfacef1a427` | Both workshop papers | Draft claim contract, version 0.1. It states that no claim is confirmed. The inventory findings for `ICB-04` and `ICB-06` were corrected after this snapshot. Review, freeze, and commit. Narrative only. |
| `docs/EXECUTION_LEDGER.md` | Untracked | Markdown, 4,209, `6afd185b9f3e7355192a8f6a9c6ce958fdd465e6cd78b8f835cd7728f104ea34` | Program | Program task and handoff ledger, version 0.1. It is not an empirical result ledger and does not link numeric claims to immutable outputs. Narrative only. |
| `docs/ICBINB_EXPERIMENT_MANIFEST.md` | Untracked | Markdown, 40,361, `8351a257e88cda11fe81616c937775eae45da7c6a999c2b6bb1489e78d5a2059` | ICBINB-BIO | Detailed execution contract with fixed claims, two-part analysis, seed registry, output schemas, optional recovery commands, and stop rules. It correctly excludes L54 and labels L55 seeds as legacy whole-run seeds. It is not frozen or committed, and its required `plm_steering.icbinb_audit` module, runner interfaces, tests, and outputs do not exist. Narrative contract, not empirical evidence. |
| `docs/INTERP4DISCOVERY_PREREGISTRATION.md` | Untracked | Markdown, 26,488, `66aa10830f68cc8863b5cfa43441fb4c2b6e213be0b7e708ea6a85b56b2e757d` | Interp4Discovery | Detailed draft design and expected artifact schema. Numerous `DECISION TO FREEZE` fields remain unresolved, so it does not authorize opening the confirmation panel. Narrative only. |
| `README.md` | Tracked | Markdown, 3,323, `b7e452a10be5dfd6d8450b24d78569b98243c54adcebe94b2c532e314119c2d9` | Shared | Repository overview only. It lists experiments but is not a policy authority or result ledger. |
| `docs/L42_STEERING_REPRO.md` | Tracked | Markdown, 14,213, `4a26b4cdc62b11fca0a3aa867dc38831581ec4c1f8d843247d40eea7df4f884b` | ICBINB-BIO optional | Narrative with reported numbers. Do not cite as empirical evidence without a current bundle. |
| `docs/L48_VIG_CAUSAL_TEST.md` | Tracked | Markdown, 5,759, `cb5fb6c61a8be29b216c4c32958a01ce4ff806260a065f3716c4d4dc30a1144c` | Interp4Discovery | Narrative interpretation of L48. The necessity claim is stronger than the new plan permits from a non-significant, non-equivalence result. Rewrite only after the new analysis. |
| `docs/L49_UNSUPERVISED_CAUSAL_SWEEP.md` | Tracked | Markdown, 7,094, `a45e5bc6e31776fec9dcbca5dee2e64a479344fe5877f205eb1699d39471e870` | Interp4Discovery | Narrative interpretation of a coarse sweep. Do not treat "exactly zero" as raw evidence of redundancy. |
| `docs/L50_CAPABILITY_GAIN_PROTOCOL.md` | Tracked | Markdown, 7,469, `354e1499a7619f1d9c8d130bbe35568235ad9d774b806d3b238362aa47a0d4c9` | Shared historical method | Narrative protocol only. It is not a current experiment manifest. |
| `docs/L51_AGGREGATION_STEERING.md` | Tracked | Markdown, 3,739, `8928f4ee0755db4df4726749ea41f2b917114b9aad0f470462453b0277fe927d` | ICBINB-BIO optional | Corrected narrative says `KILL`, while saved JSON says `PASS`. Preserve both policies in a derived bundle. |
| `docs/L52_LAYER_SUBSET_STEERING.md` | Tracked | Markdown, 8,520, `e6daf6198b53729ab79e80423cd736c944174d1dbb4e9730c13b0b03acc88c0e` | ICBINB-BIO | Narrative only. Use the JSON, not this prose, as the analysis input. |
| `docs/L53_BINDING_STEERING.md` | Tracked | Markdown, 5,849, `d1a489337498bf9c079c907a58d781146573989e09f59a1c97bb82e028c796df` | ICBINB-BIO optional boundary | Narrative only. Mechanistic explanations are hypotheses, not measured causal results. |
| `docs/L54_CATALYTIC_STEERING.md` | Tracked | Markdown, 11,737, `d24d749d3fd5552ab7fb26232e80bb8fe0453e8f70c83d4475851140e3ac39da` | Catalytic follow-up | Narrative only and excluded from workshop papers. Its `PASS` concerns a scoring surrogate, not measured catalysis. |
| `docs/L55_DISORDER_STEERING.md` | Tracked | Markdown, 6,620, `74d534321dac1ab2cf9d358163e7f3cf78a6ddd0228731ca7a17de57ae304258` | ICBINB-BIO limited use | Narrative only. The multi-seed account is not reproducibly linked to explicit seed metadata. |
| `docs/L56_IMMUNOGENICITY_KILLED.md` | Tracked | Markdown, 7,684, `c6ace93529f418d68e0bae3bae604f7146ca0ef649eb17005feff5e0c36049c1` | ICBINB-BIO | Narrative only. It is useful as an audit map, not as empirical evidence. |
| `docs/L57_EXPRESSION_STEERING.md` | Tracked | Markdown, 6,175, `a61eeb1dfa6e39157c10b0b311c980ad479169e2d616e86bcb9d6d0de9eb487b` | ICBINB-BIO | Narrative only. The "geometric echo" language is interpretation, not a causal finding. |
| `docs/SUBMISSION_GUIDE.md` | Tracked | Markdown, 2,663, `48b59e5f2642bce7e16cc97bde18751031accb90be0654fcecd41fe8a6e7d4a7` | Shared | Packaging guidance only. Verify official venue rules separately. |

No tracked `docs/L43_*.md` or `docs/L58_*.md` file exists.

## Saved research outputs

`docs/ARTIFACT_OWNERSHIP.json` is the machine-readable ownership authority for
the known saved result hashes below. The submission contract binds its exact
SHA-256. The package verifier checks artifact and lineage-ancestor hashes
against that catalog, so renaming a foreign file does not change its
ownership.

| Path | State | Type, size, SHA-256 | Raw or narrative | Ownership | Evidentiary status and action |
|---|---|---|---|---|---|
| `plm_steering/l48_replication_out.json` | Tracked | JSON, 29,271, `82f5bb8b8e3af1b15f72c0f32ce8257502449639d76ab8cf02b1b65fc308cf4d` | Derived numeric output | Interp4Discovery | Contains pooled 30 by 16 fraction and enrichment matrices and eight structure summaries. No per-residue attention values, model revision, source revision, or exclusions are saved. Pilot only. |
| `plm_steering/l48_causal_ablation_out.json` | Tracked | JSON, 5,477, `678803ef94412cce58dbe8ab63182a796530cefe7a4133d111abc0ce9c0081a5` | Derived numeric output | Interp4Discovery | Contains per-structure aggregates and pooled bootstrap summaries for 603 contact and 167 non-contact positions. Per-position outcomes are discarded before writing. Replace for confirmatory use. |
| `plm_steering/l49_causal_sweep_out.json` | Tracked | JSON, 66,421, `d8942a9e37cc97e8f7f5a8e28e10679dc48d608dc88f5f2eaf6600c0444419ca` | Derived numeric output | Interp4Discovery | Contains one aggregate effect per head for 480 heads. Sampled positions and per-position outcomes are not saved. Pilot only. |
| `plm_steering/l51_repro_out/results.json` | Tracked | JSON, 2,801, `8cf756c2de52a247ae0f1a4362fa48839a1878b4d24d85ea2ff0d52c58d1b3f2` | Derived numeric output | ICBINB-BIO optional | Summary only. No raw scores, generated sequences, eval identifiers, or seed field. Saved decision is `PASS`; corrected prose says `KILL`. Rerun or exclude. |
| `plm_steering/l52_repro_out/results.json` | Tracked | JSON, 408,921, `bb2de0ece5306ab40a4a8c875e42cb9a41028fdc7cf3c5ee2f744eefd84c99f4` | Per-generation output | ICBINB-BIO | Stores 60 scores and sequences for each of 20 arms plus baseline sequences and summaries. It does not store a seed, source revision, model revision, original source identifiers, or a two-part audit ledger. Derive a locked audit bundle. |
| `plm_steering/l53_repro_out/results.json` | Tracked | JSON, 375,593, `893f3b6ac1c691e4643ead2dba5e54ab198b75c73175ffbf41dc7f13bdf4c140` | Per-generation output | ICBINB-BIO optional boundary | Stores 150 scores and sequences for 11 arms. Dataset metadata points to `/Users/divkov/workplace/biostat/...`, not this tracked copy. Seed and source revision are absent. Normalize provenance before use. |
| `plm_steering/l54_repro_out/results.json` | Tracked | JSON, 589,446, `7b4dba5deb79101d688a40a40688879cc32503766bbb24e214a4876b361c3793` | Per-generation output | Catalytic follow-up | Stores 150 eval sequences and scores/sequences for 11 arms. No seed field; inferred as seed zero from prose and code only. Exclude from workshop papers. |
| `plm_steering/l54_repro_out_seed1/results.json` | Tracked | JSON, 601,432, `de1cb8b87bc0d99f1479f2d3de7a8b9975e3f3d304e5d32823daa469d5637ce1` | Per-generation output | Catalytic follow-up | Directory name says seed 1, but file has no seed and tracked runner hard-codes zero. Provenance is not reproducible as named. |
| `plm_steering/l54_repro_out_seed2/results.json` | Tracked | JSON, 587,374, `6e9677a254cfb6dc6930dbf8cf42c9e658213ebb14044007e484efefe22fccc2` | Per-generation output | Catalytic follow-up | Directory name says seed 2, but file has no seed and tracked runner hard-codes zero. Provenance is not reproducible as named. |
| `plm_steering/l55_repro_out/results.json` | Tracked | JSON, 524,301, `822402c49d2687bbae65b71c18815bcbe45c3dadf51ef7d16530bb46743a8d13` | Per-generation output | ICBINB-BIO limited use | Stores 150 eval sequences and scores/sequences for 11 arms. No seed field; inferred as zero only. Reproduce with explicit parameters. |
| `plm_steering/l55_repro_out_seed1/results.json` | Tracked | JSON, 519,587, `16506034e3c210ab604bb095f79fed462f8b23620cd3cc300fd848d2456b0f36` | Per-generation output | ICBINB-BIO limited use | Saved decision is `KILL`. Directory name says seed 1, but the file and runner do not establish that provenance. Reproduce before a multi-seed claim. |
| `plm_steering/l55_repro_out_seed2/results.json` | Tracked | JSON, 525,183, `e664fdf911fd4d05a8fd77736dd931fd85ab17be781a4acfd839b8f185c691e9` | Per-generation output | ICBINB-BIO limited use | Saved decision is `PASS`. Directory name says seed 2, but the file and runner do not establish that provenance. Reproduce before a multi-seed claim. |
| `plm_steering/data_cache/immunogenicity/l56_proxy_validation_summary.json` | Tracked | JSON, 7,391, `c1324feb7f174209ea5a605c24acc2eff2ecac1305ed3520af8d9399b0661a98` | Derived numeric output | ICBINB-BIO | Contains tier summaries and confounding statistics. No row-level predictions, fold assignments, seed field, or source revision. Build a derived audit bundle from the tracked record data. |
| `plm_steering/l57_repro_out/results.json` | Tracked | JSON, 522,945, `5790e1a0bb38391597c58a5141eec56753223d31073249f368cf1fd0fe9f262b` | Per-generation output | ICBINB-BIO | Stores 150 eval sequences and scores/sequences for 11 arms. Its dataset field points to `/Users/divkov/workplace/biostat/...`. No seed or source revision is saved. Rebind and audit. |
| `plm_steering/l58_vector_geometry_out/l54_catalytic_steering_vectors.npy` | Tracked | NumPy float32 array, 169,088, `4e1e5fc8d589cd6da10bd86e4327abb5cca2b80f1a7abbc2b9cc62d1bde41852` | Derived numeric output, shape 33 by 1280 | Catalytic follow-up | One inferred seed-zero direction. Exclude from ICBINB-BIO. |
| `plm_steering/l58_vector_geometry_out/l55_disorder_steering_vectors.npy` | Tracked | NumPy float32 array, 169,088, `c675605c1999a0340dc604152f543aeec8c573f6a16fed2683a61872476b9566` | Derived numeric output, shape 33 by 1280 | ICBINB-BIO supporting | One inferred seed-zero direction. Use only as a labeled diagnostic after provenance is locked. |
| `plm_steering/l58_vector_geometry_out/l57_expression_steering_vectors.npy` | Tracked | NumPy float32 array, 169,088, `f58652ba9b4f38308e57e61246399ae0ad4b3fe9de60686651447ce11dcf116b` | Derived numeric output, shape 33 by 1280 | ICBINB-BIO supporting | One inferred seed-zero direction. Use only as a labeled diagnostic after provenance is locked. |
| `plm_steering/l58_vector_geometry_out/results.json` | Tracked | JSON, 1,082, `e09e2c3c3022f1baece780ccb7df0bcf0055656653fb5889deae971dbaf30935` | Derived numeric output | Mixed | Pairwise cosine summaries only. The L55/L57 comparison is potentially ICBINB-owned; comparisons involving L54 are not. |

## Record-level datasets and structures

Tracked datasets are evidence inputs, not evidence that an intervention
worked. Dataset copies do not by themselves establish license, release
version, acquisition date, split membership, or absence of cohort overlap.

| Path | State | Type, size, SHA-256 | Ownership | Evidentiary status and action |
|---|---|---|---|---|
| `plm_steering/data_cache/meltome/mixed_split.csv` | Ignored | CSV, 16,430,295, `ea48dbb222a5e18de61fabf0e1550b50e7a22c3d0f59cf9b47c01d993104ea3e` | L42, optional ICBINB-BIO | Local record data only. Add source/version and frozen input hash to a rerun manifest. Do not treat local presence as a committed bundle. |
| `plm_steering/data_cache/solubility/train.csv` | Ignored | CSV, 18,846,152, `869f19cfd15ba8e46d4dd7cd23c51e8c4acde9338857ac8271b87644344815bc` | L43, excluded | Local record data for an ineligible case. Keep out of the workshop corpus. |
| `plm_steering/data_cache/solubility/test.csv` | Ignored | CSV, 599,818, `ab86eabd859d63ac17d6d0b79b4960ed73e64cbfd83768ab28ab3feed2bc4e90` | L43, excluded | Local record data for an ineligible case. Keep out of the workshop corpus. |
| `plm_steering/data_cache/pdb_structures/1CRN.pdb` | Tracked | PDB text, 49,491, `42199a30a0701864a2a5cc76cd7f35cc544cd0e65fbcf63e03c166543249b811` | Interp4Discovery pilot | Discovery-panel structure record. Preserve as pilot data; do not reuse it as the independent test panel. |
| `plm_steering/data_cache/pdb_structures/1LYZ.pdb` | Tracked | PDB text, 145,962, `28e95e819d4e0fc48acdf44209e37ba06f5c9d5d93d9950d67a760b32964326e` | Interp4Discovery pilot | Same status as the other seven pilot structures. |
| `plm_steering/data_cache/pdb_structures/1MBN.pdb` | Tracked | PDB text, 147,258, `689c16725344e12610032551c547e7a52dc3233f4c51273def1996c43bdbbb56` | Interp4Discovery pilot | Same status as the other seven pilot structures. |
| `plm_steering/data_cache/pdb_structures/1PGA.pdb` | Tracked | PDB text, 59,049, `908f8dbf3bb7567f36eec4683eb8cfab5ac0c011dfee1b9c940cab7f482bc841` | Interp4Discovery pilot | Same status as the other seven pilot structures. |
| `plm_steering/data_cache/pdb_structures/1SHG.pdb` | Tracked | PDB text, 61,641, `1b64db54178d7ca24b2a9c1e375e143ff4a67c5e3ed9bf17b1c0eaee6032eccb` | Interp4Discovery pilot | Same status as the other seven pilot structures. |
| `plm_steering/data_cache/pdb_structures/1TEN.pdb` | Tracked | PDB text, 114,858, `5b2165e4e495d05e230c6438a8585966578fc70006ec228ac0a0d8b65d06c73c` | Interp4Discovery pilot | Same status as the other seven pilot structures. |
| `plm_steering/data_cache/pdb_structures/1UBQ.pdb` | Tracked | PDB text, 78,570, `d4a6812d8951cf6594e6a0763f089e35f5a80b62acb3c117b2c5565228a7b161` | Interp4Discovery pilot | Same status as the other seven pilot structures. |
| `plm_steering/data_cache/pdb_structures/2LZM.pdb` | Tracked | PDB text, 149,526, `a305932376e1e45428c956164117bd3ab1bbc59cdab6b2ae38b7974c0e83ce6f` | Interp4Discovery pilot | Same status as the other seven pilot structures. |
| `plm_steering/data_cache/aggregation/agg50_clean.csv` | Tracked | CSV, 1,229,665, `10c316d96617ab93f51e0b21850783342c3613e45b47ab52478eff58838439db` | ICBINB-BIO optional L51 | Record data. Add dataset release, acquisition, split identifiers, and row hashes to any rerun manifest. |
| `plm_steering/data_cache/binding/RASK_HUMAN_Weng_2022_binding-DARPin_K55.parquet` | Tracked | Parquet, 756,864, `df20d22646069a8e0d661300820a037467ec0ec40159afe74c78859f3ee3ca6d` | ICBINB-BIO optional L53 | Record data. This is the current-tree copy that should replace the external absolute path in the saved output. |
| `plm_steering/data_cache/catalytic/dlkcat_wt_mut.json` | Tracked | JSON records, 12,132,719, `13643b0b36374f8d3f64d8b014882cf1b3b58946eeaae2b9dcd59e8b2c2d6719` | Catalytic follow-up | Record data. Excluded from workshop claims. Current sequence-level median processing loses substrate-specific identity for the planned follow-up claim. |
| `plm_steering/data_cache/disorder/disprot_clean.csv` | Tracked | CSV, 4,015,421, `eb7062c0b05e4a6172b82fd4936fffa7918e30f51d181ede26d12823ff90aaeb` | ICBINB-BIO limited L55 | Record data. A cohort manifest with release/version and clustering is absent. |
| `plm_steering/data_cache/expression/esol_clean.csv` | Tracked | CSV, 587,702, `bd099c1c9d4cc85d1f41f49a6ee12ec2142a15d6baf0e78766754e1546db7525` | ICBINB-BIO L57 | Cleaned record data. The L57 output does not point to this copy. Rebind and record derivation from the raw file. |
| `plm_steering/data_cache/expression/esol_raw.csv` | Tracked | CSV, 1,044,605, `1fb27cbc0818fc55f28d9442cd35bd2c1fb1fe8c7b791787727b3be589647e7b` | ICBINB-BIO L57 | Raw downloaded record data. Acquisition version and cleaning lineage are not recorded in a manifest. |
| `plm_steering/data_cache/immunogenicity/allergen.fasta` | Tracked | FASTA, 160,420, `62171a63d376a0132da5f23d94ce7cbf2c82370d02d3fe308fe4c7925444433a` | ICBINB-BIO L56 | Record data for a distinct allergenicity cross-check, not the T-cell endpoint. Keep endpoint ownership explicit. |
| `plm_steering/data_cache/immunogenicity/nonallergen.fasta` | Tracked | FASTA, 499,466, `42d0415c01d6cd926a9f9e32792de3c722fa19c11a06d21887f0a3ce826fc66c` | ICBINB-BIO L56 | Matched comparison record data. Save matching assignments and exclusions in the audit bundle. |
| `plm_steering/data_cache/immunogenicity/antigen_posfrac_relaxed.csv` | Tracked | CSV, 91,512, `9af7086ef1267e1d0c9b2e6c4211cf6b527d049bdf6821a8bfe24d05be59fa9c` | ICBINB-BIO L56 | Derived full-length antigen labels. Save construction lineage and record identifiers. |
| `plm_steering/data_cache/immunogenicity/antigen_seqs.json` | Tracked | JSON records, 1,537,549, `7fc424172b90f6732dd3939bef7806253c55d659f5f8350d260c876d1838f015` | ICBINB-BIO L56 | Full-length sequence records. Link exact identifiers to the derived labels. |
| `plm_steering/data_cache/immunogenicity/iedb_tcell_mhcii.json.gz` | Tracked | Gzip JSON records, 3,159,946, `e5faf4b4a3f9add14cf5aca5c95a23ad043a07c7519e5e4e13956e911c1595f6` | ICBINB-BIO L56 | T-cell assay records. The audit needs acquisition query/version and row-level cohort membership. |
| `plm_steering/data_cache/immunogenicity/mhcii_ba.csv` | Tracked | CSV, 11,432,336, `5f3829e8e8f6e0460036e8a8676da58edcaba2ecc052ac34734079acd3cef6eb` | ICBINB-BIO L56 | MHC-II binding surrogate records. Do not describe these as immunogenicity outcomes. |
| `plm_steering/data_cache/immunogenicity/mhcii_el.csv` | Tracked | CSV, 1,603,004, `766a1e957588f415f68bc453df5593d2f883f75417ab4cb7a2fcb57fcf13f067` | ICBINB-BIO L56 | Fixed-seed presentation sample. The saved data does not carry a manifest for the sampling operation. |

## Research source files

| Path | State | Type, size, SHA-256 | Ownership | Evidentiary status and action |
|---|---|---|---|---|
| `plm_steering/l42_steering_repro.py` | Tracked | Python, 15,244, `64a3affcb79995a6791272a7688d0293ba8a8692b0f7bca140ed773a0f90c9ae` | Shared and L42 | Helper functions only. It is not the deleted L42 runner and cannot reproduce L42 by itself. |
| `plm_steering/l48_vig_contact_heads.py` | Tracked | Python, 5,924, `1d72ea0488c1e39909d8ba027001bc60a755b36f170ac20b4af2d487053e6e97` | Interp4Discovery | Structure parsing and contact-enrichment functions. Retain for pilot reproduction; extend tests for new matching and outcomes. |
| `plm_steering/l48_run_replication.py` | Tracked | Python, 5,860, `49903c5c6852165f45bc50948c3285f9f3274f1e1f67cda499465d4d59844ae1` | Interp4Discovery | Reproduces the pilot enrichment matrix. Does not save model revision or raw attention values. |
| `plm_steering/l48_run_causal_ablation.py` | Tracked | Python, 10,593, `688a96c562787ad2ff9a95e416279c7703038177586b3e286a32ae91574969d3` | Interp4Discovery | Pilot binary-accuracy runner. It computes per-position records in memory but writes only aggregates. It does not implement the planned contact interaction or protein bootstrap. |
| `plm_steering/l49_unsupervised_causal_sweep.py` | Tracked | Python, 7,201, `5586f19fb2df64bd8e5edfd4591fc617e966c076b278316843dbb00cb802bae3` | Interp4Discovery | Pilot all-head runner with hard-coded seed zero and 13 positions per structure. It discards sampled identifiers and per-position outcomes. |
| `plm_steering/l51_aggregation_steering.py` | Tracked | Python, 3,263, `ec86d7acf26f182ee35d4c13115118078b3025adb0d744665e049cca2441d846` | ICBINB-BIO optional | Scoring functions only. Not empirical evidence. |
| `plm_steering/l51_run_repro.py` | Tracked | Python, 15,243, `d5d5381c84b4337c4ed5df4d8a123606dcff35cd0399928e812e1a1d8d6fedc8` | ICBINB-BIO optional | Runner hard-codes seed zero and writes summaries only. Patch provenance and output schema before rerunning. |
| `plm_steering/l52_layer_subset_causal_steering.py` | Tracked | Python, 18,894, `9db262718a66d74b76037a0cad15063852cd1ed77642dfece3b96fe6819d56a2` | ICBINB-BIO | Runner writes per-generation output but hard-codes seed zero and omits manifests and revisions. Use as a historical reproduction source, not a frozen current contract. |
| `plm_steering/l53_binding_affinity_steering.py` | Tracked | Python, 10,204, `0f5b8b7663122635393d0ce49b8fbf6d6870c06f2742fe97fb70843ab232b5fa` | ICBINB-BIO optional | Scoring and data functions. Not empirical evidence. |
| `plm_steering/l53_validate_proxy.py` | Tracked | Python, 5,924, `542e04d17aecd912ddc5a8c9b7f02ce21831b7e7203124c6aa1f1fed9487050e` | ICBINB-BIO optional | Proxy-validation analysis source. Save row-level outputs and split identifiers if used. |
| `plm_steering/l53_run_repro.py` | Tracked | Python, 21,130, `83d803656151628ec79598b0f9cfa669f966b06e5dd898d2e7148ab9cf39c2c3` | ICBINB-BIO optional | Runner hard-codes seed zero. Add portable dataset provenance and complete configuration. |
| `plm_steering/l54_catalytic_activity_steering.py` | Tracked | Python, 5,188, `c22f40fd2d32c0724f97fdc4e7773c7cf6cb068163302673cd94ec0df28cca81` | Catalytic follow-up | Scoring and data functions. Excluded from workshop evidence. |
| `plm_steering/l54_run_repro.py` | Tracked | Python, 21,322, `eaa49bafe6428d061a430b955e079a0c0b35860f5b46e4d973411d58c0c73fde` | Catalytic follow-up | Hard-codes seed zero and default output directory. Cannot reproduce the named seed 1 and seed 2 bundles without source edits. |
| `plm_steering/l55_disorder_steering.py` | Tracked | Python, 4,546, `847ab951efdca4872b4d0c45bc5fb9d4543db1c37252e27f8863be4b26a34ba0` | ICBINB-BIO limited use | Scoring functions only. Not empirical evidence. |
| `plm_steering/l55_run_repro.py` | Tracked | Python, 19,733, `1a8d2097e0b692904571f342d253c267ad32804857a89ea6231dbc145b12ae32` | ICBINB-BIO limited use | Hard-codes seed zero and default output directory. This is the main blocker for the saved three-seed claim. |
| `plm_steering/l56_fetch_tier2_and_allergen_data.py` | Tracked | Python, 11,583, `b17251501e178e8ec128c7e92b438cf8ace4cda272a297af6d431133fd971170` | ICBINB-BIO | Data-acquisition and matching source. Record upstream versions, queries, dates, and sampled identifiers in the new cohort manifest. |
| `plm_steering/l56_immunogenicity_proxy_validation.py` | Tracked | Python, 23,613, `f93f41fb1bbf9acee9a2b23bd66682fcd79a26946992b3b7a679a632e3674d52` | ICBINB-BIO | Recomputes summary JSON with seed zero. Extend it to save row-level predictions, folds, and exact cohorts. |
| `plm_steering/l57_expression_yield_steering.py` | Tracked | Python, 4,697, `1a5ed1f72392387e33f8ea3770e1629e0f24e798c79fcd84a56787d6caf28f5b` | ICBINB-BIO | Scoring and data functions. Not empirical evidence. |
| `plm_steering/l57_validate_proxy.py` | Tracked | Python, 7,361, `dfd1ce988c5ad13bae38d71c4948c956c20bebc4786b2f8a70c5ce117b3cd47a` | ICBINB-BIO | Proxy-validation analysis source. Save exact split membership and row-level output if used. |
| `plm_steering/l57_run_repro.py` | Tracked | Python, 18,325, `d386173611661c35d102ee36ca83726986f494e3d5af456120900bd75d603484` | ICBINB-BIO | Hard-codes seed zero. Its output records a different checkout path. Make dataset identity content-based and portable. |
| `plm_steering/l58_vector_geometry_crosscheck.py` | Tracked | Python, 8,485, `bb97b795d765a3b68288752c47d365195774da6ed467d5fc4eb87488b202ca8a` | Mixed | Rebuilds only seed-zero vectors and imports hard-coded seeds from three runners. Add a manifest and paper-specific output separation before reuse. |
| `requirements.txt` | Tracked | Requirements text, 209, `cd8b82afa39dc7cdce04ac0c698565cde247644dc1087c655bdf38fffecd33fa` | Shared | Lower bounds only. Add an exact environment lock and runtime hardware/model records for reproduction. |
| `requirements-lock.txt` | Untracked, added after the initial scan | Exact Python package versions | Shared | Captures the 75-package Python 3.11 environment used for the current repository test baseline. New runs must also record platform, hardware, model revision, tokenizer revision, source commit, and this file's hash. |

No tracked source exists for L43. No tracked L56 steering runner exists, which
is consistent with the documented pre-run `KILL`.

## Tests

Tests verify selected helper behavior. They do not rerun the empirical
experiments, verify saved result hashes, or establish manuscript claims.

| Path | State | Type, size, SHA-256 | Ownership | Coverage status and action |
|---|---|---|---|---|
| `tests/test_l42_steering_repro.py` | Tracked | Python test, 8,166, `bd15071f067314efde8d9293288b56192f144f8dad62dcc89a5b961f5f8810ad` | Shared and L42 | Tests helpers, degeneracy checks, bootstrap, and proxy functions. It does not test an L42 runner or saved bundle. |
| `tests/test_l48_vig_contact_heads.py` | Tracked | Python test, 3,479, `dd3de19ac245f0d530bc6685313a36dcaae0060206fb850ccac6dd54e2fedb7b` | Interp4Discovery | Tests PDB parsing, contact maps, and enrichment functions. It does not test hook isolation, continuous outcomes, matching, mean replacement, or result persistence. |
| `tests/test_l51_aggregation_steering.py` | Tracked | Python test, 1,450, `7e16366cbab11b0270f07b40cb06e3e7ffc60599c7b62c5019b62d7cf82ec10d` | ICBINB-BIO optional | Unit tests for the scoring proxy only. |
| `tests/test_l52_layer_subset_causal_steering.py` | Tracked | Python test, 1,727, `6466082c4c76abc812112ac1fd2a1698508630248b60c8e90c9165b859524421` | ICBINB-BIO | Unit tests for layer constants, safe alphas, and exclusion scoring. No end-to-end result test. |
| `tests/test_l53_binding_affinity_steering.py` | Tracked | Python test, 5,207, `5d8a278f3ec66824975145caf07cdd9db82e5978ceb2c76110cefe5d491e87ea` | ICBINB-BIO optional | Unit tests for mutation parsing and scoring. No saved-result or split-lineage test. |
| `tests/test_l54_catalytic_activity_steering.py` | Tracked | Python test, 1,480, `9da180fe1ade447dab0a3d65716f54eaab0c2d7cdc5fa24696b42b41457dd7c3` | Catalytic follow-up | Unit tests for the compositional scorer only. |
| `tests/test_l55_disorder_steering.py` | Tracked | Python test, 1,685, `2d7f920897277c94031aa1c85948120513731d1c8fdda55bd85a6cc60e9837ee` | ICBINB-BIO limited use | Unit tests for the TOP-IDP scorer only. No seed/output provenance test. |
| `tests/test_l56_immunogenicity_proxy_validation.py` | Tracked | Python test, 5,003, `2e75e77fc2e0fb89085f6f2b0c7d4e683e64db622306d1e426dd899b546b8fb3` | ICBINB-BIO | Unit and small synthetic tests for proxy calculations. No full dataset result-lock test. |
| `tests/test_l57_expression_yield_steering.py` | Tracked | Python test, 1,725, `54f2acfd8cc1699a93d849338a9a2856730f56962bfeaa06088021631aebb138` | ICBINB-BIO | Unit tests for the charge scorer only. No dataset identity test. |
| `tests/fixtures/ubiquitin.pdb` | Tracked | PDB fixture, 78,570, `d4a6812d8951cf6594e6a0763f089e35f5a80b62acb3c117b2c5565228a7b161` | Interp4Discovery test fixture | Byte-identical to tracked `1UBQ.pdb`. Test input only, not independent evidence. |

No tracked L43, L49, or L58 test file exists. L49 relies on L42 and L48
helpers, but its sampling and saved-output contract are not directly tested.

## Manuscript inputs and rendered outputs

All manuscript text, figures, bibliographies, style files, build products,
and PDFs are narrative or presentation artifacts. They are not empirical
evidence.

### ICBINB-BIO package

| Path | State | Type, size, SHA-256 | Status and action |
|---|---|---|---|
| `docs/submissions/icbinb-bio/paper.tex` | Tracked | LaTeX source, 18,315, `1ba554b0477460fa62df1778ecdceb300a910e0eba1d0f04fb051ba52fc50149` | Current narrative mixes all five steering targets and attention-head results. It violates the new ownership contract. Rewrite only from the locked ICBINB ledger. |
| `docs/submissions/icbinb-bio/reference.bib` | Tracked | BibTeX, 3,903, `15cdfe5171a8100fd5c0f3d065a237772ec24ae1ff9e7b4fe44af9d0c23c34fa` | Citation input shared byte-for-byte with Interp4Discovery and arXiv. No citation ledger exists. |
| `docs/submissions/icbinb-bio/neurips_2026.sty` | Tracked | LaTeX style, 13,834, `cedbda3f16ceae6eeb85b5aacd3e4b4d654de71427dfe82a9b553327f15e9c7c` | Template input. Verify against the official current venue package. |
| `docs/submissions/icbinb-bio/figures/fig1_dose_response.pdf` | Tracked | PDF figure, 18,195, `a3d1e20607e3332c8117a094b765b203c110cb2af051c674ee69c79b3feb5344` | Steering figure containing L54 and L55. L54 is prohibited in ICBINB-BIO. Replace. |
| `docs/submissions/icbinb-bio/figures/fig2_proxy_vs_effect.pdf` | Tracked | PDF figure, 19,584, `46567b423b7dadeb9c1036bbb8809c35a8732a653161ba98f267b2579a540917` | Five-target figure. It does not match the staged-audit design. Replace. |
| `docs/submissions/icbinb-bio/figures/fig3_seed_robustness.pdf` | Tracked | PDF figure, 19,304, `3c5ef2cf788e97002608c45987f067490a142a1229366acf702db3e6ee4b4afd` | L55 seed figure derived from files with unresolved seed provenance. Do not use until reproduction. |
| `docs/submissions/icbinb-bio/paper.bbl` | Tracked | Generated bibliography, 4,200, `83928735dc6fbc1e9249090abd54c4f293b1b7c281ad74b15120abfdc7490a70` | Derived build product, not canonical input. Regenerate after citation review. |
| `docs/submissions/icbinb-bio/paper.pdf` | Tracked | Rendered PDF, 194,034, `cf4bb5b2904379d268241d50af9cee733f69e6a9e0290f6bb00c848d6286b864` | Seven-page old draft. It is not a reviewed fallback under the new plan. |

### Interp4Discovery package

| Path | State | Type, size, SHA-256 | Status and action |
|---|---|---|---|
| `docs/submissions/interp4discovery/paper.tex` | Tracked | LaTeX source, 16,273, `6337c06892089bf074e4e36a47bc487239452a0b18df5191223cefc2e30fa423` | Current narrative is mainly a steering paper. It violates Interp claim ownership. Rewrite only if the new causal gate passes. |
| `docs/submissions/interp4discovery/reference.bib` | Tracked | BibTeX, 3,903, `15cdfe5171a8100fd5c0f3d065a237772ec24ae1ff9e7b4fe44af9d0c23c34fa` | Shared bibliography with no citation ledger. Rebuild for the Interp-only scope. |
| `docs/submissions/interp4discovery/neurips_2026.sty` | Tracked | LaTeX style, 13,861, `a5a0eec59383411dede5ea681fc52ef29ee9fe15abcad09dc34bff614d435683` | Template input. Verify against the official current venue package. |
| `docs/submissions/interp4discovery/figures/fig1_dose_response.pdf` | Tracked | PDF figure, 18,195, `a3d1e20607e3332c8117a094b765b203c110cb2af051c674ee69c79b3feb5344` | Byte-identical to the ICBINB and arXiv steering figure. It is prohibited in the Interp paper. Remove. |
| `docs/submissions/interp4discovery/figures/fig2_proxy_vs_effect.pdf` | Tracked | PDF figure, 19,584, `46567b423b7dadeb9c1036bbb8809c35a8732a653161ba98f267b2579a540917` | Byte-identical steering figure. Remove. |
| `docs/submissions/interp4discovery/figures/fig3_seed_robustness.pdf` | Tracked | PDF figure, 19,304, `3c5ef2cf788e97002608c45987f067490a142a1229366acf702db3e6ee4b4afd` | Byte-identical L55 steering figure. Remove. |
| `docs/submissions/interp4discovery/paper.bbl` | Tracked | Generated bibliography, 4,200, `83928735dc6fbc1e9249090abd54c4f293b1b7c281ad74b15120abfdc7490a70` | Derived build product, not canonical input. |
| `docs/submissions/interp4discovery/paper.pdf` | Tracked | Rendered PDF, 167,759, `38322126ecb4e48dc005860ca45c591249782547d413aefd63be926daaf46098` | Build log reports six pages, above the planned five-page limit. Old draft only. |

### Deferred arXiv package

| Path | State | Type, size, SHA-256 | Status and action |
|---|---|---|---|
| `docs/arxiv/paper.tex` | Tracked | LaTeX source, 21,514, `b198607475e95a5cd45eb08f1eea6bcdeed2b9e9eed1e083e3cc20315887a5f1` | Named mixed-scope narrative. Deferred by the portfolio plan. |
| `docs/arxiv/reference.bib` | Tracked | BibTeX, 3,903, `15cdfe5171a8100fd5c0f3d065a237772ec24ae1ff9e7b4fe44af9d0c23c34fa` | Same bibliography as both active packages. Narrative input only. |
| `docs/arxiv/make_figures.py` | Tracked | Python figure source, 7,093, `fd5be8af92c3f693f9df1dbef19324caac72e7f265701354d043959a71ef0721` | Reads L53-L57 JSON files, but some labels and layout values are coded in the script. Figure-generation source, not empirical evidence. |
| `docs/arxiv/figures/fig1_dose_response.pdf` | Tracked | PDF figure, 18,195, `a3d1e20607e3332c8117a094b765b203c110cb2af051c674ee69c79b3feb5344` | Presentation of L54/L55 derived results. Deferred. |
| `docs/arxiv/figures/fig1_dose_response.png` | Tracked | PNG figure, 98,400, `cd8c223d30bc7306f9d950c7bfdcd76db551d459f36d5282f11a324edd622c31` | Raster rendering of the same figure. Deferred. |
| `docs/arxiv/figures/fig2_proxy_vs_effect.pdf` | Tracked | PDF figure, 19,584, `46567b423b7dadeb9c1036bbb8809c35a8732a653161ba98f267b2579a540917` | Presentation artifact. Deferred. |
| `docs/arxiv/figures/fig2_proxy_vs_effect.png` | Tracked | PNG figure, 67,489, `d77dee2b80bf0fc710f0105bdab6bea3182bc74599401b866892395a9cde6447` | Raster rendering. Deferred. |
| `docs/arxiv/figures/fig3_seed_robustness.pdf` | Tracked | PDF figure, 19,304, `3c5ef2cf788e97002608c45987f067490a142a1229366acf702db3e6ee4b4afd` | Presentation of unresolved L55 seed provenance. Deferred. |
| `docs/arxiv/figures/fig3_seed_robustness.png` | Tracked | PNG figure, 64,755, `2c2ea53c6a7d40b19be78babd4ffc58f2eb0c8751c097c1d9285d26d73310bf3` | Raster rendering. Deferred. |
| `docs/arxiv/paper.pdf` | Tracked | Rendered PDF, 238,082, `e554f342a0a9e50de994ca5fcf9f1a74b9929a8874e5e0bca487ebb6dda0d2d8` | Eight-page old draft. Narrative output only. |

### Archived XAI4Science package

| Path | State | Type, size, SHA-256 | Status and action |
|---|---|---|---|
| `docs/archive/xai4science/paper.tex` | Tracked | LaTeX source, 18,247, `32a23382c63100d1da81af6cb00335871fa209b9a78272f18fb0e609825c0569` | Archived narrative. Not owned by either active paper. |
| `docs/archive/xai4science/reference.bib` | Tracked | BibTeX, 1,671, `a277cc5930c187506706af95085e11e97e4ae355d89fbef567aa2c5b7e68c42d` | Archived bibliography. |
| `docs/archive/xai4science/neurips_2026.sty` | Tracked | LaTeX style, 13,861, `a5a0eec59383411dede5ea681fc52ef29ee9fe15abcad09dc34bff614d435683` | Archived template input. |
| `docs/archive/xai4science/figures/fig1_dose_response.pdf` | Tracked | PDF figure, 19,564, `235d518e9c42bb255a8ed6b5023405f3871587d4abe4fddd5d7e288fddb3dbd2` | Archived presentation artifact. |
| `docs/archive/xai4science/figures/fig2_proxy_vs_effect.pdf` | Tracked | PDF figure, 24,057, `e7d999311831dd26273a3a33c1032d5380e3060a689c156c387dd3038ae877be` | Archived presentation artifact. |
| `docs/archive/xai4science/figures/fig3_seed_robustness.pdf` | Tracked | PDF figure, 24,228, `7f179671a13ac452b8983227691db2748f824ab351cfbcdee47458ba3aa8014e` | Archived presentation artifact. |
| `docs/archive/xai4science/paper.bbl` | Tracked | Generated bibliography, 1,789, `cf9970ea032aa4d604d232d0a23e6af54b820b3cc57e0986591c2b1366324b6e` | Archived build product. |
| `docs/archive/xai4science/paper.pdf` | Tracked | Rendered PDF, 202,425, `857ee986ff6c9da77f3a16f65b25d591148f6370841030d5e3bbbd45f0d58396` | Archived narrative output. |

## Local ignored state and logs

| Path | State | Type, size, SHA-256 | Evidentiary status and action |
|---|---|---|---|
| `docs/archive/xai4science/paper.log` | Ignored | LaTeX log, 24,814, `89d6620382c5c35f7931e02ec4766ba5ab0308cfacf28d59550b453d7986686f` | Build log only. Reports a six-page PDF. Not a research run log. |
| `docs/arxiv/paper.log` | Ignored | LaTeX log, 18,202, `6b5f04d6ba6635ffe89e159163283d6c3deed2269614d0f73871772dd3435036` | Build log only. Reports an eight-page PDF. |
| `docs/submissions/icbinb-bio/paper.log` | Ignored | LaTeX log, 25,073, `5a75fa270df0809619de015843d48a799e692ec5f2cb04035cd7d80edacd8bba` | Build log only. Reports a seven-page PDF. |
| `docs/submissions/interp4discovery/paper.log` | Ignored | LaTeX log, 24,854, `3623f8ffd4c8037e078b4d34865df8768e42e2e022a1dfb676575a384daedabf` | Build log only. Reports six pages and underfull boxes. |
| `.pytest_cache/v/cache/nodeids` | Ignored | Pytest cache JSON, 14,786, `1627ac0a9b964bb6b130b241f790222ec0a13f00b0204b680d8bf5ecddcc64e8` | Local cache lists 149 historical node IDs, including removed tests. It is not a current test report. |
| `.pytest_cache/v/cache/lastfailed` | Ignored | Pytest cache JSON, 134, `5b3d59ed70bbbed69bc25a7700ed944d111ee4238e3b47aeed4ddf8ba7aaa847` | Records one prior L53 node ID whose test name no longer exists in the current file. Treat as stale local state, not a confirmed current failure. |
| `plm_steering/__pycache__/l43_solubility_steering.cpython-311.pyc` | Ignored | Python bytecode, 4,104, `a5633369e5b0be7d4f9acf00d46f9cb442f3f63b9e4acb60fe7b971cca1ebace` | Stale compiled derivative. It is not source and not empirical evidence. |
| `tests/__pycache__/test_l43_solubility_steering.cpython-311-pytest-9.1.1.pyc` | Ignored | Python bytecode, 12,803, `62009ec5865513f9a7d9ae488c071516dd2abe5875948dc1c93be12211efa533` | Stale compiled test derivative. It does not restore the deleted test source. |
| `docs/**/paper.{aux,blg,fdb_latexmk,fls,out}` | Ignored | LaTeX build intermediates, multiple files | Build state only. Regenerate from canonical manuscript sources. No empirical value. |
| `plm_steering/__pycache__/` and `tests/__pycache__/` other files | Ignored | Python bytecode, multiple files | Local execution residue only. It cannot establish which source revision produced a saved result. |

No stdout/stderr capture, scheduler log, hardware log, model-download record,
or experiment run log was found for L42, L43, or L48 through L58.

## Historical-only L42 and L43 files

These files are reachable in Git history immediately before commit
`4faa18e`, whose parent is
`2a3aba8eee720a385989ef87416aa828eb63b86b`. They were deleted by
`4faa18e` and are not current-tree artifacts.

| Historical path | State | Type, size, SHA-256 | Evidentiary status and action |
|---|---|---|---|
| `plm_steering/l42_repro_results.json` | Historical only | JSON, 198,332, `5ccaf6fb191e7a93d089bb696641eab6a56ee0d3a46719a5b9b972c9c8f5b8cf` | Contains aggregate summaries and generated sequences for baseline and real/random arms. It has no explicit seed, source revision, model revision, raw score arrays, or complete run configuration. Recover for audit only; do not silently count it as a current immutable bundle. |
| `plm_steering/l42_run_repro.py` | Historical only | Python, 16,087, `4b737e885afb0d08cdde08b34f3a91ec19bb9bae1c8bb606e86b5c421d85aa2b` | Deleted runner with hard-coded seed zero. Review and patch before any rerun. |
| `docs/L43_SOLUBILITY_STEERING.md` | Historical only | Markdown, 9,108, `cbcb3779a95a455c1323db948aed853ae1c2259b00c4d52ff541f570dd8393b2` | Deleted narrative only. It is not current workshop evidence. |
| `plm_steering/l43_repro_results.json` | Historical only | JSON, 173,451, `ac037d1dd12e581b67dbaafff08f6b6831ed64bea7302a3109022b7c19603728` | Contains aggregate summaries and generated sequences, but lacks explicit seed, source revision, model revision, raw score arrays, and full configuration. Keep excluded under the approved corpus rule. |
| `plm_steering/l43_run_repro.py` | Historical only | Python, 13,650, `f344428a4e070b51b752948a0ad297e32520435c1eb6aed2f02cb511f38684c8` | Deleted runner with hard-coded seed zero. Not current source. |
| `plm_steering/l43_solubility_steering.py` | Historical only | Python, 3,077, `15a017c0e8976854fe0aa7b06c29d10abfbdc92f8a170cc92179f3d86ed7f14a` | Deleted scoring source. Not current source. |
| `tests/test_l43_solubility_steering.py` | Historical only | Python test, 1,764, `7468362567a122cc6ed661bc8dde10a4232b356cfa015256a55e40e577d3f2bd` | Deleted test source. Stale bytecode does not replace it. |

## Required artifacts that are absent

| Required item | Paper | Current state | Action |
|---|---|---|---|
| Frozen claim registry with one row per claim | Both | Draft and untracked | Reconcile ownership and seed-role conflicts, review, freeze, and commit before manuscript rewriting. |
| Frozen cohort manifests with source versions, IDs, exclusions, clustering, split membership, and input hashes | Both | Absent | Create per paper before final evaluation. |
| Frozen experiment manifests with outcomes, controls, seeds, failure policy, statistics, multiplicity, and expected outputs | Both | Both exist as untracked drafts; ICBINB implementation is absent; Interp decisions are unresolved | Reconcile and review ICBINB, then commit its contract before audit implementation. Resolve, review, hash, and commit the Interp preregistration lock before confirmation work. |
| Immutable result ledger linking every manuscript number to files and analysis code | Both | Absent | Create after audit bundles and before drafting. |
| Citation ledger with verified source support and search dates | Both | Absent | Create before final citation review. |
| Exact environment lock, hardware record, model revision, tokenizer revision, and source revision | Both | Package lock now exists; the remaining run-specific records are absent | Save the lock hash and all run-specific fields with every new or recovered run. |
| Per-attempt failure flags and joint two-part analysis bundles | ICBINB-BIO | Absent | Derive for included generation cases and lock the policy. |
| Current L42 runner and result bundle | ICBINB-BIO optional | Absent from current tree | Recover and patch or rerun by the cutoff; otherwise exclude. |
| Current L43 document, source, test, and result bundle | Neither | Absent from current tree | Keep excluded. |
| Parameterized L55 runner and explicitly seeded three-run bundles | ICBINB-BIO | Absent | Implement and reproduce before using seed sensitivity. |
| Independent, cluster-disjoint PDB test panel | Interp4Discovery | Absent | Build and freeze after pilot precision and compute checks. |
| Interp matching records and balance/common-support diagnostics | Interp4Discovery | Absent | Save row-level matches and diagnostics. |
| Interp continuous per-position true-residue log-probability outcomes for all 480 heads | Interp4Discovery | Absent | Run and save on the frozen independent panel. |
| Interp hook-isolation and perturbation-calibration evidence | Interp4Discovery | Absent | Add focused tests and saved calibration outputs. |
| Interp mean-replacement top-five sensitivity and branch-specific equivalence outputs | Interp4Discovery | Absent | Run only under the frozen ordered decision rule. |
| Reviewed, tagged minimum ICBINB source and PDF fallback | ICBINB-BIO | Absent | Build only after the minimum audit bundle is locked. |
| Interp-only five-page manuscript and figures | Interp4Discovery | Absent | Draft only if the August 20 evidence gate passes. |

## Inventory decision

The current tree is sufficient to start a retrospective provenance audit. It
is not sufficient to claim that either workshop paper has met its evidence
gate. Documentation, manuscript text, figures, and PDFs must remain separate
from empirical evidence. ICBINB-BIO can proceed only after its selected
cases are converted into immutable audit bundles. Interp4Discovery requires a
new independent-panel experiment rather than a reinterpretation of the
existing L48/L49 summaries.
