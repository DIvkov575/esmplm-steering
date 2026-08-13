from pathlib import Path

import pytest

from plm_steering.submission_ownership import find_violations


def test_icbinb_rejects_attention_and_catalytic_evidence(tmp_path: Path):
    (tmp_path / "paper.tex").write_text(
        "An attention head and catalytic result.", encoding="utf-8"
    )

    violations = find_violations("icbinb-bio", tmp_path)

    assert any("attention-head" in item for item in violations)
    assert any("catalytic" in item for item in violations)


def test_interp_rejects_steering_evidence(tmp_path: Path):
    (tmp_path / "paper.tex").write_text(
        "The activation steering direction changed output.", encoding="utf-8"
    )

    violations = find_violations("interp4discovery", tmp_path)

    assert any("activation-steering" in item for item in violations)


def test_clean_paper_source_passes(tmp_path: Path):
    (tmp_path / "paper.tex").write_text(
        "Contact-specific ablation damage was measured.", encoding="utf-8"
    )

    assert find_violations("interp4discovery", tmp_path) == []


def test_historical_figure_name_is_rejected(tmp_path: Path):
    figure = tmp_path / "figures" / "fig1_dose_response.pdf"
    figure.parent.mkdir()
    figure.write_bytes(b"%PDF-1.4")

    violations = find_violations("icbinb-bio", tmp_path)

    assert violations == ["figures/fig1_dose_response.pdf: prohibited historical figure"]


def test_unknown_paper_is_rejected(tmp_path: Path):
    with pytest.raises(ValueError, match="unknown paper"):
        find_violations("unknown", tmp_path)
