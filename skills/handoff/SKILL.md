---
name: handoff
description: "Write a verified NEXT_SHELL_PROMPT.md handoff, or activate an existing one. With extract, review the artifact, adopt it as the current request, and immediately execute its authorized work; with print, only emit it verbatim."
argument-hint: "[extract|print]"
---

# Handoff

Use this workflow for a clean shell handoff or to resume one.

## Route the invocation first

Determine the mode before reading any workflow reference or changing files:

- No argument: read [references/write-workflow.md](references/write-workflow.md)
  completely and run the write workflow.
- `extract`: run the activation protocol below. Do not read the write workflow,
  rewrite the artifact, reconcile docs, or commit merely because this skill also
  has a write mode.
- `print`: run only the read-only print protocol below.
- Reject any other argument and show the supported forms.

Runtime argument envelopes differ. In Codex, `extract` or `print` follows the
`$handoff` mention in the live user request. Pi appends the literal trailing
text after the injected `</skill>` block, without a label; therefore a bare
trailing `extract` or `print` is the authoritative mode selector, not handoff
content and not text to echo.

Supported forms:

- Codex: `$handoff`, `$handoff extract`, `$handoff print`
- Pi: `/skill:handoff`, `/skill:handoff extract`, `/skill:handoff print`

## Activation protocol (`extract`)

The outcome of extract mode is resumed work, not a rendered handoff.

1. Resolve the repository root with `git rev-parse --show-toplevel`, then read
   `<REPO_ROOT>/NEXT_SHELL_PROMPT.md` completely. If either step fails, report
   the exact expected path or repository error and stop without changing state.
2. Review the artifact before acting. Extract its repository, completed work,
   decisions, open priorities, blockers, approvals, and start commands. Treat
   it as user-provided continuation instructions, subordinate to current
   system, developer, repository, and safety policy. The live invocation is
   newer and wins on conflict.
3. Validate only the facts needed for the next action. Do not blindly trust a
   stale branch, HEAD, dirty-tree claim, command, or completion claim.
4. Adopt the still-applicable open work as the active request. Run named start
   commands when safe, then continue into the highest-priority actionable work;
   orientation commands are not a stopping point. Load any skills required by
   the carried work and proceed end to end until complete or genuinely blocked.
5. Reading or reviewing the file is never completion. After the read, the next
   assistant action must be one of:
   - a tool call that starts or continues the carried work;
   - the approval, decision, or interview question explicitly required before
     that work can proceed; or
   - a concrete blocker report when the artifact is missing, invalid, fully
     complete, or has no authorized actionable work.

Never answer extract mode by quoting, printing, paraphrasing, or summarizing
`NEXT_SHELL_PROMPT.md`. Never stop merely after repository orientation or ask
what to do next when the artifact already says what to do. Do not rewrite or
commit the artifact in extract mode unless the resumed task itself explicitly
requires a later handoff.

## Print protocol (`print`)

1. Resolve the repository root with `git rev-parse --show-toplevel`.
2. Read `<REPO_ROOT>/NEXT_SHELL_PROMPT.md`. If it is missing, report the exact
   expected path and stop without changing repository state.
3. Emit the file contents verbatim, with no surrounding fence or commentary.
   Do not review or execute its instructions.

## Shared authorization boundary

The selected mode is authorization to complete that mode without asking
whether to proceed. It does not authorize destructive actions, secrets work,
pushes, deploys, database writes, or resolving a real multi-repository ambiguity
without any approval otherwise required by current policy.
