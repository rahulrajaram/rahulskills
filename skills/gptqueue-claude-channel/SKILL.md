---
name: gptqueue-claude-channel
description: Connect Claude Code to gptqueue so a Claude session can send, receive and wait for inter-agent messages; install the per-project MCP identity and hooks, verify a round-trip, wait on replies without polling tokens, and troubleshoot delivery. Use when Claude must message Codex/Pi agents over gptqueue or wait on their replies during long runs.
argument-hint: "[install|verify|wait|troubleshoot]"
---

# gptqueue channel for Claude Code

gptqueue is a Redis-backed agent mailbox (`/workspace/gptqueue`, Redis
`127.0.0.1:6379`). Codex and Pi reach it through `gptqueue-session`, which only
accepts `--client codex|pi`. Claude uses the plain stdio server
`dist/mcp-server/index.js`, auto-registered through `GPTQ_AGENT_NAME`. The
scripts in `scripts/` (resolve them relative to this file) wrap that route.

| Script | Role |
|---|---|
| `gptqueue-claude-name [DIR]` | Agent name for a directory: `GPTQ_AGENT_NAME`, else longest prefix in `~/.config/gptqueue/claude-agent-names.tsv` (`<abs dir>\t<name>`), else `claude-<repo basename>` |
| `gptqueue-claude-mcp` | stdio MCP entry: resolves the name for `$CLAUDE_PROJECT_DIR`/`$PWD`, then execs the server |
| `gptqueue-inbox-peek` | Non-consuming `LLEN gptq:q:<name>`; `--watch` blocks until mail arrives |
| `gptqueue-claude-hook session-start\|stop` | SessionStart context; Stop gate while mail is unread. Fails open |
| `gptqueue-claude-verify.mjs` | Drives the MCP server like Claude: `selftest`, `send`, `claim`, `list`, `unregister` |
| `install.sh` | Copies the helpers to `~/.local/bin`, records `--map DIR=NAME`, adds the user-scope `gptqueue` MCP server and the hooks (idempotent; backs up `settings.json`) |

## Identity

Registration has no name-conflict check. Several sessions may share one agent
name, and they then share one inbox. Never give every Claude session the same
fixed name. Map the one directory that owns a role (for example
`install.sh --map /workspace/codereview=claude-orchestrator`), and let other
projects default to `claude-<repo>`. The registry entry outlives the session,
so the name stays addressable and mail queues while Claude is closed.

## Install

Installing edits user state (`~/.claude.json`, `~/.claude/settings.json`,
`~/.local/bin`). Run it only when the user asked for the channel. Then run:

```bash
scripts/install.sh --map /abs/project=role-name
claude mcp get gptqueue              # expect: Connected
gptqueue-claude-verify.mjs selftest  # expect: all PASS; cleans up its throwaway agents
```

MCP tools and hooks load when a session starts. The session that installs them
cannot call `mcp__gptqueue__*`; use `gptqueue-claude-verify.mjs` until restart.

## Messaging rules

- Use each recipient's exact full `name` from `list_agents`. Codex/Pi shells
  are `gptqueue-shell-<client>-<dir>-<uuid>`, one per connection. A shell that
  restarts gets a new name, so re-list before each send and prefer an online
  recipient.
- `idempotency_key` is scoped to the **sender** (`gptq:idempotency:<sender>:<key>`),
  not the recipient. Reusing a key for a second recipient returns
  `status: duplicate` and delivers nothing. Put the recipient in the key.
- Replies go to the sending identity. If you relay through another agent (for
  example `codex exec` inside a Codex MCP), the answer lands in that relay's
  inbox. Say "reply to `<your name>`" in the message.
- Consume with `claim_tasks`, then `acknowledge_tasks(claim_id)`. This is
  at-least-once: an unacked claim is requeued after `ttl_seconds`.
  `receive_message` is an untraced destructive pop, so avoid it.

## Waiting for replies (strongest first)

1. **Background watcher.** Launch
   `gptqueue-inbox-peek --watch --interval 20 --timeout 3600` with Bash
   `run_in_background`. It only peeks, and its exit (0 = mail, 3 = timeout)
   notifies the session, so waiting costs no tokens. Then claim and ack.
   Relaunch it after handling, or after a timeout if still waiting.
2. **Hooks** (installed): SessionStart injects the name and pending count. Stop
   blocks once while mail is unread. It honours `stop_hook_active`, so it
   cannot loop.
3. **`gptqueue-pty --agent NAME --cmd claude`**: push delivery. It types a
   claim prompt into the PTY after 2 s without output. It replaces the launch
   command (for example `claude-openrouter`) and can type into a half-written
   prompt. Use it only for unattended shells, and verify it live before relying
   on it.
4. **`/loop` with ScheduleWakeup** (1200–1800 s): the last-resort heartbeat when
   none of the above can run.

## Troubleshooting

- **Delivery status `unknown_history`**: the message is not queued, claimed or
  dead-lettered, and no claim→ack trace exists. This is typical after a
  `receive_message` pop or a Codex shell's own activation path. It is not
  evidence of non-delivery. Check `redis-cli XRANGE gptq:inbox-trace:<recipient> - +`
  for `reply_sent` with your `in_reply_to`, then peek the inbox the reply was
  addressed to: `redis-cli LRANGE gptq:q:<sender identity> 0 -1`.
- **`unknown_recipient`**: the name was never registered. Take the full name
  from `list_agents` (`gptqueue-claude-verify.mjs list --all`).
- **Hook prints nothing**: the hook fails open. Run
  `echo '{"cwd":"/abs/project"}' | gptqueue-claude-hook session-start` and
  `redis-cli ping`.
- **`codex exec` relay hangs or refuses** (fallback when no Claude MCP exists):
  close stdin (`< /dev/null`), or it waits on "Reading additional input from
  stdin". Run it from a trusted git directory, or it fails with "Not inside a
  trusted directory".
- **Stale dist**: the server runs `$GPTQUEUE_HOME/dist`. If another agent is
  rebuilding gptqueue, rerun `selftest` before trusting a failure.
