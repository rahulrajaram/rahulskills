---
name: check-antipatterns
description: "Check an in-progress conversation for known anti-patterns and immediate course corrections. Use for live checks, before risky operations, when work feels stuck, or for /check-antipatterns. Do not use for completed-session postmortems; use analyze-conversation."
argument-hint: "[conversation-jsonl]"
---

# Anti-Pattern Checker

Run a read-only live check against the current conversation and return warnings,
positive practices, a compliance score, and immediate corrections. This is a
course-correction primitive, not a retrospective report generator.

## Preconditions and invocation

The implementation is `checker.py` beside this manifest and requires one
readable JSONL transcript path:

```bash
python3 "$SKILL_DIR/checker.py" <conversation-jsonl>
```

Use the runtime-provided current transcript path when available. Otherwise list
the newest candidates under `~/.codex/sessions` without displaying transcript
contents. If more than one is plausible, ask the user to select; do not guess.
The checker prints to stdout and does not create a report file.

If the transcript is missing, unreadable, malformed, or uses an unsupported
event shape, report the exact path and error and recommend
`analyze-conversation` only after the session is complete.

## Canonical rules

`rules.json` beside the checker is the canonical rule taxonomy. The current
implementation analyzes the full transcript for credential/tool-discovery
signals and the last 50 messages for retry/preflight signals. Do not claim that
separate detector modules, `config.json`, automatic periodic execution, scope
expansion detection, or all fifteen rules are executable unless the code gains
those features.

Interpret heuristic findings as prompts to inspect evidence, not proof of a
violation. Never print credential values or other transcript secrets in output.

## Output contract

Return the checker's four result classes:

- warnings with evidence locations and a concrete correction;
- observed good practices;
- recommendations relevant to the current work; and
- the computed compliance score.

Then state whether work can continue, needs a local correction first, or needs
user authorization. Do not mutate files, run remediation commands, or turn a
live check into a completed-session postmortem.

## Routing

- Use this skill during active work.
- Use `analyze-conversation` after a session is complete when a durable markdown
  report and longitudinal/tooling analysis are wanted.
