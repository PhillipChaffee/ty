#!/usr/bin/env python3
"""Count uses of Django features in a project, by regular expression.

Usage: census.py <repo-dir> <source-root> <exclude-glob>

Prints a Markdown table of counts. The patterns are textual, so the numbers are
approximate: they count occurrences, including ones in tests and comments. The
output never names a file or an identifier from the project.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RELATION = r"\b(?:ForeignKey|OneToOneField)\(\s*"

PATTERNS = {
    "`ForeignKey(`/`OneToOneField(` with a class target": RELATION + r"(?!to=)[A-Za-z_][\w.]*\s*[,)]",
    '`ForeignKey(`/`OneToOneField(` with a string target': RELATION + r"""(?:to=)?["'](?!self["'])""",
    '`ForeignKey(`/`OneToOneField(` with `"self"`': RELATION + r"""(?:to=)?["']self["']""",
    "`related_name=`": r"\brelated_name\s*=",
    "`ManyToManyField(`": r"\bManyToManyField\(",
    "`through=`": r"\bthrough\s*=",
    "`objects = ` custom managers": r"^\s+objects\s*(?::[^=]+)?=\s*(?!models\.Manager\(\))\S",
    "`.as_manager()`": r"\.as_manager\(\)",
    "`from_queryset(`": r"\bfrom_queryset\(",
    "`.values(`": r"\.values\(",
    "`.values_list(`": r"\.values_list\(",
    "`.annotate(`": r"\.annotate\(",
    "`get_user_model(`": r"\bget_user_model\(",
    "`request.user`": r"\brequest\.user\b",
    "`settings.`": r"\bsettings\.[A-Z_]",
    "`TextChoices`/`IntegerChoices`": r"\b(?:TextChoices|IntegerChoices)\b",
    "`parent_link=`": r"\bparent_link\s*=",
    "`abstract = True`": r"^\s+abstract\s*=\s*True",
    "`proxy = True`": r"^\s+proxy\s*=\s*True",
}


def main() -> None:
    repo_dir, source_root, exclude_glob = sys.argv[1:]
    root = Path(repo_dir) / source_root
    files = [path for path in root.rglob("*.py") if not path.relative_to(root).match(exclude_glob)]
    counts = dict.fromkeys(PATTERNS, 0)
    compiled = {name: re.compile(pattern, re.MULTILINE) for name, pattern in PATTERNS.items()}
    for path in files:
        text = path.read_text(errors="replace")
        for name, pattern in compiled.items():
            counts[name] += len(pattern.findall(text))

    print("| Feature | Occurrences |")
    print("|---|---:|")
    print(f"| Python files scanned | {len(files)} |")
    for name, count in counts.items():
        print(f"| {name} | {count} |")


if __name__ == "__main__":
    main()
