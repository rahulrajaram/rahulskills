---
name: yarli-execution-loop
description: Inspect Yarli state, durably enqueue new tranches, and choose `yarli run continue` versus `yarli run --fresh-from-tranches` for long feedback loops.
argument-hint: "[project-root]"
---

# Yarli Execution Loop

Use this skill when the user wants an agent to monitor Yarli, queue newly discovered work durably, and keep execution moving without losing state.

## Outcomes

- Inspect the current Yarli run and plan state before acting.
- Enqueue new work durably in `.yarli/tranches.toml`.
- Choose the right execution path: `yarli run`, `yarli run continue`, or `yarli run --fresh-from-tranches`.
- End each cycle with a plain-text decision block that another agent or shell can follow.

## Core Tenets

- Treat Yarli as the durable control plane. Agent scratchpad is never the queue.
- Separate discovering work from executing work.
- New work must become an explicit tranche with `key`, `summary`, `allowed_paths`, `verify`, `done_when`, and optional `max_tokens`.
- Use `yarli run continue` only for work already owned by the continuation snapshot and only when no drift is present.
- Use `yarli run --fresh-from-tranches` after new tranche enqueue or other live-plan changes.
- Treat refusal as non-terminal. Convert it into a narrowed retry, a follow-up tranche enqueue, or stop-and-summarize.
- Re-inspect Yarli state after each material execution step.

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

## Step 3: Choose Execution Path

- No continuation and no active run context: use `yarli run`.
- Continuation exists, no drift is reported, and the remaining work belongs to the continuation snapshot: use `yarli run continue`.
- Drift is reported, or you just enqueued new tranches, or live plan state changed after the previous run started: use `yarli run --fresh-from-tranches`.
- If prompt selection matters, add `--prompt-file <path>` to `yarli run` or `yarli run --fresh-from-tranches`.

## Step 4: Refusal Recovery

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
status: continue|fresh-from-tranches|enqueued|stop-and-summarize
reason: <one concise sentence>
enqueued_tranches: <comma-separated keys or none>
next_command: <single command or none>
```
