#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-}"
if [[ -z "${PROJECT_ROOT}" ]]; then
  PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi
PROJECT_ROOT="$(cd "${PROJECT_ROOT}" && pwd)"

YARLI_DIR="${PROJECT_ROOT}/.yarli"
CONTINUATION_FILE="${YARLI_DIR}/continuation.json"
TRANCHES_FILE="${YARLI_DIR}/tranches.toml"

echo "=== YARLI EXECUTION LOOP INSPECT ==="
echo "project_root: ${PROJECT_ROOT}"
echo "timestamp: $(date -Iseconds)"
echo

echo "=== FILES ==="
echo "continuation_file: ${CONTINUATION_FILE}"
echo "tranches_file: ${TRANCHES_FILE}"
echo

echo "=== CONTINUATION ==="
if [[ -f "${CONTINUATION_FILE}" ]]; then
  python3 - "${CONTINUATION_FILE}" "${TRANCHES_FILE}" <<'PY'
import json
import os
import sys

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

continuation_path = sys.argv[1]
tranches_path = sys.argv[2]

with open(continuation_path, "r", encoding="utf-8") as handle:
    payload = json.load(handle)

next_tranche = payload.get("next_tranche") or {}
config_snapshot = next_tranche.get("config_snapshot") or {}
runtime = config_snapshot.get("runtime") or {}
tranche_plan = runtime.get("tranche_plan") or []
snapshot_keys = [
    item.get("key")
    for item in tranche_plan
    if isinstance(item, dict)
    and item.get("key")
    and item.get("key", "").lower() not in {"prompt", "verification"}
]

current_open = []
if os.path.exists(tranches_path):
    with open(tranches_path, "rb") as handle:
        tranches = tomllib.load(handle)
    for item in tranches.get("tranches", []):
        if item.get("status") != "complete" and item.get("key"):
            current_open.append(item["key"])

missing = [key for key in current_open if key not in snapshot_keys]
summary = payload.get("summary") or {}

print("run_id:", payload.get("run_id", "N/A"))
print("objective:", payload.get("objective", "N/A"))
print("exit_state:", payload.get("exit_state", "N/A"))
print("exit_reason:", payload.get("exit_reason", "N/A"))
print("next_tranche_kind:", next_tranche.get("kind", "N/A"))
print("next_tranche_key:", next_tranche.get("planned_tranche_key", "N/A"))
print("next_tranche_objective:", next_tranche.get("suggested_objective", "N/A"))
print(
    "task_summary:",
    "total={total} completed={completed} failed={failed} cancelled={cancelled} pending={pending}".format(
        total=summary.get("total", "?"),
        completed=summary.get("completed", "?"),
        failed=summary.get("failed", "?"),
        cancelled=summary.get("cancelled", "?"),
        pending=summary.get("pending", "?"),
    ),
)
print("continuation_snapshot_keys:", ",".join(snapshot_keys) if snapshot_keys else "-")
print("continuation_drift_keys:", ",".join(missing) if missing else "-")
PY
else
  echo "(no continuation.json found)"
fi
echo

echo "=== TRANCHES ==="
if [[ -f "${TRANCHES_FILE}" ]]; then
  python3 - "${TRANCHES_FILE}" <<'PY'
import sys

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

with open(sys.argv[1], "rb") as handle:
    data = tomllib.load(handle)

tranches = data.get("tranches", [])
counts = {"complete": 0, "incomplete": 0, "blocked": 0, "other": 0}
open_keys = []
for item in tranches:
    status = item.get("status", "other")
    if status in counts:
        counts[status] += 1
    else:
        counts["other"] += 1
    if status != "complete" and item.get("key"):
        open_keys.append(item["key"])

print("total:", len(tranches))
print("complete:", counts["complete"])
print("incomplete:", counts["incomplete"])
print("blocked:", counts["blocked"])
if counts["other"]:
    print("other:", counts["other"])
print("open_keys:", ",".join(open_keys) if open_keys else "-")
PY
else
  echo "(no tranches.toml found)"
fi
echo

RUN_ID=""
if [[ -f "${CONTINUATION_FILE}" ]]; then
  RUN_ID="$(python3 - "${CONTINUATION_FILE}" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    payload = json.load(handle)

print(payload.get("run_id", ""))
PY
)"
fi

if command -v yarli >/dev/null 2>&1 && [[ -n "${RUN_ID}" ]]; then
  echo "=== YARLI RUN STATUS ==="
  (cd "${PROJECT_ROOT}" && yarli run status "${RUN_ID}") || true
  echo
  echo "=== YARLI RUN EXPLAIN EXIT ==="
  (cd "${PROJECT_ROOT}" && yarli run explain-exit "${RUN_ID}") || true
  echo
else
  echo "=== YARLI CLI ==="
  echo "(yarli command unavailable or no run_id found)"
  echo
fi

STALE_CHECK_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/yarli-remediate-stale-runs.sh"
if command -v yarli >/dev/null 2>&1 && [[ -x "${STALE_CHECK_SCRIPT}" ]]; then
  echo "=== STALE ACTIVE RUN CHECK ==="
  (cd "${PROJECT_ROOT}" && "${STALE_CHECK_SCRIPT}" "${PROJECT_ROOT}" --dry-run) || true
  echo
fi

echo "=== END INSPECT ==="
