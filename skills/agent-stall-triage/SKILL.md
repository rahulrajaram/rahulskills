---
name: agent-stall-triage
description: Diagnose and recover an apparently stuck Pi, Codex, Claude, or OpenCode session, including sessions running in a Chasm guest. Use when tool output stops, progress appears frozen, or an agent shell may be wedged; preserve evidence and identity before any intervention.
---

# Agent stall triage

## Intent and applicability

Determine whether the host, Chasm guest, agent runtime, or a tool child is
stuck, then recover the one identified session when the operator has authority
to do so. A quiet transcript, a growing TCP receive queue, or a healthy VM is
only a symptom; none identifies the failing layer by itself.

## Inputs and local bindings

Bind these before acting:

- runtime: `pi`, `codex`, `claude`, or `opencode`;
- host or guest, guest name, project working directory, and incident time;
- exact session identity when available (session ID, terminal, PID, or parent
  process); and
- the operator's authority to send input, signal a process, end a session, or
  resume it.

If an identity or authority is missing, gather read-only evidence and stop at
that boundary. Use the runtime's current `--help` output before relying on a
flag that is not listed below.

## Non-goals

This skill does not install or upgrade agents, repair the VM, rotate
credentials, reconstruct a lost transcript, or implement a periodic watcher.
It may recommend a separate Chasm-owned watcher after the incident, but that
watcher requires its own session identity, authorization, leases, and stop
rules.

## Must not

- Do not kill by name, kill a process group, restart all VMs, or restart a
  guest as the default response to one quiet agent.
- Do not copy credentials between host and guest, print environment variables,
  dump raw command lines containing tokens, or paste raw transcripts into an
  external service. Redact paths, arguments, endpoints, and secrets in notes.
- Do not treat VM health, a live TCP connection, CPU idleness, or a changed
  receive queue as proof that the agent is making progress or is safe to stop.
- Do not send input or signals until the target session and process/terminal
  mapping are corroborated by at least two independent observations.
- Do not claim recovery until a new bounded progress observation confirms it.

## Interaction and authority

Read-only diagnosis can proceed within the named host/guest and project.
Sending input, detaching, signalling, terminating, forking, or resuming a
session is a material operation: state the exact target and request or reuse
explicit authority for that operation. A failed gentle intervention does not
grant authority for a stronger one.

## Procedure

### 1. Freeze the incident state

Record an incident ID, timestamp, runtime, project cwd, host/guest, last
known useful event, and the suspected session identity. Take two bounded
snapshots rather than an unbounded log tail. Preserve only redacted metadata:
process IDs, parent IDs, states, elapsed time, file mtimes, child counts,
socket state/queue sizes, and event timestamps.

### 2. Separate host, guest, and runtime health

For a Chasm guest, inspect the named guest with the already-installed `chasm
show <name>` surface and use an existing shell/console to inspect the guest.
Do not call `start`, `stop`, or `delete` as a diagnostic shortcut. In the
relevant namespace, check uptime/load, memory and disk pressure, scheduler
progress, and basic connectivity. A healthy guest moves triage to the runtime;
it does not establish that the runtime is healthy.

### 3. Identify exactly one session and process tree

Correlate the project cwd, terminal/PTY, runtime command, PID/PPID chain, and
session metadata or last-event timestamp. Use bounded, read-only inspection of
`ps`, `/proc/<pid>/{cwd,status,wchan,fd}`, the process tree, and (when already
available) `ss`/socket state. Inspect child processes separately: a runtime
waiting on a tool, approval, pipe, or network response differs from a runtime
that is itself blocked. Redact `argv`, file descriptors, URLs, and environment
content before recording them.

Take a second snapshot after a short, stated interval. Compare event/mtime
movement, CPU and I/O state, child state, and socket queues. A receive queue
that grows while the guest remains healthy is evidence of a transport or
consumer mismatch to investigate, not a reason to kill the VM.

### 4. Classify the stall before intervening

Classify the evidence as one of: waiting for user/approval input; waiting on a
tool child or external transport; runtime event loop/PTY blocked; process
terminated while durable session state remains; or insufficient evidence.
Record the observation supporting the classification and what remains unknown.
If classifications conflict, preserve evidence and stop for operator review.

### 5. Apply the least disruptive authorized recovery

Prefer, in order:

1. reconnect to the exact terminal or deliver the already-approved input if
   the evidence shows the session is waiting for it;
2. repair or end the identified tool child only when its ownership and effect
   are understood and that action is authorized;
3. send one gentle interrupt to the exact top-level PID, capture the result,
   and wait a bounded interval for the runtime to flush or exit; and
4. only with new explicit authorization, terminate that exact PID and use a
   native resume/fork path if durable state is confirmed.

After a failed interrupt, do not escalate automatically. The stop rule is
reached when identity is uncertain, durable state is absent or corrupted,
the bounded observation window expires without a state change, or the next
action would affect another session, guest, credential, or external system.

If the operator explicitly requests a **guest bounce**, inventory the other
live sessions in that guest and state that a VM restart ends all of them.
Use a graceful restart with a bounded wait. A timeout does not prove that the
VM stayed up: check its actual state, and if it finished stopping after the
timeout, start it through the normal lifecycle path. Verify guest-agent
readiness, mounts, and the state of every affected session. Do not claim the
sessions resumed merely because the VM is running.

### 6. Use only verified native recovery surfaces

These surfaces were verified from local CLI help during authoring; verify the
installed version again at incident time:

- Pi: `--continue`, `--resume`, `--session`, and `--fork`; the local install
  has `~/.pi/agent/sessions`, but project/runtime selection still must be
  checked.
- Codex: `codex resume [SESSION_ID]` or `codex resume --last`; `queue` and
  `fork` are separate commands. Prefer an exact ID over “last”.
- Claude: `--continue`, `--resume`, and `--fork-session`; do not assume a
  session is persisted when `--no-session-persistence` was used.
- OpenCode: `--continue`, `--session <id>`, `--fork`, and `opencode session
  list`.

Do not invent default storage paths for these runtimes. Discover them from
the exact process, current CLI help, and readable local metadata. Never resume
or fork until the project cwd, session identity, and authorization match.

## Completion and evidence

Report the incident ID, runtime and host/guest identity, two observation
windows, health-layer result, exact session/process evidence (redacted), stall
classification, authorized actions, native recovery identity if used, and a
post-action progress observation. Distinguish recovered, still stalled,
terminated-with-resume-available, and unresolved. Include the stop rule and
any evidence that could not be read. Do not report a healthy VM as a recovered
agent.
