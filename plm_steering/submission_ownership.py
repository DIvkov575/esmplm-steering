"""Check paper sources for evidence owned by another submission."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any


PROHIBITED = {
    "icbinb-bio": {
        "text": {
            "attention-head": re.compile(r"attention[- ]head", re.IGNORECASE),
            "contact-enriched": re.compile(r"contact[- ]enrich", re.IGNORECASE),
            "catalytic": re.compile(r"\bcatalytic\b|\bdlkcat\b", re.IGNORECASE),
            "l54-identifier": re.compile(
                r"(?<![A-Za-z0-9])l54(?=$|[^A-Za-z0-9])",
                re.IGNORECASE,
            ),
        },
        "filenames": {
            "fig1_dose_response.pdf",
            "fig2_proxy_vs_effect.pdf",
            "fig3_seed_robustness.pdf",
        },
    },
    "interp4discovery": {
        "text": {
            "steering": re.compile(r"\bsteer(?:s|ed|ing)?\b", re.IGNORECASE),
            "steering-targets": re.compile(
                r"\bcatalytic\b|\bdisorder steering\b|\bexpression[- ]yield\b",
                re.IGNORECASE,
            ),
        },
        "filenames": {
            "fig1_dose_response.pdf",
            "fig2_proxy_vs_effect.pdf",
            "fig3_seed_robustness.pdf",
        },
    },
}

CLAIM_PREFIX = {
    "icbinb-bio": "ICB-",
    "interp4discovery": "INT-",
}

DEFAULT_ALLOWLIST = "ownership_allowlist.json"

TEXT_SOURCE_SUFFIXES = {
    ".bbl",
    ".bib",
    ".bst",
    ".cfg",
    ".cls",
    ".def",
    ".html",
    ".htm",
    ".jl",
    ".lua",
    ".md",
    ".org",
    ".py",
    ".r",
    ".rst",
    ".sh",
    ".sty",
    ".tex",
    ".txt",
    ".typ",
    ".xml",
}

SHA256_PATTERN = re.compile(r"[0-9a-fA-F]{64}")
RESULT_LEDGER_COLUMNS = {
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
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative_path(value: Any) -> PurePosixPath | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    if re.match(r"^[A-Za-z]:", value) or any(char in value for char in "*?[]"):
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or path == PurePosixPath("."):
        return None
    if any(part in {"", ".", ".."} for part in path.parts):
        return None
    return path


def _contained_file(root: Path, relative: PurePosixPath) -> Path | None:
    root = root.resolve()
    candidate = root.joinpath(*relative.parts).resolve()
    if not candidate.is_relative_to(root) or not candidate.is_file():
        return None
    return candidate


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_PATTERN.fullmatch(value) is not None


def _load_json(path: Path, label: str, violations: list[str]) -> Any | None:
    if not path.is_file():
        violations.append(f"{label}: file does not exist: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        violations.append(f"{label}: cannot read valid UTF-8 JSON: {error}")
        return None


def _load_csv(
    path: Path,
    label: str,
    violations: list[str],
) -> list[dict[str, str]] | None:
    if not path.is_file():
        violations.append(f"{label}: file does not exist: {path}")
        return None
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                violations.append(f"{label}: missing CSV header")
                return None
            if len(fieldnames) != len(set(fieldnames)):
                violations.append(f"{label}: CSV header contains duplicate columns")
                return None
            missing = sorted(RESULT_LEDGER_COLUMNS - set(fieldnames))
            if missing:
                violations.append(
                    f"{label}: CSV header is missing columns: {', '.join(missing)}"
                )
                return None
            rows = list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as error:
        violations.append(f"{label}: cannot read valid UTF-8 CSV: {error}")
        return None

    for index, row in enumerate(rows, start=2):
        if None in row:
            violations.append(
                f"{label} row {index}: has fields beyond the CSV header"
            )
    return rows


def _decode_json_array(
    row: dict[str, str],
    field: str,
    label: str,
    violations: list[str],
) -> list[Any] | None:
    value = row.get(field)
    try:
        decoded = json.loads(value) if value is not None else None
    except json.JSONDecodeError as error:
        violations.append(f"{label}: {field} must contain a JSON array: {error.msg}")
        return None
    if not isinstance(decoded, list):
        violations.append(f"{label}: {field} must contain a JSON array")
        return None
    return decoded


def _is_compiled_manuscript(path: Path, root: Path) -> bool:
    if path.suffix.lower() != ".pdf" or path.parent != root:
        return False
    for suffix, marker in {".tex": r"\documentclass", ".typ": "#set document"}.items():
        source = path.with_suffix(suffix)
        if not source.is_file():
            continue
        try:
            if marker in source.read_text(encoding="utf-8"):
                return True
        except (OSError, UnicodeDecodeError):
            continue
    return False


def _has_figure_signature(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            prefix = handle.read(16)
    except OSError:
        return False
    return (
        prefix.startswith(b"%PDF")
        or prefix.startswith(b"\x89PNG\r\n\x1a\n")
        or prefix.startswith(b"\xff\xd8\xff")
        or prefix.startswith((b"GIF87a", b"GIF89a", b"II*\x00", b"MM\x00*"))
    )


def _package_evidence_paths(
    root: Path,
    metadata_paths: set[Path],
) -> set[str]:
    evidence: set[str] = set()
    resolved_metadata = {path.resolve() for path in metadata_paths}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.resolve() in resolved_metadata:
            continue
        suffix = path.suffix.lower()
        if _is_compiled_manuscript(path, root):
            continue
        if _has_figure_signature(path):
            evidence.add(path.relative_to(root).as_posix())
            continue
        if suffix in TEXT_SOURCE_SUFFIXES:
            continue
        evidence.add(path.relative_to(root).as_posix())
    return evidence


def _ledger_artifacts(
    paper: str,
    rows: list[dict[str, str]],
    ledger_root: Path,
    violations: list[str],
) -> dict[tuple[str, str], str]:
    prefix = CLAIM_PREFIX[paper]
    artifacts: dict[tuple[str, str], str] = {}
    seen_claims: set[str] = set()
    for index, row in enumerate(rows, start=2):
        label = f"result ledger row {index}"
        claim_id = row.get("claim_id")
        row_paper = row.get("paper_id")
        row_valid = True
        if not isinstance(claim_id, str) or not claim_id.startswith(prefix):
            violations.append(f"{label}: claim_id must start with {prefix!r}")
            row_valid = False
        elif claim_id in seen_claims:
            violations.append(f"{label}: duplicate controlling claim {claim_id!r}")
            row_valid = False
        else:
            seen_claims.add(claim_id)
        if row_paper != paper:
            violations.append(f"{label}: paper_id must be {paper!r}")
            row_valid = False

        for artifact_kind in ("raw", "derived"):
            paths = _decode_json_array(
                row,
                f"{artifact_kind}_artifact_paths",
                label,
                violations,
            )
            hashes = _decode_json_array(
                row,
                f"{artifact_kind}_artifact_sha256",
                label,
                violations,
            )
            if paths is None or hashes is None:
                continue
            if len(paths) != len(hashes):
                violations.append(
                    f"{label}: {artifact_kind} artifact paths and hashes "
                    "must have equal lengths"
                )
                continue

            for artifact_index, (value, expected_hash) in enumerate(
                zip(paths, hashes, strict=True)
            ):
                artifact_label = (
                    f"{label} {artifact_kind} artifact {artifact_index}"
                )
                relative = _safe_relative_path(value)
                if relative is None:
                    violations.append(
                        f"{artifact_label}: path must be a safe relative POSIX path"
                    )
                    continue
                if not _valid_sha256(expected_hash):
                    violations.append(
                        f"{artifact_label}: sha256 must be 64 hexadecimal characters"
                    )
                    continue

                source = _contained_file(ledger_root, relative)
                if source is None:
                    violations.append(
                        f"{artifact_label}: file does not exist inside ledger root"
                    )
                    continue
                actual_hash = _sha256(source)
                if actual_hash != expected_hash.lower():
                    violations.append(
                        f"{artifact_label}: file sha256 does not match result ledger"
                    )
                    continue
                if not row_valid:
                    continue

                key = (claim_id, relative.as_posix())
                if key in artifacts:
                    violations.append(
                        f"{artifact_label}: duplicate artifact mapping for {key!r}"
                    )
                    continue
                artifacts[key] = actual_hash
    return artifacts


def _validate_ownership_allowlist(
    paper: str,
    root: Path,
    evidence_paths: set[str],
    allowlist_path: Path | None,
    ledger_path: Path | None,
    ledger_root: Path | None,
    violations: list[str],
) -> None:
    if allowlist_path is None:
        for path in sorted(evidence_paths):
            violations.append(f"{path}: evidence file is not ownership-allowlisted")
        return

    allowlist_data = _load_json(allowlist_path, "ownership allowlist", violations)
    if not isinstance(allowlist_data, dict):
        if allowlist_data is not None:
            violations.append("ownership allowlist: top level must be a JSON object")
        return
    if allowlist_data.get("paper_id") != paper:
        violations.append(f"ownership allowlist: paper_id must be {paper!r}")

    expected_ledger_hash = allowlist_data.get("result_ledger_sha256")
    if not _valid_sha256(expected_ledger_hash):
        violations.append(
            "ownership allowlist: result_ledger_sha256 must be "
            "64 hexadecimal characters"
        )

    ledger_artifacts: dict[tuple[str, str], str] = {}
    if ledger_path is None:
        violations.append("ownership allowlist: a result ledger is required")
    else:
        ledger_rows = _load_csv(ledger_path, "result ledger", violations)
        if ledger_rows is not None:
            actual_ledger_hash = _sha256(ledger_path)
            if _valid_sha256(expected_ledger_hash):
                if actual_ledger_hash != expected_ledger_hash.lower():
                    violations.append(
                        "ownership allowlist: result ledger sha256 does not match"
                    )
            ledger_artifacts = _ledger_artifacts(
                paper,
                ledger_rows,
                ledger_root or Path.cwd(),
                violations,
            )

    entries = allowlist_data.get("artifacts")
    if not isinstance(entries, list):
        violations.append("ownership allowlist: artifacts must be a JSON array")
        entries = []

    prefix = CLAIM_PREFIX[paper]
    allowlisted_paths: set[str] = set()
    for index, entry in enumerate(entries):
        label = f"ownership allowlist entry {index}"
        if not isinstance(entry, dict):
            violations.append(f"{label}: must be a JSON object")
            continue

        package_relative = _safe_relative_path(entry.get("path"))
        if package_relative is None:
            violations.append(f"{label}: path must be a safe relative POSIX path")
            continue
        package_path = package_relative.as_posix()
        if package_path in allowlisted_paths:
            violations.append(f"{label}: duplicate package path {package_path!r}")
            continue
        allowlisted_paths.add(package_path)

        package_file = _contained_file(root, package_relative)
        if package_file is None:
            violations.append(f"{label}: package file does not exist")
            continue

        package_hash = entry.get("sha256")
        if not _valid_sha256(package_hash):
            violations.append(
                f"{label}: sha256 must be 64 hexadecimal characters"
            )
            continue
        actual_package_hash = _sha256(package_file)
        if actual_package_hash != package_hash.lower():
            violations.append(f"{label}: package file sha256 does not match")

        claim_id = entry.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id.startswith(prefix):
            violations.append(f"{label}: claim_id must start with {prefix!r}")
            continue

        ledger_relative = _safe_relative_path(entry.get("ledger_artifact_path"))
        if ledger_relative is None:
            violations.append(
                f"{label}: ledger_artifact_path must be a safe relative POSIX path"
            )
            continue
        ledger_key = (claim_id, ledger_relative.as_posix())
        ledger_hash = ledger_artifacts.get(ledger_key)
        if ledger_hash is None:
            violations.append(
                f"{label}: claim and artifact are absent from the result ledger"
            )
        elif ledger_hash != package_hash.lower():
            violations.append(
                f"{label}: package sha256 does not match the result-ledger artifact"
            )

    for path in sorted(evidence_paths - allowlisted_paths):
        violations.append(f"{path}: evidence file is not ownership-allowlisted")


def find_violations(
    paper: str,
    root: Path,
    *,
    allowlist: Path | None = None,
    ledger: Path | None = None,
    ledger_root: Path | None = None,
) -> list[str]:
    if paper not in PROHIBITED:
        raise ValueError(f"unknown paper: {paper}")
    root = Path(root)
    if not root.is_dir():
        raise ValueError(f"package root is not a directory: {root}")

    violations: list[str] = []
    rules = PROHIBITED[paper]
    resolved_root = root.resolve()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if not path.resolve().is_relative_to(resolved_root):
            violations.append(f"{relative}: file resolves outside package root")
            continue
        if path.name in rules["filenames"]:
            violations.append(f"{relative}: prohibited historical figure")
        if path.suffix.lower() not in TEXT_SOURCE_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            violations.append(f"{relative}: cannot scan UTF-8 text source: {error}")
            continue
        for name, pattern in rules["text"].items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                violations.append(f"{relative}:{line}: prohibited {name} evidence")

    allowlist_path = Path(allowlist) if allowlist is not None else None
    default_allowlist = root / DEFAULT_ALLOWLIST
    if allowlist_path is None and default_allowlist.is_file():
        allowlist_path = default_allowlist
    ledger_path = Path(ledger) if ledger is not None else None
    ledger_root_path = Path(ledger_root) if ledger_root is not None else None
    metadata_paths = {
        path
        for path in (allowlist_path, ledger_path)
        if path is not None and path.is_file()
    }
    evidence_paths = _package_evidence_paths(root, metadata_paths)
    if evidence_paths or allowlist_path is not None or ledger_path is not None:
        _validate_ownership_allowlist(
            paper,
            root,
            evidence_paths,
            allowlist_path,
            ledger_path,
            ledger_root_path,
            violations,
        )
    return violations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", choices=sorted(PROHIBITED), required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument(
        "--allowlist",
        type=Path,
        help=f"package ownership allowlist (default: ROOT/{DEFAULT_ALLOWLIST})",
    )
    parser.add_argument("--ledger", type=Path, help="hash-locked result ledger CSV")
    parser.add_argument(
        "--ledger-root",
        type=Path,
        help=(
            "root for repository-relative ledger artifacts "
            "(default: current directory)"
        ),
    )
    args = parser.parse_args()

    violations = find_violations(
        args.paper,
        args.root,
        allowlist=args.allowlist,
        ledger=args.ledger,
        ledger_root=args.ledger_root,
    )
    for violation in violations:
        print(violation)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
