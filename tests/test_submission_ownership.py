import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from plm_steering.submission_ownership import find_violations


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


LEDGER_COLUMNS = [
    "claim_id",
    "paper_id",
    "claim_text_sha256",
    "claim_status",
    "provenance",
    "estimand",
    "statistical_unit",
    "control",
    "cohort_manifest_path",
    "cohort_manifest_sha256",
    "experiment_manifest_path",
    "experiment_manifest_sha256",
    "raw_artifact_paths",
    "raw_artifact_sha256",
    "derived_artifact_paths",
    "derived_artifact_sha256",
    "point_estimate",
    "interval",
    "denominator",
    "gate_result",
    "limitation",
    "review_status",
    "source_git_commit",
]


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _ledger_row(
    paper: str,
    claim_id: str,
    artifact_path: str,
    artifact_sha256: str,
) -> dict[str, str]:
    row = dict.fromkeys(LEDGER_COLUMNS, "")
    row.update(
        {
            "claim_id": claim_id,
            "paper_id": paper,
            "claim_status": "confirmed",
            "raw_artifact_paths": "[]",
            "raw_artifact_sha256": "[]",
            "derived_artifact_paths": json.dumps([artifact_path]),
            "derived_artifact_sha256": json.dumps([artifact_sha256]),
            "gate_result": "pass",
        }
    )
    return row


def _owned_package(
    tmp_path: Path,
    *,
    paper: str = "interp4discovery",
    claim_id: str = "INT-01",
) -> dict[str, Path]:
    package = tmp_path / "package"
    package_artifact = package / "figures" / "renamed_result.pdf"
    package_artifact.parent.mkdir(parents=True)
    package_artifact.write_bytes(b"%PDF-1.4\nowned result\n")
    (package / "paper.tex").write_text(
        "Contact-specific ablation damage was measured.\n",
        encoding="utf-8",
    )

    ledger_root = tmp_path / "ledger-root"
    ledger_artifact = ledger_root / "results" / "locked_figure.pdf"
    ledger_artifact.parent.mkdir(parents=True)
    ledger_artifact.write_bytes(package_artifact.read_bytes())

    ledger = tmp_path / "result_ledger.csv"
    _write_csv(
        ledger,
        [
            _ledger_row(
                paper,
                claim_id,
                "results/locked_figure.pdf",
                _sha256(ledger_artifact),
            )
        ],
    )

    allowlist = package / "ownership_allowlist.json"
    _write_json(
        allowlist,
        {
            "paper_id": paper,
            "result_ledger_sha256": _sha256(ledger),
            "artifacts": [
                {
                    "path": "figures/renamed_result.pdf",
                    "sha256": _sha256(package_artifact),
                    "claim_id": claim_id,
                    "ledger_artifact_path": "results/locked_figure.pdf",
                }
            ],
        },
    )
    return {
        "package": package,
        "package_artifact": package_artifact,
        "allowlist": allowlist,
        "ledger": ledger,
        "ledger_root": ledger_root,
        "ledger_artifact": ledger_artifact,
    }


def _rewrite_allowlist_ledger_hash(paths: dict[str, Path]) -> None:
    allowlist = json.loads(paths["allowlist"].read_text(encoding="utf-8"))
    allowlist["result_ledger_sha256"] = _sha256(paths["ledger"])
    _write_json(paths["allowlist"], allowlist)


def _find_owned_violations(
    paper: str,
    paths: dict[str, Path],
) -> list[str]:
    return find_violations(
        paper,
        paths["package"],
        ledger=paths["ledger"],
        ledger_root=paths["ledger_root"],
    )


def test_icbinb_rejects_attention_and_catalytic_evidence(tmp_path: Path):
    (tmp_path / "paper.tex").write_text(
        "An attention head and catalytic result.", encoding="utf-8"
    )

    violations = find_violations("icbinb-bio", tmp_path)

    assert any("attention-head" in item for item in violations)
    assert any("catalytic" in item for item in violations)


@pytest.mark.parametrize(
    ("paper", "text", "rule"),
    [
        ("icbinb-bio", "The L54 result supports the paper.", "l54-identifier"),
        (
            "icbinb-bio",
            "The l54_repro_out result supports the paper.",
            "l54-identifier",
        ),
        (
            "interp4discovery",
            "Steering improves the measured score.",
            "steering",
        ),
        (
            "interp4discovery",
            "The steered sequence changed the result.",
            "steering",
        ),
    ],
)
def test_m02_prohibited_text_examples_are_rejected(
    tmp_path: Path,
    paper: str,
    text: str,
    rule: str,
):
    (tmp_path / "paper.tex").write_text(text, encoding="utf-8")

    violations = find_violations(paper, tmp_path)

    assert any(f"prohibited {rule} evidence" in item for item in violations)


@pytest.mark.parametrize("suffix", [".bbl", ".bib", ".md", ".sty", ".txt", ".typ"])
def test_package_text_sources_are_scanned(tmp_path: Path, suffix: str):
    (tmp_path / f"source{suffix}").write_text(
        "The steered sequence changed the result.",
        encoding="utf-8",
    )

    violations = find_violations("interp4discovery", tmp_path)

    assert any("prohibited steering evidence" in item for item in violations)


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

    assert any("prohibited historical figure" in item for item in violations)
    assert any("not ownership-allowlisted" in item for item in violations)


def test_renamed_figure_without_allowlist_is_rejected(tmp_path: Path):
    figure = tmp_path / "figures" / "renamed_result.pdf"
    figure.parent.mkdir()
    figure.write_bytes(b"%PDF-1.4")
    figure.with_suffix(".tex").write_text("Standalone figure source.", encoding="utf-8")

    violations = find_violations("interp4discovery", tmp_path)

    assert violations == [
        "figures/renamed_result.pdf: evidence file is not ownership-allowlisted"
    ]


def test_figure_signature_cannot_be_hidden_by_generated_suffix(tmp_path: Path):
    figure = tmp_path / "renamed_result.aux"
    figure.write_bytes(b"%PDF-1.4")

    violations = find_violations("interp4discovery", tmp_path)

    assert violations == [
        "renamed_result.aux: evidence file is not ownership-allowlisted"
    ]


def test_compiled_root_manuscript_is_not_an_evidence_file(tmp_path: Path):
    (tmp_path / "paper.tex").write_text(
        "\\documentclass{article}\nContact ablation result.\n",
        encoding="utf-8",
    )
    (tmp_path / "paper.pdf").write_bytes(b"%PDF-1.4")

    assert find_violations("interp4discovery", tmp_path) == []


def test_valid_allowlisted_package_passes(tmp_path: Path):
    paths = _owned_package(tmp_path)

    assert _find_owned_violations("interp4discovery", paths) == []


def test_tampered_package_file_is_rejected(tmp_path: Path):
    paths = _owned_package(tmp_path)
    paths["package_artifact"].write_bytes(b"%PDF-1.4\ntampered package\n")

    violations = _find_owned_violations("interp4discovery", paths)

    assert any("package file sha256 does not match" in item for item in violations)


def test_tampered_ledger_artifact_is_rejected(tmp_path: Path):
    paths = _owned_package(tmp_path)
    paths["ledger_artifact"].write_bytes(b"%PDF-1.4\ntampered ledger artifact\n")

    violations = _find_owned_violations("interp4discovery", paths)

    assert any(
        "file sha256 does not match result ledger" in item for item in violations
    )


def test_result_ledger_hash_mismatch_is_rejected(tmp_path: Path):
    paths = _owned_package(tmp_path)
    rows = _read_csv(paths["ledger"])
    rows[0]["review_status"] = "changed after allowlist lock"
    _write_csv(paths["ledger"], rows)

    violations = _find_owned_violations("interp4discovery", paths)

    assert any("result ledger sha256 does not match" in item for item in violations)


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        (
            "paper_id",
            "icbinb-bio",
            "paper_id must be 'interp4discovery'",
        ),
        (
            "claim_id",
            "ICB-01",
            "claim_id must start with 'INT-'",
        ),
        (
            "derived_artifact_paths",
            "results/locked_figure.pdf",
            "must contain a JSON array",
        ),
    ],
)
def test_wrong_result_ledgers_are_rejected(
    tmp_path: Path,
    field: str,
    value: str,
    expected: str,
):
    paths = _owned_package(tmp_path)
    rows = _read_csv(paths["ledger"])
    rows[0][field] = value
    _write_csv(paths["ledger"], rows)
    _rewrite_allowlist_ledger_hash(paths)

    violations = _find_owned_violations("interp4discovery", paths)

    assert any(expected in item for item in violations)


@pytest.mark.parametrize(
    ("target", "field"),
    [
        ("allowlist", "path"),
        ("allowlist", "ledger_artifact_path"),
        ("ledger", "derived_artifact_paths"),
    ],
)
def test_path_escapes_are_rejected(
    tmp_path: Path,
    target: str,
    field: str,
):
    paths = _owned_package(tmp_path)
    if target == "allowlist":
        allowlist = json.loads(paths["allowlist"].read_text(encoding="utf-8"))
        allowlist["artifacts"][0][field] = "../outside.pdf"
        _write_json(paths["allowlist"], allowlist)
    else:
        rows = _read_csv(paths["ledger"])
        rows[0][field] = json.dumps(["../outside.pdf"])
        _write_csv(paths["ledger"], rows)
        _rewrite_allowlist_ledger_hash(paths)

    violations = _find_owned_violations("interp4discovery", paths)

    assert any("safe relative POSIX path" in item for item in violations)


@pytest.mark.parametrize("missing", ["package_artifact", "ledger_artifact"])
def test_missing_allowlisted_files_are_rejected(tmp_path: Path, missing: str):
    paths = _owned_package(tmp_path)
    paths[missing].unlink()

    violations = _find_owned_violations("interp4discovery", paths)

    assert any("file does not exist" in item for item in violations)


def test_mismatched_csv_artifact_arrays_are_rejected(tmp_path: Path):
    paths = _owned_package(tmp_path)
    rows = _read_csv(paths["ledger"])
    rows[0]["derived_artifact_sha256"] = "[]"
    _write_csv(paths["ledger"], rows)
    _rewrite_allowlist_ledger_hash(paths)

    violations = _find_owned_violations("interp4discovery", paths)

    assert any("must have equal lengths" in item for item in violations)


def test_csv_without_required_artifact_column_is_rejected(tmp_path: Path):
    paths = _owned_package(tmp_path)
    rows = _read_csv(paths["ledger"])
    with paths["ledger"].open("w", encoding="utf-8", newline="") as handle:
        columns = [
            column for column in LEDGER_COLUMNS if column != "derived_artifact_sha256"
        ]
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    _rewrite_allowlist_ledger_hash(paths)

    violations = _find_owned_violations("interp4discovery", paths)

    assert any("missing columns: derived_artifact_sha256" in item for item in violations)


def test_duplicate_controlling_claim_is_rejected(tmp_path: Path):
    paths = _owned_package(tmp_path)
    rows = _read_csv(paths["ledger"])
    rows.append(rows[0].copy())
    _write_csv(paths["ledger"], rows)
    _rewrite_allowlist_ledger_hash(paths)

    violations = _find_owned_violations("interp4discovery", paths)

    assert any("duplicate controlling claim" in item for item in violations)


@pytest.mark.parametrize("paper", ["icbinb-bio", "interp4discovery"])
def test_current_historical_packages_remain_rejected(paper: str):
    repository = Path(__file__).resolve().parents[1]
    package = repository / "docs" / "submissions" / paper

    assert find_violations(paper, package)


def test_unknown_paper_is_rejected(tmp_path: Path):
    with pytest.raises(ValueError, match="unknown paper"):
        find_violations("unknown", tmp_path)
