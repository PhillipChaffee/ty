#!/usr/bin/env python3
"""Summarize a ty run as counts per rule.

Usage: summarize.py <label> [<baseline-label>]

Reads $SCRATCH/runs/<label>.txt, as written by run_ty.sh, and prints Markdown
tables. The output holds counts only: it never prints a file path, an identifier
from the checked project, or source text.

Imports of the packages left out of the environment are reported on their own
line and excluded from every other number. Their top-level module names are read
from $SCRATCH/skipped-modules.txt (one per line), which stays out of git.
"""

from __future__ import annotations

import os
import re
import sys
from collections import Counter
from pathlib import Path

SCRATCH = Path(os.environ["SCRATCH"])

# `path:line:column: error[rule-name] message`
DIAGNOSTIC = re.compile(r"^(?P<path>.+?):\d+:\d+: (?P<level>\w+)\[(?P<rule>[\w-]+)\] (?P<message>.*)$")
MISSING_ATTRIBUTE = re.compile(r"(?:has no attribute|Unresolved attribute) `(?P<name>[^`]+)`")
UNRESOLVED_IMPORT = re.compile(r"Cannot resolve imported module `(?P<module>[^`]+)`")

ATTRIBUTE_SHAPES = ["*_set", "*_id", "*_ptr", "get_*_display", "objects", "other"]


def attribute_shape(name: str) -> str:
    if name == "objects":
        return "objects"
    if name.endswith("_set"):
        return "*_set"
    if name.endswith("_id"):
        return "*_id"
    if name.endswith("_ptr"):
        return "*_ptr"
    if re.fullmatch(r"get_\w+_display", name):
        return "get_*_display"
    return "other"


class Summary:
    def __init__(self, label: str) -> None:
        skipped_file = SCRATCH / "skipped-modules.txt"
        skipped = set(skipped_file.read_text().split()) if skipped_file.exists() else set()

        self.rules: Counter[str] = Counter()
        self.shapes: Counter[str] = Counter()
        self.skipped_imports = 0
        self.unparsed = 0

        for line in (SCRATCH / "runs" / f"{label}.txt").read_text().splitlines():
            match = DIAGNOSTIC.match(line)
            if match is None:
                # The last lines of the output are a total, not a diagnostic.
                if line and not line.startswith(("Found ", "All checks passed")):
                    self.unparsed += 1
                continue
            rule, message = match["rule"], match["message"]
            if rule == "import-not-found":
                imported = UNRESOLVED_IMPORT.search(message)
                if imported and imported["module"].split(".")[0] in skipped:
                    self.skipped_imports += 1
                    continue
            self.rules[rule] += 1
            if rule == "missing-attribute":
                attribute = MISSING_ATTRIBUTE.search(message)
                self.shapes[attribute_shape(attribute["name"]) if attribute else "other"] += 1


def table(title: str, keys: list[str], current: Counter[str], baseline: Counter[str] | None) -> None:
    header = f"| {title} | Count |" + (" Baseline | Delta |" if baseline is not None else "")
    print(header)
    print("|---|---:|" + ("---:|---:|" if baseline is not None else ""))
    for key in keys:
        row = f"| `{key}` | {current[key]} |"
        if baseline is not None:
            row += f" {baseline[key]} | {current[key] - baseline[key]:+d} |"
        print(row)
    total = f"| **Total** | {sum(current.values())} |"
    if baseline is not None:
        total += f" {sum(baseline.values())} | {sum(current.values()) - sum(baseline.values()):+d} |"
    print(total)
    print()


def main() -> None:
    label = sys.argv[1]
    baseline_label = sys.argv[2] if len(sys.argv) > 2 else None
    current = Summary(label)
    baseline = Summary(baseline_label) if baseline_label else None

    print(f"### `{label}`" + (f" against `{baseline_label}`" if baseline_label else ""))
    print()
    rules = set(current.rules) | (set(baseline.rules) if baseline else set())
    ordered = sorted(rules, key=lambda rule: (-current.rules[rule], rule))
    table("Rule", ordered, current.rules, baseline.rules if baseline else None)
    table(
        "`missing-attribute` name",
        ATTRIBUTE_SHAPES,
        current.shapes,
        baseline.shapes if baseline else None,
    )
    print(
        f"`import-not-found` for packages left out of the environment: {current.skipped_imports}"
        + (f" (baseline {baseline.skipped_imports})" if baseline else "")
    )
    if current.unparsed:
        print(f"\nLines that are not diagnostics: {current.unparsed}")
    print()


if __name__ == "__main__":
    main()
