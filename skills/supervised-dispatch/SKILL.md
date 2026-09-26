---
name: supervised-dispatch
description: "Dispatch long-running or hang-capable worker commands under Overwatch with a reproducible environment, cursor-driven monitoring, and evidence-bound completion. Use when launching agent CLI workers, campaign queues, or any process that may outlive the call."
---

# Supervised dispatch

Use this when launching a command that may outlive the call, hang, or need
cancellation — agent CLI workers (`opencode run`, backend CLIs), builds, index
runs, campaign queues. The dispatch contract below is the extraction of real
failures: an inherited service-manager environment broke nested agent sessions,
and turns ended after status probes instead of real terminal waits.

## Environment contract (reproducible children)

Do NOT rely on the daemon's ambient environment for nested agent CLIs. Dispatch
with `env_mode="caller_only"` and an explicit mapping:

```
PATH=$HOME/.opencode/bin:$HOME/.local/bin:<runtime bins>:/usr/local/bin:/usr/bin:/bin
HOME=<operator-home>
LOGNAME=<operator>  USER=<operator>  SHELL=<login shell>  TERM=xterm-256color
XDG_RUNTIME_DIR=/run/user/<uid>      # add CARGO_NET_OFFLINE=true for cargo work
```

Why: the daemon may run under systemd/desktop session variables (DISPLAY,
DBUS_SESSION_BUS_ADDRESS, INVOCATION_ID, NIX_*, QT_*) that nested CLIs mishandle;
`ambient_merge` now merges only an allowlist in Overwatch core, but `caller_only`
remains the reproducible default.

## Backend preflight

Before dispatching multi-backend work, prove usability — binary presence is not
authentication, eligibility, or quota:

```bash
gptengage status --preflight --timeout 60 --require codex
```

Typed reasons: `not-found`, `auth-expired`, `client-deprecated`, `quota`,
`timeout`, `invocation-failed`.

## Launch patterns

Single worker (detached), from the working project root:

```bash
overwatch run --wait=false --env-mode caller_only --env PATH=... --env HOME=... \
  --cwd "$PWD" -- /usr/bin/timeout 10800 <cli> run --agent <worker> --auto \
  --title <id> "<bounded assignment>"
```

Queue of tasks with dependencies and resume:

```bash
campaign-driver queue.json            # dry-run first with --dry-run
```

The driver records `results.jsonl`, per-entry event streams, and a summary under
`~/.local/state/campaign-driver/<queue>/`, blocks dependencies on failure, skips
already-succeeded entries, and never cancels on interrupt.

## Monitoring (cursor-driven, never sleep-poll)

- Snapshot: `overwatch status <task_id> --json`
- Events: advance the cursor (`events --after N`, or the MCP events tool);
  `overwatch events <task_id> --follow` blocks until the terminal event.
- Output: `output --after <cursor>` for incremental chunks.
- Receipt: `overwatch receipt <task_id>` (delegated tasks; task-registry runs use
  status/events/output).

The terminal event or receipt gates the next orchestrator action. If a turn must
end while a task runs, say so explicitly with the task id — do not report a
non-terminal status probe as if it were a milestone.

## Evidence rules

- Worker output is a CLAIM. Admit only controller-observed evidence: exit codes
  from receipts, recomputed digests, PATH-scrubbed probes, focused test reruns.
- Run gates through `gate-run` for identity-bound receipts:

```bash
gate-run <name> --require-executed -- cargo clippy --offline --all-features -- -D warnings
```

  (`--require-executed` exits 3 when cargo-style evidence is a cached rerun.)
- One writer per tree; workers commit locally only, never push.

## Pitfalls

- Backends die mid-run on auth expiry or quota; keep a per-entry watchdog and
  record the task id so a running task can be collected or cancelled deliberately.
- A failed run directory cannot be reused; use a fresh one.
- Set silent/soft timeouts so hangs self-report instead of stalling a queue.
- Never substitute models to work around a missing one; record the routing fact.


## Optional completion and child inspection tools

When the package's `ow-run` helper and OpenCode continuation bridge have been
explicitly installed, address a completion to the known orchestrator process,
session, and workspace:

```bash
ow-run task-label --cwd WORKSPACE --log DURABLE_LOG \
  --target-pid PID --target-session SESSION_ID -- COMMAND ARGUMENTS
ow-child --session SESSION_ID --db OPENCODE_DATABASE
```

An unspecified recipient leaves a record for inspection. A dead recipient is
not permission to deliver to another session. Reconcile pending or uncertain
claims manually before retrying; the bridge does not promise exactly-once
notification or authorize the next task. Prove the installed wake path before
promising unattended continuation. Without a verified bridge, retain the task
handle and report that an agent turn is still needed to collect completion.

The read-only inspector depends on the installed OpenCode database schema;
a missing database, schema mismatch, or empty result is not evidence of completion.
Process liveness, CPU use, and log growth are observations, not proof that a child
is progressing toward the requested outcome. Pair status with task artifacts.

Avoid silent timeouts shorter than a known quiet phase, especially with buffered
pipelines such as `tee | tail`. A killed wrapper may never write its sentinel;
controller exit evidence remains authoritative. Preserve inherited
`AGENT_ATTRIBUTION_*` and `SELFIMPROVE_*` attribution fields for authorized child
calls without treating those fields as new effects or credentials authority.
