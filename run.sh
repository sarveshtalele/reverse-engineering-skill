#!/usr/bin/env bash
# =====================================================================
# Reverse Engineer Skill — macOS/Linux Runner
# =====================================================================
# This script runs the pipeline smoothly on Unix shells, forcing UTF-8
# and automatically selecting the correct python3 executable.
# =====================================================================

# Force UTF-8 encoding
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

# Determine python command
if command -v python3 >/dev/null 2>&1; then
    PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PY_CMD="python"
else
    echo "[error] Python 3 was not found on your system PATH." >&2
    echo "[error] Please install Python 3 before running the script." >&2
    exit 1
fi

if [ -z "$1" ]; then
    echo "[error] No GitHub URL or local path provided." >&2
    echo "Usage: ./run.sh <github-repo-url-or-local-path>" >&2
    echo "Example: ./run.sh https://github.com/spring-projects/spring-petclinic" >&2
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
"$PY_CMD" "$SCRIPT_DIR/reverse_engineer_skill.py" "$@"
