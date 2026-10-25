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
     # $HOME/.local/bin holds the native `claude` launcher; keep only bins the child needs
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

## Defensive-security worker briefs

For an authorized defensive-security assignment, include this block in the
worker brief using the actual grant. Omit it for unrelated work. The reroute
bound is an exception only for this stated case, not a general model fallback.

```markdown
## Authorized defensive-security context and blocker reporting

Project: <project>. Authorization: <actual grant and source>. This assignment
is authorized defensive code review, evaluation or detection within <scope>.
Explicitly out of scope: exploit weaponization, targeting real third-party
systems, malware, and detection evasion. Do not claim authorization beyond the
genuine grant or broaden the task to make this description fit.

Proceed with in-scope work without re-asking permission already granted.
If you hesitate or decline, restate the genuine context once, accurately.
Do not reword or disguise the request to get around a refusal. Respect a
refusal of genuinely out-of-scope work; never reroute that work.

If an in-scope step is still declined, the dispatch owner may reroute it once
to another allowed worker under the operator's preference order, using the
same accurate context and existing authority. Rerouting must not bypass a
safety boundary or imply a new model, capability, spend or scope grant.
If no allowed reroute is available, or that attempt is still declined, send
an immediate blocker packet to <parent>: exact step, verbatim decline text,
and what was tried (including the one context restatement and any reroute).
Never stall silently. A blocker report is a result, not permission to expand
scope or keep retrying.
```

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

## Typed packets and model-terminal acceptance

Bind each worker to a versioned dispatch packet and its schema/validator digest.
Required fixed identity: role, runtime, model, effort, cwd, write_roots,
parent_mailbox, task_id. Carry the owner's structured authority record unchanged:
decision_id, issuer_mailbox, issuer_session, issuer_level, scope (effect_class,
exact target), derived_from, expiry. Structure is not authentication; verify
transport identity, authority attenuation and any reserved-effect chain separately.

Require an early checkpoint/BLOCKER before the bound early-report deadline,
then enforce the explicit budget and stop_rule. Missing or late early evidence
refuses success; issue a blocker instead of waiting silently. Native queue ACKs
remain required for completed claims; do not add ACK-only conversations.

The worker's final structured verdict is success/blocked/failed/cancelled/uncertain
with fixed identity, concise summary and cited artifact evidence. The controller
builds a result packet from the real model event stream and output, not from
process state or a worker-authored terminal flag. Keep these separate:
- process state and exit code;
- last model assistant terminal and stop reason, or an explicit missing terminal;
- final structured model verdict, evidence and acceptance result.

Exit 0 or a COMPLETED receipt alone is never semantic success. Reject successful
admission for content filtering, model error/abort, intermediate tool-use stops,
missing assistant terminal/final output, identity drift or missing artifacts.
If native model terminal evidence is unavailable, emit an uncertain/failed typed
packet and the exact blocker; do not infer a terminal from wrapper shutdown.
Run the qualified packet validator and existing artifact/acceptance verification.
Do not report this format installed or a runtime adapter qualified merely because
a draft schema/validator exists. No new service, model call or retry is authorized.

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

In Claude Code, the native wake path is the Bash tool's `run_in_background`:
launch a blocking terminal wait such as `overwatch events <task_id> --follow`
as a background Bash command, and Claude Code re-invokes the same session when
that command exits. Then collect `overwatch status`/`receipt` as the terminal
evidence; the re-invocation itself proves only that the wait command ended. A
host-provided monitor tool, when present, may stream the same events. Stop,
Notification, or PostToolUse hooks in `settings.json` can also signal
completion, but adding or changing hooks is a settings change that needs its
own authorization. Do not use `ow-run --target-session` or `ow-child` for a
Claude session: they address OpenCode sessions only. A background command does
not survive the Claude session ending; if the session may end first, retain the
task id and report that a later turn must collect completion.

The read-only inspector depends on the installed OpenCode database schema;
a missing database, schema mismatch, or empty result is not evidence of completion.
Process liveness, CPU use, and log growth are observations, not proof that a child
is progressing toward the requested outcome. Pair status with task artifacts.

Avoid silent timeouts shorter than a known quiet phase, especially with buffered
pipelines such as `tee | tail`. A killed wrapper may never write its sentinel;
controller exit evidence remains authoritative. Preserve inherited
`AGENT_ATTRIBUTION_*` and `SELFIMPROVE_*` attribution fields for authorized child
calls without treating those fields as new effects or credentials authority.
