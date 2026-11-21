#!/usr/bin/env bash
# Run one ty build on a project with one environment and keep the raw output.
#
# Usage: run_ty.sh <ty-binary> <env-name> <label> <source-root> <exclude-glob>
#
# Run it from the repository directory. The source root is also passed as an extra
# search path, because the project's first-party imports are rooted there. Writes $SCRATCH/runs/<label>.txt. The raw
# output names files and identifiers, so it must never leave the scratchpad.
set -uo pipefail

: "${SCRATCH:?set SCRATCH to the session scratchpad}"
ty_binary=$1
env_name=$2
label=$3
source_root=$4
exclude_glob=$5

mkdir -p "$SCRATCH/runs"
"$ty_binary" check "$source_root" \
    --python "$SCRATCH/envs/$env_name" \
    --extra-search-path "$source_root" \
    --exclude "$exclude_glob" \
    --output-format concise \
    >"$SCRATCH/runs/$label.txt" 2>"$SCRATCH/runs/$label.stderr"
status=$?
# ty exits with 1 when it reports diagnostics; anything higher is a crash.
if [ "$status" -gt 1 ]; then
    echo "ty exited with status $status; see $SCRATCH/runs/$label.stderr" >&2
    exit "$status"
fi
wc -l <"$SCRATCH/runs/$label.txt"
