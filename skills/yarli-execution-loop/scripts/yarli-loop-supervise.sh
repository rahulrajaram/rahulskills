#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-}"
if [[ -z "${PROJECT_ROOT}" ]]; then
  PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
else
  shift
fi
PROJECT_ROOT="$(cd "${PROJECT_ROOT}" && pwd)"

SUPERVISOR="${PROJECT_ROOT}/scripts/yarli_supervisor.py"
STALE_REMEDIATION="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/yarli-remediate-stale-runs.sh"

if [[ ! -f "${SUPERVISOR}" ]]; then
  echo "repo-local Yarli supervisor not found at ${SUPERVISOR}" >&2
  exit 3
fi

if [[ -x "${STALE_REMEDIATION}" ]]; then
  "${STALE_REMEDIATION}" "${PROJECT_ROOT}" --fix
fi

HAS_MAX_LAUNCHES=0
for arg in "$@"; do
  if [[ "${arg}" == "--max-launches" || "${arg}" == --max-launches=* ]]; then
    HAS_MAX_LAUNCHES=1
    break
  fi
done

if [[ "${HAS_MAX_LAUNCHES}" -eq 0 ]]; then
  set -- --max-launches 1 "$@"
fi

exec python3 "${SUPERVISOR}" --project-root "${PROJECT_ROOT}" "$@"
