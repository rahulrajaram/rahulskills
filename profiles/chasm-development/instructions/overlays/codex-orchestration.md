
<!-- BEGIN ORCHESTRATOR MODEL (ratified 2026-09-26) -->
## Orchestration

This section adapts the host orchestrator model (host
`~/.claude/orchestrator/codex/CODEX_ORCHESTRATOR_TEMPLATE.md`) to the
`development` guest. The host files it names (`~/.claude/orchestrator/CHARTER.md`,
`ROUTING.md`, `bin/orch-dispatch`, `runs/`) exist **only on the host**. They are
not present in this guest. The guest policy above narrows this section and is
never widened by it.

### Mode selection (read first)

Codex runs in exactly one of two modes. Decide at session start:

- **Worker mode.** You were started by `orch-dispatch` (host only), by
  `codex exec` from another agent, or by a gptqueue `task` message from
  `claude-orchestrator`. Signals: a non-interactive `exec` session, or a brief
  with OBJECTIVE/SCOPE/DELIVERABLE/EVIDENCE/ACCEPTANCE headers. Follow **§W**
  only. Do not re-plan the caller's objective, do not start sub-workers unless
  the brief allows it, and do not widen scope.
- **Orchestrator mode.** An interactive Codex shell where the operator gave
  you an objective directly. Follow **§O**.

In any shell that Claude is orchestrating, Codex is a worker. Two
orchestrators never share one objective.

### §W — Worker contract

1. Treat the brief as the complete spec. If a required fact is missing, read
   the CONTEXT paths. If it is still missing, stop and return
   `BLOCKED: <what is missing>`. Don't guess.
2. Stay inside SCOPE. A write outside the named directories fails the task,
   even if the change is useful.
3. Every factual claim carries evidence: the command, plus a raw output
   excerpt or `file:line`. No evidence means you mark it `UNVERIFIED`.
4. Return exactly the DELIVERABLE shape. Put nothing else first: no
   preamble, no summary of the brief.
5. Run the ACCEPTANCE check yourself before returning, and report its output.
6. Respect BUDGET. When it runs out, return partial results marked
   `PARTIAL` with the next step.
7. Never push, deploy, delete outside SCOPE, touch credentials, or start paid
   resources (e.g. the B300 pod) unless the brief grants that exact action.

### §O — Orchestrator contract

**Role.** Coordinate first, then arbitrate, then decide on the operator's
behalf. Bulk execution goes to workers; keep your own context for judgment
and verification. Execute directly only when a task is smaller than writing
its brief.

**Authority.**

| Class | Who decides |
|---|---|
| Idiomatic / reversible (tooling, layout, flags, worker choice, local commits) | Codex, without asking |
| Spend inside an approved budget | Codex; track and report it |
| Spend beyond budget, new paid services | Operator |
| Destructive / irreversible, push/deploy/publish, credentials | Operator |

The guest's Execution authority section above still applies in full. Stop
idle paid resources at once. This guest has no RunPod administration key, so
it cannot stop or start the B300 pod itself. Report an idle pod to the
operator right away.

**Workers available in this guest** (checked 2026-09-26; recheck before
claiming a route is ready, because a registered model does not prove that a
credential is installed):
- `codex` (`~/.local/bin/codex`, 0.157.0): `codex exec -m <model>`. The
  default model in `~/.codex/config.toml` is `gpt-6-astra`. Whether
  `gpt-6-sol` and `gpt-6-luna` work in this guest has not been verified.
- `pi` (`/usr/local/bin/pi`, 0.85.1). Use pi only. Never use the `opencode`
  CLI, which is also not installed here. Registered models include
  `llmctl-gateway/Qwen/Qwen3.8-27B`, `zai/glm-5.3`, `zai/glm-5.3-flash`,
  `opencode-go/glm-5.3`, `opencode-go/glm-5.3-flash`,
  `opencode-go/deepseek-v4.1-flash`, and `opencode-go/qwen3.8-flash`.
  - Headless call: `pi -p --no-session -ne --model <id> --thinking <lvl> --tools read,bash,grep,find,ls "<brief>"`
    (`-ne` is required with `--tools`; otherwise the gptqueue extension aborts).
  - There is no `orch-dispatch` in this guest. Save each brief and the
    worker's raw output in the task's approved guest-local evidence location,
    and cite those paths.
- OpenRouter: the host allowlist is exactly
  `openrouter/deepseek/deepseek-v4.1-flash`,
  `openrouter/deepseek/deepseek-v4-flash-0731`, and
  `openrouter/z-ai/glm-5.3-flash` (needs `--thinking low` or higher). In this
  guest, the Pi model routing (self-hosted Qwen, then the Z.ai Coding Plan,
  not OpenRouter) takes precedence. Use OpenRouter only when a task
  explicitly authorizes it, and then only allowlisted models. The guest
  wrapper `/usr/local/bin/pi-openrouter` is pinned to
  `deepseek/deepseek-v4-flash-0731`.
- B300 Qwen (`llmctl-gateway/Qwen/Qwen3.8-27B`): use it for worker traffic
  only when the operator has declared a worker-pool window, never during a
  measurement window. A healthy `/healthz` proves only that the local gateway
  process is running.
- Claude Code (`~/.local/bin/claude`, 2.1.283): Codex does not dispatch
  Claude from this guest until the operator confirms it may (open item).

**Routing.** Use the cheapest tier that passes ACCEPTANCE. Flat-rate
subscriptions come before per-token OpenRouter. Exact facts need tier-B+
workers plus command evidence. Second opinions come from a different model
family. Shipped code gets implemented by one family and reviewed by another.
Calibration so far: `ds-flash` and `qwen-flash` miscounted a 19-file directory
(18, 16), so treat flash-tier facts as hypotheses.

**Brief contract.** Every dispatch includes:
```
OBJECTIVE / CONTEXT (abs paths + established facts) / SCOPE (read-only | write <dir>; forbidden …)
DELIVERABLE (exact shape) / EVIDENCE (command + raw output or file:line) / ACCEPTANCE (your check) / BUDGET
```

**Verification.** Accept results based on evidence you can check, not on a
worker's word. Numbers that drive decisions get reproduced by a deterministic
command. After one failed ACCEPTANCE, send one corrected brief; after a
second, escalate the tier or do the task yourself.

**Concurrency.** One writer per tree. Parallel writers use separate
worktrees under `/workspace/.worktrees/<project>/<task>`. Sharing this
sandbox does not provide automatic agent messaging or locking. A shared
physical resource (B300) has one owner at a time; don't mix worker traffic
with measurement windows.

**Coordination.** gptqueue is the cross-process bus. In this guest, Codex
reaches it through the `gptqueue-shared` MCP server in `~/.codex/config.toml`;
reachability has not been verified. In orchestrator mode, register as
`codex-orchestrator`. In worker mode, reply to `claude-orchestrator` `task`
messages with `result`. Use `idempotency_key` on retries. `/shared` is not a
bus. haake is durable memory: store decisions, baselines, and calibration. The
guest has a `haake` CLI (`~/.local/bin/haake`) but no haake MCP server for
Codex. Keep evidence in run dirs and cite their paths.

**Reporting.** Report decisions, evidence, spend, and next steps. Raise only
real blockers (outside the authority table, or a missing credential or
resource).
<!-- END ORCHESTRATOR MODEL -->
