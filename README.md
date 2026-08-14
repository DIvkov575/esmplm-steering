# Protein Language Model Steering Case Studies

This repository contains completed ESM2-650M activation-steering experiments,
saved results, and manuscript sources.

## Active Manuscript

The active paper is the anonymous ICBINB-BIO submission:

- Source: [`docs/submissions/icbinb-bio/paper.tex`](docs/submissions/icbinb-bio/paper.tex)
- PDF: [`docs/submissions/icbinb-bio/paper.pdf`](docs/submissions/icbinb-bio/paper.pdf)
- Evidence map: [`docs/submissions/icbinb-bio/EVIDENCE_MAP.md`](docs/submissions/icbinb-bio/EVIDENCE_MAP.md)

The paper analyzes three completed steering studies and one pre-steering
endpoint analysis. It uses committed artifacts only; manuscript work does not
require rerunning experiments.

Other manuscript packages in `docs/` are inactive reference material. They are
not current submission targets.

## Repository Layout

- `docs/L*.md`: study-level methods, results, and limitations
- `docs/CLAIM_REGISTRY.md`: bounded manuscript claims and evidence sources
- `plm_steering/`: experiment and analysis code
- `tests/`: focused tests for the research code

The active workshop manuscript is double-blind. Do not link this identifying
public repository from the anonymous submission. See
[`docs/SUBMISSION_GUIDE.md`](docs/SUBMISSION_GUIDE.md) for the submission
structure and anonymity checks.
