import csv
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

import pytest

from plm_steering import submission_ownership
from plm_steering.submission_ownership import find_violations


LEDGER_COLUMNS = [
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
]

SOURCE_COMMIT = "a" * 40
L43_SHA256 = "ac037d1dd12e581b67dbaafff08f6b6831ed64bea7302a3109022b7c19603728"
L54_SHA256 = "7b4dba5deb79101d688a40a40688879cc32503766bbb24e214a4876b361c3793"
L55_SHA256 = "822402c49d2687bbae65b71c18815bcbe45c3dadf51ef7d16530bb46743a8d13"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _default_spec(paper: str, claim_id: str) -> dict[str, Any]:
    study = "L52" if paper == "icbinb-bio" else "INTERP-CONFIRMATORY"
    return {
        "claim_id": claim_id,
        "source_study_ids": [study],
        "status": "confirmed",
        "gate": "pass",
        "status_reason": "",
        "artifact_bytes": f"owned result for {claim_id}\n".encode(),
        "parent_bytes": f"owned input for {claim_id}\n".encode(),
        "artifact_count": 1,
        "result_requirements": {
            "point_estimate": "required",
            "interval": "required",
            "denominator": "required",
        },
    }


def _reported_results(confirmed: bool) -> dict[str, str]:
    if not confirmed:
        unavailable = json.dumps(
            {"status": "not_available", "reason": "claim did not confirm"}
        )
        return {
            "point_estimate": unavailable,
            "interval": unavailable,
            "denominator": unavailable,
        }
    return {
        "point_estimate": json.dumps({"status": "reported", "value": 0.25}),
        "interval": json.dumps(
            {
                "status": "reported",
                "level": 0.95,
                "method": "percentile bootstrap",
                "bounds": {"lower": 0.1, "upper": 0.4},
                "interpretation": "finite-cohort stability interval",
            }
        ),
        "denominator": json.dumps(
            {"status": "reported", "counts": {"attempted": 20, "retained": 18}}
        ),
    }


def _artifact_list_from_row(row: dict[str, str]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for kind in ("raw", "derived"):
        paths = json.loads(row[f"{kind}_artifact_paths"])
        hashes = json.loads(row[f"{kind}_artifact_sha256"])
        result.extend(
            {"path": path, "sha256": sha256, "kind": kind}
            for path, sha256 in zip(paths, hashes, strict=True)
        )
    return result


def _build_package(
    tmp_path: Path,
    *,
    paper: str = "interp4discovery",
    specs: list[dict[str, Any]] | None = None,
    package_claim_id: str | None = None,
) -> dict[str, Any]:
    default_claim = "ICB-01" if paper == "icbinb-bio" else "INT-01"
    if specs is None:
        specs = [_default_spec(paper, default_claim)]
    specs = [{**_default_spec(paper, spec["claim_id"]), **spec} for spec in specs]
    if package_claim_id is None:
        package_claim_id = next(
            (
                spec["claim_id"]
                for spec in specs
                if spec["status"] == "confirmed"
            ),
            None,
        )

    package = tmp_path / "package"
    package.mkdir()
    (package / "paper.tex").write_text(
        "Contact-specific ablation damage was measured.\n"
        if paper == "interp4discovery"
        else "A staged evaluation audit was measured.\n",
        encoding="utf-8",
    )
    root = tmp_path / "repository"
    root.mkdir()

    registry = root / "docs" / "CLAIM_REGISTRY.md"
    registry.parent.mkdir()
    registry_text = ["# Claim Registry", ""]
    claim_text_hashes: dict[str, str] = {}
    for spec in specs:
        claim_text = f"Registered claim text for {spec['claim_id']}."
        claim_text_hashes[spec["claim_id"]] = hashlib.sha256(
            claim_text.encode()
        ).hexdigest()
        registry_text.extend(
            [f"### {spec['claim_id']}", "", "Claim:", "", f"> {claim_text}", ""]
        )
    registry.write_text("\n".join(registry_text), encoding="utf-8")

    roles = root / "locks" / "role_assignments.json"
    experiment_owner_ids = (
        [
            "experiment-owner",
            "cohort-owner",
            "ablation-owner",
            "analysis-owner",
        ]
        if paper == "interp4discovery"
        else ["experiment-owner"]
    )
    _write_json(
        roles,
        {
            "schema_version": "1.0",
            "paper_id": paper,
            "source_git_commit": SOURCE_COMMIT,
            "orchestrator_id": "orchestrator",
            "paper_owner_id": "paper-owner",
            "experiment_owner_ids": experiment_owner_ids,
            "statistical_reviewer_id": "statistical-reviewer",
            "final_technical_reviewer_id": "technical-reviewer",
        },
    )

    claim_files: dict[str, dict[str, Any]] = {}
    catalog_entries: list[dict[str, Any]] = []
    for spec in specs:
        claim_id = spec["claim_id"]
        slug = claim_id.lower()
        cohort = root / "manifests" / f"{slug}_cohort.json"
        experiment = root / "manifests" / f"{slug}_experiment.json"
        parent_lock = root / "locks" / f"{slug}_stage_lock.json"
        _write_json(cohort, {"claim_id": claim_id, "status": "frozen"})
        _write_json(experiment, {"claim_id": claim_id, "status": "frozen"})

        artifact_records: list[dict[str, Any]] = []
        for artifact_index in range(spec["artifact_count"]):
            suffix = "" if artifact_index == 0 else f"_{artifact_index}"
            artifact = root / "results" / f"{slug}{suffix}_result.pdf"
            parent = root / "inputs" / f"{slug}{suffix}_source.json"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            parent.parent.mkdir(parents=True, exist_ok=True)
            exact_artifact = spec.get("artifact_bytes_exact")
            exact_parent = spec.get("parent_bytes_exact")
            artifact.write_bytes(
                exact_artifact
                if exact_artifact is not None
                else spec["artifact_bytes"] + f"artifact {artifact_index}\n".encode()
            )
            parent.write_bytes(
                exact_parent
                if exact_parent is not None
                else spec["parent_bytes"] + f"parent {artifact_index}\n".encode()
            )
            artifact_records.append(
                {
                    "artifact": artifact,
                    "parent": parent,
                    "study": spec["source_study_ids"][
                        artifact_index % len(spec["source_study_ids"])
                    ],
                }
            )

        if spec.get("known_parent_policy") is None:
            for item in artifact_records:
                catalog_entries.append(
                    {
                        "path": item["parent"].relative_to(root).as_posix(),
                        "sha256": _sha256(item["parent"]),
                        "study_id": item["study"],
                        "allowed_papers": [paper],
                        "permitted_claim_ids": [claim_id],
                    }
                )

        for target_name in ("known_artifact_policy", "known_parent_policy"):
            policy = spec.get(target_name)
            if policy is None:
                continue
            source = (
                artifact_records[0]["artifact"]
                if target_name == "known_artifact_policy"
                else artifact_records[0]["parent"]
            )
            canonical = root / "known" / f"{slug}_{target_name}.bin"
            canonical.parent.mkdir(parents=True, exist_ok=True)
            canonical.write_bytes(source.read_bytes())
            catalog_entries.append(
                {
                    "path": canonical.relative_to(root).as_posix(),
                    "sha256": _sha256(canonical),
                    "study_id": policy["study_id"],
                    "allowed_papers": policy["allowed_papers"],
                    "permitted_claim_ids": policy["permitted_claim_ids"],
                }
            )

        claim_files[claim_id] = {
            "cohort": cohort,
            "experiment": experiment,
            "parent_lock": parent_lock,
            "artifacts": artifact_records,
        }

    ownership = root / "docs" / "ARTIFACT_OWNERSHIP.json"
    _write_json(
        ownership,
        {"schema_version": "1.0", "artifacts": catalog_entries},
    )

    contract = root / "docs" / "SUBMISSION_CONTRACT.json"
    claim_contracts = {}
    for spec in specs:
        claim_id = spec["claim_id"]
        claim_contracts[claim_id] = {
            "source_study_ids": spec["source_study_ids"],
            "provenance": "prospective",
            "estimand": f"Fixed estimand for {claim_id}",
            "statistical_unit": "protein",
            "control": "matched control",
            "limitation": "fixed limitation",
            "result_requirements": spec["result_requirements"],
        }
    _write_json(
        contract,
        {
            "schema_version": "1.0",
            "claim_registry_sha256": _sha256(registry),
            "artifact_ownership_path": ownership.relative_to(root).as_posix(),
            "artifact_ownership_sha256": _sha256(ownership),
            "papers": {
                paper: {
                    "required_claim_ids": [
                        spec["claim_id"] for spec in specs
                    ],
                    "claims": claim_contracts,
                }
            },
        },
    )

    for spec in specs:
        claim_id = spec["claim_id"]
        files = claim_files[claim_id]
        common = {
            "schema_version": "1.0",
            "paper_id": paper,
            "experiment_id": "synthetic-test-run",
            "claim_ids": [claim_id],
            "source_git_commit": SOURCE_COMMIT,
            "submission_contract_sha256": _sha256(contract),
            "role_assignments_sha256": _sha256(roles),
            "source_study_ids": spec["source_study_ids"],
            "owner_id": "experiment-owner",
        }
        _write_json(files["cohort"], {**common, "status": "frozen"})
        _write_json(files["experiment"], {**common, "status": "locked"})
        _write_json(
            files["parent_lock"],
            {
                "schema_version": "1.0",
                "paper_id": paper,
                "claim_ids": [claim_id],
                "source_git_commit": SOURCE_COMMIT,
                "submission_contract_sha256": _sha256(contract),
                "role_assignments_sha256": _sha256(roles),
                "owner_id": "experiment-owner",
                "status": "accepted",
                "artifacts": [
                    {
                        "path": item["parent"].relative_to(root).as_posix(),
                        "sha256": _sha256(item["parent"]),
                        "source_study_id": item["study"],
                    }
                    for item in files["artifacts"]
                ],
            },
        )

    rows: list[dict[str, str]] = []
    for spec in specs:
        claim_id = spec["claim_id"]
        files = claim_files[claim_id]
        not_run = spec["gate"] == "not_run"
        include_artifacts = not not_run
        artifacts = files["artifacts"] if include_artifacts else []
        lineage = root / "lineage" / f"{claim_id.lower()}_lineage.json"
        if include_artifacts:
            lineage_entries = [
                {
                    "path": item["artifact"].relative_to(root).as_posix(),
                    "sha256": _sha256(item["artifact"]),
                    "kind": "derived",
                    "source_study_id": item["study"],
                    "derivation": "fixed synthetic test transformation",
                    "parents": [
                        {
                            "path": item["parent"].relative_to(root).as_posix(),
                            "sha256": _sha256(item["parent"]),
                        }
                    ],
                }
                for item in artifacts
            ]
            _write_json(
                lineage,
                {
                    "schema_version": "1.0",
                    "paper_id": paper,
                    "claim_id": claim_id,
                    "source_git_commit": SOURCE_COMMIT,
                    "experiment_owner_id": "experiment-owner",
                    "claim_registry_sha256": _sha256(registry),
                    "submission_contract_sha256": _sha256(contract),
                    "cohort_manifest_path": files["cohort"]
                    .relative_to(root)
                    .as_posix(),
                    "cohort_manifest_sha256": _sha256(files["cohort"]),
                    "experiment_manifest_path": files["experiment"]
                    .relative_to(root)
                    .as_posix(),
                    "experiment_manifest_sha256": _sha256(files["experiment"]),
                    "status": "locked",
                    "parent_locks": [
                        {
                            "path": files["parent_lock"]
                            .relative_to(root)
                            .as_posix(),
                            "sha256": _sha256(files["parent_lock"]),
                        }
                    ],
                    "artifacts": lineage_entries,
                },
            )

        row = dict.fromkeys(LEDGER_COLUMNS, "")
        row.update(
            {
                "claim_id": claim_id,
                "paper_id": paper,
                "claim_text_sha256": claim_text_hashes[claim_id],
                "source_study_ids": json.dumps(spec["source_study_ids"]),
                "claim_status": spec["status"],
                "status_reason": spec["status_reason"],
                "provenance": "prospective",
                "estimand": f"Fixed estimand for {claim_id}",
                "statistical_unit": "protein",
                "control": "matched control",
                "cohort_manifest_path": (
                    files["cohort"].relative_to(root).as_posix()
                    if include_artifacts
                    else ""
                ),
                "cohort_manifest_sha256": (
                    _sha256(files["cohort"]) if include_artifacts else ""
                ),
                "experiment_manifest_path": (
                    files["experiment"].relative_to(root).as_posix()
                    if include_artifacts
                    else ""
                ),
                "experiment_manifest_sha256": (
                    _sha256(files["experiment"]) if include_artifacts else ""
                ),
                "lineage_manifest_path": (
                    lineage.relative_to(root).as_posix()
                    if include_artifacts
                    else ""
                ),
                "lineage_manifest_sha256": (
                    _sha256(lineage) if include_artifacts else ""
                ),
                "raw_artifact_paths": "[]",
                "raw_artifact_sha256": "[]",
                "derived_artifact_paths": json.dumps(
                    [
                        item["artifact"].relative_to(root).as_posix()
                        for item in artifacts
                    ]
                ),
                "derived_artifact_sha256": json.dumps(
                    [_sha256(item["artifact"]) for item in artifacts]
                ),
                "gate_result": spec["gate"],
                "limitation": "fixed limitation",
                "review_status": json.dumps(
                    {
                        "status": "not_required",
                        "reason": "claim did not confirm",
                    }
                ),
                "source_git_commit": SOURCE_COMMIT,
                **_reported_results(spec["status"] == "confirmed"),
            }
        )
        rows.append(row)

    for row in rows:
        if row["claim_status"] != "confirmed":
            continue
        review = root / "reviews" / f"{row['claim_id'].lower()}_decision.json"
        decision = {
            "schema_version": "1.0",
            "paper_id": paper,
            "claim_id": row["claim_id"],
            "reviewer_id": "statistical-reviewer",
            "reviewer_role": "statistical_reviewer",
            "decision": "accepted",
            "findings": [],
            "source_git_commit": SOURCE_COMMIT,
            "claim_registry_sha256": _sha256(registry),
            "submission_contract_sha256": _sha256(contract),
            "role_assignments_sha256": _sha256(roles),
            "row_payload_sha256": submission_ownership._row_payload_sha256(row),
            "cohort_manifest_path": row["cohort_manifest_path"],
            "cohort_manifest_sha256": row["cohort_manifest_sha256"],
            "experiment_manifest_path": row["experiment_manifest_path"],
            "experiment_manifest_sha256": row["experiment_manifest_sha256"],
            "lineage_manifest_path": row["lineage_manifest_path"],
            "lineage_manifest_sha256": row["lineage_manifest_sha256"],
            "artifacts": _artifact_list_from_row(row),
        }
        _write_json(review, decision)
        row["review_status"] = json.dumps(
            {
                "decision_path": review.relative_to(root).as_posix(),
                "decision_sha256": _sha256(review),
            }
        )

    ledger = root / "results" / "result_ledger.csv"
    _write_csv(ledger, rows)

    package_artifact = None
    allowlist_artifacts = []
    if package_claim_id is not None:
        package_artifact = package / "figures" / "owned_figure.pdf"
        package_artifact.parent.mkdir()
        source_artifact = claim_files[package_claim_id]["artifacts"][0]["artifact"]
        package_artifact.write_bytes(source_artifact.read_bytes())
        allowlist_artifacts.append(
            {
                "path": package_artifact.relative_to(package).as_posix(),
                "sha256": _sha256(package_artifact),
                "claim_id": package_claim_id,
                "ledger_artifact_path": source_artifact
                .relative_to(root)
                .as_posix(),
            }
        )

    allowlist = package / "ownership_allowlist.json"
    _write_json(
        allowlist,
        {
            "paper_id": paper,
            "claim_registry_sha256": _sha256(registry),
            "submission_contract_path": contract.relative_to(root).as_posix(),
            "submission_contract_sha256": _sha256(contract),
            "role_assignments_path": roles.relative_to(root).as_posix(),
            "role_assignments_sha256": _sha256(roles),
            "artifact_ownership_sha256": _sha256(ownership),
            "result_ledger_sha256": _sha256(ledger),
            "artifacts": allowlist_artifacts,
        },
    )
    return {
        "paper": paper,
        "package": package,
        "package_artifact": package_artifact,
        "allowlist": allowlist,
        "root": root,
        "registry": registry,
        "contract": contract,
        "roles": roles,
        "ownership": ownership,
        "ledger": ledger,
        "claim_files": claim_files,
        "specs": specs,
        "trusted_contract_hash": _sha256(contract),
        "trusted_ownership_hash": _sha256(ownership),
        "trusted_claim_ids": {spec["claim_id"] for spec in specs},
    }


def _find(paths: dict[str, Any]) -> list[str]:
    old_contract_hash = submission_ownership.EXPECTED_SUBMISSION_CONTRACT_SHA256
    old_ownership_hash = submission_ownership.EXPECTED_ARTIFACT_OWNERSHIP_SHA256
    old_claim_ids = submission_ownership.EXPECTED_CLAIM_IDS[
        paths["paper"]
    ].copy()
    submission_ownership.EXPECTED_SUBMISSION_CONTRACT_SHA256 = paths[
        "trusted_contract_hash"
    ]
    submission_ownership.EXPECTED_ARTIFACT_OWNERSHIP_SHA256 = paths[
        "trusted_ownership_hash"
    ]
    submission_ownership.EXPECTED_CLAIM_IDS[paths["paper"]] = set(
        paths["trusted_claim_ids"]
    )
    try:
        return find_violations(
            paths["paper"],
            paths["package"],
            ledger=paths["ledger"],
            ledger_root=paths["root"],
            claim_registry=paths["registry"],
        )
    finally:
        submission_ownership.EXPECTED_SUBMISSION_CONTRACT_SHA256 = old_contract_hash
        submission_ownership.EXPECTED_ARTIFACT_OWNERSHIP_SHA256 = old_ownership_hash
        submission_ownership.EXPECTED_CLAIM_IDS[paths["paper"]] = old_claim_ids


def _refresh_ledger_hash(paths: dict[str, Any]) -> None:
    allowlist = json.loads(paths["allowlist"].read_text(encoding="utf-8"))
    allowlist["result_ledger_sha256"] = _sha256(paths["ledger"])
    _write_json(paths["allowlist"], allowlist)


def _rewrite_rows(paths: dict[str, Any], rows: list[dict[str, str]]) -> None:
    _write_csv(paths["ledger"], rows)
    _refresh_ledger_hash(paths)


def _refresh_review_for_row(
    paths: dict[str, Any],
    row_index: int,
    mutate: Callable[[dict[str, Any]], None] | None = None,
) -> None:
    rows = _read_csv(paths["ledger"])
    row = rows[row_index]
    pointer = json.loads(row["review_status"])
    review_path = paths["root"] / pointer["decision_path"]
    decision = json.loads(review_path.read_text(encoding="utf-8"))
    decision.update(
        {
            "row_payload_sha256": submission_ownership._row_payload_sha256(row),
            "cohort_manifest_path": row["cohort_manifest_path"],
            "cohort_manifest_sha256": row["cohort_manifest_sha256"],
            "experiment_manifest_path": row["experiment_manifest_path"],
            "experiment_manifest_sha256": row["experiment_manifest_sha256"],
            "lineage_manifest_path": row["lineage_manifest_path"],
            "lineage_manifest_sha256": row["lineage_manifest_sha256"],
            "artifacts": _artifact_list_from_row(row),
        }
    )
    if mutate is not None:
        mutate(decision)
    _write_json(review_path, decision)
    row["review_status"] = json.dumps(
        {
            "decision_path": review_path.relative_to(paths["root"]).as_posix(),
            "decision_sha256": _sha256(review_path),
        }
    )
    _rewrite_rows(paths, rows)


def _mutate_lineage(
    paths: dict[str, Any],
    row_index: int,
    mutate: Callable[[dict[str, Any], dict[str, str]], None],
) -> None:
    rows = _read_csv(paths["ledger"])
    row = rows[row_index]
    lineage = paths["root"] / row["lineage_manifest_path"]
    data = json.loads(lineage.read_text(encoding="utf-8"))
    mutate(data, row)
    _write_json(lineage, data)
    row["lineage_manifest_sha256"] = _sha256(lineage)
    _write_csv(paths["ledger"], rows)
    _refresh_review_for_row(paths, row_index)


@pytest.mark.parametrize(
    ("paper", "text", "rule"),
    [
        ("icbinb-bio", "The L54 result supports this.", "excluded-study"),
        ("icbinb-bio", "Use l54_repro_out here.", "excluded-study"),
        (
            "icbinb-bio",
            "Steering improves thermostability and biological property control.",
            "biological-property-improvement",
        ),
        (
            "icbinb-bio",
            "A scoring-surrogate change proves biological property control.",
            "surrogate-proves-control",
        ),
        (
            "icbinb-bio",
            "The non-significant result proves that there is no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "L58 proves that L57 is caused by L55.",
            "l58-causal-explanation",
        ),
        (
            "icbinb-bio",
            "The three L55 runs isolate direction-build sensitivity.",
            "l55-isolated-direction-sensitivity",
        ),
        (
            "icbinb-bio",
            "L56 shows that no immune endpoint can be predicted from sequence.",
            "universal-immune-unpredictability",
        ),
        (
            "icbinb-bio",
            "Steering improves\nthermostability.",
            "biological-property-improvement",
        ),
        (
            "icbinb-bio",
            "Expression yield was higher after steering.",
            "biological-property-improvement",
        ),
        (
            "icbinb-bio",
            "The lack of statistical significance means zero effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "A causal relationship between L55 and L57 is established by L58.",
            "l58-causal-explanation",
        ),
        (
            "icbinb-bio",
            "The L55 and L57 vectors encode an identical direction according "
            "to L58.",
            "l58-causal-explanation",
        ),
        (
            "icbinb-bio",
            "Our intervention produced proteins with greater thermostability.",
            "biological-property-improvement",
        ),
        (
            "icbinb-bio",
            "A proxy shift is proof of phenotype control.",
            "surrogate-proves-control",
        ),
        (
            "icbinb-bio",
            "The method did not reduce decoder failures, but it improved "
            "thermostability.",
            "biological-property-improvement",
        ),
        (
            "icbinb-bio",
            "Without changing composition, steering improves thermostability.",
            "biological-property-improvement",
        ),
        (
            "icbinb-bio",
            "Steering was applied; consequently, thermostability improved.",
            "biological-property-improvement",
        ),
        (
            "icbinb-bio",
            "L58, i.e. the geometry diagnostic, establishes that L55 caused "
            "L57.",
            "l58-causal-explanation",
        ),
        (
            "icbinb-bio",
            "The pilot was not significant and does not establish an effect, "
            "but the confirmatory non-significant result means no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "The steered proteins were more thermostable.",
            "biological-property-improvement",
        ),
        (
            "icbinb-bio",
            "Steered sequences had less disorder.",
            "biological-property-improvement",
        ),
        (
            "icbinb-bio",
            "Steering made proteins safer.",
            "biological-property-improvement",
        ),
        (
            "icbinb-bio",
            "Score changes validate control over a phenotype.",
            "surrogate-proves-control",
        ),
        (
            "icbinb-bio",
            "L58 shows that L55 and L57 encode equivalent directions.",
            "l58-causal-explanation",
        ),
        (
            "icbinb-bio",
            "No immune response is predictable from sequence.",
            "universal-immune-unpredictability",
        ),
        (
            "icbinb-bio",
            "Failure to reject the null establishes an absence of effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "Steering did not improve calibration but improved thermostability.",
            "biological-property-improvement",
        ),
        (
            "icbinb-bio",
            "The surrogate did not prove calibration but established "
            "biological property control.",
            "surrogate-proves-control",
        ),
        (
            "icbinb-bio",
            "L58 did not explain L55 alone but established that L57 was caused "
            "by L55.",
            "l58-causal-explanation",
        ),
        (
            "icbinb-bio",
            "The L55 runs did not isolate cohort sensitivity but isolated "
            "direction-build sensitivity.",
            "l55-isolated-direction-sensitivity",
        ),
        (
            "icbinb-bio",
            "The non-significant result does not imply no effect but means "
            "zero effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "We do not claim calibration; no immune endpoint can be predicted "
            "from sequence.",
            "universal-immune-unpredictability",
        ),
        (
            "icbinb-bio",
            "Thermal stability was higher after treatment.",
            "biological-property-improvement",
        ),
        (
            "icbinb-bio",
            "L58 shows that the L55 and L57 directions are equivalent.",
            "l58-causal-explanation",
        ),
        (
            "icbinb-bio",
            "Sequence scores are insufficient to predict any immune endpoint.",
            "universal-immune-unpredictability",
        ),
        (
            "icbinb-bio",
            "The p-value exceeded 0.05, so there was no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "Steering confers thermostability.",
            "biological-property-improvement",
        ),
        (
            "icbinb-bio",
            "Steering yields thermostable proteins.",
            "biological-property-improvement",
        ),
        (
            "icbinb-bio",
            "L58 shows that the L55 and L57 vectors are collinear.",
            "l58-causal-explanation",
        ),
        (
            "icbinb-bio",
            "L55 attributes the observed sensitivity solely to direction "
            "construction.",
            "l55-isolated-direction-sensitivity",
        ),
        (
            "icbinb-bio",
            "Immune endpoints cannot be inferred from sequence.",
            "universal-immune-unpredictability",
        ),
        (
            "icbinb-bio",
            "The test did not reject the null, therefore there is no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "A p-value of 0.08 means no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "L58 cannot establish causation, direction identity, or "
            "independent validation.",
            "l58-causal-explanation",
        ),
        (
            "icbinb-bio",
            "Immune endpoints are unknowable from sequence.",
            "universal-immune-unpredictability",
        ),
        (
            "icbinb-bio",
            "Sequence contains insufficient information to recover immune "
            "endpoints.",
            "universal-immune-unpredictability",
        ),
        (
            "icbinb-bio",
            "p > 0.05 means no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "p >= .05 means no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "The p-value > 0.05 means no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "The p-value was 0.08, so there was no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "L - 58 proves that L - 57 was caused by L - 55.",
            "l58-causal-explanation",
        ),
        (
            "icbinb-bio",
            "p \u2265 0.05 means no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "$p \\geq 0.05$ means no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "The p-value was at least 0.08, so there was no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "No immune-endpoint can be predicted from sequence.",
            "universal-immune-unpredictability",
        ),
        (
            "icbinb-bio",
            "L\u201358 proves that L\u201357 was caused by L\u201355.",
            "l58-causal-explanation",
        ),
        (
            "icbinb-bio",
            "A value of 0.08 for p means no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "p = 5e-2 means no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "Sequence lacks enough information to infer immune endpoints.",
            "universal-immune-unpredictability",
        ),
        (
            "icbinb-bio",
            "No immune end points can be predicted from sequence.",
            "universal-immune-unpredictability",
        ),
        (
            "icbinb-bio",
            "L\u221258 proves that L\u221257 was caused by L\u221255.",
            "l58-causal-explanation",
        ),
        (
            "icbinb-bio",
            "$p_{\\mathrm{adj}} = 0.08$ means no effect.",
            "null-result-as-no-effect",
        ),
        (
            "icbinb-bio",
            "Sequence provides inadequate information to infer immune endpoints.",
            "universal-immune-unpredictability",
        ),
        (
            "icbinb-bio",
            "No immune end\\-points can be predicted from sequence.",
            "universal-immune-unpredictability",
        ),
        (
            "icbinb-bio",
            "L--58 proves that L--57 was caused by L--55.",
            "l58-causal-explanation",
        ),
        ("interp4discovery", "Steering improves this.", "steering"),
        ("interp4discovery", "The steered sequence changed.", "steering"),
    ],
)
def test_prohibited_text_is_rejected(
    tmp_path: Path,
    paper: str,
    text: str,
    rule: str,
):
    (tmp_path / "paper.tex").write_text(text, encoding="utf-8")

    violations = find_violations(paper, tmp_path)

    assert any(rule in item for item in violations)


@pytest.mark.parametrize(
    "text",
    [
        "The audit does not establish that steering improves a biological "
        "property.",
        "A scoring-surrogate change does not establish biological property "
        "control.",
        "L58 does not establish causation, direction identity, or independent "
        "validation.",
        "The L55 runs do not isolate direction-build sensitivity.",
        "This analysis does not support a universal claim about immune-endpoint "
        "predictability.",
        "A non-significant result does not establish no effect.",
    ],
)
def test_canonical_claim_boundaries_are_not_rejected(
    tmp_path: Path,
    text: str,
):
    (tmp_path / "paper.tex").write_text(text, encoding="utf-8")

    assert find_violations("icbinb-bio", tmp_path) == []


def test_canonical_claim_boundaries_match_manifest():
    repository = Path(__file__).resolve().parents[1]
    manifest = (
        repository / "docs" / "ICBINB_EXPERIMENT_MANIFEST.md"
    ).read_text(encoding="utf-8")
    start = manifest.index("corresponding sentence exactly:")
    end = manifest.index("The six boundary sentences above are always", start)
    statements: list[str] = []
    for line in manifest[start:end].splitlines():
        if line.startswith("- "):
            statements.append(line[2:])
        elif statements and line.startswith("  "):
            statements[-1] += " " + line.strip()
    documented = {
        submission_ownership._claim_key(statement) for statement in statements
    }

    assert documented == {
        submission_ownership._claim_key(statement)
        for statement in submission_ownership.ICBINB_CANONICAL_BOUNDARY_STATEMENTS
    }


def test_allowed_claim_statements_match_registry():
    repository = Path(__file__).resolve().parents[1]
    violations: list[str] = []
    claims = submission_ownership._load_claim_registry(
        repository / "docs" / "CLAIM_REGISTRY.md",
        violations,
    )
    registered = {
        claim["claim_text"]
        for claim_id, claim in claims.items()
        if claim_id.startswith("ICB-")
    }

    assert violations == []
    assert registered == submission_ownership.ICBINB_REGISTERED_CLAIM_STATEMENTS


@pytest.mark.parametrize(
    "text",
    sorted(submission_ownership.ICBINB_REGISTERED_CLAIM_STATEMENTS),
)
def test_registered_icbinb_claim_statements_require_confirmation(
    tmp_path: Path,
    text: str,
):
    (tmp_path / "paper.tex").write_text(text, encoding="utf-8")

    assert find_violations("icbinb-bio", tmp_path)


@pytest.mark.parametrize(
    "text",
    sorted(submission_ownership.ICBINB_REGISTERED_CLAIM_STATEMENTS),
)
def test_confirmed_icbinb_claim_statements_are_allowed(
    text: str,
):
    violations: list[str] = []
    submission_ownership._scan_icbinb_claim_boundaries(
        text,
        Path("paper.tex"),
        violations,
        {submission_ownership._claim_key(text)},
    )

    assert violations == []


def test_only_confirmed_ledger_rows_supply_claim_keys(tmp_path: Path):
    paths = _build_package(tmp_path, paper="icbinb-bio")
    expected = submission_ownership._claim_key(
        "Registered claim text for ICB-01."
    )

    assert submission_ownership._confirmed_registry_claim_keys(
        paths["ledger"],
        paths["registry"],
    ) == {expected}

    rows = _read_csv(paths["ledger"])
    rows[0]["claim_status"] = "conditional"
    _write_csv(paths["ledger"], rows)

    assert submission_ownership._confirmed_registry_claim_keys(
        paths["ledger"],
        paths["registry"],
    ) == set()


def test_paper_level_allowed_sentence_matches_manifest():
    repository = Path(__file__).resolve().parents[1]
    manifest = (
        repository / "docs" / "ICBINB_EXPERIMENT_MANIFEST.md"
    ).read_text(encoding="utf-8")
    start = manifest.index("The paper-level claim is:")
    end = manifest.index("The following claims are prohibited:", start)
    quoted = " ".join(
        line.removeprefix(">").strip()
        for line in manifest[start:end].splitlines()
        if line.startswith(">")
    )
    segment_keys = {
        submission_ownership._claim_key(sentence)
        for _, sentence in submission_ownership._claim_segments(quoted)
    }

    assert {
        submission_ownership._claim_key(statement)
        for statement in submission_ownership.ICBINB_ADDITIONAL_ALLOWED_STATEMENTS
    } == segment_keys


@pytest.mark.parametrize(
    "text",
    sorted(submission_ownership.ICBINB_ADDITIONAL_ALLOWED_STATEMENTS),
)
def test_paper_level_allowed_sentences_are_not_rejected(
    tmp_path: Path,
    text: str,
):
    (tmp_path / "paper.tex").write_text(text, encoding="utf-8")

    assert find_violations("icbinb-bio", tmp_path) == []


@pytest.mark.parametrize(
    "text",
    [
        "The surrogate does not prove biological property control.",
        "A non-significant result does not prove that there is no effect.",
        "L58 does not causally explain the L57 result.",
        "We do not claim that no immune endpoint can be predicted from sequence.",
        "Steering does not improve thermostability.",
        "No immune endpoint was claimed to be predictable from sequence.",
        "No improvement in thermostability was caused by steering.",
        "L58 provides no causal explanation for L55 or L57.",
        "L56 failed to show that no immune endpoint can be predicted from "
        "sequence.",
        "The non-significant result means the gate failed, not that there was "
        "no effect.",
        "There is no evidence that steering improves thermostability.",
        "Steering yielded no increase in thermostability.",
        "Steering improves calibration, not thermostability.",
        "No immune endpoint prediction was attempted.",
        "Not all immune endpoints are predictable from sequence.",
        "L58 reports attribution scores for L55 and L57.",
        "The non-significant result indicates uncertainty rather than no effect.",
        "Our method improves statistical power for testing thermostability.",
        "A non-significant result does not establish no effect?",
        "A non-significant result does not establish no effect!",
        "A non-significant result does not establish no effect.\u2713",
    ],
)
def test_noncanonical_boundary_language_fails_closed(
    tmp_path: Path,
    text: str,
):
    (tmp_path / "paper.tex").write_text(text, encoding="utf-8")

    assert find_violations("icbinb-bio", tmp_path)


@pytest.mark.parametrize(
    "suffix",
    ["?", "!", ".\u2713"],
)
def test_registered_claim_punctuation_variants_fail_closed(
    tmp_path: Path,
    suffix: str,
):
    statement = sorted(
        submission_ownership.ICBINB_REGISTERED_CLAIM_STATEMENTS
    )[0]
    (tmp_path / "paper.tex").write_text(
        statement.removesuffix(".") + suffix,
        encoding="utf-8",
    )

    assert find_violations("icbinb-bio", tmp_path)


@pytest.mark.parametrize(
    ("canonical_fragment", "replacement"),
    [
        ("observed T-cell response", "measured T-cell response"),
        ("performance fell", "performance declined"),
        ("analysis met its positive rule", "analysis satisfied its positive rule"),
    ],
)
def test_registered_claim_word_variants_fail_closed_even_when_confirmed(
    canonical_fragment: str,
    replacement: str,
):
    statement = next(
        item
        for item in submission_ownership.ICBINB_REGISTERED_CLAIM_STATEMENTS
        if canonical_fragment in item
    )
    variant = statement.replace(canonical_fragment, replacement)
    violations: list[str] = []

    submission_ownership._scan_icbinb_claim_boundaries(
        variant,
        Path("paper.tex"),
        violations,
        {submission_ownership._claim_key(statement)},
    )

    assert any("noncanonical registered ICBINB claim" in item for item in violations)


@pytest.mark.parametrize(
    ("claim_fragment", "variant"),
    [
        (
            "source-organism confounding.",
            "In the saved full-length cohort, validation performance fell under "
            "organism-grouped evaluation, a pattern consistent with "
            "source-organism confounding in the retained data and evaluation "
            "setting.",
        ),
        (
            "observed T-cell response.",
            "Saved L56 sequence-composition scores linked to peptide MHC-II "
            "binding performed worse for observed T-cell response.",
        ),
        (
            "source-organism confounding.",
            "In the saved full-length cohort, validation declined with "
            "organism-grouped evaluation, consistent with source-organism "
            "confounding.",
        ),
        (
            "substitutions were excluded",
            "The saved L57 analysis passed before E/L substitutions were "
            "excluded but failed after exclusion.",
        ),
    ],
)
def test_registered_claim_restatements_fail_closed_even_when_confirmed(
    claim_fragment: str,
    variant: str,
):
    statement = next(
        item
        for item in submission_ownership.ICBINB_REGISTERED_CLAIM_STATEMENTS
        if claim_fragment in item
    )
    violations: list[str] = []

    submission_ownership._scan_icbinb_claim_boundaries(
        variant,
        Path("paper.tex"),
        violations,
        {submission_ownership._claim_key(statement)},
    )

    assert any("noncanonical registered ICBINB claim" in item for item in violations)


@pytest.mark.parametrize(
    ("claim_fragment", "variant"),
    [
        (
            "observed T-cell response.",
            "Composition metrics tied to MHC class II binding performed worse "
            "for T-cell response.",
        ),
        (
            "source-organism confounding.",
            "In the full-length cohort, evaluation grouped on source organism "
            "showed performance loss consistent with confounding by source "
            "organism.",
        ),
        (
            "dominant-residue exclusion decision changes",
            "Across replicate runs, the most common residue exclusion decision "
            "changed with the disorder contrast.",
        ),
    ],
)
def test_registered_claim_anchor_variants_fail_closed_even_when_confirmed(
    claim_fragment: str,
    variant: str,
):
    statement = next(
        item
        for item in submission_ownership.ICBINB_REGISTERED_CLAIM_STATEMENTS
        if claim_fragment in item
    )
    violations: list[str] = []

    submission_ownership._scan_icbinb_claim_boundaries(
        variant,
        Path("paper.tex"),
        violations,
        {submission_ownership._claim_key(statement)},
    )

    assert any("noncanonical registered ICBINB claim" in item for item in violations)


def test_property_scanner_does_not_reject_bibliographic_word_proximity(
    tmp_path: Path,
):
    (tmp_path / "reference.bib").write_text(
        "title={DisProt in 2022: improved quality and accessibility of "
        "protein intrinsic disorder annotation}\n",
        encoding="utf-8",
    )

    assert find_violations("icbinb-bio", tmp_path) == []


@pytest.mark.parametrize("suffix", [".bbl", ".bib", ".md", ".sty", ".txt", ".typ"])
def test_package_text_sources_are_scanned(tmp_path: Path, suffix: str):
    (tmp_path / f"source{suffix}").write_text(
        "A steered sequence changed.",
        encoding="utf-8",
    )

    assert any(
        "prohibited steering" in item
        for item in find_violations("interp4discovery", tmp_path)
    )


@pytest.mark.parametrize("name", ["foreign-result.txt", "notes.md", "analysis.py"])
def test_only_named_manuscript_sources_are_exempt_from_allowlisting(
    tmp_path: Path,
    name: str,
):
    (tmp_path / name).write_text("Clean result text.\n", encoding="utf-8")

    assert (
        f"{name}: evidence file is not ownership-allowlisted"
        in find_violations("icbinb-bio", tmp_path)
    )


@pytest.mark.parametrize(
    "name",
    ["paper.tex", "reference.bib", "neurips_2026.sty", "paper.bbl"],
)
def test_named_manuscript_sources_do_not_require_allowlisting(
    tmp_path: Path,
    name: str,
):
    (tmp_path / name).write_text("Clean manuscript text.\n", encoding="utf-8")

    assert find_violations("icbinb-bio", tmp_path) == []


@pytest.mark.parametrize(
    "name",
    ["paper.tex", "reference.bib", "neurips_2026.sty", "paper.bbl"],
)
def test_all_exempt_manuscript_sources_receive_claim_boundary_scan(
    tmp_path: Path,
    name: str,
):
    (tmp_path / name).write_text(
        "Steering improves thermostability.\n",
        encoding="utf-8",
    )

    assert any(
        "biological-property-improvement" in item
        for item in find_violations("icbinb-bio", tmp_path)
    )


@pytest.mark.parametrize("target_kind", ["file", "directory", "broken"])
def test_package_symlinks_are_rejected_without_reading_targets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target_kind: str,
):
    repository = Path(__file__).resolve().parents[1]
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    if target_kind == "file":
        outside.write_bytes(
            (
                repository / "plm_steering" / "l54_repro_out" / "results.json"
            ).read_bytes()
        )
    elif target_kind == "directory":
        outside.mkdir()
    link = tmp_path / "package-link"
    link.symlink_to(outside, target_is_directory=target_kind == "directory")
    original_sha256 = submission_ownership._sha256

    def reject_symlink_read(path: Path) -> str:
        if path.is_symlink():
            raise AssertionError("package discovery read an outside symlink")
        return original_sha256(path)

    monkeypatch.setattr(submission_ownership, "_sha256", reject_symlink_read)

    assert any(
        "package symlinks are prohibited" in item
        for item in find_violations(
            "icbinb-bio",
            tmp_path,
            ledger_root=repository,
        )
    )


def test_symlinked_package_root_is_rejected_before_discovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    package = tmp_path / "package"
    package.mkdir()
    (package / "paper.tex").write_text("Clean report.\n", encoding="utf-8")
    package_link = tmp_path / "package-link"
    package_link.symlink_to(package, target_is_directory=True)

    def fail(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("symlinked package root was read")

    monkeypatch.setattr(
        submission_ownership,
        "_load_trusted_artifact_catalog",
        fail,
    )
    monkeypatch.setattr(submission_ownership, "_package_evidence_paths", fail)

    assert find_violations("icbinb-bio", package_link) == [
        "package root: path contains a prohibited symlink"
    ]


def test_symlinked_ledger_root_is_rejected_before_catalog_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    (tmp_path / "paper.tex").write_text("Clean report.\n", encoding="utf-8")
    repository = tmp_path.parent / f"{tmp_path.name}-repository"
    repository.mkdir()
    repository_link = tmp_path.parent / f"{tmp_path.name}-repository-link"
    repository_link.symlink_to(repository, target_is_directory=True)

    def fail(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("symlinked ledger root was read")

    monkeypatch.setattr(
        submission_ownership,
        "_load_trusted_artifact_catalog",
        fail,
    )

    assert find_violations(
        "icbinb-bio",
        tmp_path,
        ledger_root=repository_link,
    ) == ["ledger root: path contains a prohibited symlink"]


@pytest.mark.parametrize("link_kind", ["file", "directory"])
def test_contained_file_rejects_every_symlink_component(
    tmp_path: Path,
    link_kind: str,
):
    root = tmp_path / "repository"
    target_dir = root / "targets"
    target_dir.mkdir(parents=True)
    target = target_dir / "data.json"
    target.write_text('{"value":1}\n', encoding="utf-8")
    if link_kind == "file":
        link = root / "direct.json"
        link.symlink_to(target)
        relative = submission_ownership._safe_relative_path("direct.json")
    else:
        link = root / "linked"
        link.symlink_to(target_dir, target_is_directory=True)
        relative = submission_ownership._safe_relative_path("linked/data.json")

    assert relative is not None
    assert submission_ownership._contained_file(root, relative) is None


def test_canonical_contract_symlink_is_rejected_before_json_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    paths = _build_package(tmp_path)
    target = paths["contract"].with_name("contract-target.json")
    target.write_bytes(paths["contract"].read_bytes())
    paths["contract"].unlink()
    paths["contract"].symlink_to(target)
    original_load_json = submission_ownership._load_json

    def guarded_json(
        path: Path,
        label: str,
        violations: list[str],
    ) -> Any:
        if path.resolve() == target.resolve():
            raise AssertionError("canonical contract symlink target was read")
        return original_load_json(path, label, violations)

    monkeypatch.setattr(submission_ownership, "_load_json", guarded_json)

    assert any(
        "submission contract: file does not exist inside ledger root" in item
        for item in _find(paths)
    )


def test_default_allowlist_symlink_is_rejected_before_json_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    outside = tmp_path.parent / f"{tmp_path.name}-allowlist.json"
    _write_json(outside, {"paper_id": "icbinb-bio"})
    allowlist_link = tmp_path / "ownership_allowlist.json"
    allowlist_link.symlink_to(outside)
    original_load_json = submission_ownership._load_json

    def reject_symlink_read(
        path: Path,
        label: str,
        violations: list[str],
    ) -> Any:
        if path.is_symlink():
            raise AssertionError("metadata symlink was read")
        return original_load_json(path, label, violations)

    monkeypatch.setattr(submission_ownership, "_load_json", reject_symlink_read)

    violations = find_violations(
        "icbinb-bio",
        tmp_path,
        ledger_root=Path(__file__).resolve().parents[1],
    )

    assert (
        "ownership allowlist: path contains a prohibited symlink"
        in violations
    )
    assert any("package symlinks are prohibited" in item for item in violations)


def test_allowlisted_artifact_symlink_is_rejected_before_hash_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    paths = _build_package(tmp_path)
    package_artifact = paths["package_artifact"]
    target = package_artifact.with_name("target.pdf")
    target.write_bytes(package_artifact.read_bytes())
    package_artifact.unlink()
    package_artifact.symlink_to(target)
    original_contained_file = submission_ownership._contained_file

    def reject_symlink_resolution(
        root: Path,
        relative: Any,
    ) -> Path | None:
        unresolved = root.joinpath(*relative.parts)
        if unresolved.is_symlink():
            raise AssertionError("allowlisted artifact symlink was resolved")
        return original_contained_file(root, relative)

    monkeypatch.setattr(
        submission_ownership,
        "_contained_file",
        reject_symlink_resolution,
    )

    assert any(
        "package path contains a prohibited symlink" in item
        for item in _find(paths)
    )


@pytest.mark.parametrize(
    ("metadata_kind", "expected"),
    [
        (
            "allowlist",
            "ownership allowlist: path contains a prohibited symlink",
        ),
        ("ledger", "result ledger: path contains a prohibited symlink"),
        ("registry", "claim registry: path contains a prohibited symlink"),
    ],
)
def test_metadata_under_symlinked_directory_is_rejected_before_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    metadata_kind: str,
    expected: str,
):
    paths = _build_package(tmp_path)
    outside = tmp_path.parent / f"{tmp_path.name}-{metadata_kind}"
    outside.mkdir()
    source = {
        "allowlist": paths["allowlist"],
        "ledger": paths["ledger"],
        "registry": paths["registry"],
    }[metadata_kind]
    target = outside / source.name
    target.write_bytes(source.read_bytes())
    link_dir = paths["package"] / "metadata"
    link_dir.symlink_to(outside, target_is_directory=True)
    linked_path = link_dir / target.name
    resolved_outside = outside.resolve()

    original_load_json = submission_ownership._load_json
    original_load_csv = submission_ownership._load_csv
    original_load_registry = submission_ownership._load_claim_registry

    def is_outside(path: Path) -> bool:
        return path.resolve().is_relative_to(resolved_outside)

    def guarded_json(
        path: Path,
        label: str,
        violations: list[str],
    ) -> Any:
        if is_outside(path):
            raise AssertionError("JSON metadata was read through a symlink")
        return original_load_json(path, label, violations)

    def guarded_csv(
        path: Path,
        label: str,
        violations: list[str],
    ) -> Any:
        if is_outside(path):
            raise AssertionError("CSV metadata was read through a symlink")
        return original_load_csv(path, label, violations)

    def guarded_registry(path: Path, violations: list[str]) -> Any:
        if is_outside(path):
            raise AssertionError("claim registry was read through a symlink")
        return original_load_registry(path, violations)

    monkeypatch.setattr(submission_ownership, "_load_json", guarded_json)
    monkeypatch.setattr(submission_ownership, "_load_csv", guarded_csv)
    monkeypatch.setattr(
        submission_ownership,
        "_load_claim_registry",
        guarded_registry,
    )

    kwargs = {
        "allowlist": linked_path if metadata_kind == "allowlist" else None,
        "ledger": linked_path if metadata_kind == "ledger" else paths["ledger"],
        "ledger_root": paths["root"],
        "claim_registry": (
            linked_path if metadata_kind == "registry" else paths["registry"]
        ),
    }
    violations = find_violations(paths["paper"], paths["package"], **kwargs)

    assert expected in violations


def test_renamed_figure_without_allowlist_is_rejected(tmp_path: Path):
    figure = tmp_path / "figures" / "renamed.pdf"
    figure.parent.mkdir()
    figure.write_bytes(b"%PDF-1.4")

    assert find_violations("interp4discovery", tmp_path) == [
        "figures/renamed.pdf: evidence file is not ownership-allowlisted"
    ]


def test_clean_root_pdf_is_scanned(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    (tmp_path / "paper.pdf").write_bytes(b"%PDF-1.4")
    monkeypatch.setattr(
        submission_ownership,
        "_extract_pdf_text",
        lambda path: "Contact ablation result.",
    )

    assert find_violations("interp4discovery", tmp_path) == []


def test_only_named_manuscript_pdf_is_exempt_from_allowlisting(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    (tmp_path / "paper.pdf").write_bytes(b"%PDF-1.4")
    (tmp_path / "extra-result.pdf").write_bytes(b"%PDF-1.4")
    monkeypatch.setattr(
        submission_ownership,
        "_extract_pdf_text",
        lambda path: "A clean evaluation report.",
    )

    violations = find_violations("interp4discovery", tmp_path)

    assert (
        "extra-result.pdf: evidence file is not ownership-allowlisted"
        in violations
    )
    assert not any(item.startswith("paper.pdf: evidence") for item in violations)


def test_prohibited_root_pdf_text_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    (tmp_path / "paper.pdf").write_bytes(b"%PDF-1.4")
    monkeypatch.setattr(
        submission_ownership,
        "_extract_pdf_text",
        lambda path: "The steered result changed.",
    )

    assert any(
        "paper.pdf:1: prohibited steering" in item
        for item in find_violations("interp4discovery", tmp_path)
    )


def test_unreadable_root_pdf_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    (tmp_path / "paper.pdf").write_bytes(b"%PDF-1.4")

    def fail(path: Path) -> str:
        raise RuntimeError("invalid PDF")

    monkeypatch.setattr(submission_ownership, "_extract_pdf_text", fail)

    assert any(
        "cannot extract compiled PDF text" in item
        for item in find_violations("interp4discovery", tmp_path)
    )


@pytest.mark.parametrize(
    ("paper", "claim_id"),
    [("icbinb-bio", "ICB-01"), ("interp4discovery", "INT-01")],
)
def test_valid_confirmed_package_passes(
    tmp_path: Path,
    paper: str,
    claim_id: str,
):
    paths = _build_package(
        tmp_path,
        paper=paper,
        specs=[_default_spec(paper, claim_id)],
    )

    assert _find(paths) == []


@pytest.mark.parametrize("case", ["missing", "extra", "duplicate"])
def test_exact_claim_membership_is_required(tmp_path: Path, case: str):
    specs = [
        _default_spec("interp4discovery", "INT-01"),
        _default_spec("interp4discovery", "INT-02"),
    ]
    paths = _build_package(tmp_path, specs=specs, package_claim_id="INT-01")
    rows = _read_csv(paths["ledger"])
    if case == "missing":
        rows.pop()
    elif case == "duplicate":
        rows.append(rows[0].copy())
    else:
        extra = rows[0].copy()
        extra["claim_id"] = "INT-99"
        rows.append(extra)
    _rewrite_rows(paths, rows)

    violations = _find(paths)

    assert any(f"{case} controlling claim" in item for item in violations)


def test_rehashed_contract_cannot_omit_trusted_claims(tmp_path: Path):
    paths = _build_package(
        tmp_path,
        specs=[
            _default_spec("interp4discovery", "INT-01"),
            _default_spec("interp4discovery", "INT-02"),
            _default_spec("interp4discovery", "INT-03"),
        ],
        package_claim_id="INT-01",
    )
    contract = json.loads(paths["contract"].read_text(encoding="utf-8"))
    paper_contract = contract["papers"]["interp4discovery"]
    paper_contract["required_claim_ids"] = ["INT-01"]
    paper_contract["claims"] = {"INT-01": paper_contract["claims"]["INT-01"]}
    _write_json(paths["contract"], contract)
    paths["trusted_contract_hash"] = _sha256(paths["contract"])
    allowlist = json.loads(paths["allowlist"].read_text(encoding="utf-8"))
    allowlist["submission_contract_sha256"] = paths["trusted_contract_hash"]
    _write_json(paths["allowlist"], allowlist)

    assert any(
        "required_claim_ids do not match the trusted set" in item
        for item in _find(paths)
    )


def test_stopped_and_rejected_rows_are_retained_without_authorizing(
    tmp_path: Path,
):
    specs = [
        _default_spec("interp4discovery", "INT-01"),
        {
            **_default_spec("interp4discovery", "INT-02"),
            "status": "stopped",
            "gate": "fail",
            "status_reason": "stopped by gate",
        },
        {
            **_default_spec("interp4discovery", "INT-03"),
            "status": "rejected",
            "gate": "fail",
            "status_reason": "claim rejected",
        },
    ]
    paths = _build_package(tmp_path, specs=specs, package_claim_id="INT-01")
    assert _find(paths) == []

    stopped_artifact = paths["claim_files"]["INT-02"]["artifacts"][0]["artifact"]
    paths["package_artifact"].write_bytes(stopped_artifact.read_bytes())
    allowlist = json.loads(paths["allowlist"].read_text(encoding="utf-8"))
    entry = allowlist["artifacts"][0]
    entry["sha256"] = _sha256(paths["package_artifact"])
    entry["claim_id"] = "INT-02"
    entry["ledger_artifact_path"] = stopped_artifact.relative_to(
        paths["root"]
    ).as_posix()
    _write_json(paths["allowlist"], allowlist)

    assert any("not authorized by a confirmed row" in item for item in _find(paths))


def test_nonconfirmed_row_requires_status_reason(tmp_path: Path):
    spec = {
        **_default_spec("interp4discovery", "INT-01"),
        "status": "stopped",
        "gate": "fail",
        "status_reason": "",
    }
    paths = _build_package(tmp_path, specs=[spec], package_claim_id=None)

    assert any("requires a nonempty status_reason" in item for item in _find(paths))


def test_deferred_not_run_row_may_omit_manifests_and_artifacts(tmp_path: Path):
    spec = {
        **_default_spec("interp4discovery", "INT-01"),
        "status": "deferred",
        "gate": "not_run",
        "status_reason": "deferred by contract",
    }
    paths = _build_package(tmp_path, specs=[spec], package_claim_id=None)

    assert _find(paths) == []


@pytest.mark.parametrize(
    "field",
    ["provenance", "estimand", "statistical_unit", "control", "limitation"],
)
def test_blank_confirmed_semantics_are_rejected(tmp_path: Path, field: str):
    paths = _build_package(tmp_path)
    rows = _read_csv(paths["ledger"])
    rows[0][field] = ""
    _rewrite_rows(paths, rows)

    assert any(
        f"{field} does not match the submission contract" in item
        for item in _find(paths)
    )


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("point_estimate", "", "contains invalid JSON"),
        (
            "point_estimate",
            json.dumps({"status": "reported", "value": None}),
            "nonempty finite value",
        ),
        (
            "point_estimate",
            json.dumps({"status": "reported", "value": {"primary": None}}),
            "nonempty finite value",
        ),
        (
            "point_estimate",
            json.dumps({"status": "reported", "value": "0.25"}),
            "nonempty finite value",
        ),
        (
            "point_estimate",
            json.dumps({"status": "reported", "value": float("nan")}),
            "nonempty finite value",
        ),
        (
            "interval",
            json.dumps(
                {
                    "status": "reported",
                    "level": 2,
                    "method": "x",
                    "bounds": [0, 1],
                    "interpretation": "x",
                }
            ),
            "0 < level <= 1",
        ),
        (
            "interval",
            json.dumps(
                {
                    "status": "reported",
                    "level": 10**1000,
                    "method": "x",
                    "bounds": [0, 1],
                    "interpretation": "x",
                }
            ),
            "0 < level <= 1",
        ),
        (
            "interval",
            json.dumps(
                {
                    "status": "reported",
                    "level": 0.95,
                    "method": "x",
                    "bounds": {"lower": None, "upper": 1},
                    "interpretation": "x",
                }
            ),
            "ordered finite bounds",
        ),
        (
            "interval",
            json.dumps(
                {
                    "status": "reported",
                    "level": 0.95,
                    "method": "x",
                    "bounds": {"lower": 1, "upper": 0},
                    "interpretation": "x",
                }
            ),
            "ordered finite bounds",
        ),
        (
            "denominator",
            json.dumps({"status": "reported", "counts": {"attempted": -1}}),
            "nonnegative integer",
        ),
    ],
)
def test_malformed_typed_results_are_rejected(
    tmp_path: Path,
    field: str,
    value: str,
    expected: str,
):
    paths = _build_package(tmp_path)
    rows = _read_csv(paths["ledger"])
    rows[0][field] = value
    _rewrite_rows(paths, rows)

    assert any(expected in item for item in _find(paths))


def test_oversized_json_integer_fails_closed(tmp_path: Path):
    paths = _build_package(tmp_path)
    rows = _read_csv(paths["ledger"])
    rows[0]["interval"] = (
        '{"status":"reported","level":'
        + ("9" * 5000)
        + ',"method":"x","bounds":[0,1],"interpretation":"x"}'
    )
    _rewrite_rows(paths, rows)

    assert any(
        "interval contains invalid JSON" in item
        for item in _find(paths)
    )


def test_deeply_nested_json_fails_closed(tmp_path: Path):
    paths = _build_package(tmp_path)
    rows = _read_csv(paths["ledger"])
    nested = ("[" * 2000) + "0" + ("]" * 2000)
    rows[0]["point_estimate"] = (
        '{"status":"reported","value":' + nested + "}"
    )
    _rewrite_rows(paths, rows)

    assert any(
        "point_estimate contains invalid JSON" in item
        for item in _find(paths)
    )


def test_medium_depth_numeric_payload_fails_closed_without_recursion(
    tmp_path: Path,
):
    paths = _build_package(tmp_path)
    rows = _read_csv(paths["ledger"])
    nested_null = ("[" * 800) + "null" + ("]" * 800)
    rows[0]["point_estimate"] = (
        '{"status":"reported","value":' + nested_null + "}"
    )
    _rewrite_rows(paths, rows)

    assert any(
        "point_estimate must contain a nonempty finite value" in item
        for item in _find(paths)
    )


def test_contract_not_applicable_result_passes(tmp_path: Path):
    spec = _default_spec("interp4discovery", "INT-01")
    spec["result_requirements"] = {
        "point_estimate": "required",
        "interval": "not_applicable",
        "denominator": "required",
    }
    paths = _build_package(tmp_path, specs=[spec])
    rows = _read_csv(paths["ledger"])
    rows[0]["interval"] = json.dumps(
        {"status": "not_applicable", "reason": "fixed descriptive object"}
    )
    _write_csv(paths["ledger"], rows)
    _refresh_review_for_row(paths, 0)

    assert _find(paths) == []


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda review: review.update(decision="hold"), "must be 'accepted'"),
        (
            lambda review: review.update(
                findings=[{"severity": "Major", "resolved": False}]
            ),
            "unresolved Critical or Major",
        ),
        (
            lambda review: review.update(claim_id="INT-99"),
            "claim_id does not match",
        ),
        (
            lambda review: review.update(source_git_commit="b" * 40),
            "source_git_commit does not match",
        ),
        (
            lambda review: review.update(artifacts=[]),
            "artifacts does not match",
        ),
        (
            lambda review: review.update(
                submission_contract_sha256="0" * 64
            ),
            "submission_contract_sha256 does not match",
        ),
        (
            lambda review: review.update(role_assignments_sha256="0" * 64),
            "role_assignments_sha256 does not match",
        ),
        (
            lambda review: review.update(lineage_manifest_sha256="0" * 64),
            "lineage_manifest_sha256 does not match",
        ),
    ],
)
def test_invalid_review_decisions_are_rejected(
    tmp_path: Path,
    mutate: Callable[[dict[str, Any]], None],
    expected: str,
):
    paths = _build_package(tmp_path)
    _refresh_review_for_row(paths, 0, mutate)

    assert any(expected in item for item in _find(paths))


def test_stale_reviewed_row_is_rejected(tmp_path: Path):
    paths = _build_package(tmp_path)
    rows = _read_csv(paths["ledger"])
    estimate = json.loads(rows[0]["point_estimate"])
    estimate["value"] = 0.5
    rows[0]["point_estimate"] = json.dumps(estimate)
    _rewrite_rows(paths, rows)

    assert any("row_payload_sha256 does not match" in item for item in _find(paths))


def test_owner_reviewer_collision_is_rejected(tmp_path: Path):
    paths = _build_package(tmp_path)
    roles = json.loads(paths["roles"].read_text(encoding="utf-8"))
    roles["statistical_reviewer_id"] = "experiment-owner"
    _write_json(paths["roles"], roles)
    roles_hash = _sha256(paths["roles"])
    allowlist = json.loads(paths["allowlist"].read_text(encoding="utf-8"))
    allowlist["role_assignments_sha256"] = roles_hash
    _write_json(paths["allowlist"], allowlist)

    def rebind(review: dict[str, Any]) -> None:
        review["reviewer_id"] = "experiment-owner"
        review["role_assignments_sha256"] = roles_hash

    _refresh_review_for_row(paths, 0, rebind)

    assert any("must be pairwise distinct" in item for item in _find(paths))


def test_trailing_whitespace_cannot_bypass_role_separation(tmp_path: Path):
    paths = _build_package(tmp_path)
    roles = json.loads(paths["roles"].read_text(encoding="utf-8"))
    roles["paper_owner_id"] = f"{roles['statistical_reviewer_id']} "
    _write_json(paths["roles"], roles)
    roles_hash = _sha256(paths["roles"])
    allowlist = json.loads(paths["allowlist"].read_text(encoding="utf-8"))
    allowlist["role_assignments_sha256"] = roles_hash
    _write_json(paths["allowlist"], allowlist)
    _refresh_review_for_row(
        paths,
        0,
        lambda review: review.update(role_assignments_sha256=roles_hash),
    )

    assert any(
        "paper_owner_id must be a canonical identity" in item
        for item in _find(paths)
    )


def test_interp_requires_four_experiment_owners(tmp_path: Path):
    paths = _build_package(tmp_path)
    roles = json.loads(paths["roles"].read_text(encoding="utf-8"))
    roles["experiment_owner_ids"] = ["experiment-owner"]
    _write_json(paths["roles"], roles)
    roles_hash = _sha256(paths["roles"])
    allowlist = json.loads(paths["allowlist"].read_text(encoding="utf-8"))
    allowlist["role_assignments_sha256"] = roles_hash
    _write_json(paths["allowlist"], allowlist)
    _refresh_review_for_row(
        paths,
        0,
        lambda review: review.update(role_assignments_sha256=roles_hash),
    )

    assert any(
        "requires four distinct experiment owners" in item for item in _find(paths)
    )


@pytest.mark.parametrize(
    ("paper", "claim_id", "study", "foreign_path", "foreign_hash", "allowed_paper"),
    [
        (
            "icbinb-bio",
            "ICB-01",
            "L54",
            "plm_steering/l54_repro_out/results.json",
            L54_SHA256,
            "catalytic",
        ),
        (
            "interp4discovery",
            "INT-01",
            "L55",
            "plm_steering/l55_repro_out/results.json",
            L55_SHA256,
            "icbinb-bio",
        ),
    ],
)
def test_renamed_foreign_artifact_hash_is_rejected(
    tmp_path: Path,
    paper: str,
    claim_id: str,
    study: str,
    foreign_path: str,
    foreign_hash: str,
    allowed_paper: str,
):
    repository = Path(__file__).resolve().parents[1]
    foreign_bytes = (repository / foreign_path).read_bytes()
    assert hashlib.sha256(foreign_bytes).hexdigest() == foreign_hash
    spec = _default_spec(paper, claim_id)
    spec["artifact_bytes_exact"] = foreign_bytes
    spec["known_artifact_policy"] = {
        "study_id": study,
        "allowed_papers": [allowed_paper],
        "permitted_claim_ids": ["FOREIGN-01"],
    }
    paths = _build_package(tmp_path, paper=paper, specs=[spec])

    assert any(
        "known artifact hash is owned by another paper" in item
        for item in _find(paths)
    )


def test_known_foreign_bytes_renamed_as_text_are_evidence(tmp_path: Path):
    repository = Path(__file__).resolve().parents[1]
    foreign = repository / "plm_steering" / "l54_repro_out" / "results.json"
    assert _sha256(foreign) == L54_SHA256
    (tmp_path / "renamed.txt").write_bytes(foreign.read_bytes())

    violations = find_violations(
        "icbinb-bio",
        tmp_path,
        ledger_root=repository,
    )

    assert any(
        "renamed.txt: evidence file is not ownership-allowlisted" in item
        for item in violations
    )


def test_modified_foreign_bytes_renamed_as_text_require_allowlisting(
    tmp_path: Path,
):
    repository = Path(__file__).resolve().parents[1]
    foreign = repository / "plm_steering" / "l54_repro_out" / "results.json"
    assert _sha256(foreign) == L54_SHA256
    (tmp_path / "foreign-result.txt").write_bytes(foreign.read_bytes() + b"\n")

    violations = find_violations(
        "icbinb-bio",
        tmp_path,
        ledger_root=repository,
    )

    assert any(
        "foreign-result.txt: evidence file is not ownership-allowlisted" in item
        for item in violations
    )


def test_catalog_records_excluded_historical_l43_hash():
    repository = Path(__file__).resolve().parents[1]
    catalog = json.loads(
        (repository / "docs" / "ARTIFACT_OWNERSHIP.json").read_text(
            encoding="utf-8"
        )
    )
    entry = next(
        item for item in catalog["artifacts"] if item["sha256"] == L43_SHA256
    )

    assert entry == {
        "path": "plm_steering/l43_repro_results.json",
        "sha256": L43_SHA256,
        "study_id": "L43",
        "allowed_papers": [],
        "permitted_claim_ids": [],
        "canonical_present": False,
    }


def test_exact_historical_l43_bytes_require_allowlisting(tmp_path: Path):
    repository = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [
            "git",
            "show",
            "2a3aba8eee720a385989ef87416aa828eb63b86b:"
            "plm_steering/l43_repro_results.json",
        ],
        cwd=repository,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        pytest.skip("historical L43 blob is unavailable without Git history")
    assert hashlib.sha256(completed.stdout).hexdigest() == L43_SHA256
    (tmp_path / "renamed.txt").write_bytes(completed.stdout)

    violations = find_violations(
        "icbinb-bio",
        tmp_path,
        ledger_root=repository,
    )

    assert any(
        "renamed.txt: evidence file is not ownership-allowlisted" in item
        for item in violations
    )


def test_foreign_hash_in_lineage_parent_is_rejected(tmp_path: Path):
    repository = Path(__file__).resolve().parents[1]
    foreign_bytes = (
        repository / "plm_steering" / "l55_repro_out" / "results.json"
    ).read_bytes()
    assert hashlib.sha256(foreign_bytes).hexdigest() == L55_SHA256
    spec = _default_spec("interp4discovery", "INT-01")
    spec["parent_bytes_exact"] = foreign_bytes
    spec["known_parent_policy"] = {
        "study_id": "L55",
        "allowed_papers": ["icbinb-bio"],
        "permitted_claim_ids": ["ICB-04"],
    }
    paths = _build_package(tmp_path, specs=[spec])

    assert any(
        "known artifact hash is owned by another paper" in item
        for item in _find(paths)
    )


def test_catalytic_source_data_cannot_be_used_as_l52_parent(tmp_path: Path):
    repository = Path(__file__).resolve().parents[1]
    foreign_bytes = (
        repository
        / "plm_steering"
        / "data_cache"
        / "catalytic"
        / "dlkcat_wt_mut.json"
    ).read_bytes()
    spec = _default_spec("icbinb-bio", "ICB-01")
    spec["parent_bytes_exact"] = foreign_bytes
    spec["known_parent_policy"] = {
        "study_id": "L54",
        "allowed_papers": ["catalytic"],
        "permitted_claim_ids": [],
    }
    paths = _build_package(
        tmp_path,
        paper="icbinb-bio",
        specs=[spec],
    )

    assert any(
        "known artifact hash is owned by another paper" in item
        for item in _find(paths)
    )


def test_spoofed_lineage_study_is_rejected(tmp_path: Path):
    paths = _build_package(tmp_path)

    def mutate(lineage: dict[str, Any], row: dict[str, str]) -> None:
        lineage["artifacts"][0]["source_study_id"] = "L55"

    _mutate_lineage(paths, 0, mutate)

    assert any("source_study_id is not allowed" in item for item in _find(paths))


def test_missing_lineage_parent_is_rejected(tmp_path: Path):
    paths = _build_package(tmp_path)

    def mutate(lineage: dict[str, Any], row: dict[str, str]) -> None:
        lineage["artifacts"][0]["parents"] = []

    _mutate_lineage(paths, 0, mutate)

    assert any("parents must be a nonempty" in item for item in _find(paths))


def test_missing_lineage_derivation_is_rejected(tmp_path: Path):
    paths = _build_package(tmp_path)

    def mutate(lineage: dict[str, Any], row: dict[str, str]) -> None:
        lineage["artifacts"][0]["derivation"] = ""

    _mutate_lineage(paths, 0, mutate)

    assert any("derivation must be nonempty" in item for item in _find(paths))


def test_existing_undeclared_lineage_parent_is_rejected(tmp_path: Path):
    paths = _build_package(tmp_path)
    undeclared = paths["root"] / "inputs" / "undeclared.json"
    undeclared.write_text('{"source":"undeclared"}\n', encoding="utf-8")

    def mutate(lineage: dict[str, Any], row: dict[str, str]) -> None:
        lineage["artifacts"][0]["parents"] = [
            {
                "path": undeclared.relative_to(paths["root"]).as_posix(),
                "sha256": _sha256(undeclared),
            }
        ]

    _mutate_lineage(paths, 0, mutate)

    assert any(
        "unknown parent is absent from accepted parent locks" in item
        for item in _find(paths)
    )


def test_lineage_self_reference_is_rejected(tmp_path: Path):
    paths = _build_package(tmp_path)

    def mutate(lineage: dict[str, Any], row: dict[str, str]) -> None:
        artifact = lineage["artifacts"][0]
        artifact["parents"] = [
            {"path": artifact["path"], "sha256": artifact["sha256"]}
        ]

    _mutate_lineage(paths, 0, mutate)

    assert any("self-reference is prohibited" in item for item in _find(paths))


def test_lineage_cycle_is_rejected(tmp_path: Path):
    spec = _default_spec("interp4discovery", "INT-01")
    spec["artifact_count"] = 2
    paths = _build_package(tmp_path, specs=[spec])

    def mutate(lineage: dict[str, Any], row: dict[str, str]) -> None:
        first, second = lineage["artifacts"]
        first["parents"] = [{"path": second["path"], "sha256": second["sha256"]}]
        second["parents"] = [{"path": first["path"], "sha256": first["sha256"]}]

    _mutate_lineage(paths, 0, mutate)

    assert any("lineage contains a cycle" in item for item in _find(paths))


def test_catalog_tamper_is_rejected(tmp_path: Path):
    paths = _build_package(tmp_path)
    catalog = json.loads(paths["ownership"].read_text(encoding="utf-8"))
    catalog["tampered"] = True
    _write_json(paths["ownership"], catalog)

    assert any(
        "artifact ownership: sha256 does not match" in item
        for item in _find(paths)
    )


def test_malformed_parent_lock_content_is_rejected(tmp_path: Path):
    paths = _build_package(tmp_path)
    parent_lock = paths["claim_files"]["INT-01"]["parent_lock"]
    _write_json(parent_lock, {"note": "this is not a stage lock"})

    def rebind_lock(lineage: dict[str, Any], row: dict[str, str]) -> None:
        lineage["parent_locks"][0]["sha256"] = _sha256(parent_lock)

    _mutate_lineage(paths, 0, rebind_lock)

    assert any(
        "parent lock 0: schema_version does not match the ledger contract" in item
        for item in _find(paths)
    )


@pytest.mark.parametrize("manifest_kind", ["cohort", "experiment"])
def test_hash_matched_malformed_manifest_content_is_rejected(
    tmp_path: Path,
    manifest_kind: str,
):
    paths = _build_package(tmp_path)
    manifest = paths["claim_files"]["INT-01"][manifest_kind]
    _write_json(manifest, {"note": "this is not a valid manifest"})
    rows = _read_csv(paths["ledger"])
    rows[0][f"{manifest_kind}_manifest_sha256"] = _sha256(manifest)
    _rewrite_rows(paths, rows)

    assert any(
        f"{manifest_kind} manifest for INT-01: schema_version" in item
        for item in _find(paths)
    )


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ("package", "package file sha256 does not match"),
        ("ledger_artifact", "file sha256 does not match result ledger"),
        ("cohort", "cohort_manifest sha256 does not match"),
        ("parent_lock", "parent lock 0: file sha256 does not match"),
    ],
)
def test_tampered_bound_files_are_rejected(
    tmp_path: Path,
    target: str,
    expected: str,
):
    paths = _build_package(tmp_path)
    if target == "package":
        file_path = paths["package_artifact"]
    elif target == "ledger_artifact":
        file_path = paths["claim_files"]["INT-01"]["artifacts"][0]["artifact"]
    else:
        file_path = paths["claim_files"]["INT-01"][target]
    file_path.write_bytes(file_path.read_bytes() + b"tampered")

    assert any(expected in item for item in _find(paths))


@pytest.mark.parametrize(
    ("target", "field"),
    [
        ("allowlist", "path"),
        ("allowlist", "ledger_artifact_path"),
        ("ledger", "derived_artifact_paths"),
        ("lineage", "parent"),
    ],
)
def test_path_escapes_are_rejected(
    tmp_path: Path,
    target: str,
    field: str,
):
    paths = _build_package(tmp_path)
    if target == "allowlist":
        allowlist = json.loads(paths["allowlist"].read_text(encoding="utf-8"))
        allowlist["artifacts"][0][field] = "../outside.pdf"
        _write_json(paths["allowlist"], allowlist)
    elif target == "ledger":
        rows = _read_csv(paths["ledger"])
        rows[0][field] = json.dumps(["../outside.pdf"])
        _rewrite_rows(paths, rows)
    else:

        def mutate(lineage: dict[str, Any], row: dict[str, str]) -> None:
            lineage["artifacts"][0]["parents"][0]["path"] = "../outside.json"

        _mutate_lineage(paths, 0, mutate)

    assert any("safe relative POSIX path" in item for item in _find(paths))


@pytest.mark.parametrize(
    ("pin", "expected"),
    [
        (
            "submission_contract_sha256",
            "submission_contract_sha256 is not trusted",
        ),
        (
            "role_assignments_sha256",
            "role assignments: sha256 does not match",
        ),
        (
            "claim_registry_sha256",
            "claim registry sha256 does not match",
        ),
        (
            "artifact_ownership_sha256",
            "artifact_ownership_sha256 is not trusted",
        ),
    ],
)
def test_allowlist_hash_pins_are_enforced(
    tmp_path: Path,
    pin: str,
    expected: str,
):
    paths = _build_package(tmp_path)
    allowlist = json.loads(paths["allowlist"].read_text(encoding="utf-8"))
    allowlist[pin] = "0" * 64
    _write_json(paths["allowlist"], allowlist)

    assert any(expected in item for item in _find(paths))


def test_submission_contract_path_must_be_canonical(tmp_path: Path):
    paths = _build_package(tmp_path)
    allowlist = json.loads(paths["allowlist"].read_text(encoding="utf-8"))
    allowlist["submission_contract_path"] = "docs/alternate_contract.json"
    _write_json(paths["allowlist"], allowlist)

    assert any(
        "submission_contract_path is not canonical" in item
        for item in _find(paths)
    )


@pytest.mark.parametrize("paper", ["icbinb-bio", "interp4discovery"])
def test_current_historical_packages_remain_rejected(paper: str):
    repository = Path(__file__).resolve().parents[1]
    package = repository / "docs" / "submissions" / paper

    assert find_violations(paper, package)


def test_unknown_paper_is_rejected(tmp_path: Path):
    with pytest.raises(ValueError, match="unknown paper"):
        find_violations("unknown", tmp_path)
