---
name: yarli-execution-loop
description: Inspect Yarli state, supervise active runs, durably enqueue new tranches, and choose the right relaunch path without handing off control of the loop.
argument-hint: "[project-root]"
---

# Yarli Execution Loop

Use this skill when the user wants an agent to monitor Yarli, queue newly discovered work durably, and keep execution moving without losing state or giving up supervision.

## Autonomy Routing

Use Yarli when durable tranche state, background orchestration, or cross-shell
continuation materially helps. Do not recommend Yarli as a default replacement
for ordinary local implementation when direct execution is sufficient. If the
user explicitly invokes this skill, execute the Yarli workflow and keep
supervising until a real stop condition appears; do not ask whether to switch to
`/goal` or direct execution unless the choice changes safety, durability, shared
state, or user-visible behavior.

## Outcomes

- Inspect the current Yarli run and plan state before acting.
- Enqueue new work durably in `.yarli/tranches.toml`.
- Keep the agent as the active supervisor of the loop; repo scripts are actuators, not replacement judgment.
- Monitor active runs on a 60-second cadence and report only deltas.
- Use the repo-local Yarli supervisor only as a one-shot launcher or resumer when present.
- Fall back to manual `yarli run`, `yarli run continue`, or `yarli run --fresh-from-tranches` only when no supervisor exists or an exceptional condition needs agent judgment.
- Emit a decision block as an in-loop checkpoint, not as an automatic reason to stop supervising or return control.

## Intent Resolution

Resolve the user's intent before choosing execution behavior:

- Bare skill invocation, "keep going", "continue", "drive the loop", or equivalent means `supervise-loop`.
- "Watch", "monitor", or "keep an eye on it" means `watch-active-run`.
- "Start", "resume", or "launch" means `launch-and-supervise`, not "launch once and return", unless the user explicitly asks for one-shot behavior.
- "Inspect", "status", or "what state is it in" means `inspect-only`.
- "Queue this work" or "add tranches" means `enqueue-only` unless the user also asked to execute.

Default mode for `$yarli-execution-loop` is `supervise-loop`.

## Default Stop Rules

In `supervise-loop` mode, do not stop merely because:

- you emitted a `YARLI_DECISION_V1` block
- you launched a run successfully
- a continuation file was written
- one tranche completed successfully

After a launch or resume, stay in supervision mode until one of these is true:

- the run reaches a meaningful state change: blocked, stuck, failed, verification start/finish, or completed
- you observe `3` quiet ticks and classify the run with a deeper pulse check
- the loop becomes idle with no immediate next action
- the user explicitly asked for inspect-only or one-shot launch behavior

After a run completes successfully, re-inspect state before yielding control. If eligible work remains and no blocker or drift mismatch prevents progress, choose the next launch path in the same turn. A completed run is not, by itself, terminal for the supervisor.

In bare `$yarli-execution-loop` / `supervise-loop` mode, do not yield control back to the user while a run is `RunActive` and healthy. Keep supervising through watch ticks, pulse checks, and tranche transitions until the run becomes terminal, blocked, stuck, or idle, or until the user explicitly asks for inspect-only or one-shot behavior.

## Core Tenets

- Treat Yarli as the durable control plane. Agent scratchpad is never the queue.
- The agent remains the supervisor even when a repo-local `scripts/yarli_supervisor.py` exists.
- Separate discovering work from executing work.
- New work must become an explicit tranche with `key`, `summary`, `allowed_paths`, `verify`, `done_when`, and optional `max_tokens`.
- Use `yarli run continue` only for work already owned by the continuation snapshot and only when no drift is present.
- Use `yarli run --fresh-from-tranches` after new tranche enqueue or other live-plan changes.
- Treat refusal as non-terminal. Convert it into a narrowed retry, a follow-up tranche enqueue, or stop-and-summarize.
- Treat orphaned active runs as repairable state, not an automatic stop condition. When an active/verifying run points at a missing workspace and is older than the stale threshold, auto-cancel it with the bundled remediation helper before launching again.
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
- stale active run candidates from the bundled dry-run remediation check

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

In bare `supervise-loop` mode, a healthy `RunActive` state is a mandatory continue-watching condition, not a valid stopping point.

If the watch output reports `stale_run_detected`, classify the loop as `stuck`, not `healthy`, and remediate before watching further.

If you just launched or resumed a run, do not yield control immediately. Watch until at least the first meaningful delta after launch:

- task leaves `waiting` / `ready`
- task enters verifying, blocked, failed, or complete
- run becomes stuck, blocked, or disappears
- `3` quiet ticks force a deeper pulse check

After that first delta, continue watching if the run is still healthy and active. The first delta authorizes supervision updates, not a return to the user.

## Step 4: Launch And Then Keep Supervising

If no run is active and the repository provides `scripts/yarli_supervisor.py`, prefer the wrapper:

```bash
bash "$SKILL_DIR/scripts/yarli-loop-supervise.sh" [project-root]
```

This wrapper must perform at most one top-level launch by default and then return control to the agent. Use it only when:

- no run is currently active
- no tranche mismatch needs to be resolved first
- no architectural or refusal-recovery intervention is required yet

The repo-local supervisor is an actuator for ordinary launch policy, not a replacement supervisor.
Before launch, the wrapper should run the bundled stale-run remediation helper in fix mode so orphaned `RunActive` / `RunVerifying` rows do not block the next real launch.

After the wrapper or a manual launch returns, immediately re-inspect state and switch into watch mode. Do not treat "launch succeeded" as the end of the turn unless the user explicitly asked for a one-shot launch.

## Step 5: Fallback Manual Execution Path

- No continuation and no active run context: use `yarli run`.
- Continuation exists, no drift is reported, and the remaining work belongs to the continuation snapshot: use `yarli run continue`.
- Drift is reported, or you just enqueued new tranches, or live plan state changed after the previous run started: use `yarli run --fresh-from-tranches`.
- If prompt selection matters, add `--prompt-file <path>` to `yarli run` or `yarli run --fresh-from-tranches`.
- Before any fresh launch or continue attempt, run `bash "$SKILL_DIR/scripts/yarli-remediate-stale-runs.sh" [project-root] --fix` when stale-run symptoms are possible. The helper auto-cancels orphaned active/verifying runs whose recorded workspace directories are missing and older than the default `300` second threshold (`YARLI_STALE_RUN_MIN_AGE_SECONDS` overrides it).

Use this fallback only when the repo-local supervisor does not exist, or when you intentionally need to override it for an exceptional case.

## Step 6: Post-Completion Re-Inspection

Whenever a run reaches `RunCompleted`, `RunFailed`, `RunBlocked`, or another terminal state:

1. Re-run the inspect helper.
2. Compare continuation snapshot keys against current open tranches.
3. Decide whether the next correct action is:
   - `watch` a still-active run
   - `continue`
   - `fresh-from-tranches`
   - `enqueued`
   - `stop-and-summarize`
4. If more eligible work remains and no blocker prevents progress, keep the loop moving in the same turn.

Do not stop solely because Yarli wrote a continuation file or printed "Auto-advance stopped."

If re-inspection finds a healthy active run or more eligible work with no blocker, keep supervising in the same turn.

## Step 7: Intervention Heuristics

- After `3` quiet ticks with no tranche change, run a deeper pulse check: run list, process health, `yarli run explain-exit` when applicable, and the latest meaningful log notes.
- If the same verification or helper command fails `2` times, inspect the exact failure before retrying again.
- If the same tranche stays active for more than `10` minutes with no edit, verification, or worker-note movement, classify it as `slow`.
- If the active process disappears without a matching completion or cancellation update, inspect before relaunching.
- If an active/verifying run still exists in Yarli but its `workspace_dir` is missing and its last update is older than the stale threshold, auto-cancel it with the remediation helper and then re-inspect state.
- If blocked or no-eligible-tranche conditions appear, stop and summarize instead of thrashing.

## Step 8: Intervention Ladder

1. Inspect live state.
2. Inspect process health, log tail, and `yarli run explain-exit` when relevant.
3. Auto-remediate orphaned active runs with `scripts/yarli-remediate-stale-runs.sh --fix` when the run is active/verifying, the workspace is missing, and the stale threshold is met.
4. Classify the loop as `healthy`, `slow`, `stuck`, `blocked`, or `idle`.
5. Choose exactly one action: keep watching, narrow a retry, enqueue a follow-up tranche, do one launch, use `fresh-from-tranches`, or stop-and-summarize.

Do not relaunch while a healthy active run is still making progress.

## Step 9: Refusal Recovery

- Narrow scope once: reduce objective, allowed paths, or verification command size.
- If the work clearly needs decomposition, enqueue a follow-up tranche immediately.
- If execution should stop, produce a stop-and-summarize handoff with the next recommended Yarli command.

Do not end a cycle with an unstructured refusal and no next step.

## Backend Notes

- For Codex-specific operating hints, read `references/codex.md`.
- For Claude-specific operating hints, read `references/claude.md`.
- Do not duplicate the core workflow in backend notes.

## Output Contract

Emit the decision block at the end of each meaningful supervisor cycle or before yielding control back to the user. The block is a checkpoint, not by itself a stop condition.

In `supervise-loop` mode, prefer emitting the block only for:

- an in-loop status update while continuing to watch
- a terminal/blocked/stuck/idle state that justifies yielding control
- an explicit user-requested inspect-only or one-shot return

Do not emit the block as a turn-ending handoff while the run is healthy and active.

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
