#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-}"
if [[ -z "${PROJECT_ROOT}" || "${PROJECT_ROOT}" == --* ]]; then
  PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
else
  shift
fi
PROJECT_ROOT="$(cd "${PROJECT_ROOT}" && pwd)"

MODE="dry-run"
CONFIRMED=0
MIN_AGE_SECONDS="${YARLI_STALE_RUN_MIN_AGE_SECONDS:-300}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run|--check)
      MODE="dry-run"
      shift
      ;;
    --fix)
      MODE="fix"
      shift
      ;;
    --confirmed)
      CONFIRMED=1
      shift
      ;;
    --min-age-seconds)
      MIN_AGE_SECONDS="${2:?missing value for --min-age-seconds}"
      shift 2
      ;;
    --min-age-seconds=*)
      MIN_AGE_SECONDS="${1#*=}"
      shift
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ "${MODE}" == "fix" && "${CONFIRMED}" -ne 1 ]]; then
  echo "--fix requires --confirmed after explicit user approval" >&2
  exit 2
fi

if ! command -v yarli >/dev/null 2>&1; then
  echo "yarli unavailable"
  exit 0
fi

RUN_IDS="$(
  cd "${PROJECT_ROOT}" &&
    yarli run list | awk '
      NR > 2 && ($2 == "RunActive" || $2 == "RunVerifying") { print $1 }
    '
)"

if [[ -z "${RUN_IDS}" ]]; then
  echo "stale_runs_detected: 0"
  echo "stale_runs_fixed: 0"
  exit 0
fi

export YARLI_STALE_MIN_AGE_SECONDS="${MIN_AGE_SECONDS}"

detect_run() {
  local run_id="$1"
  python3 - "${run_id}" <<'PY'
import datetime as dt
import json
import os
import re
import subprocess
import sys

run_id = sys.argv[1]
min_age_seconds = int(os.environ["YARLI_STALE_MIN_AGE_SECONDS"])

result = subprocess.run(
    ["yarli", "run", "status", run_id],
    check=False,
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    payload = {
        "run_id": run_id,
        "stale": False,
        "reason": f"status command failed: {result.stderr.strip() or result.stdout.strip()}",
    }
    print(json.dumps(payload))
    sys.exit(0)

lines = result.stdout.splitlines()
state = ""
updated = ""
workspace_dirs = []
for line in lines:
    if line.startswith("State:"):
        state = line.split(":", 1)[1].strip()
    elif line.startswith("Updated:"):
        updated = line.split(":", 1)[1].strip()
    else:
        match = re.search(r"workspace_dir:\s*(.+)$", line)
        if match:
            workspace_dirs.append(match.group(1).strip())

missing_workspace_dirs = [path for path in workspace_dirs if path and not os.path.isdir(path)]
age_seconds = None
if updated:
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            updated_dt = dt.datetime.strptime(updated, fmt)
            age_seconds = int((dt.datetime.now() - updated_dt).total_seconds())
            break
        except ValueError:
            continue

stale = bool(missing_workspace_dirs) and (
    age_seconds is None or age_seconds >= min_age_seconds
)

payload = {
    "run_id": run_id,
    "state": state or "unknown",
    "updated": updated or "unknown",
    "age_seconds": age_seconds,
    "workspace_dirs": workspace_dirs,
    "missing_workspace_dirs": missing_workspace_dirs,
    "stale": stale,
    "reason": (
        "missing workspace for active run"
        if stale
        else "workspace still present or active run too recent"
    ),
}
print(json.dumps(payload))
PY
}

DETECTED=0
FIXED=0

while IFS= read -r run_id; do
  [[ -z "${run_id}" ]] && continue
  STATUS_JSON="$(cd "${PROJECT_ROOT}" && detect_run "${run_id}")"
  STALE_FLAG="$(python3 -c 'import json,sys; print("yes" if json.load(sys.stdin).get("stale") else "no")' <<<"${STATUS_JSON}")"
  if [[ "${STALE_FLAG}" == "yes" ]]; then
    DETECTED=$((DETECTED + 1))
    STATE="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("state","unknown"))' <<<"${STATUS_JSON}")"
    AGE="$(python3 -c 'import json,sys; age=json.load(sys.stdin).get("age_seconds"); print(age if age is not None else "unknown")' <<<"${STATUS_JSON}")"
    MISSING="$(python3 -c 'import json,sys; print(",".join(json.load(sys.stdin).get("missing_workspace_dirs") or []))' <<<"${STATUS_JSON}")"
    echo "stale_run_detected: run_id=${run_id} state=${STATE} age_seconds=${AGE} missing_workspace_dirs=${MISSING}"
    if [[ "${MODE}" == "fix" ]]; then
      (
        cd "${PROJECT_ROOT}" &&
          yarli run cancel --reason "user-approved cancellation of orphaned active run with missing workspace" "${run_id}"
      )
      FIXED=$((FIXED + 1))
      echo "stale_run_fixed: run_id=${run_id}"
    fi
  fi
done <<<"${RUN_IDS}"

echo "stale_runs_detected: ${DETECTED}"
echo "stale_runs_fixed: ${FIXED}"
