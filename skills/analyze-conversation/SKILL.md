---
name: analyze-conversation
description: "Analyze a completed conversation retrospectively for anti-patterns, tooling gaps, and durable learnings, then generate a markdown report. Use for postmortems of finished sessions or when the user explicitly says /analyze-conversation. Do not use for live, in-progress checks; use check-antipatterns instead."
argument-hint: "[conversation-id | transcript-path] [--runtime claude|codex|pi] [--include-subagents]"
---

# Conversation Analyzer

Performs comprehensive post-mortem analysis of conversations to extract:
- Systemic anti-patterns (retry-without-diagnosis, credential assumptions, scope creep, etc.)
- Tooling opportunities (repeated commands that should be automated)
- Universal rules violated (using the shared infrastructure rule taxonomy)
- Recommendations for improvement

## Autonomy Routing

When invoked, generate the retrospective artifact directly. Do not turn the
analysis into a choice between `/goal` and direct execution. If the report
identifies clear low-risk wording or tooling fixes and the user asked to fix the
problem, continue into those fixes after reporting the findings; otherwise stop
after producing the retrospective.

## Usage

`/analyze-conversation [conversation-id | transcript-path]`

Bind `SKILL_DIR` to the absolute directory containing this `SKILL.md`: Claude
Code supplies it as `${CLAUDE_SKILL_DIR}`; in other runtimes use the directory
the skill was loaded from (for example `~/.codex/skills/analyze-conversation`).
Substitute that absolute path; do not rely on an unset shell variable.

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR:-<directory containing this SKILL.md>}"
python3 "$SKILL_DIR/generate_report.py" --current                 # current session (auto runtime)
python3 "$SKILL_DIR/generate_report.py" --current --runtime claude --include-subagents
python3 "$SKILL_DIR/generate_report.py" --id <conversation-id> [--runtime claude|codex|pi]
python3 "$SKILL_DIR/generate_report.py" <conversation-jsonl>
python3 "$SKILL_DIR/generate_report.py" --list [--runtime ...]    # candidate paths only
```

Supported JSONL transcripts (format is detected from the records, not the path):

- **Claude Code**: `${CLAUDE_CONFIG_DIR:-~/.claude}/projects/<slug>/<session-id>.jsonl`,
  where `<slug>` is the absolute cwd with every non-alphanumeric character
  replaced by `-`. Tool-result records are not counted as human turns;
  `isMeta` injections are skipped. `--include-subagents` merges
  `<session-id>/subagents/*.jsonl` by timestamp (subagent actions and tool
  results only; the parent-authored subagent prompt is not a human turn).
- **Codex**: `${CODEX_HOME:-~/.codex}/sessions/**/*.jsonl` (`item_completed`
  and legacy `response_item` streams).
- **Pi**: `${PI_CODING_AGENT_DIR:-~/.pi/agent}/sessions/--<cwd with / as ->--/*.jsonl`
  (`message` records with `user`, `assistant`, and `toolResult` roles; `bash`,
  `read`, `write`, `edit`, `grep` tool calls map to the shared tool names).

The project root used for context checks comes from the transcript's own
recorded `cwd` (Claude record `cwd`, Codex `session_meta`, Pi `session`
header), never from decoding the lossy directory slug.

### opencode runtime (SQLite sessions)

opencode stores sessions in SQLite (`~/.local/share/opencode/opencode.db`),
not JSONL. Use the `--opencode` flag; the selected session is exported to
the normalized shape and analyzed by the standard pipeline. The analyzed
session identity is printed in the output — never assume which session ran.

```bash
python3 "$SKILL_DIR/generate_report.py" --opencode                        # most recently updated session
python3 "$SKILL_DIR/generate_report.py" --opencode <session-id-or-slug>   # exact, then substring match
python3 "$SKILL_DIR/opencode_adapter.py" --list                           # list candidate sessions
```

Adapter: `opencode_adapter.py` (exports message+part rows to normalized
JSONL: text parts → text items, tool parts → tool-call items with bash
commands; reasoning/step parts omitted for Codex-parity). Sessions that
export zero supported messages are refused with an explicit error rather
than producing an empty report.

## Arguments

- `conversation-id` / `--id ID` (optional): select one exact session. Claude
  matches `<id>.jsonl` exactly; Codex and Pi match a filename fragment and
  refuse an ambiguous match.
- `transcript-path` (optional): analyze this JSONL file directly.
- `--current` (default when no id or path is given): analyze the current
  session. `--runtime auto` (default) resolves Claude Code when `CLAUDECODE`
  or `CLAUDE_CODE_SESSION_ID` is set, then Codex when a `CODEX_*` session
  variable (other than `CODEX_HOME`) is set, then Pi when `PI_CODING_AGENT`
  is set; otherwise it takes the newest transcript across the Claude and Pi
  directories for the cwd and all Codex sessions. For Claude, the current
  session is `$CLAUDE_CODE_SESSION_ID` when set, else the newest `*.jsonl` in
  the cwd's project slug directory. For Codex it is the newest session file;
  for Pi, the newest file in the cwd's session directory.
- `--runtime claude|codex|pi|auto`: restrict `--current`, `--id`, and `--list`.
- `--include-subagents`: merge Claude Code subagent transcripts.
- `--list`: print up to ten newest candidate paths (no contents) and exit.

## Output

Generates a retrospective report beneath the transcript's runtime home:

- Claude Code: `${CLAUDE_CONFIG_DIR:-~/.claude}/retrospectives/[conversation-id]_retrospective.md`
- Codex: `${CODEX_HOME:-~/.codex}/retrospectives/[conversation-id]_retrospective.md`
- Pi: `${PI_CODING_AGENT_DIR:-~/.pi/agent}/retrospectives/[conversation-id]_retrospective.md`

The selected directory is created on first successful run. The report header
names the transcript path, runtime adapter, and included subagent count.

## Shared taxonomy

Treat `check-antipatterns/rules.json` as the canonical live rule taxonomy when
both skills are installed. This retrospective may add longitudinal and tooling
findings, but it must not redefine the shared rule meanings.

## What It Analyzes

### Anti-Patterns Detected

1. **Credential Anti-Patterns**
   - Hardcoded passwords/secrets
   - Credential assumptions that require contextual review
   - Assumed credentials without verification

2. **Retry Patterns**
   - Commands retried without checking logs/events between attempts
   - Blind retries without diagnosis

3. **Scope Drift**
   - Task expansions beyond original request
   - Creating new services/components without asking user

4. **Tool Blindness**
   - Existing tools not discovered or used
   - Manual commands when automation exists

5. **Verification Gaps**
   - Unverified external values (IPs, URLs, endpoints)
   - Integration tests run without preflight checks

6. **Command Repetition**
   - Same command run 3+ times (tool opportunity)
   - Manual command sequences that should be scripted

### Report Sections

The generated report includes:

- **Executive Summary**: Top anti-patterns, tool needs, rule violations
- **Detailed Anti-Pattern Analysis**: Each instance with context and fix
- **Tool Opportunities**: Commands that should be automated
- **Rule-related candidates**: Stable shared rule IDs, evidence categories, and review counts
- **Recommendations**: Priority-ranked action items
- **Success Metrics**: Comparison with target behavior

## Example Output

```markdown
# Conversation Retrospective: 5e6380e9-fb47-493b-9944-b029d43dae40

## Summary
- Total turns: 532
- Duration: ~8 hours
- Commands executed: 162
- Anti-patterns found: 13

## Anti-Patterns Found

1. **Retry-Without-Diagnosis**: 10 instances
   - Example: `git status` retried 3 times without checking logs
   - Fix: Run `git status --verbose` or check git daemon logs

2. **Credential Assumption**: 1 instance
   - Example: Emitted a credential-like assignment in assistant text
   - Fix: Review source, authorization, and exposure without printing or decoding secrets

3. **Tool Blindness**: 5 tools not discovered
   - Repeated command sequences that may justify a project-specific helper
   - Impact: potential automation opportunity; no avoided-command estimate is established

## Tool Opportunities

- **Repeated 10x**: git status → Review whether project-specific automation is warranted
- **Repeated 5x**: kubectl get pods → Review whether project-specific automation is warranted
- **Repeated 5x**: pytest → Review whether project-specific automation is warranted

## Rule-related candidates

- **DIAG-002** (diagnose before retry): 10 candidates
- **DIAG-001** (credential assumption): 1 candidate
- **DIAG-005** (tool discovery): 5 candidates

## Recommendations

1. **HIGH**: Review repeated test failures and decide whether a project preflight is warranted
2. **HIGH**: Review credential handling against the project’s authorized mechanism
3. **HIGH**: Review retry evidence and add a diagnostic helper only if the project needs one
4. **MEDIUM**: Consider documenting available tools for discoverability
5. **MEDIUM**: Consider a verification reminder where the evidence supports it
```

## Implementation

This skill uses scripts beside this manifest (`$SKILL_DIR`):

- **generate_report.py**: CLI, Codex transcript normalization, and report writer
- **session_discovery.py**: runtime detection, current-session and id
  discovery, Claude/Pi normalization, subagent merging, and recorded-cwd
  lookup (byte-identical copy ships with `check-antipatterns`)
- **analyzer.py**: Main analysis engine that parses normalized JSONL
- **patterns.py**: Pattern detectors for each anti-pattern type
- **opencode_adapter.py**: opencode SQLite export

The analyzer adds:
- Report generation in structured markdown
- Severity ranking (HIGH/MEDIUM/LOW)
- Actionable recommendations
- Success metric tracking
- Observed transcript-span, command-runtime, failure, and tool-kind metrics
- Autonomy-break detection for user re-prompts and assistant workflow-routing questions

If `--current` cannot identify a readable transcript, the command exits
non-zero and lists the newest candidate paths without printing their contents;
ask the user to choose (or run `--list`). Do not silently analyze a different
session. On malformed or unreadable JSONL, report the path and parse/access
error; do not emit a partial report as if it were complete. Empty or
unsupported input is an explicit coverage failure and must not produce a
successful no-findings report. A conversation ID selects one exact file; never
silently analyze a different session because it is newer or merely has a
similar filename.

## Benefits

- **Learn from past mistakes**: Identify patterns that led to wasted effort
- **Improve processes**: Generate actionable recommendations
- **Track progress**: Compare metrics across conversations
- **Build better tools**: Discover automation opportunities
- **Refine system prompts**: Identify rules that need enforcement

## Related Skills

- `/check-antipatterns`: Real-time anti-pattern detection during active work
- Both skills work together in a learning loop:
  1. `/check-antipatterns` prevents issues during work
  2. `/analyze-conversation` identifies what wasn't caught
  3. Learnings improve both skills over time
