#!/usr/bin/env bash
# yarli-introspect data gatherer
# Usage: introspect.sh [run_id]
# Collects raw data for analysis by the AI agent.

set -euo pipefail

RUN_ID="${1:-}"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
YARLI_DIR="${PROJECT_ROOT}/.yarli"
YARL_DIR="${PROJECT_ROOT}/.yarl"
WORKTREE_ROOT="${HOME}/Documents/worktree/yarli"
CODEX_SESSIONS="${HOME}/.codex/sessions"

echo "=== YARLI INTROSPECTION ==="
echo "project_root: ${PROJECT_ROOT}"
echo "timestamp: $(date -Iseconds)"
echo ""

# --- 1. Process health ---
echo "=== PROCESS HEALTH ==="
ps aux --no-headers 2>/dev/null | grep -E '(yarli|codex)' | grep -v grep || echo "(no yarli/codex processes found)"
echo ""

# --- 2. Continuation state ---
echo "=== CONTINUATION STATE ==="
CONT="${YARLI_DIR}/continuation.json"
if [ -f "${CONT}" ]; then
    # Extract key fields with python for reliable JSON parsing
    python3 -c "
import json, sys
with open('${CONT}') as f:
    data = json.load(f)
print('run_id:', data.get('run_id', 'N/A'))
print('objective:', (data.get('objective', 'N/A') or 'N/A')[:120])
print('exit_state:', data.get('exit_state', 'N/A'))
print('exit_reason:', data.get('exit_reason', 'N/A'))
print('completed_at:', data.get('completed_at', 'N/A'))
print('next_tranche:', data.get('next_tranche', 'N/A'))
summary = data.get('summary', {})
print('task_summary: total=%s completed=%s failed=%s cancelled=%s pending=%s' % (
    summary.get('total', '?'), summary.get('completed', '?'),
    summary.get('failed', '?'), summary.get('cancelled', '?'),
    summary.get('pending', '?')
))
qg = data.get('quality_gate', {})
if qg:
    print('quality_gate: allow_auto_advance=%s trend=%s score=%s action=%s' % (
        qg.get('allow_auto_advance', '?'), qg.get('trend', '?'),
        qg.get('score', '?'), qg.get('task_health_action', '?')
    ))
tasks = data.get('tasks', [])
for t in tasks[-5:]:
    print('  task: key=%s state=%s attempt=%s error=%s' % (
        t.get('task_key', '?'), t.get('state', '?'),
        t.get('attempt_no', '?'), (t.get('last_error') or '-')[:80]
    ))
" 2>/dev/null || echo "(failed to parse continuation.json)"
else
    echo "(no continuation.json found)"
fi
echo ""

# --- 3. Tranche progress ---
echo "=== TRANCHE PROGRESS ==="
TRANCHES="${YARLI_DIR}/tranches.toml"
if [ -f "${TRANCHES}" ]; then
    TOTAL=$(grep -c '^\[\[tranches\]\]' "${TRANCHES}" 2>/dev/null || echo 0)
    COMPLETE=$(grep -c 'status = "complete"' "${TRANCHES}" 2>/dev/null || echo 0)
    BLOCKED=$(grep -c 'status = "blocked"' "${TRANCHES}" 2>/dev/null || echo 0)
    INCOMPLETE=$(grep -c 'status = "incomplete"' "${TRANCHES}" 2>/dev/null || echo 0)
    echo "total: ${TOTAL}  complete: ${COMPLETE}  blocked: ${BLOCKED}  incomplete: ${INCOMPLETE}"
    # Show current (first incomplete) tranche
    python3 -c "
import tomllib, sys
with open('${TRANCHES}', 'rb') as f:
    data = tomllib.load(f)
for t in data.get('tranches', []):
    if t.get('status') != 'complete':
        print('current_tranche: key=%s summary=%s status=%s' % (
            t.get('key', '?'), (t.get('summary', '?') or '?')[:80], t.get('status', '?')
        ))
        break
" 2>/dev/null || true
else
    echo "(no tranches.toml found)"
fi
echo ""

# --- 4. Codex session logs ---
echo "=== CODEX SESSION ANALYSIS ==="
TODAY=$(date +%Y/%m/%d)
YESTERDAY=$(date -d 'yesterday' +%Y/%m/%d 2>/dev/null || date -v-1d +%Y/%m/%d 2>/dev/null || echo "")
LATEST_SESSION=""
for DIR in "${CODEX_SESSIONS}/${TODAY}" "${CODEX_SESSIONS}/${YESTERDAY}"; do
    if [ -d "${DIR}" ]; then
        FOUND=$(ls -t "${DIR}"/*.jsonl 2>/dev/null | head -1)
        if [ -n "${FOUND}" ]; then
            LATEST_SESSION="${FOUND}"
            break
        fi
    fi
done

if [ -n "${LATEST_SESSION}" ]; then
    echo "session_file: ${LATEST_SESSION}"
    echo "session_size: $(du -h "${LATEST_SESSION}" | cut -f1)"
    # Count key metrics
    COMPACTIONS=$(grep -c '"type":"context_compaction"' "${LATEST_SESSION}" 2>/dev/null || \
                  grep -c 'context.compaction\|context_compaction\|compacted' "${LATEST_SESSION}" 2>/dev/null || echo 0)
    COMMANDS=$(grep -c '"type":"shell_command"\|"type":"command"' "${LATEST_SESSION}" 2>/dev/null || \
               grep -c 'exec\|shell_command\|command_run' "${LATEST_SESSION}" 2>/dev/null || echo 0)
    echo "context_compactions: ${COMPACTIONS}"
    echo "shell_commands: ${COMMANDS}"
    # Token usage from last few lines
    tail -5 "${LATEST_SESSION}" 2>/dev/null | python3 -c "
import json, sys
for line in sys.stdin:
    try:
        d = json.loads(line.strip())
        usage = d.get('usage', {})
        if usage:
            print('latest_token_usage: input=%s output=%s cached=%s total=%s' % (
                usage.get('input_tokens', '?'), usage.get('output_tokens', '?'),
                usage.get('cache_read_input_tokens', '?'), usage.get('total_tokens', '?')
            ))
    except: pass
" 2>/dev/null || true
else
    echo "(no recent codex session log found)"
fi
echo ""

# --- 5. Worktree state ---
echo "=== WORKTREE STATE ==="
if [ -d "${WORKTREE_ROOT}" ]; then
    for WD in "${WORKTREE_ROOT}"/run-*/; do
        [ -d "${WD}" ] || continue
        echo "worktree: ${WD}"
        (cd "${WD}" && git status --short 2>/dev/null | head -10) || true
        (cd "${WD}" && git diff --stat 2>/dev/null | tail -3) || true
        echo ""
    done
else
    echo "(no worktree directory found)"
fi

# --- 6. Audit log tail ---
echo "=== RECENT AUDIT EVENTS ==="
AUDIT="${YARL_DIR}/audit.jsonl"
if [ -f "${AUDIT}" ]; then
    tail -5 "${AUDIT}" 2>/dev/null | python3 -c "
import json, sys
for line in sys.stdin:
    try:
        d = json.loads(line.strip())
        print('%s | %s | %s | %s | %s' % (
            d.get('timestamp', '?')[:19],
            d.get('category', '?'),
            d.get('action', '?'),
            d.get('outcome', '?'),
            (d.get('reason', '') or '')[:60]
        ))
    except: pass
" 2>/dev/null || true
else
    echo "(no audit log found)"
fi
echo ""

echo "=== END INTROSPECTION ==="
