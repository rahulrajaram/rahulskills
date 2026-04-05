#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=""
ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-root)
      PROJECT_ROOT="$2"
      shift 2
      ;;
    *)
      ARGS+=("$1")
      shift
      ;;
  esac
done

if [[ "${#ARGS[@]}" -eq 0 ]]; then
  echo "usage: yarli-enqueue-tranche.sh [--project-root DIR] --key KEY --summary \"Summary\" [other yarli plan tranche add flags]" >&2
  exit 2
fi

if ! command -v yarli >/dev/null 2>&1; then
  echo "yarli command not found in PATH" >&2
  exit 127
fi

if [[ -n "${PROJECT_ROOT}" ]]; then
  cd "${PROJECT_ROOT}"
fi

exec yarli plan tranche add --idempotent "${ARGS[@]}"
