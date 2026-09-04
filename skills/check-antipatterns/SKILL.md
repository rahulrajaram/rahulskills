---
name: check-antipatterns
description: "Check an in-progress conversation and active code changes for anti-patterns, evidence-backed review findings, and immediate course corrections. Use for live checks, code review during active work, before risky operations, or when work feels stuck. Do not use for completed-session postmortems; use analyze-conversation."
argument-hint: "[conversation-jsonl] [--code PATH | --conversation-only]"
---

# Anti-Pattern Checker

Run a read-only live check against the current conversation and, when code is in
scope, the active code changes. Return transcript warnings, observed good
practices, evidence-backed code-review findings, and immediate corrections. This
is a course-correction primitive, not a retrospective report generator.

## Preconditions and invocation

The implementation is `checker.py` beside this manifest and requires one
readable JSONL transcript path:

```bash
python3 "$SKILL_DIR/checker.py" <conversation-jsonl>
```

`--code` and `--conversation-only` are skill-routing hints for the agent, not
arguments to `checker.py`; the script performs only transcript normalization
and heuristics. The agent performs the read-only code-review phase described
below.

Use the runtime-provided current transcript path when available. Otherwise list
the newest candidates under `~/.codex/sessions` without displaying transcript
contents. If more than one is plausible, ask the user to select; do not guess.
The checker normalizes current and legacy Codex event streams as well as Claude
message streams. It prints to stdout and does not create a report file.

If the transcript is missing, unreadable, malformed, or uses an unsupported
event shape, report the exact path and error and recommend
`analyze-conversation` only after the session is complete.

## Canonical rules

`rules.json` beside the checker is the human-facing rule taxonomy. The current
implementation analyzes the full normalized transcript for credentials, tool
discovery, and destructive operations, and the last 50 normalized messages for
retry and preflight signals. The reported heuristic signal score covers only
those five implemented checks. It is not a compliance or completeness score.

Do not claim that separate detector modules, `config.json`, automatic periodic
execution, scope expansion detection, or every rule in the taxonomy is
executable unless the code gains those features.

Interpret heuristic findings as prompts to inspect evidence, not proof of a
violation. Never print credential values or other transcript secrets in output.

## Code-review phase

Unless `--conversation-only` was requested, run a code-review phase when the
user supplied `--code PATH` or the current workspace has active code changes.
Read [references/code-review.md](references/code-review.md) completely before
that phase.

- With `--code PATH`, review that path in its repository context.
- Otherwise use staged and unstaged changes as focus hints, then inspect their
  callers, sibling implementations, configuration, and relevant tests.
- If the repository is clean and no path was supplied, state that the code phase
  was skipped; do not invent a target.
- Do not install an indexer, dispatch another model, or spawn reviewers merely
  because code review is enabled. Use an already-present source index only when
  it materially improves evidence.
- Keep the review phase read-only. A separately authorized implementation task
  may act on findings after the check is complete.

## Output contract

Return two clearly separated result groups.

For the transcript check:

- warnings with evidence locations and a concrete correction;
- observed good practices;
- recommendations relevant to the current work; and
- the bounded heuristic signal score, labeled as non-comprehensive.

For the code review:

- actionable findings ordered by severity;
- exact file and line, review lens, concrete defect, and failure scenario;
- expected versus observed behavior and a focused remedy or test; and
- one review miss-cause tag per finding, or an explicit no-supported-findings
  statement.

Then state whether work can continue, needs a local correction first, or needs
user authorization. Do not mutate files, run remediation commands, or turn a
live check into a completed-session postmortem.

## Routing

- Use this skill during active work.
- Use `--conversation-only` when no source review is desired.
- Use `analyze-conversation` after a session is complete when a durable markdown
  report and longitudinal/tooling analysis are wanted.
