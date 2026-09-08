---
name: grilling
description: "Ask dependency-aware questions about a plan, decision, or idea. Default to an interview with the user; select researched multi-agent answers, linear runtime, or a gradient lattice only when requested. Use for grilling, stress-testing assumptions, or /grilling and /grill-me."
argument-hint: "[spec|factory|debate|gradient|linear-runtime] [topic or artifact] [--depth <n>] [--n <stems>] [--branch <b>] [--keep <k>] [--zones <z>] [--cap <nodes>]"
---

# Grilling

## Intent and applicability

Expose the questions on which a plan's conclusions depend. The default is a
question-only interview in which the user answers. In a selected speculative
mode, a respondent supplies researched candidate answers and the orchestrator
closes with an advisory recommendation. The griller remains question-only in
both cases; respondent answers and orchestrator synthesis are separate roles.

## Inputs and local bindings

Resolve the topic/artifact, existing decisions, selected mode, and any requested
depth, time/cost limits, backend/model or stop boundary from current context.
Inspect recoverable local facts instead of asking the user to remember them.
Bind genuinely variable artifact paths, host tools, transport, persistence and
backend capabilities from local evidence. Record missing/conflicting bindings
only when they affect the selected work; do not invent commands or reinterpret
a missing capability as permission to change the requested profile.

A requested depth is a useful-exploration budget in ordinary/linear native
modes; stop when further questions cannot change a decision. Gradient depth is
a hard ceiling with separate executed-node/resource constraints. The explicit
linear runtime instead bounds completed exchanges and each direct invocation's
timeout; it does not provide a nested-call or token budget.

## Procedure: select the mode before loading mechanics

| Selected mode | Who answers / execution | Read |
| --- | --- | --- |
| Default / ordinary interview | User answers; no speculative agents | [Ordinary interview](references/ordinary-interview.md) |
| `spec`, `speculative`, `-s`, `sx` | Native griller/respondent; linear projected answers | [Native linear modes](references/linear-speculative.md) and its shared question/state references |
| `factory` | Native linear mode plus a bounded respondent-owned specialist evidence wave | [Native linear modes](references/linear-speculative.md) |
| `debate` | Native linear mode with an explicit internal debate phase | [Native linear modes](references/linear-speculative.md) |
| `gradient` | Native roles in a bounded branching lattice, wave barriers and explicit budgets | [Lattice](references/lattice.md) and its required state/correctness references |
| Explicit `linear-runtime` profile | Bounded two-role `gptengage grill` calls with private checkpoints | [Linear runtime](references/linear-runtime.md) |

`factory` changes the evidence wave inside a linear interview; `gradient`
changes the topology of the whole inquiry. Mode names never imply debug output.
Do not load lattice mechanics for an ordinary interview or linear run.

The native named modes preserve direct respondent-to-specialist delegation.
Only an explicitly selected [mediated compatibility profile](references/compatibility-profile.md)
may change that transport. Host capability alone does not select it.
For an explicit raw graph/protocol request, load
[review-boundaries.md](references/review-boundaries.md) after preparing the
human review. For private machine transport or any offered resume/replay, load
[rendering-and-replay.md](references/rendering-and-replay.md) whether or not
the user asks to see internals.

## Non-goals

An ordinary interview does not select agent-authored answers, external backend
calls, a lattice, debug diagrams or implementation. Those can be selected by
an explicit user request or authorized parent scope. A comparison does not
select a software execution handoff. Supporting investigation and bounded
recovery remain available within the agreed objective and permissions.

## Must not

- Turn the griller into an advocate, critic, judge, answerer or recommender.
  Each substantive griller block must be a genuine question. A short verified
  fact may support a question; research gives the griller no decision authority.
- Present candidate answers, scheduled branches, model agreement or silence as
  user ratification. Preserve exact approved nodes/effects; invalidate only
  dependency descendants when an upstream premise changes.
- Put graph identifiers, ledgers, control deltas or diagnostics in an ordinary
  human turn. Render plain prose with turn-local question numbers. An explicit
  debug view follows the complete human review; it never substitutes for it.
- Claim an automated validator, private-content guarantee, hard nested token
  cap, atomic graph replay or resume merely because a skill describes it.
  Bind actual implementation and verification evidence. The linear runtime's
  checkpoints do not implement the native graph protocol or lattice scheduler.
- Fabricate findings, missing provider output, completion, sources or authority.
  Retain incomplete turns and unresolved evidence with their resolution paths.

## Interaction and authority

Preserve the selected interview: ask dependency-ready questions and wait for
the user's answers in ordinary mode. In speculative modes, reuse settled
scope, backend/data authority, budgets and decisions, then research and conduct
bounded turns autonomously. Ask at material unresolved choices about objective,
external data/backend, execution topology, budget guarantees or ratification;
prepare the concrete options and evidence first. Do not ask for routine method
choices or reconfirm unchanged approval through an alias or composed skill.

The user ratifies decisions unless they have explicitly delegated that exact
authority. A respondent cannot fill a user-judgment gap by guessing. Stop only
dependent work at a real unresolved boundary and continue useful authorized
preparation. Research, spawning and model agreement confer no implementation,
external-write or installation authority. Existing authority for the same
settled implementation scope remains valid; a grilling recommendation adds none.

## Completion and evidence

An ordinary run ends at the user's stop, no useful ready questions, or explicit
resolution paths for remaining uncertainties. Return questions during the
interview and a small plain-language review at a review boundary.

A native speculative close includes a bounded internal debate whenever
materially different positions remain; `debate` explicitly selects that phase.
Skip it only when there is no material split, explaining why. Preserve minority
findings. Then give the orchestrator's recommendation, implications, relevant
trajectory and evidence-supported effort range. Include the full autonomous
execution handoff when implementation planning is selected, not for every
comparison. These remain proposals until the required authority is supplied.

Report observed execution, actual bounds/usage when available, unresolved
capabilities, provisional claims and what requires user judgment. A file's
presence is not evidence that its runtime is installed, and manual review is
not automated proof. Resumability, when selected, requires verified state
reconstruction and dependency/ratification checks even when all state stays
private. Keep user prose readable without requiring any protocol knowledge.

When a MetaBuilder harness campaign follows, transfer each resolved question
into the harness brief's `grilling.resolved_questions` with its basis and
evidence digest; `metabuilder-harness-design` then grills only what remains
uncovered.
