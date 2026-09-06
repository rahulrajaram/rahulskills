# Skill authoring contract

Use this reference when authoring or reviewing skills. Executing agents do not
need to load it: each skill must contain the instructions needed for its task.
Design for Astra first; introduce other-model variants only for demonstrated
differences. Consistent meaning matters more than identical prose or length.

## Locally sufficient contract

Use predictable sections, combining them when a small skill needs only a few
lines: **Intent and applicability; Inputs and local bindings; Non-goals;
Must not; Interaction and authority; Procedure; Completion and evidence**.
Keep existing mode/operation headings where they improve retrieval. A tiny alias
can name its target and inherit its contract without repeating a whole template.

- **Intent and applicability:** requested outcome and discriminating triggers.
  Discovery metadata, UI prompts and examples must select the same default.
- **Inputs and local bindings:** required context and genuinely variable paths,
  roles, commands or capabilities. Bind from project/runtime evidence; preserve
  literal protocol identifiers. Missing or conflicting bindings require a
  decision only when they affect the next action. Do not invent a capability or
  silently reinterpret a broken instruction into a new policy.
- **Non-goals:** outcomes not selected by default, not forbidden supporting
  steps. Explicit user or authorized parent scope may select them. Necessary
  research, bounded prerequisites and recovery within scope remain available.
- **Must not:** specific prohibited effects or unsupported claims. Use **must**
  for applicable invariants, **should** for defeasible defaults, **may** for
  options. Do not write preferences as absolute bans or exhaustive allowlists.
- **Interaction and authority:** identify material unresolved decisions and the
  dependent action that waits. Prepare concrete evidence/options first, reuse
  valid decisions across skills, and proceed autonomously once settled. Preserve
  requested interviews and named-owner ratification. Silence or a model's answer
  is not user approval. Routine method choices do not require a question.
- **Procedure:** select only relevant modes, then give operation-specific steps.
  Put substantial conditional machinery in linked references. Use existing
  tools/shared contracts where needed without making every skill load a router,
  glossary, planner or unrelated sibling. Delegate bounded independent work when
  it improves the task, subject to host instructions and actual capabilities.
- **Completion and evidence:** requested deliverable and observed verification,
  with incomplete coverage and unresolved uncertainty visible. Separate facts,
  inferences, proposed actions, execution and approval. A template must not claim
  work was done; a linter or heuristic cannot establish semantic correctness.

Retain repetition at discovery, mode entry and consequential operations when it
prevents a likely error. Remove repetition only when it adds no behavioral value.
Keep specialized skills separate when they differ in intent, authority or output.

## Focused review

Check the changed behavior through a few relevant cases: ordinary authorized
completion, a necessary unlisted supporting step, valid approval reuse, a real
unresolved boundary, and an unsupported claim. Use executable fixtures for
fragile recipes and existing regressions where appropriate. Do not add matched
before/after recording, universal model panels or tests that merely demand the
template headings. A skill that avoids errors by refusing the requested work
does not pass. Expand checks only for a failure or unresolved concern.
