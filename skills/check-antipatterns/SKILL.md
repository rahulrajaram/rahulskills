---
name: check-antipatterns
description: "Inspect a supplied live or completed agentic session for execution anti-patterns, evidence-backed findings, and immediate course corrections. Use when checking how work was carried out or when execution feels stuck. For direct source/code review, use the separate code-review skill. Use analyze-conversation when a completed-session retrospective, durable markdown report, or longitudinal tooling analysis is wanted."
argument-hint: "[conversation-jsonl] [--lookback N]"
---

# Anti-Pattern Checker

## Intent and applicability

Inspect the execution of a supplied agentic session, whether it is still in
progress or already complete. Identify heuristic anti-pattern candidates,
observed practices, evidence limits, and useful course corrections. This is a
session check; it does not become a durable retrospective merely because the
session has ended.

## Inputs and local bindings

Use the supplied readable JSONL transcript path. When the runtime provides the
current session transcript, use that path for a live check. If no path is
provided, identify the current runtime session when available; otherwise list
newest candidates under `~/.codex/sessions` without displaying transcript
contents. If multiple candidates are plausible, ask the user to select one.

The implementation is `checker.py` beside this manifest. It accepts one
positional transcript path and the optional positive integer `--lookback`
(default `50`):

```bash
python3 "$SKILL_DIR/checker.py" <conversation-jsonl> [--lookback N]
```

The checker normalizes current and legacy Codex event streams and Claude
message streams. It prints to stdout and does not create a report file.

## Non-goals

This check does not repair files, perform a source/code audit, generate a
durable retrospective report, install tools, or invoke external model review.
Read-only inspection of relevant source or repository state may be used only
to corroborate what a session action did or what evidence means. Such
inspection must not produce code-review findings or expand the check into a
source review. Use the separate code-review skill for direct code-review
requests; it does not require a transcript.

## Must not

Do not infer authority, a violation, or comprehensive coverage from a keyword,
score, or missing event. Do not print transcript secrets or fabricate
unavailable transcript context. A HIGH label alone cannot require stopping
authorized work. Do not claim that unsupported detector modules, automatic
periodic execution, scope expansion detection, or every taxonomy rule is
implemented.

## Interaction and authority

Proceed with the supplied session evidence. Report a missing, unreadable,
malformed, or unsupported transcript as an exact coverage limitation. Preserve
valid user decisions and existing task authority. Findings do not grant
permission for remediation or change the authority of the underlying task.
If evidence establishes an applicable authority or safety boundary, state the
affected action and the corresponding pause or correction; otherwise continue
the authorized work.

## Procedure

1. Select the requested session transcript and establish its path, event
   format, normalized message count, and coverage window without exposing raw
   transcript contents.
2. Run `checker.py` with the supplied `--lookback` when one was given. In the
   implementation, credential, tool-discovery, and destructive-operation
   checks inspect the full normalized transcript; retry and preflight checks
   inspect only the last `lookback` normalized messages.
3. Interpret the output as prompts for evidence review. The six implemented
   checks are `RETRY_WITHOUT_DIAGNOSIS`, `CREDENTIAL_ASSUMPTION`,
   `MISSING_PREFLIGHT`, `TOOL_DISCOVERY_GAP`,
   `DESTRUCTIVE_OPERATION_WITHOUT_EXACT_GUARD`, and
   `IDLE_WITH_PENDING_WORK` (a turn that ends right after a non-blocking
   supervised-task status probe instead of a terminal-event wait).
4. Review the session sequence against the user's actual objective, grants and
   stop conditions: actions taken, evidence obtained, and claims made. Look for
   consequential execution failures such as repeated work without diagnosis,
   premature completion, lost authorization, unnecessary approval loops or
   scope drift where the transcript supports them. Separate this contextual
   judgment from the six automated heuristics; a zero heuristic score does not
   establish good execution.
5. Where needed, inspect nearby source or repository evidence solely to
   corroborate a recorded session action, keeping the result read-only and
   explicitly bounded.
6. Report findings with message locations, redacted evidence, uncertainty, and
   a concrete review or course-correction step. Include observed practices and
   the score's limits. Do not mutate files or turn this check into a
   completed-session retrospective.

`rules.json` is the canonical heuristic taxonomy; its stable `DIAG-*` IDs
correspond to the shared diagnostic taxonomy. Do not invent an implemented
detector for a contextual finding.

## Completion and evidence

Return the actual transcript path or runtime identity, source format, event and
normalized-message counts, and the analyzed window. Include heuristic
candidates with evidence locations, uncertainty, and a review step; observed
practices; recommendations relevant to current execution; and the bounded
heuristic signal score. The score is computed across the six implemented
checks only and is not a compliance, correctness, or completeness score.

Never print credential values or other transcript secrets; retain the
implementation's redaction behavior. Missing or unsupported inputs are
coverage limits, not a no-findings result. If a durable markdown report and
longitudinal/tooling analysis are wanted after completion, route explicitly to
`analyze-conversation`.

When findings need durable follow-through, record them using the shared
[learning-record schema](../../references/learning-record.schema.json), citing
session evidence and the applicable diagnostic ID (or null when none applies).
This preserves a finding for a consumer without turning the whole check into
a retrospective report.

## Routing

- Use this skill for live or completed execution inspection of a supplied
  agentic session.
- Use `analyze-conversation` for a completed-session retrospective and durable
  report, when explicitly requested; session completion alone does not force
  that route.
- Use the separate `code-review` skill for direct source/code review. No
  transcript is required for that skill.
