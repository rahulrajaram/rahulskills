---
name: yarli-introspect
description: Live introspection of running or completed yarli runs — process health, tranche progress, backend output analysis, stuck detection, and actionable recommendations.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---

# Yarli Run Introspection

Use this skill when the user asks to check a yarli run's health, diagnose a stuck process, or understand what a running/completed yarli session is doing.

**Trigger phrases:** `/yarli-introspect`, "check yarli run", "yarli status", "is yarli stuck", "introspect run"

## What this skill does

1. **Discover context** — finds `.yarli/` by walking up from CWD, reads `continuation.json` and `tranches.toml`
2. **Process health** — checks `ps aux` for yarli/codex PIDs, reports elapsed time, CPU%, RSS
3. **Run state** — parses continuation.json for run_id, objective, task summary, exit state
4. **Tranche progress** — counts complete vs incomplete tranches, identifies current
5. **Backend output analysis** — if a codex session log exists, extracts:
   - Total token usage (input/output/cached)
   - Context compaction count
   - Commands executed count
   - Last N agent messages
   - Time since last activity
6. **Worktree inspection** — checks worktree dirs for `git status --short` and `git diff --stat`
7. **Health assessment** — classifies run as healthy / degraded / stuck:
   - 0 commands in >30min = stuck
   - >50 context compactions = likely looping
   - Token burn rate vs progress made
8. **Recommendations** — suggests actions (kill, let run, adjust timeout config)

## Data sources

| Source | Path | What it provides |
|--------|------|-----------------|
| continuation.json | `.yarli/continuation.json` | Run ID, objective, exit state, task summary, next tranche, config snapshot |
| tranches.toml | `.yarli/tranches.toml` | All tranches with status (complete/incomplete/blocked) |
| Audit log | `.yarl/audit.jsonl` | Structured audit events |
| Run artifacts | `.yarl/runs/{run_id}.jsonl` | Per-run backend output |
| Codex session logs | `~/.codex/sessions/YYYY/MM/DD/*.jsonl` | Token counts, context compactions, commands, agent messages |
| Worktree state | `~/Documents/worktree/yarli/run-{id}/` | Parallel workspace directories |
| Process table | `ps aux` | Running yarli/codex PIDs, elapsed time, CPU/RSS |
| CLI commands | `yarli run status`, `yarli run explain-exit` | Rich run/task state |

## Workflow

Run the data-gathering script, then analyze its output:

```bash
bash /home/rahul/.agents/skills/yarli-introspect/scripts/introspect.sh [run_id]
```

Parse the script output, then provide:

1. **Status summary** — one-line health verdict (Healthy / Degraded / Stuck / Completed / Failed)
2. **Tranche progress bar** — `[=========>       ] 21/29 tranches`
3. **Active processes** — table of yarli/codex PIDs with elapsed time and resource usage
4. **Current task** — what task is executing and what it's doing
5. **Token economy** — total tokens burned, burn rate, tokens per completed tranche
6. **Stuck indicators** — if any:
   - Context compaction count (>50 = looping)
   - Time since last shell command
   - Time since last file change
   - Commands executed count
7. **Recommendations** — kill PID, adjust config, wait, etc.

## Stuck detection heuristics

A run is **stuck** when any of:
- Codex process has >50 context compactions AND 0 shell commands executed
- No file changes in worktree for >30 minutes while process is running
- Token input >100M with 0 shell commands (read-think-compact-forget loop)
- Process CPU% is near zero but elapsed time is >60 minutes

A run is **degraded** when any of:
- >20 context compactions but some commands executed
- Token burn rate >1M/min with low commit rate
- Multiple failed task attempts visible in continuation.json
