#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-}"
if [[ -z "${PROJECT_ROOT}" ]]; then
  PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
else
  shift
fi
PROJECT_ROOT="$(cd "${PROJECT_ROOT}" && pwd)"

INTERVAL="60"
ONCE="0"
for arg in "$@"; do
  if [[ "${arg}" == "--once" ]]; then
    ONCE="1"
  else
    INTERVAL="${arg}"
  fi
done

LOG_PATH=""
if [[ -f "${PROJECT_ROOT}/.yarl/yarli-supervisor.log" ]]; then
  LOG_PATH="${PROJECT_ROOT}/.yarl/yarli-supervisor.log"
elif [[ -f "${PROJECT_ROOT}/.yarli/yarli-supervisor.log" ]]; then
  LOG_PATH="${PROJECT_ROOT}/.yarli/yarli-supervisor.log"
fi

STALE_CHECK_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/yarli-remediate-stale-runs.sh"

while true; do
  printf '\n=== %s ===\n' "$(date -Iseconds)"
  printf 'active: '
  (
    cd "${PROJECT_ROOT}"
    yarli run list | awk '/RunActive/ {print $0; found=1} END {if (!found) print "none"}'
  )
  printf 'last done: '
  (
    cd "${PROJECT_ROOT}"
    yarli run list | awk '/RunCompleted/ {line=$0} END {if (line) print line; else print "none"}'
  )
  printf 'proc: '
  pgrep -af 'yarli run --fresh-from-tranches --stream|yarli run continue --stream|yarli run --stream' | head -n 1 || true
  echo
  printf 'stale: '
  if [[ -x "${STALE_CHECK_SCRIPT}" ]]; then
    (
      cd "${PROJECT_ROOT}"
      "${STALE_CHECK_SCRIPT}" "${PROJECT_ROOT}" --dry-run \
        | awk '/^stale_run_detected:/ {print; found=1} /^stale_runs_detected:/ {summary=$0} END {if (found) exit 0; if (summary) print summary; else print "unknown"}'
    )
  else
    echo "stale checker unavailable"
  fi
  echo 'latest note:'
  if [[ -n "${LOG_PATH}" && -f "${LOG_PATH}" ]]; then
    tac "${LOG_PATH}" | awk '($0 !~ /shell: /) && ($0 !~ /command started/) && ($0 !~ /Reading additional input/) && ($0 !~ /^$/) {print; count++; if (count==3) exit}'
  else
    echo "no supervisor log found"
  fi
  if [[ "${ONCE}" == "1" ]]; then
    exit 0
  fi
  sleep "${INTERVAL}"
done
