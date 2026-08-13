# Validating Causal Steering in Protein Language Models

Workshop submission packages, a named arXiv manuscript, and the
supporting experiments for "Validating Causal Steering in Protein
Language Models: Proxy Accuracy Does Not Guarantee Steering Success."

## Planned submissions

The two planned workshop submissions are double-blind. Their LaTeX
sources and PDFs are therefore anonymous.

| Venue | Path | Page limit | Review format |
|---|---|---:|---|
| ICBINB-BIO | [`docs/submissions/icbinb-bio/`](docs/submissions/icbinb-bio/) | 8 | Double-blind |
| Interp4Discovery | [`docs/submissions/interp4discovery/`](docs/submissions/interp4discovery/) | 5 | Double-blind |

The XAI4Science package in
[`docs/archive/xai4science/`](docs/archive/xai4science/) is an
archived draft, not a planned submission. The 2026 workshop focuses on
weather and climate foundation models, so this protein-language-model
paper is not a close fit.

Both planned workshop deadlines are August 29, 2026, at 11:59 p.m.
Anywhere on Earth.

## arXiv manuscript

[`docs/arxiv/`](docs/arxiv/) contains the named manuscript:

- Dmitriy Ivkov
- University of Michigan, Ann Arbor
- `divkov@umich.edu`

The arXiv manuscript and the workshop manuscripts are separate files.
The arXiv version may contain the author's name, while the workshop
versions must remain anonymous during review. A public preprint can make
an anonymous submission easy to identify through its title and wording.
The conservative sequence is to prepare the arXiv version now and post
it after workshop review, unless the workshop explicitly permits
preprints during review.

## Anonymous code sharing

An anonymous GitHub repository is not needed for the current workshop
drafts. If code is included with a double-blind submission, the safest
option is an anonymous supplementary archive uploaded through the
submission system. An anonymous repository snapshot is useful only when
the venue allows external links and the code is too large for the
supplement.

Do not link this repository from an anonymous paper. It is public, its
URL contains the author's username, and its history contains identifying
information. An anonymous snapshot must remove names, email addresses,
usernames, acknowledgments, remote URLs, and commit history. Even then,
an exact-title search may connect the snapshot to this public repository.

See [`docs/SUBMISSION_GUIDE.md`](docs/SUBMISSION_GUIDE.md) for the
structure of each manuscript and the pre-submission anonymity checks.

## Supporting experiments

The code, data, and saved results supporting the manuscripts include:

- L42: thermostability steering baseline
- L48/L49: attention-head causal ablation and the 480-head sweep
- L50: the six-criterion evaluation protocol
- L51-L57: the five-target steering study
- L58: cross-target steering-vector comparison

Install the Python dependencies and run the unit tests with:

```bash
pip install -r requirements.txt
pytest tests/ -q
```

Experiment scripts require ESM2-650M and select CUDA, MPS, or CPU in
that order:

```bash
python -m plm_steering.l54_run_repro
python -m plm_steering.l55_run_repro
python -m plm_steering.l53_run_repro
python -m plm_steering.l57_run_repro
python -m plm_steering.l56_immunogenicity_proxy_validation
python -m plm_steering.l58_vector_geometry_crosscheck
```
