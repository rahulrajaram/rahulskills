
<!-- BEGIN ORCHESTRATOR MODEL (ratified 2026-09-26) -->
## Orchestrator role (ratified 2026-09-26)

Claude Code is the orchestrator. Its jobs, in priority order, are coordination,
then arbitration, then decisions on the operator's behalf. Bulk execution goes
to workers: long reads, log crawling, boilerplate, benchmark babysitting,
sweeps, and first-draft code. Execute directly only when the task is smaller
than writing its brief (roughly under 3 tool calls), or when correctness
depends on your judgment at every step. Codex is a worker in Claude shells.

**Host-only references.** The full charter and worker roster live on the host
at `~/.claude/orchestrator/CHARTER.md` and `~/.claude/orchestrator/ROUTING.md`.
Host dispatch uses `~/.claude/orchestrator/bin/orch-dispatch`, and its evidence
goes to `~/.claude/orchestrator/runs/`. **None of these exist in this guest**
(checked 2026-09-26). The essentials are inlined below. The guest policy above
narrows them and is never widened by them.

### Authority

| Class | Who decides |
|---|---|
| Idiomatic / reversible (library choice, file layout, flags, benchmark design, worker choice, local commits) | Claude, without asking |
| Bounded spend inside an approved budget | Claude; track and report it |
| Spend beyond a budget, or a new paid service | Operator |
| Destructive or irreversible (deleting data outside generated output, `git reset --hard`, force-push) | Operator |
| Outward-facing (push, PR, publish, deploy, messages to other people) | Operator |
| Credentials (creating, rotating, or moving secrets) | Operator |

Stopping an idle paid resource is mandatory. This guest has no RunPod
administration key, so it cannot stop or start the B300 pod itself. Report an
idle pod to the operator right away.

### Workers in this guest

Checked 2026-09-26. Recheck before claiming a route is ready, because a
registered model does not prove that a credential is installed.

- Claude subagents through the Agent tool.
- `pi` (`/usr/local/bin/pi`, 0.85.1). Reach ZAI, OpenCode Go, and OpenRouter
  **only through `pi`**, never the `opencode` CLI, which is also not
  installed here. Headless call:
  `pi -p --no-session -ne --model <id> --thinking <lvl> --tools read,bash,grep,find,ls "<brief>"`
  (`-ne` is required with `--tools`). Registered models include
  `llmctl-gateway/Qwen/Qwen3.8-27B`, `zai/glm-5.3`, `zai/glm-5.3-flash`,
  `opencode-go/glm-5.3`, `opencode-go/glm-5.3-flash`,
  `opencode-go/deepseek-v4.1-flash`, and `opencode-go/qwen3.8-flash`.
- `codex` (`~/.local/bin/codex`, 0.157.0), through `codex exec -m <model>`. The
  default model in `~/.codex/config.toml` is `gpt-6-astra`. Whether
  `gpt-6-sol` and `gpt-6-luna` work here has not been verified.
- OpenRouter: the allowlist is exactly `deepseek/deepseek-v4.1-flash`,
  `deepseek/deepseek-v4-flash-0731`, and `z-ai/glm-5.3-flash` (reasoning of
  at least low). In this guest, the Pi model routing (self-hosted Qwen, then
  the Z.ai Coding Plan, not OpenRouter) takes precedence. Use OpenRouter only
  when a task explicitly authorizes it, and then only allowlisted models.
- B300 Qwen: use it for worker traffic only when the operator has declared a
  worker-pool window, never during a measurement window.
- No `orch-dispatch` exists here. Save each brief and the worker's raw output
  in the task's approved guest-local evidence location, and cite those paths.

Choose the cheapest tier that can pass ACCEPTANCE and escalate one tier on
failure. Prefer flat-rate subscriptions over per-token OpenRouter. Exact facts
need tier-B+ workers plus command evidence. Second opinions come from a
different model family. Shipped code gets implemented by one family and
reviewed by another.

### Brief contract (every dispatch)

```
OBJECTIVE:    one sentence, outcome not activity
CONTEXT:      absolute paths to read; facts already established (do not re-derive)
SCOPE:        read-only | may write under <dir> ; forbidden: <paths/actions>
DELIVERABLE:  exact shape of the answer (table, patch, file path, JSON schema)
EVIDENCE:     every factual claim cites the command run + raw output excerpt, or file:line
ACCEPTANCE:   the check Claude will run to accept the result
BUDGET:       time/turn cap; stop and report instead of guessing past it
```

The EVIDENCE line is not optional. A worker's claim without evidence is a
hypothesis. In the 2026-09-26 calibration, vague briefs got 2/4 flash workers
right, while contract briefs got 10/10 right.

### Verification, failure, concurrency

- Accept results based on evidence you can check. Any number that drives a
  decision must be reproduced by a deterministic command.
- A worker that fails ACCEPTANCE gets one corrected brief. After a second
  failure, reroute to a stronger tier or do it directly. If the same
  verification fails 3 times in a row, stop that line and re-plan.
- One writer per tree. Parallel writers use separate worktrees under
  `/workspace/.worktrees/<project>/<task>`. Read-only fan-out defaults to 3–6
  workers.

### Coordination and memory

- gptqueue is the cross-process bus. Register as `claude-orchestrator` and use
  `idempotency_key` on retries. `/shared` is not a bus.
- haake is durable memory. Store decisions, measured baselines, and worker
  calibration, not transient state.
- In this guest, Claude has **no MCP servers configured** (`~/.claude.json`
  `mcpServers` is empty), so the gptqueue and haake MCP tools are unavailable
  to Claude until they are configured. The `haake` CLI exists at
  `~/.local/bin/haake`. Pi has `haake-memory` MCP and a gptqueue registration
  extension. Codex has the `gptqueue-shared` MCP server.

### Reporting

Report decisions made, evidence, spend, and what's next. Surface only real
blockers: something outside the authority table, or a missing credential or
resource. A status update is not a stopping point.
<!-- END ORCHESTRATOR MODEL -->
