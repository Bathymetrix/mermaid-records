#!/bin/sh
set -eu

ROOT_DIR=$(
    CDPATH= cd -- "$(dirname -- "$0")/.." && pwd
)

cleanup_dirs=""

cleanup() {
    for dir in $cleanup_dirs; do
        rm -rf "$dir"
    done
}

trap cleanup EXIT INT TERM

run_fast_check() {
    if [ ! -x "$ROOT_DIR/.venv/bin/python" ]; then
        echo "error: expected $ROOT_DIR/.venv/bin/python for the default fast check" >&2
        echo "hint: run scripts/check_pre_push.sh --ci or pass explicit Python interpreters" >&2
        exit 1
    fi

    echo "Running fast pre-push check with .venv..."
    "$ROOT_DIR/.venv/bin/python" -m pytest -q
}

run_ci_check_for_python() {
    python_cmd=$1

    if ! command -v "$python_cmd" >/dev/null 2>&1; then
        echo "error: missing interpreter: $python_cmd" >&2
        exit 1
    fi

    work_dir=$(mktemp -d "${TMPDIR:-/tmp}/mermaid-records-ci.XXXXXX")
    cleanup_dirs="$cleanup_dirs $work_dir"
    venv_dir="$work_dir/venv"
    python_path="$venv_dir/bin/python"

    echo "Running CI-style check with $python_cmd..."
    "$python_cmd" -m venv "$venv_dir"
    "$python_path" -m pip install --upgrade pip
    "$python_path" -m pip install -e "$ROOT_DIR"
    "$python_path" -m pip install pytest
    "$python_path" -m pytest -q
}

if [ $# -eq 0 ]; then
    run_fast_check
    exit 0
fi

if [ "$1" = "--ci" ]; then
    shift
    if [ $# -eq 0 ]; then
        set -- python3.12 python3.13 python3.14
    fi
fi

for python_cmd in "$@"; do
    run_ci_check_for_python "$python_cmd"
done
