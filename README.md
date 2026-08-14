# Protein Language Model Steering Case Studies

This repository contains completed ESM2-650M activation-steering experiments,
saved results, and manuscript sources.

## Papers

The active paper is the anonymous ICBINB-BIO submission:

- Source: [`papers/icbinb-bio/paper.tex`](papers/icbinb-bio/paper.tex)
- PDF: [`papers/icbinb-bio/paper.pdf`](papers/icbinb-bio/paper.pdf)

The paper analyzes three completed steering studies and one pre-steering
endpoint analysis. It uses committed artifacts only; manuscript work does not
require rerunning experiments.

Inactive manuscript drafts are under `papers/archive/`:

- `arxiv/`: earlier general manuscript
- `interp4discovery/`: workshop draft that will not be submitted from the
  current evidence
- `xai4science/`: archived workshop draft

The repository does not contain one paper per steered attribute. L54
(catalytic activity) and L55 (intrinsic disorder) are study records, not
separate manuscript packages.

## Repository Layout

- `papers/`: active manuscript and archived drafts
- `studies/`: study-level methods, results, and limitations
- `plm_steering/`: experiment and analysis code
- `tests/`: focused tests for the research code

The active workshop manuscript is double-blind. Do not link this identifying
public repository from the anonymous submission or its review materials.
