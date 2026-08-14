# Paper Portfolio Plan

Date: 2026-08-14

ICBINB-BIO deadline: 2026-08-29 at 11:59 p.m. Anywhere on Earth

Interp4Discovery operational deadline: 2026-08-30 at 01:00 UTC. The workshop
website states 2026-08-29 at 11:59 p.m. Anywhere on Earth, but the current
OpenReview portal closes 10 hours and 59 minutes earlier. Use the portal time
until the venue resolves the conflict.

## 1. Author directive and scope

The experiments are complete. Existing result files, figures, paper drafts,
and study documents are the evidence base for this writing phase.

The active plan contains no experiment reruns, Python execution, new audit
tooling, compute benchmarks, result-lock construction, or new data collection.
Do not modify or execute experiment code. If the saved evidence does not
support a sentence, narrow or remove the sentence. Do not generate new evidence
to preserve a planned claim.

No new experiment, analysis program, or research code may be started without
explicit author approval.

The active work is:

1. inspect the existing manuscript sources, figures, references, and saved
   results;
2. refactor ICBINB-BIO around one clear thesis;
3. record the completed Interp4Discovery suitability decision;
4. rewrite the ICBINB paper in simple technical English;
5. verify claims, citations, anonymity, formatting, and final PDFs.

arXiv and XAI4Science remain out of scope. Catalytic and disorder mini-papers
remain deferred until the workshop papers are resolved.

## 2. Portfolio decision

| Paper | Decision | Evidence policy | Priority |
|---|---|---|---|
| ICBINB-BIO | Refactor and submit if the existing evidence supports the final thesis | Use only completed experiment artifacts | Primary |
| Interp4Discovery | Do not submit from the current evidence | L48 is a one-head pilot and L49 does not test the proposed enrichment-effect association; do not run rescue work | Closed |
| Catalytic steering | Develop later as a focused mini-paper | Start from the successful existing result; any new side-effect or toxicity work requires author approval | Deferred |
| Disorder steering | Develop later only if the existing evidence supports a result beyond composition sensitivity | Do not rerun steering to rescue the claim | Deferred and conditional |

ICBINB-BIO is the only active workshop submission. Interp4Discovery is closed
for this cycle because the completed evidence does not support the proposed
causal contribution.

## 3. Research identity

The papers are not a catalog of unrelated protein properties. The research
program asks one broad question:

> When do internal signals in protein language models support reliable
> interventions, and which checks separate a real effect from an evaluation
> artifact?

Each paper must answer a narrower question.

- ICBINB-BIO explains how steering evaluations can produce false or unstable
  success.
- A future Interp4Discovery study could ask whether contact-attention evidence
  identifies model components with a meaningful causal role. That question is
  not supported as a current submission.
- The later catalytic paper will examine the strongest successful steering
  result without presenting a computational prediction as experimental
  validation.
- The later disorder paper will proceed only if its claim survives direct
  composition-based interpretation.

We present ourselves as investigators who tested an intervention, found
important limits in the original evaluation, and converted those limits into
clear methodological guidance. The paper must not read like a sequence of
unrelated trials.

## 4. Evidence and language boundaries

Use these terms consistently.

| Term | Meaning |
|---|---|
| Property label | An experimental or curated measurement |
| Scoring surrogate | A sequence-derived score associated with a property label |
| Steering endpoint | The quantity measured after an intervention |
| Technical failure | An empty, malformed, length-mismatched, or unscorable generated sequence |
| Composition sensitivity | A conclusion that changes when dominant residue contributions are removed or controlled |
| Causal outcome | A measured change caused by an intervention relative to a defined control |

Avoid the word `proxy` unless the sentence immediately states what stands in
for what. Prefer `scoring surrogate`, `measured endpoint`, or `control
measurement`.

The workshop papers must not claim:

- that a score change proves biological property control;
- that steering improves catalysis, safety, toxicity, or another biological
  property without the required experimental evidence;
- that a non-significant result proves no effect;
- that the current studies establish a general result beyond the tested
  models, data, interventions, and saved runs.

## 5. ICBINB-BIO strategy

### 5.1 Thesis

Working title:

> When Protein Language Model Steering Appears to Work: Retrospective Checks
> Across Four Case Studies

Research question:

> Which evaluation failures can make activation steering appear successful,
> and which checks expose those failures before a biological claim is made?

Thesis:

> Across four completed case studies, endpoint mismatch, output
> low-complexity, composition sensitivity, and whole-run variation changed the
> strength or meaning of score-based steering conclusions. These retrospective
> cases motivate a staged reporting sequence, but they do not validate a
> general audit or establish biological control.

This is a methods and failure-analysis paper. It is not a five-property
steering report and it is not a collection of null results.

### 5.2 Existing evidence

The writing team must inspect the source files before deciding how much space
each case receives.

| Study | Planned use |
|---|---|
| L52 | Main low-complexity and survivor-only interpretation case |
| L56 | Main endpoint-mismatch and grouped-validation sensitivity case |
| L55 | Existing three-run evidence for run-level and composition-sensitive interpretation |
| L57 | Main composition-sensitivity case |
| L58 | Optional one-seed geometric observation, clearly labeled as limited |
| L53 | Optional boundary example only if it clarifies the thesis |
| L42 and L51 | Exclude unless the existing tracked material is already sufficient for a carefully bounded statement |
| L54 | Exclude from ICBINB-BIO and reserve for the catalytic paper |
| L48 and L49 | Exclude from ICBINB-BIO and reserve for Interp4Discovery |

The three existing L55 result files are completed experiment artifacts. Do not
rerun them. The paper may describe the observed two-of-three pattern if direct
inspection confirms that wording. If provenance limits prevent a stronger
statement, report the limitation and keep the narrower claim.

### 5.3 Material to remove

- Remove the attention-head method and results.
- Remove the five-property catalog as the paper's organizing structure.
- Remove the null-result narrative.
- Remove catalytic steering results and biological-success language.
- Remove the old correlation-versus-effect overview if it does not serve the
  staged-audit thesis.
- Remove experiment chronology that does not explain a failure mechanism.
- Remove abrupt result statements that do not explain what failed, why it
  matters, and how the interpretation changes.

### 5.4 Structure

Use the venue's required content elements as visible top-level sections unless
the official template requires different headings.

1. **Problem**
   Define why a changed sequence score is not enough to establish reliable
   steering. State the research question and the staged-audit thesis.
2. **Proposed Approach**
   Present the validity checks in the order a researcher should apply them:
   endpoint validity, output validity and denominators, composition
   sensitivity, whole-run consistency, and claim calibration.
3. **Observed Outcomes**
   Present three connected cases:
   endpoint mismatch from L56, low-complexity and missing comparisons from L52,
   composition sensitivity from L57, and whole-run variation from L55.
4. **Reasons for Failure**
   Explain the mistaken inference in each case and show how the relevant check
   changes the conclusion.
5. **Discussion and Limitations**
   State what the completed evidence supports, what it does not support, and
   how future steering studies should report these checks.
6. **Conclusion**
   Restate one practical message. Steering claims need endpoint, generation,
   robustness, and composition checks before biological interpretation.

L58 may appear in a short limitations or supporting-evidence paragraph. It
must not become a separate mechanism or a causal explanation.

### 5.5 Figures and tables

- Figure 1: the staged evaluation procedure and the claim protected by each
  check.
- Figure 2: compact evidence for decoder instability and composition or
  run-level sensitivity, using existing figure data only.
- Table 1: case, original interpretation, failed check, corrected
  interpretation, and reporting recommendation.

Do not include a figure merely to list all attempted targets. Reuse and edit
existing figures where possible. Do not regenerate experiment results.

### 5.6 Writing rules

- Use simple technical English.
- Explain the relationship between a result and the paper's thesis.
- Do not compress several logical steps into one sentence.
- Remove em dashes and excessive parenthetical remarks.
- Remove decorative italics and excessive bolding, including constructions
  such as `\textbf{PASS}`.
- Keep technical terms stable instead of cycling through synonyms.
- Split long sentences when they contain more than one main claim.
- Preserve enough explanation that a reader can follow why the interpretation
  changed.

### 5.7 Completion gate

ICBINB-BIO is ready for submission when:

- one thesis controls the abstract, introduction, results, and conclusion;
- every result statement is traceable to an existing artifact or study
  document;
- no sentence depends on a rerun, missing output, or planned audit program;
- attention-head and L54 results are absent;
- the paper does not present a score change as biological validation;
- limitations describe the provenance limits of the completed studies;
- citations have been checked against the sources they are used to support;
- the prose and formatting rules in Section 5.6 have been applied;
- an independent reader can state the contribution in one sentence;
- the anonymous PDF fits the venue template and page limit.

## 6. Interp4Discovery strategy

Interp4Discovery was screened from the completed L48 and L49 evidence. The
decision is DO NOT SUBMIT in the current cycle.

L48 supports a one-head pilot. L49 does not calculate the proposed association
between contact enrichment and contact-specific causal effect. The completed
materials also lack an independent panel, row-level outcomes, protein-level
uncertainty, and a prespecified equivalence analysis. These are evidence limits,
not active implementation tasks.

Do not refactor the Interp manuscript. Do not run a confirmation panel, new
ablations, runtime benchmarks, Python analysis, or other rescue work.

The old preregistration remains useful as a record of what stronger future
evidence would require. It is not part of the current execution path.

## 7. Later mini-papers

### 7.1 Catalytic steering

The catalytic paper will start from the completed successful steering result.
Its claim must remain computational unless experimental validation exists.
The paper should discuss structural plausibility, substrate specificity, and
possible liabilities. Boltz, toxicity prediction, or other new property
analysis may be considered only in a separate author-approved plan. These
tools must not be run during the current paper refactor.

### 7.2 Disorder steering

The disorder paper proceeds only if the completed results support a useful
claim after composition sensitivity is explained directly. Do not rerun the
experiment to obtain a cleaner result. If the surviving contribution is only
that the score is composition-sensitive, keep that evidence in ICBINB-BIO
instead of creating a second paper.

## 8. Parallel paper subtasks

Subagents may work independently on paper tasks with non-overlapping files or
clearly separated review outputs.

| Subtask | Output |
|---|---|
| ICBINB source and figure inventory | Evidence map from each planned sentence and figure to existing files |
| ICBINB structure refactor | Revised outline and reordered LaTeX source |
| ICBINB prose edit | Simple technical English with formatting cleanup |
| Citation review | Claim-to-source table and corrected bibliography |
| Interp suitability review | Completed do-not-submit recommendation based only on existing evidence |
| PDF review | Page-by-page report on layout, anonymity, references, and figure readability |

No subagent may run experiments, execute Python research scripts, write audit
infrastructure, or change scientific results. Subagents are limited to
read-only manuscript, citation, and argument review.

## 9. Active sequence

1. Completed: integrated the independent citation and argument reviews.
2. Completed: verified result statements against the existing evidence map.
3. Completed: inspected all six pages of the anonymous ICBINB PDF.
4. Completed: ran manuscript-only citation, anonymity, prose, and layout
   checks.
5. Commit the paper and planning changes.

## 10. Authorship and anonymity

Venue submission versions remain anonymous where required. They must not
contain identifying repository links or PDF metadata.

Named versions use:

- Dmitriy Ivkov
- divkov@umich.edu
- University of Michigan, Ann Arbor

Do not place a generic `Submitted to ...` footer in the manuscript unless the
official venue template inserts or requires it. Appendix material should use
normal appendix sectioning in the same source unless the venue requires a
separate supplement.

## 11. Definition of done

### 11.1 Manuscript

- one research question and one main thesis;
- conventional section order adapted to the venue requirements;
- every paragraph has a clear role in the argument;
- every scientific statement is supported by an existing result or verified
  source;
- simple technical English without abrupt semantic compression;
- no em dashes, excessive parentheticals, or decorative emphasis;
- correct anonymous or named author block for the intended version;
- no unnecessary submission footer;
- references compile without missing entries.

### 11.2 Submission package

- correct template and page limit;
- anonymity scan completed;
- PDF metadata checked;
- figures legible at final size;
- source archive contains only required manuscript files;
- final PDF opened and inspected page by page;
- no experiment or code task remains in the submission checklist.

## 12. Current board

| Item | Status |
|---|---|
| Experiment execution | Complete before this refactor; no reruns authorized |
| Experiment and audit code | Out of scope |
| ICBINB manuscript restructuring | Complete |
| ICBINB prose and formatting revision | Complete |
| ICBINB citation and source review | Complete |
| ICBINB PDF review | Complete; six pages inspected |
| Interp existing-evidence suitability review | Complete; do not submit |
| Interp manuscript restructuring | Canceled |
| Catalytic and disorder mini-papers | Deferred |

The manuscript refactor and paper-only checks are complete. No result lock,
runner patch, audit module, benchmark, or Python command was part of this work.
