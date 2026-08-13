"""Fail-closed guard for legacy experiment entry points."""


def refuse_legacy_runner(script_name: str) -> None:
    raise SystemExit(
        f"{script_name} is disabled because its legacy entry point uses "
        "hard-coded seeds and output paths that can overwrite research "
        "evidence. Implement and test the audited command interface before "
        "running this experiment."
    )
