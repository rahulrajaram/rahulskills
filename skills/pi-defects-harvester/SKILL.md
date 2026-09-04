---
name: pi-defects-harvester
description: "Scavenge local shell history and pi/agent artifacts at the end of an interactive pi session, extracting actionable defect signals into a short redacted markdown digest. Use to capture errors, repeated tool failures, truncations, cost spikes, or unfinished shells without manually opening every history file. Source-preserving; writes one digest under ~/.pi/agent/reports/."
argument-hint: "[--since \"2026-08-20\" | --last 3d | --out <file>]"
---

# Pi Defects Harvester

Run at the end of an interactive pi session (or any time you want a digest of
past terminal/agent activity) to turn scattered pi history and agent artifact
files into one actionable defect summary, without the main agent having to open
every log by hand.

## When to Use

- User finishes a shell/pi session and wants "what did the agent/scavenger do today".
- User wants a survey of recent commands, errors, or unfinished work without reading raw history.
- Follow-up after autonomous subagents (examine transcript artifacts in the temp pi subtree).
- Before a handoff, to include what was actually run.

## Output

A single markdown digest, default written to the user digests dir
(`~/.pi/agent/reports/YYYY-MM-DD_shell-harvest.md`; override with
`--out <file>`). The digest also prints to the chat.

## Sensitive-source boundary

Shell histories and agent artifacts are sensitive local sources and may contain
credentials even when credential discovery is not the task. Treat explicit
invocation as authorization to read only the named/default sources for the
requested time window; do not broaden into unrelated home-directory content.

Before counting, grouping, retaining, writing, or displaying any source-derived
text, replace credential values with `[REDACTED]`. At minimum, redact:

- assignments such as `API_TOKEN=value` or `password="value"`;
- mapping fields such as `"api_key": "value"`;
- flags such as `--token value` and `--secret=value`;
- `Authorization: Bearer ...` and `Authorization: Basic ...` values; and
- URL userinfo between the `//` and `@` delimiters.

Run all frequency and failure aggregation on the redacted copy so a repeated
command cannot leak a value through a count table. Never print a credential
value to chat, the digest, diagnostics, or error output. If a form cannot be
redacted confidently, omit that source line and record only its source path,
timestamp, and signal category.

## Sources

Scavenge, in order (skip any that do not exist):

1. **Shell history** — the primary source. Prefer the extended zsh format
   (`: <epoch>:<duration>;<command>`). Bash history is `: <epoch>:<command>`.
   Apply the window filter (default: last 24h, or `--window`/`--dir`).
2. **Pi/agent session artifacts** — look under platform tmpdir subtrees that the
   harness writes (e.g. a `pi-*` subtree for per-session or per-subagent task
   output). In package-level and evolution/per-session caches there may be
   transcript JSONL, `.output` files, and campaign dossiers.
3. **Notable files** — `NEXT_SHELL_PROMPT`-style handoff notes, `*.md`
   reports, openrouter/inference CSV export in a Downloads dir, and `*.log`.

Be robust: some paths may be absent or permission-restricted; skip and note
skipped ones. Do not chase entries that are empty or still being written.

## Procedure

1. **Locate histories.** Resolve `$SHELL` and read `~/.zsh_history` /
   `~/.bash_history` if present. For extended zsh lines, decode epoch + duration
   and map to map timestamps.
2. **Filter and redact a window.** Only include entries newer than the window start
   (default last 24h; honor `--window <n>d` / `--dir <date>`). Keep enough raw
   lines to create an in-memory redacted copy, then discard raw values from the
   working set. Run the analytics below only on redacted text; do not token-dump
   everything.
3. **Extract history signals**:
   - **Repeated commands** — collapsed count of stem (command word); flag ones seen
     more than a threshold (default 3x) as possible inefficiency/loops.
   - **Failures** — lines containing error markers (`error:`, `failed`, `exit code`,
     `not found`, `No such file`, `Could not`, `EACCES`, `ENOENT`, `FAIL`).
   - **Unfinished work** — commands whose first token is `sudo`-less but trailing
     `&&` or a trailing backslash, or a heredoc that never closed, or a tailing
     `;`-chain that seems cutoff at the end of history.
   - **Relevant/env commands** — `cd`, `export`, `source`, `npm`, `git`, `pi`,
     `gh`, and network/exfil-only commands if present (note, do not run them).
4. **Extract agent/tool signals** (from pi/agent artifacts):
   - Tool results with `error`/`Error` statuses — group by tool name.
   - Recurring messages (e.g. edit matching "Could not find the exact text",
     "Found N occurrences", grep "regex parse error", tool argument rejects).
   - Termination reasons (`stop` `length`, `tool_use`, `error`) counts.
   - Cost/pruning markers: any "context", "reserve", "reduced", "token" budget
     warnings, or saved CSV cost/reasoning columns (report only; do not alter).
5. **Write the summary**, sections:
   - Header: date range, number of commands/artifacts scanned, sources used.
   - Top commands (most frequent), with counts.
   - Failures/errors and repeated failure themes.
   - Unfinished / possibly-abandoned work.
   - Notable agent/tool signals (grouped).
   - Sanity warnings (skipped/unreadable sources).
   - Always end with "next step" suggestions (1 per theme, actionable).

## Rules

- **Source-preserving.** Only write the redacted digest file; never modify the
  histories, agent artifacts, or any tool. `audit`/`report` are the only allowed
  writes.
- Keep the digest short: no raw dump of every command; a compact table where
  useful. Remove nothing from the originals.
- Do not run network commands or side-effecting analyses.
- If the user specified `--out`, write there; else default above.
- Stop ratio: prefer fewer, better-signal rows over a maximal inventory.
