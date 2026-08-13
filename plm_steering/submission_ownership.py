"""Check paper sources for evidence owned by another submission."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PROHIBITED = {
    "icbinb-bio": {
        "text": {
            "attention-head": re.compile(r"attention[- ]head", re.IGNORECASE),
            "contact-enriched": re.compile(r"contact[- ]enrich", re.IGNORECASE),
            "catalytic": re.compile(r"\bcatalytic\b|\bdlkcat\b", re.IGNORECASE),
        },
        "filenames": {
            "fig1_dose_response.pdf",
            "fig2_proxy_vs_effect.pdf",
            "fig3_seed_robustness.pdf",
        },
    },
    "interp4discovery": {
        "text": {
            "activation-steering": re.compile(
                r"activation[- ]steering|steering direction|steering vector",
                re.IGNORECASE,
            ),
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


def find_violations(paper: str, root: Path) -> list[str]:
    if paper not in PROHIBITED:
        raise ValueError(f"unknown paper: {paper}")
    if not root.is_dir():
        raise ValueError(f"package root is not a directory: {root}")

    violations: list[str] = []
    rules = PROHIBITED[paper]
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if path.name in rules["filenames"]:
            violations.append(f"{relative}: prohibited historical figure")
        if path.suffix.lower() not in {".tex", ".md"}:
            continue
        text = path.read_text(encoding="utf-8")
        for name, pattern in rules["text"].items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                violations.append(f"{relative}:{line}: prohibited {name} evidence")
    return violations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", choices=sorted(PROHIBITED), required=True)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()

    violations = find_violations(args.paper, args.root)
    for violation in violations:
        print(violation)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
