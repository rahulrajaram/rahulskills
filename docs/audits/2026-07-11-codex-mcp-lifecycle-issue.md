# Draft Codex MCP Lifecycle Issue

Date: 2026-07-11
Source: friction f-1636
Destination: `openai/codex`
Status: draft only; not submitted

## Proposed title

Expose MCP process ownership, health, reload, idle expiry, and safe orphan cleanup

## Body draft

### Summary

Codex lacks a first-class lifecycle view for configured MCP processes. During a
local remediation we found multiple long-lived Haake and Cultivar stdio children
owned by different Codex sessions, including old processes whose source/runtime
metadata no longer matched fresh builds. We deliberately did not kill them
because process age and command name are insufficient proof of orphanhood.

### Requested lifecycle contract

Add a structured status surface, for example `codex mcp ps`, that reports for
each configured server process:

- server/config name, transport, PID, start time, and executable provenance;
- owning Codex client/session PID and stable session identifier;
- connection state, initialize/tool-list status, last successful call, and last
  transport error;
- configured artifact hash versus the running executable/source hash when
  available;
- ownership classification: active, owner-exited/orphan, idle-but-owned, or
  indeterminate.

Provide explicit operations that share this ownership model:

- `codex mcp reload <name>` starts a replacement, initializes and refreshes
  tools, switches only after health succeeds, and terminates the old child it
  owns; failed reload leaves the old healthy connection intact.
- Configurable idle expiry applies only to owned, inactive processes and is
  visible in status.
- `codex mcp prune --orphans --dry-run` lists candidates and evidence without
  signaling them. The non-dry-run form requires explicit confirmation and must
  refuse active, indeterminate, or foreign-owned processes.

### Acceptance criteria

1. A user can identify which session owns every Codex-spawned MCP child.
2. A closed transport can be reconnected without restarting the whole client.
3. Source changes can be loaded per server with health-check-before-switch and
   rollback on failure.
4. Idle expiry never terminates a process with an active request or live owner.
5. Orphan cleanup is dry-run-first, evidence-backed, explicitly confirmed, and
   reports every signal/termination result.
6. Status and lifecycle events are available as structured output for tooling.

### Relationship to existing issues

- #4955 requests restarting one configured MCP server. This issue includes that
  capability but adds ownership, observability, safe handoff, and idle policy.
- #21008 reports large numbers of orphaned MCP helpers. This issue does not
  duplicate the leak report; it proposes the status and safe-control plane
  needed to diagnose and clean up ownership failures without broad process
  matching.

No process was pruned to produce this report. Fresh child verification was kept
separate from existing Codex-owned stdio children.

## Approval boundary

Submitting this issue is one external write and requires explicit approval of
the destination, title, and final redacted body. That approval does not authorize
comments on #4955/#21008 or any local process cleanup.
