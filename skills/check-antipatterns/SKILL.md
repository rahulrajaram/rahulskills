---
name: check-antipatterns
description: "Check an in-progress conversation and active code changes for anti-patterns, evidence-backed review findings, and immediate course corrections. Use for live checks, code review during active work, before risky operations, or when work feels stuck. Do not use for completed-session postmortems; use analyze-conversation."
argument-hint: "[conversation-jsonl] [--code PATH | --conversation-only]"
---

# Anti-Pattern Checker

## Intent and applicability

Perform a read-only check of the requested live conversation, source changes,
or both. A live conversation check does not automatically select code review.
An explicit source review does not require a transcript. Use `analyze-conversation`
for completed-session retrospectives.

## Inputs and local bindings

Select the target from the request: transcript path/runtime session identity,
`--code PATH`, or both when explicitly requested or needed for a specific
cross-cutting finding. For a bare live check, use the current conversation.

## Non-goals

This check does not select repairs, a complete source audit, retrospective
artifact generation, tool installation or external model review. Necessary
read-only context gathering remains within scope.

## Must not

Do not infer authority, a violation or comprehensive coverage from a keyword,
score or missing event. Do not print transcript secrets or fabricate unavailable
transcript context. A HIGH label alone cannot require stopping authorized work.

## Interaction and authority

Proceed with available target evidence. Resolve ambiguous session identity only
when transcript checking is selected; independent source review can continue.
Pause an affected action when evidence establishes an applicable authority or
safety boundary, carrying valid user decisions forward. Findings do not grant
permission for remediation; an existing implementation request may already do so.

## Procedure

## Preconditions and invocation

The implementation is `checker.py` beside this manifest and requires one
readable JSONL transcript path **only for transcript mode**:

```bash
python3 "$SKILL_DIR/checker.py" <conversation-jsonl>
```

`--code` and `--conversation-only` are skill-routing hints for the agent, not
arguments to `checker.py`; the script performs only transcript normalization
and heuristics. The agent performs the read-only code-review phase described
below.

In transcript mode only, use the runtime-provided current transcript path when available. Otherwise list
the newest candidates under `~/.codex/sessions` without displaying transcript
contents. If more than one is plausible, ask the user to select; do not guess.
The checker normalizes current and legacy Codex event streams as well as Claude
message streams. It prints to stdout and does not create a report file.

When transcript mode is selected and the transcript is missing, unreadable, malformed, or uses an unsupported
event shape, report the exact path and error and recommend
`analyze-conversation` only after the session is complete.

## Canonical rules

`rules.json` beside the checker is the human-facing rule taxonomy, with stable
`DIAG-*` identities and evidence categories mirrored in
`references/diagnostic-taxonomy.json` when the corpus is available. The current
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

Run this phase when the user requested source review, supplied `--code PATH`,
or selected both modes. Active workspace changes alone do not select it.
Read [references/code-review.md](references/code-review.md) completely before
that phase.

- With `--code PATH`, review that path in its repository context.
- With an explicit branch/commit range, review that diff even if the worktree
  is clean; resolve the requested base from local evidence.
- Otherwise use staged and unstaged changes as focus hints, then inspect their
  callers, sibling implementations, configuration, and relevant tests.
- If the repository is clean and no path or ref range was supplied, state that the code phase
  was skipped; do not invent a target.
- Do not install an indexer, dispatch another model, or spawn reviewers merely
  because code review is enabled. Use an already-present source index only when
  it materially improves evidence.
- Keep the review phase read-only. A separately authorized implementation task
  may act on findings after the check is complete.

## Completion and evidence

Return only the selected result groups, separated when both modes ran. Identify
the actual transcript/path and coverage window. Missing or unsupported inputs
are coverage limits, not a no-findings result. Disclose when reviewing your own changes.

For the transcript check:

- heuristic candidates with evidence locations, uncertainty and a concrete review step;
- observed practices, without assuming authorization or effectiveness;
- recommendations relevant to the current work; and
- the bounded heuristic signal score, labeled as non-comprehensive.

For the code review:

- actionable findings ordered by severity;
- exact file and line, review lens, concrete defect, and failure scenario;
- expected versus observed behavior and a focused remedy or test; and
- one review miss-cause tag per finding, or an explicit no-supported-findings
  statement.

State any evidence-backed correction or unresolved boundary; otherwise continue
the active authorized task. Severity alone does not create a gate. Do not mutate files, run remediation commands, or turn a
live check into a completed-session postmortem.

## Routing

- Use this skill during active work.
- Use `--conversation-only` when no source review is desired.
- Use `analyze-conversation` after a session is complete when a durable markdown
  report and longitudinal/tooling analysis are wanted.
- Emit findings that warrant durable follow-up as learning records in the
  shared shape (`references/learning-record.schema.json`), citing the
  diagnostic-taxonomy `rule_id`; a MetaBuilder campaign retrospective or the
  friction ledger consumes them from there.
