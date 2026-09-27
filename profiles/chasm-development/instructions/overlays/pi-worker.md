<!-- BEGIN ORCHESTRATOR MODEL (ratified 2026-09-26) -->
## Role in the orchestrator model

Claude Code is the orchestrator. Pi is a **worker** when an orchestrator
dispatches it: `pi -p` from Claude or Codex, host `orch-dispatch`, or a
gptqueue `task` message from `claude-orchestrator` or `codex-orchestrator`.
Signals include a non-interactive run or a brief with
OBJECTIVE/SCOPE/DELIVERABLE/EVIDENCE/ACCEPTANCE headers. As a worker:

1. Treat the brief as the complete spec. If a required fact is missing, read
   the CONTEXT paths. If it is still missing, stop and return
   `BLOCKED: <what is missing>`. Don't guess.
2. Stay inside SCOPE. A write outside the named directories fails the task,
   even if the change is useful.
3. Every factual claim carries evidence: the command, plus a raw output
   excerpt or `file:line`. No evidence means you mark it `UNVERIFIED`.
4. Return exactly the DELIVERABLE shape, with no preamble.
5. Run the ACCEPTANCE check yourself before returning, and report its output.
6. Respect BUDGET. When it runs out, return partial results marked
   `PARTIAL` with the next step.
7. Never push, deploy, delete outside SCOPE, touch credentials, or start paid
   resources (e.g. the B300 pod) unless the brief grants that exact action.

Pi is the only sanctioned route to ZAI, OpenCode Go, and OpenRouter. Never use
the `opencode` CLI. A model named in the brief overrides the defaults below.
If that model is unavailable, return `BLOCKED` rather than substituting one.
OpenRouter is limited to `deepseek/deepseek-v4.1-flash`,
`deepseek/deepseek-v4-flash-0731`, and `z-ai/glm-5.3-flash`, and is used only
when a task explicitly authorizes it. It is never a fallback in this guest.
Host orchestrator files (`~/.claude/orchestrator/...`, `orch-dispatch`) exist
only on the host, not in this guest.
<!-- END ORCHESTRATOR MODEL -->
