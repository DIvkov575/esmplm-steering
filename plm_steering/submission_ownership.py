"""Check submission packages against claim and evidence ownership contracts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any


PROHIBITED = {
    "icbinb-bio": {
        "text": {
            "attention-head": re.compile(r"attention[- ]head", re.IGNORECASE),
            "contact-enriched": re.compile(r"contact[- ]enrich", re.IGNORECASE),
            "catalytic": re.compile(r"\bcatalytic\b|\bdlkcat\b", re.IGNORECASE),
            "excluded-study-identifier": re.compile(
                r"(?<![A-Za-z0-9])l(?:43|48|49|54)(?=$|[^A-Za-z0-9])",
                re.IGNORECASE,
            ),
        },
        "artifact_paths": {
            "excluded-study-identifier": re.compile(
                r"(?<![A-Za-z0-9])l(?:43|48|49|54)(?=$|[^A-Za-z0-9])",
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
            "steering": re.compile(
                r"(?<![A-Za-z0-9])steer(?:s|ed|ing)?(?=$|[^A-Za-z0-9])",
                re.IGNORECASE,
            ),
            "steering-targets": re.compile(
                r"\bcatalytic\b|\bdisorder steering\b|\bexpression[- ]yield\b",
                re.IGNORECASE,
            ),
            "foreign-study-identifier": re.compile(
                r"(?<![A-Za-z0-9])l(?:42|43|51|52|53|54|55|56|57|58)"
                r"(?=$|[^A-Za-z0-9])",
                re.IGNORECASE,
            ),
        },
        "artifact_paths": {
            "steering": re.compile(
                r"(?<![A-Za-z0-9])steer(?:s|ed|ing)?(?=$|[^A-Za-z0-9])",
                re.IGNORECASE,
            ),
            "foreign-study-identifier": re.compile(
                r"(?<![A-Za-z0-9])l(?:42|43|51|52|53|54|55|56|57|58)"
                r"(?=$|[^A-Za-z0-9])",
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
DEFAULT_CLAIM_REGISTRY = "docs/CLAIM_REGISTRY.md"
MANUSCRIPT_PDF = "paper.pdf"
CANONICAL_SUBMISSION_CONTRACT = "docs/SUBMISSION_CONTRACT.json"
CANONICAL_ARTIFACT_OWNERSHIP = "docs/ARTIFACT_OWNERSHIP.json"
EXPECTED_SUBMISSION_CONTRACT_SHA256 = (
    "6aee4fc1d51cfa21d19662ff6cd6c3c71f5411cb47c1065e15292a408852041f"
)
EXPECTED_ARTIFACT_OWNERSHIP_SHA256 = (
    "b6adfd175b79eca596bf31608b8bed63728b29da0851fc80248fdbfc34c522e3"
)
EXPECTED_CLAIM_IDS = {
    "icbinb-bio": {"ICB-01", "ICB-02", "ICB-03", "ICB-04", "ICB-05", "ICB-06"},
    "interp4discovery": {"INT-01", "INT-02", "INT-03"},
}

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

RESULT_LEDGER_COLUMNS = {
    "claim_id",
    "paper_id",
    "claim_text_sha256",
    "source_study_ids",
    "claim_status",
    "status_reason",
    "provenance",
    "estimand",
    "statistical_unit",
    "control",
    "cohort_manifest_path",
    "cohort_manifest_sha256",
    "experiment_manifest_path",
    "experiment_manifest_sha256",
    "lineage_manifest_path",
    "lineage_manifest_sha256",
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

CONTRACT_FIELDS = {
    "provenance",
    "estimand",
    "statistical_unit",
    "control",
    "limitation",
}

RESULT_FIELDS = {"point_estimate", "interval", "denominator"}

STATUS_GATES = {
    "confirmed": {"pass"},
    "conditional": {"not_run"},
    "rejected": {"fail", "not_estimable"},
    "deferred": {"not_run"},
    "stopped": {"fail", "not_estimable", "not_run"},
}

REVIEW_ROLES = {
    "statistical_reviewer": "statistical_reviewer_id",
    "final_technical_reviewer": "final_technical_reviewer_id",
}

SHA256_PATTERN = re.compile(r"[0-9a-fA-F]{64}")
COMMIT_PATTERN = re.compile(r"[0-9a-fA-F]{40}")
CLAIM_HEADING_PATTERN = re.compile(r"^### ((?:ICB|INT)-\d+)$")
IDENTITY_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:@/-]{0,127}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_PATTERN.fullmatch(value) is not None


def _valid_commit(value: Any) -> bool:
    return isinstance(value, str) and COMMIT_PATTERN.fullmatch(value) is not None


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_identity(value: Any) -> bool:
    return isinstance(value, str) and IDENTITY_PATTERN.fullmatch(value) is not None


def _finite_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    return isinstance(value, float) and math.isfinite(value)


def _numeric_payload(value: Any) -> bool:
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, bool) or item is None or isinstance(item, str):
            return False
        if _finite_number(item):
            continue
        if isinstance(item, list):
            if not item:
                return False
            pending.extend(item)
            continue
        if isinstance(item, dict):
            if not item or not all(_nonempty_string(key) for key in item):
                return False
            pending.extend(item.values())
            continue
        return False
    return True


def _valid_interval_bounds(value: Any) -> bool:
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, list):
            if (
                len(item) != 2
                or not all(_finite_number(bound) for bound in item)
                or item[0] > item[1]
            ):
                return False
            continue
        if not isinstance(item, dict) or not item:
            return False
        if set(item) == {"lower", "upper"}:
            lower = item["lower"]
            upper = item["upper"]
            if (
                not _finite_number(lower)
                or not _finite_number(upper)
                or lower > upper
            ):
                return False
            continue
        if not all(_nonempty_string(key) for key in item):
            return False
        pending.extend(item.values())
    return True


def _safe_relative_path(value: Any) -> PurePosixPath | None:
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or "\x00" in value
    ):
        return None
    if re.match(r"^[A-Za-z]:", value) or any(char in value for char in "*?[]"):
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or path == PurePosixPath("."):
        return None
    if any(part in {"", ".", ".."} for part in path.parts):
        return None
    return path


def _has_symlink_component(path: Path) -> bool:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            return True
    return False


def _contained_file(root: Path, relative: PurePosixPath) -> Path | None:
    unresolved = root.joinpath(*relative.parts)
    if _has_symlink_component(unresolved):
        return None
    try:
        resolved_root = root.resolve()
        candidate = unresolved.resolve()
    except (OSError, RuntimeError):
        return None
    if not candidate.is_relative_to(resolved_root) or not candidate.is_file():
        return None
    return candidate


def _load_json(path: Path, label: str, violations: list[str]) -> Any | None:
    if not path.is_file():
        violations.append(f"{label}: file does not exist: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        RecursionError,
    ) as error:
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
            unexpected = sorted(set(fieldnames) - RESULT_LEDGER_COLUMNS)
            if unexpected:
                violations.append(
                    f"{label}: CSV header has unexpected columns: "
                    f"{', '.join(unexpected)}"
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


def _load_bound_repository_json(
    root: Path,
    path_value: Any,
    hash_value: Any,
    label: str,
    violations: list[str],
) -> tuple[str, str, Path | None, Any | None, bool]:
    valid = True
    relative = _safe_relative_path(path_value)
    if relative is None:
        violations.append(f"{label}: path must be a safe relative POSIX path")
        valid = False
    if not _valid_sha256(hash_value):
        violations.append(f"{label}: sha256 must be 64 hexadecimal characters")
        valid = False
    if relative is None:
        return "", "", None, None, False

    file_path = _contained_file(root, relative)
    if file_path is None:
        violations.append(f"{label}: file does not exist inside ledger root")
        return relative.as_posix(), "", None, None, False
    actual_hash = _sha256(file_path)
    if _valid_sha256(hash_value) and actual_hash != hash_value.lower():
        violations.append(f"{label}: sha256 does not match")
        valid = False
    data = _load_json(file_path, label, violations)
    if data is None:
        valid = False
    return relative.as_posix(), actual_hash, file_path, data, valid


def _decode_json_cell(
    value: Any,
    expected_type: type,
    field: str,
    label: str,
    violations: list[str],
) -> Any | None:
    try:
        decoded = json.loads(value) if isinstance(value, str) else None
    except (json.JSONDecodeError, ValueError, RecursionError) as error:
        detail = getattr(error, "msg", str(error))
        violations.append(f"{label}: {field} contains invalid JSON: {detail}")
        return None
    if not isinstance(decoded, expected_type):
        violations.append(
            f"{label}: {field} must contain a JSON {expected_type.__name__}"
        )
        return None
    return decoded


def _load_claim_registry(
    path: Path,
    violations: list[str],
) -> dict[str, dict[str, str]]:
    if not path.is_file():
        violations.append(f"claim registry: file does not exist: {path}")
        return {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as error:
        violations.append(f"claim registry: cannot read valid UTF-8: {error}")
        return {}

    headings: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = CLAIM_HEADING_PATTERN.fullmatch(line)
        if match is not None:
            headings.append((index, match.group(1)))

    claims: dict[str, dict[str, str]] = {}
    for heading_index, (start, claim_id) in enumerate(headings):
        end = (
            headings[heading_index + 1][0]
            if heading_index + 1 < len(headings)
            else len(lines)
        )
        block = lines[start + 1 : end]
        try:
            claim_marker = block.index("Claim:")
        except ValueError:
            violations.append(f"claim registry: {claim_id} has no Claim field")
            continue
        quote_lines = [
            line.removeprefix(">").strip()
            for line in block[claim_marker + 1 :]
            if line.startswith(">")
        ]
        claim_text = " ".join(part for part in quote_lines if part)
        if not claim_text:
            violations.append(f"claim registry: {claim_id} has no quoted claim text")
            continue
        if claim_id in claims:
            violations.append(f"claim registry: duplicate claim ID {claim_id!r}")
            continue
        paper = "icbinb-bio" if claim_id.startswith("ICB-") else "interp4discovery"
        claims[claim_id] = {
            "paper_id": paper,
            "claim_text_sha256": hashlib.sha256(
                claim_text.encode("utf-8")
            ).hexdigest(),
        }
    return claims


def _validate_submission_contract(
    data: Any,
    paper: str,
    registry_hash: str,
    registry_claims: dict[str, dict[str, str]],
    violations: list[str],
) -> tuple[dict[str, dict[str, Any]], str, str, bool]:
    start = len(violations)
    if not isinstance(data, dict):
        violations.append("submission contract: top level must be a JSON object")
        return {}, "", "", False
    if data.get("schema_version") != "1.0":
        violations.append("submission contract: schema_version must be '1.0'")
    if data.get("claim_registry_sha256") != registry_hash:
        violations.append(
            "submission contract: claim_registry_sha256 does not match"
        )

    ownership_path = data.get("artifact_ownership_path")
    ownership_hash = data.get("artifact_ownership_sha256")
    if _safe_relative_path(ownership_path) is None:
        violations.append(
            "submission contract: artifact_ownership_path must be a safe "
            "relative POSIX path"
        )
        ownership_path = ""
    elif ownership_path != CANONICAL_ARTIFACT_OWNERSHIP:
        violations.append(
            "submission contract: artifact_ownership_path is not canonical"
        )
    if not _valid_sha256(ownership_hash):
        violations.append(
            "submission contract: artifact_ownership_sha256 must be "
            "64 hexadecimal characters"
        )
        ownership_hash = ""
    elif ownership_hash.lower() != EXPECTED_ARTIFACT_OWNERSHIP_SHA256:
        violations.append(
            "submission contract: artifact_ownership_sha256 is not trusted"
        )

    papers = data.get("papers")
    if not isinstance(papers, dict):
        violations.append("submission contract: papers must be a JSON object")
        return {}, str(ownership_path), str(ownership_hash), False
    paper_contract = papers.get(paper)
    if not isinstance(paper_contract, dict):
        violations.append(
            f"submission contract: missing paper contract for {paper!r}"
        )
        return {}, str(ownership_path), str(ownership_hash), False

    required_ids = paper_contract.get("required_claim_ids")
    claims = paper_contract.get("claims")
    if (
        not isinstance(required_ids, list)
        or not required_ids
        or not all(_nonempty_string(item) for item in required_ids)
        or len(required_ids) != len(set(required_ids))
    ):
        violations.append(
            "submission contract: required_claim_ids must contain unique strings"
        )
        required_ids = []
    if not isinstance(claims, dict):
        violations.append("submission contract: claims must be a JSON object")
        claims = {}
    if set(required_ids) != set(claims):
        violations.append(
            "submission contract: required_claim_ids and claims must match exactly"
        )
    if set(required_ids) != EXPECTED_CLAIM_IDS[paper]:
        violations.append(
            "submission contract: required_claim_ids do not match the trusted set"
        )

    prefix = CLAIM_PREFIX[paper]
    validated: dict[str, dict[str, Any]] = {}
    for claim_id in required_ids:
        label = f"submission contract claim {claim_id}"
        claim = claims.get(claim_id)
        if not claim_id.startswith(prefix):
            violations.append(f"{label}: claim ID must start with {prefix!r}")
        registry_claim = registry_claims.get(claim_id)
        if registry_claim is None:
            violations.append(f"{label}: claim is absent from the claim registry")
        elif registry_claim["paper_id"] != paper:
            violations.append(f"{label}: claim registry assigns another paper")
        if not isinstance(claim, dict):
            violations.append(f"{label}: must be a JSON object")
            continue

        studies = claim.get("source_study_ids")
        if (
            not isinstance(studies, list)
            or not studies
            or not all(_nonempty_string(item) for item in studies)
            or len(studies) != len(set(studies))
        ):
            violations.append(
                f"{label}: source_study_ids must contain unique nonempty strings"
            )

        for field in CONTRACT_FIELDS:
            if not _nonempty_string(claim.get(field)):
                violations.append(f"{label}: {field} must be a nonempty string")
        if claim.get("provenance") not in {
            "prospective",
            "retrospective",
            "post_hoc_sensitivity",
        }:
            violations.append(f"{label}: provenance is invalid")

        requirements = claim.get("result_requirements")
        if not isinstance(requirements, dict) or set(requirements) != RESULT_FIELDS:
            violations.append(
                f"{label}: result_requirements must contain exactly "
                "point_estimate, interval, and denominator"
            )
        elif any(
            value not in {"required", "not_applicable"}
            for value in requirements.values()
        ):
            violations.append(
                f"{label}: result requirements must be required or not_applicable"
            )
        validated[claim_id] = claim

    return (
        validated,
        str(ownership_path),
        str(ownership_hash),
        len(violations) == start,
    )


def _validate_role_assignments(
    data: Any,
    paper: str,
    violations: list[str],
) -> tuple[dict[str, Any], bool]:
    start = len(violations)
    if not isinstance(data, dict):
        violations.append("role assignments: top level must be a JSON object")
        return {}, False
    if data.get("schema_version") != "1.0":
        violations.append("role assignments: schema_version must be '1.0'")
    if data.get("paper_id") != paper:
        violations.append(f"role assignments: paper_id must be {paper!r}")
    if not _valid_commit(data.get("source_git_commit")):
        violations.append(
            "role assignments: source_git_commit must be a full commit hash"
        )
    for field in (
        "orchestrator_id",
        "paper_owner_id",
        "statistical_reviewer_id",
        "final_technical_reviewer_id",
    ):
        if not _valid_identity(data.get(field)):
            violations.append(
                f"role assignments: {field} must be a canonical identity"
            )

    owners = data.get("experiment_owner_ids")
    if (
        not isinstance(owners, list)
        or not owners
        or not all(_valid_identity(item) for item in owners)
        or len(owners) != len(set(owners))
    ):
        violations.append(
            "role assignments: experiment_owner_ids must contain unique "
            "canonical identities"
        )
        owners = []

    separated_ids = [
        data.get("paper_owner_id"),
        *owners,
        data.get("statistical_reviewer_id"),
        data.get("final_technical_reviewer_id"),
    ]
    nonempty_ids = [value for value in separated_ids if _valid_identity(value)]
    if len(nonempty_ids) != len(set(nonempty_ids)):
        violations.append(
            "role assignments: paper, experiment, and reviewer identities "
            "must be pairwise distinct"
        )
    if paper == "interp4discovery" and len(owners) != 4:
        violations.append(
            "role assignments: Interp4Discovery requires four distinct "
            "experiment owners"
        )
    return data, len(violations) == start


def _validate_artifact_ownership(
    data: Any,
    root: Path,
    violations: list[str],
) -> tuple[dict[str, dict[str, Any]], bool]:
    start = len(violations)
    if not isinstance(data, dict):
        violations.append("artifact ownership: top level must be a JSON object")
        return {}, False
    if data.get("schema_version") != "1.0":
        violations.append("artifact ownership: schema_version must be '1.0'")
    entries = data.get("artifacts")
    if not isinstance(entries, list):
        violations.append("artifact ownership: artifacts must be a JSON array")
        return {}, False

    by_hash: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        label = f"artifact ownership entry {index}"
        if not isinstance(entry, dict):
            violations.append(f"{label}: must be a JSON object")
            continue
        relative = _safe_relative_path(entry.get("path"))
        artifact_hash = entry.get("sha256")
        if relative is None:
            violations.append(f"{label}: path must be a safe relative POSIX path")
        if not _valid_sha256(artifact_hash):
            violations.append(
                f"{label}: sha256 must be 64 hexadecimal characters"
            )
        if not _nonempty_string(entry.get("study_id")):
            violations.append(f"{label}: study_id must be nonempty")
        for field in ("allowed_papers", "permitted_claim_ids"):
            values = entry.get(field)
            if (
                not isinstance(values, list)
                or not all(_nonempty_string(item) for item in values)
                or len(values) != len(set(values))
            ):
                violations.append(
                    f"{label}: {field} must contain unique nonempty strings"
                )
        canonical_present = entry.get("canonical_present", True)
        if not isinstance(canonical_present, bool):
            violations.append(f"{label}: canonical_present must be a boolean")
        if relative is not None and _valid_sha256(artifact_hash):
            normalized_hash = artifact_hash.lower()
            if normalized_hash in by_hash:
                violations.append(f"{label}: duplicate known artifact sha256")
                continue
            canonical = _contained_file(root, relative)
            if canonical_present and canonical is None:
                violations.append(
                    f"{label}: canonical artifact does not exist inside ledger root"
                )
            elif canonical_present and _sha256(canonical) != normalized_hash:
                violations.append(f"{label}: canonical artifact sha256 does not match")
            elif not canonical_present:
                if canonical is not None:
                    violations.append(
                        f"{label}: historical-only canonical artifact still exists"
                    )
                if entry.get("allowed_papers") or entry.get("permitted_claim_ids"):
                    violations.append(
                        f"{label}: historical-only hash cannot authorize evidence"
                    )
            by_hash[normalized_hash] = entry
    return by_hash, len(violations) == start


def _load_trusted_artifact_catalog(
    root: Path,
    violations: list[str],
) -> dict[str, dict[str, Any]]:
    (
        loaded_path,
        loaded_hash,
        _,
        data,
        file_valid,
    ) = _load_bound_repository_json(
        root,
        CANONICAL_ARTIFACT_OWNERSHIP,
        EXPECTED_ARTIFACT_OWNERSHIP_SHA256,
        "trusted artifact ownership",
        violations,
    )
    if loaded_path != CANONICAL_ARTIFACT_OWNERSHIP:
        violations.append("trusted artifact ownership: path is not canonical")
    if loaded_hash != EXPECTED_ARTIFACT_OWNERSHIP_SHA256:
        violations.append("trusted artifact ownership: hash is not trusted")
    catalog, catalog_valid = _validate_artifact_ownership(data, root, violations)
    return catalog if file_valid and catalog_valid else {}


def _known_hash_allowed(
    artifact_hash: str,
    paper: str,
    claim_id: str,
    catalog: dict[str, dict[str, Any]],
    label: str,
    violations: list[str],
    *,
    declared_study: str | None = None,
) -> bool:
    entry = catalog.get(artifact_hash.lower())
    if entry is None:
        return True
    valid = True
    if paper not in entry.get("allowed_papers", []):
        violations.append(f"{label}: known artifact hash is owned by another paper")
        valid = False
    if claim_id not in entry.get("permitted_claim_ids", []):
        violations.append(f"{label}: known artifact hash is not permitted for claim")
        valid = False
    if declared_study is not None and entry.get("study_id") != declared_study:
        violations.append(f"{label}: source study conflicts with known artifact hash")
        valid = False
    return valid


def _validate_bound_file_pair(
    row: dict[str, str],
    prefix: str,
    label: str,
    root: Path,
    required: bool,
    violations: list[str],
) -> tuple[str, str, Path | None, bool]:
    path_value = row.get(f"{prefix}_path", "")
    hash_value = row.get(f"{prefix}_sha256", "")
    if not path_value and not hash_value:
        if required:
            violations.append(f"{label}: {prefix} path and sha256 are required")
            return "", "", None, False
        return "", "", None, True
    valid = True
    relative = _safe_relative_path(path_value)
    if relative is None:
        violations.append(
            f"{label}: {prefix}_path must be a safe relative POSIX path"
        )
        valid = False
    if not _valid_sha256(hash_value):
        violations.append(
            f"{label}: {prefix}_sha256 must be 64 hexadecimal characters"
        )
        valid = False
    if relative is None:
        return "", "", None, False
    file_path = _contained_file(root, relative)
    if file_path is None:
        violations.append(
            f"{label}: {prefix} file does not exist inside ledger root"
        )
        return relative.as_posix(), "", None, False
    actual_hash = _sha256(file_path)
    if _valid_sha256(hash_value) and actual_hash != hash_value.lower():
        violations.append(f"{label}: {prefix} sha256 does not match")
        valid = False
    return relative.as_posix(), actual_hash, file_path, valid


def _validate_manifest_content(
    data: Any,
    kind: str,
    paper: str,
    claim_id: str,
    row: dict[str, str],
    claim_contract: dict[str, Any],
    roles: dict[str, Any],
    contract_hash: str,
    roles_hash: str,
    violations: list[str],
) -> bool:
    start = len(violations)
    label = f"{kind} manifest for {claim_id}"
    if not isinstance(data, dict):
        violations.append(f"{label}: top level must be a JSON object")
        return False
    expected = {
        "schema_version": "1.0",
        "paper_id": paper,
        "source_git_commit": row.get("source_git_commit"),
        "submission_contract_sha256": contract_hash,
        "role_assignments_sha256": roles_hash,
        "source_study_ids": claim_contract.get("source_study_ids"),
    }
    for field, expected_value in expected.items():
        if data.get(field) != expected_value:
            violations.append(f"{label}: {field} does not match the ledger contract")
    if not _nonempty_string(data.get("experiment_id")):
        violations.append(f"{label}: experiment_id must be nonempty")
    claim_ids = data.get("claim_ids")
    if (
        not isinstance(claim_ids, list)
        or claim_id not in claim_ids
        or not all(_nonempty_string(item) for item in claim_ids)
        or len(claim_ids) != len(set(claim_ids))
    ):
        violations.append(
            f"{label}: claim_ids must contain this claim and unique strings"
        )
    expected_statuses = {"frozen"} if kind == "cohort" else {"frozen", "locked"}
    if data.get("status") not in expected_statuses:
        violations.append(f"{label}: status is not accepted for this manifest")
    if data.get("owner_id") not in roles.get("experiment_owner_ids", []):
        violations.append(f"{label}: owner_id is not an assigned experiment owner")
    return len(violations) == start


def _validate_parent_lock(
    data: Any,
    label: str,
    paper: str,
    claim_id: str,
    row: dict[str, str],
    claim_contract: dict[str, Any],
    roles: dict[str, Any],
    contract_hash: str,
    roles_hash: str,
    catalog: dict[str, dict[str, Any]],
    root: Path,
    violations: list[str],
) -> set[tuple[str, str]]:
    start = len(violations)
    if not isinstance(data, dict):
        violations.append(f"{label}: top level must be a JSON object")
        return set()
    expected = {
        "schema_version": "1.0",
        "paper_id": paper,
        "source_git_commit": row.get("source_git_commit"),
        "submission_contract_sha256": contract_hash,
        "role_assignments_sha256": roles_hash,
    }
    for field, expected_value in expected.items():
        if data.get(field) != expected_value:
            violations.append(f"{label}: {field} does not match the ledger contract")
    claim_ids = data.get("claim_ids")
    if (
        not isinstance(claim_ids, list)
        or claim_id not in claim_ids
        or not all(_nonempty_string(item) for item in claim_ids)
        or len(claim_ids) != len(set(claim_ids))
    ):
        violations.append(
            f"{label}: claim_ids must contain this claim and unique strings"
        )
    if data.get("status") not in {"accepted", "locked"}:
        violations.append(f"{label}: status must be accepted or locked")
    if data.get("owner_id") not in roles.get("experiment_owner_ids", []):
        violations.append(f"{label}: owner_id is not an assigned experiment owner")

    allowed_studies = set(claim_contract.get("source_study_ids", []))
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        violations.append(f"{label}: artifacts must be a nonempty JSON array")
        return set()
    references: set[tuple[str, str]] = set()
    for index, artifact in enumerate(artifacts):
        artifact_label = f"{label} artifact {index}"
        if not isinstance(artifact, dict) or set(artifact) != {
            "path",
            "sha256",
            "source_study_id",
        }:
            violations.append(
                f"{artifact_label}: must contain path, sha256, and source_study_id"
            )
            continue
        relative = _safe_relative_path(artifact.get("path"))
        artifact_hash = artifact.get("sha256")
        study = artifact.get("source_study_id")
        if relative is None:
            violations.append(
                f"{artifact_label}: path must be a safe relative POSIX path"
            )
            continue
        if not _valid_sha256(artifact_hash):
            violations.append(
                f"{artifact_label}: sha256 must be 64 hexadecimal characters"
            )
            continue
        if study not in allowed_studies:
            violations.append(f"{artifact_label}: source_study_id is not allowed")
        file_path = _contained_file(root, relative)
        if file_path is None:
            violations.append(f"{artifact_label}: file does not exist")
            continue
        actual_hash = _sha256(file_path)
        if actual_hash != artifact_hash.lower():
            violations.append(f"{artifact_label}: file sha256 does not match")
            continue
        _known_hash_allowed(
            actual_hash,
            paper,
            claim_id,
            catalog,
            artifact_label,
            violations,
            declared_study=study if isinstance(study, str) else None,
        )
        reference = (relative.as_posix(), actual_hash)
        if reference in references:
            violations.append(f"{artifact_label}: duplicate artifact reference")
        references.add(reference)
    if len(violations) != start:
        return set()
    return references


def _validate_typed_result(
    value: Any,
    field: str,
    requirement: str,
    confirmed: bool,
    label: str,
    violations: list[str],
) -> bool:
    result = _decode_json_cell(value, dict, field, label, violations)
    if result is None:
        return False
    status = result.get("status")
    if not confirmed and status == "not_available":
        if set(result) != {"status", "reason"} or not _nonempty_string(
            result.get("reason")
        ):
            violations.append(
                f"{label}: {field} not_available requires only a nonempty reason"
            )
            return False
        return True
    if requirement == "not_applicable":
        if (
            set(result) != {"status", "reason"}
            or status != "not_applicable"
            or not _nonempty_string(result.get("reason"))
        ):
            violations.append(
                f"{label}: {field} must be a typed not_applicable result"
            )
            return False
        return True
    if status != "reported":
        violations.append(f"{label}: {field} must have status 'reported'")
        return False

    if field == "point_estimate":
        value = result.get("value")
        if (
            set(result) != {"status", "value"}
            or value is None
            or value == ""
            or value == []
            or value == {}
            or not _numeric_payload(value)
        ):
            violations.append(
                f"{label}: point_estimate must contain a nonempty finite value"
            )
            return False
        return True
    if field == "interval":
        expected = {"status", "level", "method", "bounds", "interpretation"}
        level = result.get("level")
        bounds = result.get("bounds")
        valid = True
        if set(result) != expected:
            violations.append(
                f"{label}: interval must contain exactly {sorted(expected)}"
            )
            valid = False
        if (
            not _finite_number(level)
            or not 0 < level <= 1
        ):
            violations.append(f"{label}: interval level must satisfy 0 < level <= 1")
            valid = False
        if not _nonempty_string(result.get("method")):
            violations.append(f"{label}: interval method must be nonempty")
            valid = False
        if not _nonempty_string(result.get("interpretation")):
            violations.append(f"{label}: interval interpretation must be nonempty")
            valid = False
        if not _valid_interval_bounds(bounds):
            violations.append(
                f"{label}: interval bounds must contain ordered finite bounds"
            )
            valid = False
        return valid

    counts = result.get("counts")
    if set(result) != {"status", "counts"}:
        violations.append(
            f"{label}: denominator must contain only status and counts"
        )
        return False
    if (
        not isinstance(counts, dict)
        or not counts
        or not all(_nonempty_string(key) for key in counts)
        or not all(
            isinstance(count, int) and not isinstance(count, bool) and count >= 0
            for count in counts.values()
        )
    ):
        violations.append(
            f"{label}: denominator counts must be nonnegative integer values"
        )
        return False
    return True


def _decode_row_artifacts(
    row: dict[str, str],
    label: str,
    root: Path,
    paper: str,
    claim_id: str,
    catalog: dict[str, dict[str, Any]],
    violations: list[str],
) -> tuple[list[dict[str, str]], bool]:
    start = len(violations)
    artifacts: list[dict[str, str]] = []
    seen_paths: set[str] = set()
    for kind in ("raw", "derived"):
        paths = _decode_json_cell(
            row.get(f"{kind}_artifact_paths"),
            list,
            f"{kind}_artifact_paths",
            label,
            violations,
        )
        hashes = _decode_json_cell(
            row.get(f"{kind}_artifact_sha256"),
            list,
            f"{kind}_artifact_sha256",
            label,
            violations,
        )
        if paths is None or hashes is None:
            continue
        if len(paths) != len(hashes):
            violations.append(
                f"{label}: {kind} artifact paths and hashes must have equal lengths"
            )
            continue
        for index, (path_value, hash_value) in enumerate(
            zip(paths, hashes, strict=True)
        ):
            artifact_label = f"{label} {kind} artifact {index}"
            relative = _safe_relative_path(path_value)
            if relative is None:
                violations.append(
                    f"{artifact_label}: path must be a safe relative POSIX path"
                )
                continue
            normalized_path = relative.as_posix()
            if normalized_path in seen_paths:
                violations.append(f"{artifact_label}: duplicate artifact path")
                continue
            seen_paths.add(normalized_path)
            for rule_name, pattern in PROHIBITED[paper]["artifact_paths"].items():
                if pattern.search(normalized_path) is not None:
                    violations.append(
                        f"{artifact_label}: prohibited {rule_name} evidence"
                    )
            if not _valid_sha256(hash_value):
                violations.append(
                    f"{artifact_label}: sha256 must be 64 hexadecimal characters"
                )
                continue
            file_path = _contained_file(root, relative)
            if file_path is None:
                violations.append(
                    f"{artifact_label}: file does not exist inside ledger root"
                )
                continue
            actual_hash = _sha256(file_path)
            if actual_hash != hash_value.lower():
                violations.append(
                    f"{artifact_label}: file sha256 does not match result ledger"
                )
                continue
            _known_hash_allowed(
                actual_hash,
                paper,
                claim_id,
                catalog,
                artifact_label,
                violations,
            )
            artifacts.append(
                {"path": normalized_path, "sha256": actual_hash, "kind": kind}
            )
    return artifacts, len(violations) == start


def _has_cycle(graph: dict[str, set[str]]) -> bool:
    states: dict[str, int] = {}
    for start in graph:
        if states.get(start) == 2:
            continue
        states[start] = 1
        stack = [(start, iter(graph.get(start, set())))]
        while stack:
            node, parents = stack[-1]
            try:
                parent = next(parents)
            except StopIteration:
                states[node] = 2
                stack.pop()
                continue
            state = states.get(parent, 0)
            if state == 1:
                return True
            if state == 2:
                continue
            states[parent] = 1
            stack.append((parent, iter(graph.get(parent, set()))))
    return False


def _validate_lineage(
    data: Any,
    lineage_path: str,
    paper: str,
    claim_id: str,
    row: dict[str, str],
    row_artifacts: list[dict[str, str]],
    claim_contract: dict[str, Any],
    roles: dict[str, Any],
    registry_hash: str,
    contract_hash: str,
    roles_hash: str,
    catalog: dict[str, dict[str, Any]],
    root: Path,
    violations: list[str],
) -> bool:
    start = len(violations)
    label = f"lineage manifest for {claim_id}"
    if not isinstance(data, dict):
        violations.append(f"{label}: top level must be a JSON object")
        return False
    expected_scalars = {
        "schema_version": "1.0",
        "paper_id": paper,
        "claim_id": claim_id,
        "source_git_commit": row.get("source_git_commit"),
        "claim_registry_sha256": registry_hash,
        "submission_contract_sha256": contract_hash,
        "cohort_manifest_path": row.get("cohort_manifest_path"),
        "cohort_manifest_sha256": row.get("cohort_manifest_sha256"),
        "experiment_manifest_path": row.get("experiment_manifest_path"),
        "experiment_manifest_sha256": row.get("experiment_manifest_sha256"),
        "status": "locked",
    }
    for field, expected in expected_scalars.items():
        if data.get(field) != expected:
            violations.append(f"{label}: {field} does not match the ledger contract")

    owner_id = data.get("experiment_owner_id")
    if owner_id not in roles.get("experiment_owner_ids", []):
        violations.append(f"{label}: experiment_owner_id is not assigned")

    lineage_relative = _safe_relative_path(lineage_path)
    lineage_name = lineage_relative.as_posix() if lineage_relative else lineage_path

    parent_locks = data.get("parent_locks")
    if not isinstance(parent_locks, list) or not parent_locks:
        violations.append(f"{label}: parent_locks must be a nonempty JSON array")
        parent_locks = []
    lock_references: set[tuple[str, str]] = {
        (
            str(row.get("cohort_manifest_path", "")),
            str(row.get("cohort_manifest_sha256", "")),
        ),
        (
            str(row.get("experiment_manifest_path", "")),
            str(row.get("experiment_manifest_sha256", "")),
        ),
    }
    for index, lock in enumerate(parent_locks):
        lock_label = f"{label} parent lock {index}"
        if not isinstance(lock, dict) or set(lock) != {"path", "sha256"}:
            violations.append(
                f"{lock_label}: must contain exactly path and sha256"
            )
            continue
        relative = _safe_relative_path(lock.get("path"))
        lock_hash = lock.get("sha256")
        if relative is None:
            violations.append(
                f"{lock_label}: path must be a safe relative POSIX path"
            )
            continue
        if relative.as_posix() == lineage_name:
            violations.append(f"{lock_label}: lineage cannot reference itself")
        if not _valid_sha256(lock_hash):
            violations.append(
                f"{lock_label}: sha256 must be 64 hexadecimal characters"
            )
            continue
        lock_file = _contained_file(root, relative)
        if lock_file is None:
            violations.append(f"{lock_label}: file does not exist")
            continue
        actual_hash = _sha256(lock_file)
        if actual_hash != lock_hash.lower():
            violations.append(f"{lock_label}: file sha256 does not match")
            continue
        _known_hash_allowed(
            actual_hash,
            paper,
            claim_id,
            catalog,
            lock_label,
            violations,
        )
        lock_references.add((relative.as_posix(), actual_hash))
        lock_data = _load_json(lock_file, lock_label, violations)
        lock_references.update(
            _validate_parent_lock(
                lock_data,
                lock_label,
                paper,
                claim_id,
                row,
                claim_contract,
                roles,
                contract_hash,
                roles_hash,
                catalog,
                root,
                violations,
            )
        )

    entries = data.get("artifacts")
    if not isinstance(entries, list):
        violations.append(f"{label}: artifacts must be a JSON array")
        return False

    normalized: list[dict[str, str]] = []
    artifact_hashes: dict[str, str] = {}
    graph: dict[str, set[str]] = {}
    parent_references: list[tuple[str, str, str]] = []
    observed_studies: set[str] = set()
    allowed_studies = set(claim_contract.get("source_study_ids", []))
    for index, entry in enumerate(entries):
        artifact_label = f"{label} artifact {index}"
        if not isinstance(entry, dict):
            violations.append(f"{artifact_label}: must be a JSON object")
            continue
        expected_artifact_fields = {
            "path",
            "sha256",
            "kind",
            "source_study_id",
            "derivation",
            "parents",
        }
        if set(entry) != expected_artifact_fields:
            violations.append(
                f"{artifact_label}: must contain exactly "
                f"{sorted(expected_artifact_fields)}"
            )
        relative = _safe_relative_path(entry.get("path"))
        artifact_hash = entry.get("sha256")
        kind = entry.get("kind")
        study = entry.get("source_study_id")
        derivation = entry.get("derivation")
        if relative is None:
            violations.append(
                f"{artifact_label}: path must be a safe relative POSIX path"
            )
            continue
        path_value = relative.as_posix()
        if path_value == lineage_name:
            violations.append(f"{artifact_label}: lineage cannot contain itself")
        if path_value in artifact_hashes:
            violations.append(f"{artifact_label}: duplicate artifact path")
            continue
        if not _valid_sha256(artifact_hash):
            violations.append(
                f"{artifact_label}: sha256 must be 64 hexadecimal characters"
            )
            continue
        if kind not in {"raw", "derived"}:
            violations.append(f"{artifact_label}: kind must be raw or derived")
        if not _nonempty_string(derivation):
            violations.append(f"{artifact_label}: derivation must be nonempty")
        if study not in allowed_studies:
            violations.append(f"{artifact_label}: source_study_id is not allowed")
        else:
            observed_studies.add(study)

        artifact_file = _contained_file(root, relative)
        if artifact_file is None:
            violations.append(f"{artifact_label}: file does not exist")
        else:
            actual_hash = _sha256(artifact_file)
            if actual_hash != artifact_hash.lower():
                violations.append(f"{artifact_label}: file sha256 does not match")
            else:
                _known_hash_allowed(
                    actual_hash,
                    paper,
                    claim_id,
                    catalog,
                    artifact_label,
                    violations,
                    declared_study=study if isinstance(study, str) else None,
                )

        parents = entry.get("parents")
        if not isinstance(parents, list) or not parents:
            violations.append(
                f"{artifact_label}: parents must be a nonempty JSON array"
            )
            parents = []
        graph[path_value] = set()
        for parent_index, parent in enumerate(parents):
            parent_label = f"{artifact_label} parent {parent_index}"
            if not isinstance(parent, dict) or set(parent) != {"path", "sha256"}:
                violations.append(
                    f"{parent_label}: must contain exactly path and sha256"
                )
                continue
            parent_relative = _safe_relative_path(parent.get("path"))
            parent_hash = parent.get("sha256")
            if parent_relative is None:
                violations.append(
                    f"{parent_label}: path must be a safe relative POSIX path"
                )
                continue
            parent_path = parent_relative.as_posix()
            if parent_path in {path_value, lineage_name}:
                violations.append(f"{parent_label}: self-reference is prohibited")
            if not _valid_sha256(parent_hash):
                violations.append(
                    f"{parent_label}: sha256 must be 64 hexadecimal characters"
                )
                continue
            parent_file = _contained_file(root, parent_relative)
            if parent_file is None:
                violations.append(f"{parent_label}: file does not exist")
                continue
            actual_parent_hash = _sha256(parent_file)
            if actual_parent_hash != parent_hash.lower():
                violations.append(f"{parent_label}: file sha256 does not match")
                continue
            _known_hash_allowed(
                actual_parent_hash,
                paper,
                claim_id,
                catalog,
                parent_label,
                violations,
            )
            graph[path_value].add(parent_path)
            parent_references.append(
                (parent_label, parent_path, actual_parent_hash)
            )

        artifact_hashes[path_value] = artifact_hash.lower()
        normalized.append(
            {
                "path": path_value,
                "sha256": artifact_hash.lower(),
                "kind": str(kind),
            }
        )

    for child, parents in graph.items():
        for parent in parents:
            if parent in artifact_hashes:
                parent_entry_hash = next(
                    (
                        item["sha256"]
                        for item in normalized
                        if item["path"] == parent
                    ),
                    None,
                )
                parent_file = _contained_file(root, PurePosixPath(parent))
                if (
                    parent_entry_hash is None
                    or parent_file is None
                    or _sha256(parent_file) != parent_entry_hash
                ):
                    violations.append(
                        f"{label}: lineage parent disagrees with artifact node"
                    )
    for parent_label, parent_path, parent_hash in parent_references:
        if parent_path in artifact_hashes:
            if artifact_hashes[parent_path] != parent_hash:
                violations.append(
                    f"{parent_label}: hash disagrees with lineage artifact node"
                )
            continue
        if (parent_path, parent_hash) in lock_references:
            continue
        if parent_hash in catalog:
            continue
        violations.append(
            f"{parent_label}: unknown parent is absent from accepted parent locks"
        )
    if _has_cycle(
        {
            node: {parent for parent in parents if parent in graph}
            for node, parents in graph.items()
        }
    ):
        violations.append(f"{label}: artifact lineage contains a cycle")

    if normalized != row_artifacts:
        violations.append(
            f"{label}: artifacts do not exactly match the ledger artifact arrays"
        )
    if row.get("claim_status") == "confirmed" and observed_studies != allowed_studies:
        violations.append(
            f"{label}: confirmed lineage does not cover every contracted study"
        )
    return len(violations) == start


def _row_payload_sha256(row: dict[str, str]) -> str:
    payload = {
        field: row.get(field, "")
        for field in sorted(RESULT_LEDGER_COLUMNS - {"review_status"})
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _review_artifacts(row_artifacts: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": item["path"], "sha256": item["sha256"], "kind": item["kind"]}
        for item in row_artifacts
    ]


def _validate_review(
    value: Any,
    label: str,
    row: dict[str, str],
    row_artifacts: list[dict[str, str]],
    paper: str,
    claim_id: str,
    roles: dict[str, Any],
    registry_hash: str,
    contract_hash: str,
    roles_hash: str,
    root: Path,
    confirmed: bool,
    violations: list[str],
) -> bool:
    try:
        pointer = json.loads(value) if isinstance(value, str) else None
    except (json.JSONDecodeError, ValueError, RecursionError) as error:
        detail = getattr(error, "msg", str(error))
        violations.append(f"{label}: review_status contains invalid JSON: {detail}")
        return False
    if isinstance(pointer, dict) and set(pointer) == {"status", "reason"}:
        if confirmed:
            violations.append(f"{label}: confirmed row requires a review decision")
            return False
        if pointer.get("status") != "not_required" or not _nonempty_string(
            pointer.get("reason")
        ):
            violations.append(
                f"{label}: non-review status requires not_required and a reason"
            )
            return False
        return True
    if not isinstance(pointer, dict) or set(pointer) != {
        "decision_path",
        "decision_sha256",
    }:
        violations.append(
            f"{label}: review_status must contain only decision_path and "
            "decision_sha256"
        )
        return False

    relative = _safe_relative_path(pointer.get("decision_path"))
    decision_hash = pointer.get("decision_sha256")
    if relative is None:
        violations.append(
            f"{label}: review decision path must be a safe relative POSIX path"
        )
        return False
    if not _valid_sha256(decision_hash):
        violations.append(
            f"{label}: review decision sha256 must be 64 hexadecimal characters"
        )
        return False
    decision_path = _contained_file(root, relative)
    if decision_path is None:
        violations.append(f"{label}: review decision file does not exist")
        return False
    if _sha256(decision_path) != decision_hash.lower():
        violations.append(f"{label}: review decision sha256 does not match")
        return False
    decision = _load_json(decision_path, f"{label} review decision", violations)
    if not isinstance(decision, dict):
        if decision is not None:
            violations.append(f"{label}: review decision must be a JSON object")
        return False

    start = len(violations)
    expected = {
        "schema_version": "1.0",
        "paper_id": paper,
        "claim_id": claim_id,
        "source_git_commit": row.get("source_git_commit"),
        "claim_registry_sha256": registry_hash,
        "submission_contract_sha256": contract_hash,
        "role_assignments_sha256": roles_hash,
        "row_payload_sha256": _row_payload_sha256(row),
        "cohort_manifest_path": row.get("cohort_manifest_path"),
        "cohort_manifest_sha256": row.get("cohort_manifest_sha256"),
        "experiment_manifest_path": row.get("experiment_manifest_path"),
        "experiment_manifest_sha256": row.get("experiment_manifest_sha256"),
        "lineage_manifest_path": row.get("lineage_manifest_path"),
        "lineage_manifest_sha256": row.get("lineage_manifest_sha256"),
        "artifacts": _review_artifacts(row_artifacts),
    }
    for field, expected_value in expected.items():
        if decision.get(field) != expected_value:
            violations.append(
                f"{label}: review decision {field} does not match the reviewed row"
            )

    reviewer_role = decision.get("reviewer_role")
    reviewer_id = decision.get("reviewer_id")
    role_field = REVIEW_ROLES.get(reviewer_role)
    if role_field is None:
        violations.append(f"{label}: review decision reviewer_role is invalid")
    elif reviewer_id != roles.get(role_field):
        violations.append(
            f"{label}: review decision reviewer_id does not match assigned role"
        )

    findings = decision.get("findings")
    unresolved_blocker = False
    if decision.get("decision") not in {"accepted", "hold", "rejected"}:
        violations.append(f"{label}: review decision value is invalid")
    if not isinstance(findings, list):
        violations.append(f"{label}: review decision findings must be a JSON array")
    else:
        for index, finding in enumerate(findings):
            finding_label = f"{label} review finding {index}"
            if not isinstance(finding, dict):
                violations.append(f"{finding_label}: must be a JSON object")
                continue
            severity = finding.get("severity")
            resolved = finding.get("resolved")
            if severity not in {"Critical", "Major", "Minor"}:
                violations.append(f"{finding_label}: severity is invalid")
            if not isinstance(resolved, bool):
                violations.append(
                    f"{finding_label}: resolved must be a boolean"
                )
                is_resolved = False
            else:
                is_resolved = resolved
            if severity in {"Critical", "Major"} and not is_resolved:
                unresolved_blocker = True

    if confirmed:
        if decision.get("decision") != "accepted":
            violations.append(
                f"{label}: confirmed review decision must be 'accepted'"
            )
        if unresolved_blocker:
            violations.append(
                f"{label}: confirmed review has unresolved Critical or Major findings"
            )
    return len(violations) == start


def _validate_claim_set(
    rows: list[dict[str, str]],
    required_claim_ids: set[str],
    violations: list[str],
) -> bool:
    start = len(violations)
    counts: dict[str, int] = {}
    for row in rows:
        claim_id = row.get("claim_id", "")
        counts[claim_id] = counts.get(claim_id, 0) + 1
    for claim_id in sorted(required_claim_ids):
        count = counts.get(claim_id, 0)
        if count == 0:
            violations.append(f"result ledger: missing controlling claim {claim_id!r}")
        elif count > 1:
            violations.append(
                f"result ledger: duplicate controlling claim {claim_id!r}"
            )
    for claim_id in sorted(set(counts) - required_claim_ids):
        violations.append(f"result ledger: extra controlling claim {claim_id!r}")
    return len(violations) == start


def _validate_ledger_rows(
    paper: str,
    rows: list[dict[str, str]],
    root: Path,
    registry_claims: dict[str, dict[str, str]],
    claim_contracts: dict[str, dict[str, Any]],
    roles: dict[str, Any],
    registry_hash: str,
    contract_hash: str,
    roles_hash: str,
    catalog: dict[str, dict[str, Any]],
    base_valid: bool,
    violations: list[str],
) -> dict[tuple[str, str], str]:
    claim_set_valid = _validate_claim_set(rows, set(claim_contracts), violations)
    authorized: dict[tuple[str, str], str] = {}
    for index, row in enumerate(rows, start=2):
        label = f"result ledger row {index}"
        row_start = len(violations)
        claim_id = row.get("claim_id", "")
        claim_contract = claim_contracts.get(claim_id)
        registry_claim = registry_claims.get(claim_id)
        if claim_contract is None:
            continue
        if row.get("paper_id") != paper:
            violations.append(f"{label}: paper_id must be {paper!r}")
        if registry_claim is None:
            violations.append(f"{label}: claim is absent from the claim registry")
        elif row.get("claim_text_sha256") != registry_claim["claim_text_sha256"]:
            violations.append(
                f"{label}: claim_text_sha256 does not match the claim registry"
            )

        studies = _decode_json_cell(
            row.get("source_study_ids"),
            list,
            "source_study_ids",
            label,
            violations,
        )
        if studies != claim_contract.get("source_study_ids"):
            violations.append(
                f"{label}: source_study_ids do not match the submission contract"
            )
        for field in CONTRACT_FIELDS:
            if row.get(field) != claim_contract.get(field):
                violations.append(
                    f"{label}: {field} does not match the submission contract"
                )

        status = row.get("claim_status")
        gate = row.get("gate_result")
        if status not in STATUS_GATES:
            violations.append(f"{label}: claim_status is invalid")
        elif gate not in STATUS_GATES[status]:
            violations.append(
                f"{label}: gate_result {gate!r} is invalid for status {status!r}"
            )
        confirmed = status == "confirmed"
        if confirmed and row.get("status_reason", ""):
            violations.append(f"{label}: confirmed row status_reason must be empty")
        elif not confirmed and not _nonempty_string(row.get("status_reason")):
            violations.append(
                f"{label}: nonconfirmed row requires a nonempty status_reason"
            )

        source_commit = row.get("source_git_commit")
        if not _valid_commit(source_commit):
            violations.append(
                f"{label}: source_git_commit must be a full commit hash"
            )
        elif source_commit != roles.get("source_git_commit"):
            violations.append(
                f"{label}: source_git_commit does not match role assignments"
            )

        requirements = claim_contract.get("result_requirements", {})
        for field in sorted(RESULT_FIELDS):
            _validate_typed_result(
                row.get(field),
                field,
                requirements.get(field, ""),
                confirmed,
                label,
                violations,
            )

        manifests_required = confirmed or gate != "not_run"
        cohort_path, _, cohort_file, cohort_valid = _validate_bound_file_pair(
            row,
            "cohort_manifest",
            label,
            root,
            manifests_required,
            violations,
        )
        experiment_path, _, experiment_file, experiment_valid = (
            _validate_bound_file_pair(
            row,
            "experiment_manifest",
            label,
            root,
            manifests_required,
            violations,
            )
        )
        lineage_path, _, lineage_file, lineage_file_valid = (
            _validate_bound_file_pair(
                row,
                "lineage_manifest",
                label,
                root,
                manifests_required,
                violations,
            )
        )

        row_artifacts, artifacts_valid = _decode_row_artifacts(
            row,
            label,
            root,
            paper,
            claim_id,
            catalog,
            violations,
        )
        if confirmed and not row_artifacts:
            violations.append(f"{label}: confirmed row requires at least one artifact")
        if row_artifacts and not lineage_path:
            violations.append(
                f"{label}: supplied artifacts require a lineage manifest"
            )
        if row_artifacts and (not cohort_path or not experiment_path):
            violations.append(
                f"{label}: supplied artifacts require cohort and experiment manifests"
            )

        cohort_content_valid = cohort_file is None and not cohort_path
        if cohort_file is not None:
            cohort_data = _load_json(
                cohort_file,
                f"{label} cohort manifest",
                violations,
            )
            cohort_content_valid = _validate_manifest_content(
                cohort_data,
                "cohort",
                paper,
                claim_id,
                row,
                claim_contract,
                roles,
                contract_hash,
                roles_hash,
                violations,
            )
        experiment_content_valid = experiment_file is None and not experiment_path
        if experiment_file is not None:
            experiment_data = _load_json(
                experiment_file,
                f"{label} experiment manifest",
                violations,
            )
            experiment_content_valid = _validate_manifest_content(
                experiment_data,
                "experiment",
                paper,
                claim_id,
                row,
                claim_contract,
                roles,
                contract_hash,
                roles_hash,
                violations,
            )

        lineage_valid = not lineage_path and not row_artifacts
        if lineage_file is not None:
            lineage_data = _load_json(lineage_file, f"{label} lineage", violations)
            lineage_valid = _validate_lineage(
                lineage_data,
                lineage_path,
                paper,
                claim_id,
                row,
                row_artifacts,
                claim_contract,
                roles,
                registry_hash,
                contract_hash,
                roles_hash,
                catalog,
                root,
                violations,
            )

        review_valid = _validate_review(
            row.get("review_status"),
            label,
            row,
            row_artifacts,
            paper,
            claim_id,
            roles,
            registry_hash,
            contract_hash,
            roles_hash,
            root,
            confirmed,
            violations,
        )

        row_valid = (
            len(violations) == row_start
            and base_valid
            and claim_set_valid
            and cohort_valid
            and cohort_content_valid
            and experiment_valid
            and experiment_content_valid
            and lineage_file_valid
            and lineage_valid
            and artifacts_valid
            and review_valid
        )
        if confirmed and row_valid:
            for artifact in row_artifacts:
                key = (claim_id, artifact["path"])
                if key in authorized:
                    violations.append(
                        f"{label}: duplicate authorized artifact mapping {key!r}"
                    )
                    continue
                authorized[key] = artifact["sha256"]
    return authorized


def _validate_package_entries(
    paper: str,
    root: Path,
    entries: Any,
    evidence_paths: set[str],
    authorized: dict[tuple[str, str], str],
    violations: list[str],
) -> None:
    if not isinstance(entries, list):
        violations.append("ownership allowlist: artifacts must be a JSON array")
        entries = []
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
        unresolved_package_file = root.joinpath(*package_relative.parts)
        if _has_symlink_component(unresolved_package_file):
            violations.append(
                f"{label}: package path contains a prohibited symlink"
            )
            continue
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
        actual_hash = _sha256(package_file)
        if actual_hash != package_hash.lower():
            violations.append(f"{label}: package file sha256 does not match")

        claim_id = entry.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id.startswith(
            CLAIM_PREFIX[paper]
        ):
            violations.append(
                f"{label}: claim_id must start with {CLAIM_PREFIX[paper]!r}"
            )
            continue
        ledger_relative = _safe_relative_path(entry.get("ledger_artifact_path"))
        if ledger_relative is None:
            violations.append(
                f"{label}: ledger_artifact_path must be a safe relative POSIX path"
            )
            continue
        ledger_hash = authorized.get((claim_id, ledger_relative.as_posix()))
        if ledger_hash is None:
            violations.append(
                f"{label}: claim and artifact are not authorized by a confirmed row"
            )
        elif ledger_hash != package_hash.lower():
            violations.append(
                f"{label}: package sha256 does not match the authorized artifact"
            )

    for path in sorted(evidence_paths - allowlisted_paths):
        violations.append(f"{path}: evidence file is not ownership-allowlisted")


def _validate_ownership_allowlist(
    paper: str,
    root: Path,
    evidence_paths: set[str],
    allowlist_path: Path | None,
    ledger_path: Path | None,
    ledger_root: Path,
    claim_registry_path: Path | None,
    violations: list[str],
) -> None:
    if allowlist_path is None:
        for path in sorted(evidence_paths):
            violations.append(f"{path}: evidence file is not ownership-allowlisted")
        return
    allowlist = _load_json(allowlist_path, "ownership allowlist", violations)
    if not isinstance(allowlist, dict):
        if allowlist is not None:
            violations.append("ownership allowlist: top level must be a JSON object")
        return
    validation_start = len(violations)
    if allowlist.get("paper_id") != paper:
        violations.append(f"ownership allowlist: paper_id must be {paper!r}")

    if claim_registry_path is None or not claim_registry_path.is_file():
        violations.append("ownership allowlist: a claim registry is required")
        registry_hash = ""
        registry_claims: dict[str, dict[str, str]] = {}
    else:
        registry_hash = _sha256(claim_registry_path)
        expected_registry_hash = allowlist.get("claim_registry_sha256")
        if not _valid_sha256(expected_registry_hash):
            violations.append(
                "ownership allowlist: claim_registry_sha256 must be "
                "64 hexadecimal characters"
            )
        elif registry_hash != expected_registry_hash.lower():
            violations.append(
                "ownership allowlist: claim registry sha256 does not match"
            )
        registry_claims = _load_claim_registry(claim_registry_path, violations)

    if allowlist.get("submission_contract_path") != CANONICAL_SUBMISSION_CONTRACT:
        violations.append(
            "ownership allowlist: submission_contract_path is not canonical"
        )
    if (
        allowlist.get("submission_contract_sha256")
        != EXPECTED_SUBMISSION_CONTRACT_SHA256
    ):
        violations.append(
            "ownership allowlist: submission_contract_sha256 is not trusted"
        )
    (
        contract_path,
        contract_hash,
        _,
        contract_data,
        contract_file_valid,
    ) = _load_bound_repository_json(
        ledger_root,
        CANONICAL_SUBMISSION_CONTRACT,
        EXPECTED_SUBMISSION_CONTRACT_SHA256,
        "submission contract",
        violations,
    )
    claim_contracts, ownership_path, ownership_hash, contract_valid = (
        _validate_submission_contract(
            contract_data,
            paper,
            registry_hash,
            registry_claims,
            violations,
        )
    )

    (
        _,
        roles_hash,
        _,
        roles_data,
        roles_file_valid,
    ) = _load_bound_repository_json(
        ledger_root,
        allowlist.get("role_assignments_path"),
        allowlist.get("role_assignments_sha256"),
        "role assignments",
        violations,
    )
    roles, roles_valid = _validate_role_assignments(
        roles_data,
        paper,
        violations,
    )

    expected_ownership_hash = allowlist.get("artifact_ownership_sha256")
    if not _valid_sha256(expected_ownership_hash):
        violations.append(
            "ownership allowlist: artifact_ownership_sha256 must be "
            "64 hexadecimal characters"
        )
    elif expected_ownership_hash.lower() != EXPECTED_ARTIFACT_OWNERSHIP_SHA256:
        violations.append(
            "ownership allowlist: artifact_ownership_sha256 is not trusted"
        )
    (
        loaded_ownership_path,
        loaded_ownership_hash,
        _,
        ownership_data,
        ownership_file_valid,
    ) = _load_bound_repository_json(
        ledger_root,
        CANONICAL_ARTIFACT_OWNERSHIP,
        EXPECTED_ARTIFACT_OWNERSHIP_SHA256,
        "artifact ownership",
        violations,
    )
    if loaded_ownership_path != CANONICAL_ARTIFACT_OWNERSHIP:
        violations.append("artifact ownership: path does not match contract")
    if loaded_ownership_hash != EXPECTED_ARTIFACT_OWNERSHIP_SHA256:
        violations.append("artifact ownership: hash does not match contract")
    catalog, ownership_valid = _validate_artifact_ownership(
        ownership_data,
        ledger_root,
        violations,
    )

    rows: list[dict[str, str]] | None = None
    ledger_hash_valid = True
    if ledger_path is None:
        violations.append("ownership allowlist: a result ledger is required")
        ledger_hash_valid = False
    else:
        expected_ledger_hash = allowlist.get("result_ledger_sha256")
        if not _valid_sha256(expected_ledger_hash):
            violations.append(
                "ownership allowlist: result_ledger_sha256 must be "
                "64 hexadecimal characters"
            )
            ledger_hash_valid = False
        elif not ledger_path.is_file():
            violations.append(f"result ledger: file does not exist: {ledger_path}")
            ledger_hash_valid = False
        elif _sha256(ledger_path) != expected_ledger_hash.lower():
            violations.append(
                "ownership allowlist: result ledger sha256 does not match"
            )
            ledger_hash_valid = False
        rows = _load_csv(ledger_path, "result ledger", violations)

    pins_valid = (
        len(violations) == validation_start
        and contract_file_valid
        and contract_valid
        and roles_file_valid
        and roles_valid
        and ownership_file_valid
        and ownership_valid
        and ledger_hash_valid
        and bool(contract_path)
    )
    authorized: dict[tuple[str, str], str] = {}
    if rows is not None:
        authorized = _validate_ledger_rows(
            paper,
            rows,
            ledger_root,
            registry_claims,
            claim_contracts,
            roles,
            registry_hash,
            contract_hash,
            roles_hash,
            catalog,
            pins_valid,
            violations,
        )
    _validate_package_entries(
        paper,
        root,
        allowlist.get("artifacts"),
        evidence_paths,
        authorized,
        violations,
    )


def _extract_pdf_text(path: Path) -> str:
    executable = shutil.which("pdftotext")
    if executable is None:
        raise RuntimeError("pdftotext is not installed")
    try:
        completed = subprocess.run(
            [executable, "-enc", "UTF-8", str(path), "-"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("pdftotext timed out") from error
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(detail or f"pdftotext exited {completed.returncode}")
    text = completed.stdout.decode("utf-8")
    if not text.strip():
        raise RuntimeError("pdftotext returned no text")
    return text


def _scan_text(
    text: str,
    relative: Path,
    rules: dict[str, Any],
    violations: list[str],
) -> None:
    for name, pattern in rules["text"].items():
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            violations.append(f"{relative}:{line}: prohibited {name} evidence")


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
    resolved_root = root.resolve()
    resolved_metadata = {path.resolve() for path in metadata_paths}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            continue
        if not path.is_file():
            continue
        try:
            resolved = path.resolve()
        except (OSError, RuntimeError):
            continue
        if resolved in resolved_metadata:
            continue
        if not resolved.is_relative_to(resolved_root):
            continue
        if path.name == MANUSCRIPT_PDF and path.parent == root:
            continue
        if _has_figure_signature(path):
            evidence.add(path.relative_to(root).as_posix())
            continue
        if path.suffix.lower() in TEXT_SOURCE_SUFFIXES:
            continue
        evidence.add(path.relative_to(root).as_posix())
    return evidence


def _known_hash_evidence_paths(
    root: Path,
    metadata_paths: set[Path],
    catalog: dict[str, dict[str, Any]],
) -> set[str]:
    evidence: set[str] = set()
    resolved_root = root.resolve()
    resolved_metadata = {path.resolve() for path in metadata_paths}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            continue
        if not path.is_file():
            continue
        try:
            resolved = path.resolve()
        except (OSError, RuntimeError):
            continue
        if resolved in resolved_metadata:
            continue
        if not resolved.is_relative_to(resolved_root):
            continue
        if _sha256(path) in catalog:
            evidence.add(path.relative_to(root).as_posix())
    return evidence


def _scan_package_sources(
    paper: str,
    root: Path,
    violations: list[str],
) -> None:
    rules = PROHIBITED[paper]
    resolved_root = root.resolve()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_symlink():
            violations.append(f"{relative}: package symlinks are prohibited")
            continue
        if not path.is_file():
            continue
        try:
            resolved = path.resolve()
        except (OSError, RuntimeError) as error:
            violations.append(f"{relative}: cannot resolve package file: {error}")
            continue
        if not resolved.is_relative_to(resolved_root):
            violations.append(f"{relative}: file resolves outside package root")
            continue
        if path.name in rules["filenames"]:
            violations.append(f"{relative}: prohibited historical figure")
        if path.suffix.lower() == ".pdf" and path.parent == root:
            try:
                pdf_text = _extract_pdf_text(path)
            except (OSError, UnicodeDecodeError, RuntimeError) as error:
                violations.append(
                    f"{relative}: cannot extract compiled PDF text: {error}"
                )
            else:
                _scan_text(pdf_text, relative, rules, violations)
            continue
        if path.suffix.lower() not in TEXT_SOURCE_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            violations.append(f"{relative}: cannot scan UTF-8 text source: {error}")
            continue
        _scan_text(text, relative, rules, violations)


def find_violations(
    paper: str,
    root: Path,
    *,
    allowlist: Path | None = None,
    ledger: Path | None = None,
    ledger_root: Path | None = None,
    claim_registry: Path | None = None,
) -> list[str]:
    if paper not in PROHIBITED:
        raise ValueError(f"unknown paper: {paper}")
    root = Path(root)
    if _has_symlink_component(root):
        return ["package root: path contains a prohibited symlink"]
    if not root.is_dir():
        raise ValueError(f"package root is not a directory: {root}")

    violations: list[str] = []
    default_allowlist = root / DEFAULT_ALLOWLIST
    if allowlist is not None:
        allowlist_path = Path(allowlist)
        if _has_symlink_component(allowlist_path):
            violations.append(
                "ownership allowlist: path contains a prohibited symlink"
            )
            allowlist_path = None
    elif _has_symlink_component(default_allowlist):
        violations.append(
            "ownership allowlist: path contains a prohibited symlink"
        )
        allowlist_path = None
    elif default_allowlist.is_file():
        allowlist_path = default_allowlist
    else:
        allowlist_path = None

    ledger_path = Path(ledger) if ledger is not None else None
    if ledger_path is not None and _has_symlink_component(ledger_path):
        violations.append("result ledger: path contains a prohibited symlink")
        ledger_path = None
    ledger_root_path = Path(ledger_root) if ledger_root is not None else Path.cwd()
    if _has_symlink_component(ledger_root_path):
        violations.append(
            "ledger root: path contains a prohibited symlink"
        )
        _scan_package_sources(paper, root, violations)
        return violations
    claim_registry_path = (
        Path(claim_registry) if claim_registry is not None else None
    )
    if claim_registry_path is None and allowlist_path is not None:
        claim_registry_path = ledger_root_path / DEFAULT_CLAIM_REGISTRY
    if (
        claim_registry_path is not None
        and _has_symlink_component(claim_registry_path)
    ):
        violations.append("claim registry: path contains a prohibited symlink")
        claim_registry_path = None

    metadata_paths = {
        path
        for path in (allowlist_path, ledger_path)
        if path is not None and path.is_file()
    }
    trusted_catalog = _load_trusted_artifact_catalog(
        ledger_root_path,
        violations,
    )
    evidence_paths = _package_evidence_paths(root, metadata_paths)
    evidence_paths.update(
        _known_hash_evidence_paths(root, metadata_paths, trusted_catalog)
    )
    if evidence_paths or allowlist_path is not None or ledger_path is not None:
        _validate_ownership_allowlist(
            paper,
            root,
            evidence_paths,
            allowlist_path,
            ledger_path,
            ledger_root_path,
            claim_registry_path,
            violations,
        )
    _scan_package_sources(paper, root, violations)
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
        help="root for repository-relative contract files (default: current directory)",
    )
    parser.add_argument(
        "--claim-registry",
        type=Path,
        help=(
            "claim registry Markdown "
            f"(default: LEDGER_ROOT/{DEFAULT_CLAIM_REGISTRY})"
        ),
    )
    args = parser.parse_args()

    violations = find_violations(
        args.paper,
        args.root,
        allowlist=args.allowlist,
        ledger=args.ledger,
        ledger_root=args.ledger_root,
        claim_registry=args.claim_registry,
    )
    for violation in violations:
        print(violation)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
