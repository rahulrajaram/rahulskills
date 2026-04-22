---
name: yarli-execution-loop
description: Inspect Yarli state, supervise active runs, durably enqueue new tranches, and choose the right relaunch path without handing off control of the loop.
argument-hint: "[project-root]"
---

# Yarli Execution Loop

Use this skill when the user wants an agent to monitor Yarli, queue newly discovered work durably, and keep execution moving without losing state or giving up supervision.

## Outcomes

- Inspect the current Yarli run and plan state before acting.
- Enqueue new work durably in `.yarli/tranches.toml`.
- Keep the agent as the active supervisor of the loop; repo scripts are actuators, not replacement judgment.
- Monitor active runs on a 60-second cadence and report only deltas.
- Use the repo-local Yarli supervisor only as a one-shot launcher or resumer when present.
- Fall back to manual `yarli run`, `yarli run continue`, or `yarli run --fresh-from-tranches` only when no supervisor exists or an exceptional condition needs agent judgment.
- End each cycle with a plain-text decision block that another agent or shell can follow.

## Core Tenets

- Treat Yarli as the durable control plane. Agent scratchpad is never the queue.
- The agent remains the supervisor even when a repo-local `scripts/yarli_supervisor.py` exists.
- Separate discovering work from executing work.
- New work must become an explicit tranche with `key`, `summary`, `allowed_paths`, `verify`, `done_when`, and optional `max_tokens`.
- Use `yarli run continue` only for work already owned by the continuation snapshot and only when no drift is present.
- Use `yarli run --fresh-from-tranches` after new tranche enqueue or other live-plan changes.
- Treat refusal as non-terminal. Convert it into a narrowed retry, a follow-up tranche enqueue, or stop-and-summarize.
- Re-inspect Yarli state after each material execution step.
- Record notable interventions, cancellations, or repeated failures into memory/checkpoints when those tools are available.

## Step 1: Inspect State

Run the helper script:

```bash
bash "$SKILL_DIR/scripts/yarli-loop-inspect.sh" [project-root]
```

Review:

- current repository root
- `.yarli/continuation.json`
- `.yarli/tranches.toml`
- continuation snapshot keys versus current open tranche keys
- `yarli run status` and `yarli run explain-exit` output when a run ID is available
- active-process health when a run is already live

## Step 2: Enqueue New Work Durably

Use the enqueue wrapper instead of ad hoc prose:

```bash
bash "$SKILL_DIR/scripts/yarli-enqueue-tranche.sh" \
  --project-root <project-root> \
  --key TP-05 \
  --summary "Implement config loader hardening" \
  --allowed-paths crates/yarli-cli/src \
  --verify "cargo test -p yarli --bin yarli cli_parses_" \
  --done-when "fresh-versus-continue workflow is documented and tested"
```

This wrapper always uses `yarli plan tranche add --idempotent`.

If the tranche key already exists with different effective fields, stop and report the mismatch instead of silently mutating scope.

## Step 3: Agent-As-Supervisor Mode

If a Yarli run is already active, do not relaunch immediately. Start a monitoring loop first:

```bash
bash "$SKILL_DIR/scripts/yarli-loop-watch.sh" [project-root] [interval-seconds]
```

Default to `60` seconds between checks. While monitoring:

- summarize only deltas: tranche transitions, repeated retries, verification start or finish, blocked state, and completion
- avoid dumping raw tails unless the user asks for them
- keep watching while the run is still healthy and making progress
- re-inspect with a deeper pulse check before deciding the run is stuck

The repo-local supervisor is not the supervisor in this mode. The agent owns cadence, interpretation, intervention, and user-facing updates.

## Step 4: One-Shot Launch Or Resume

If no run is active and the repository provides `scripts/yarli_supervisor.py`, prefer the wrapper:

```bash
bash "$SKILL_DIR/scripts/yarli-loop-supervise.sh" [project-root]
```

This wrapper must perform at most one top-level launch by default and then return control to the agent. Use it only when:

- no run is currently active
- no tranche mismatch needs to be resolved first
- no architectural or refusal-recovery intervention is required yet

The repo-local supervisor is an actuator for ordinary launch policy, not a replacement supervisor.

## Step 5: Fallback Manual Execution Path

- No continuation and no active run context: use `yarli run`.
- Continuation exists, no drift is reported, and the remaining work belongs to the continuation snapshot: use `yarli run continue`.
- Drift is reported, or you just enqueued new tranches, or live plan state changed after the previous run started: use `yarli run --fresh-from-tranches`.
- If prompt selection matters, add `--prompt-file <path>` to `yarli run` or `yarli run --fresh-from-tranches`.

Use this fallback only when the repo-local supervisor does not exist, or when you intentionally need to override it for an exceptional case.

## Step 6: Intervention Heuristics

- After `3` quiet ticks with no tranche change, run a deeper pulse check: run list, process health, `yarli run explain-exit` when applicable, and the latest meaningful log notes.
- If the same verification or helper command fails `2` times, inspect the exact failure before retrying again.
- If the same tranche stays active for more than `10` minutes with no edit, verification, or worker-note movement, classify it as `slow`.
- If the active process disappears without a matching completion or cancellation update, inspect before relaunching.
- If blocked or no-eligible-tranche conditions appear, stop and summarize instead of thrashing.

## Step 7: Intervention Ladder

1. Inspect live state.
2. Inspect process health, log tail, and `yarli run explain-exit` when relevant.
3. Classify the loop as `healthy`, `slow`, `stuck`, `blocked`, or `idle`.
4. Choose exactly one action: keep watching, narrow a retry, enqueue a follow-up tranche, do one launch, use `fresh-from-tranches`, or stop-and-summarize.

Do not relaunch while a healthy active run is still making progress.

## Step 8: Refusal Recovery

- Narrow scope once: reduce objective, allowed paths, or verification command size.
- If the work clearly needs decomposition, enqueue a follow-up tranche immediately.
- If execution should stop, produce a stop-and-summarize handoff with the next recommended Yarli command.

Do not end a cycle with an unstructured refusal and no next step.

## Backend Notes

- For Codex-specific operating hints, read `references/codex.md`.
- For Claude-specific operating hints, read `references/claude.md`.
- Do not duplicate the core workflow in backend notes.

## Output Contract

End every cycle with this plain-text block:

```text
YARLI_DECISION_V1
run_id: <id or none>
active_tranche: <key or none>
last_completed_tranche: <key or none>
health: healthy|slow|stuck|blocked|idle
status: watch|continue|fresh-from-tranches|enqueued|stop-and-summarize
reason: <one concise sentence>
action_taken: <one concise sentence>
enqueued_tranches: <comma-separated keys or none>
next_check_at: <ISO-8601 timestamp or none>
next_command: <single command or none>
```
