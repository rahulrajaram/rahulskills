---
name: analyze-conversation
description: "Analyze a completed conversation retrospectively for anti-patterns, tooling gaps, and durable learnings, then generate a markdown report. Use for postmortems of finished sessions or when the user explicitly says /analyze-conversation. Do not use for live, in-progress checks; use check-antipatterns instead."
argument-hint: "[conversation-id]"
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

`/analyze-conversation [conversation-id]`

The underlying report generator can also be run directly:

```bash
python ~/.codex/skills/analyze-conversation/generate_report.py --current
python ~/.codex/skills/analyze-conversation/generate_report.py --id <conversation-id>
python ~/.codex/skills/analyze-conversation/generate_report.py <conversation-jsonl>
```

Other runtimes may install the same scripts beside their own manifest; invoke
the script from the active skill directory.

## Arguments

- `conversation-id` (optional): ID of conversation to analyze. If omitted, analyzes current conversation.
- `--current`: Analyze the most recently updated Codex JSONL session under `~/.codex/sessions`.

## Output

Generates a retrospective report beneath the active runtime:

- Codex transcripts: `~/.codex/retrospectives/[conversation-id]_retrospective.md`
- Claude transcripts: `~/.claude/retrospectives/[conversation-id]_retrospective.md`

The selected directory is created on first successful run.

## Shared taxonomy

Treat `check-antipatterns/rules.json` as the canonical live rule taxonomy when
both skills are installed. This retrospective may add longitudinal and tooling
findings, but it must not redefine the shared rule meanings.

Findings that warrant durable follow-up are emitted as learning records in the
shared shape (`references/learning-record.schema.json`); a MetaBuilder campaign
retrospective or the friction ledger consumes them from there.

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

This skill uses scripts beside this manifest (normally
`~/.codex/skills/analyze-conversation/` for Codex or
`~/.claude/skills/analyze-conversation/` for Claude Code):

- **analyzer.py**: Main analysis engine that parses JSONL conversations
- **patterns.py**: Pattern detectors for each anti-pattern type
- **generate_report.py**: CLI, Codex transcript normalization, and report writer

The analyzer reuses the analysis scripts created during retrospective analysis and enhances them with:
- Report generation in structured markdown
- Severity ranking (HIGH/MEDIUM/LOW)
- Actionable recommendations
- Success metric tracking
- Codex JSONL normalization for current `item_completed` command,
  file-change, MCP, collaboration, user-message, and agent-message events under
  `~/.codex/sessions`
- Observed transcript-span, command-runtime, failure, and tool-kind metrics
- Autonomy-break detection for user re-prompts and assistant workflow-routing questions

If `--current` cannot identify a readable transcript, list the newest candidate
JSONL files under `~/.codex/sessions` without printing their contents and ask the
user to choose. Do not silently analyze a different session. On malformed or
unreadable JSONL, report the path and parse/access error; do not emit a partial
report as if it were complete. Empty or unsupported input is an explicit
coverage failure and must not produce a successful no-findings report. A
conversation ID selects one exact file; never silently analyze a different
session because it is newer or merely has a similar filename.

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
