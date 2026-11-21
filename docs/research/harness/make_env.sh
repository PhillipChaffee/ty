#!/usr/bin/env bash
# Build a virtual environment for measuring ty on a Django project.
#
# Usage: make_env.sh <repo-dir> <name> <stub-requirement> <skip-list-file>
#
# Creates $SCRATCH/envs/<name> with the Python version the project pins and the
# packages in its poetry.lock at their locked versions, minus every Django stub
# package and minus the packages named in <skip-list-file> (one name per line,
# kept outside git), plus <stub-requirement>.
set -euo pipefail

: "${SCRATCH:?set SCRATCH to the session scratchpad}"
repo_dir=$1
name=$2
stub_requirement=$3
skip_list=$4

env_dir="$SCRATCH/envs/$name"
requirements="$SCRATCH/envs/$name.requirements.txt"
mkdir -p "$SCRATCH/envs"

python_version=$(python3 - "$repo_dir" "$skip_list" "$requirements" <<'PY'
import re
import sys
import tomllib
from pathlib import Path

repo_dir, skip_list, requirements = sys.argv[1:]

DJANGO_STUBS = {
    "django-stubs",
    "django-stubs-ext",
    "django-types",
    "djangorestframework-stubs",
    "djangorestframework-types",
}


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


skipped = {
    normalize(line.strip())
    for line in Path(skip_list).read_text().splitlines()
    if line.strip() and not line.startswith("#")
}
lock = tomllib.loads((Path(repo_dir) / "poetry.lock").read_text())
lines = [
    f"{package['name']}=={package['version']}"
    for package in lock["package"]
    if normalize(package["name"]) not in skipped | DJANGO_STUBS
]
Path(requirements).write_text("\n".join(lines) + "\n")

project = tomllib.loads((Path(repo_dir) / "pyproject.toml").read_text())
pinned = project["tool"]["poetry"]["dependencies"]["python"]
print(re.sub(r"^[^0-9]*", "", pinned))
PY
)

uv venv --quiet --clear --python "$python_version" "$env_dir"
# The locked versions already form a consistent set, so skip resolution. This also
# keeps the skipped packages from being pulled back in as dependencies.
uv pip install --quiet --python "$env_dir" --no-deps -r "$requirements"
# Resolve the stub package's own dependencies, but never move a locked package.
uv pip install --quiet --python "$env_dir" --constraint "$requirements" "$stub_requirement"

uv pip list --python "$env_dir" --format freeze \
    | grep -i -E '^(django|django[-_]stubs.*|django[-_]types|djangorestframework[-_](stubs|types))(==| @)' || true
