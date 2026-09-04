---
name: clean-code-refine
description: "Review or refactor code across multiple clean-code dimensions: behavior preservation, language idiom, function size, complexity, cohesion, FP/dataflow opportunities, testability, and simplicity. Use for clean-code review/refactoring or when fp-refine may conflict with broader readability."
argument-hint: "[file, module, repo path, or review-only]"
---

# Clean Code Refine

Review or refactor code using multiple aspect lenses instead of letting one
style preference dominate. Functional refactoring is one useful lens, but it
must not override behavior preservation, language idiom, small functions,
complexity reduction, cohesion, testability, or simplicity.

## Mode routing

- If the user asks for a **review**, **audit**, **assessment**, or explicitly says
  review-only, do not edit. Report prioritized findings and proposed changes.
- If the user asks to **fix**, **refactor**, **clean up**, or approves edits,
  make one coherent behavior-preserving change at a time and verify it.
- If the request is specifically FP-oriented, use `fp-refine` for that aspect but
  keep this skill's veto and evidence rules in force.

## Core workflow

1. Read repository instructions, nearby code, tests, and dependency manifests.
2. Identify the target language, framework, and available verification commands.
3. Build a short aspect map using
   [references/aspect-rubric.md](references/aspect-rubric.md) only as needed.
4. Rank findings by expected maintainability gain and behavior risk.
5. State the intended invariant and why the change is cleaner across aspects.
6. Edit narrowly, preserving public APIs and user-visible behavior unless the
   user explicitly authorizes a change.
7. Run the narrowest reliable test or static check, then broader verification
   when the focused check passes.

## Aspect passes

Evaluate the code through these lenses:

1. **Behavior and API safety** — observable behavior, persistence formats,
   public APIs, compatibility, and error semantics are preserved.
2. **Language idiom** — the solution fits the language and repository style.
3. **Function size and shape** — long functions are split around meaningful
   concepts, not arbitrary line counts.
4. **Cyclomatic/cognitive complexity** — branching, nesting, flags, and hidden
   control flow are reduced or made finite and explicit.
5. **Cohesion and coupling** — responsibilities are located together and
   unrelated policies are not mixed into one abstraction.
6. **Data flow and state ownership** — mutation, aliasing, and temporal coupling
   are visible or removed; invoke `fp-refine` when declarative state/data shapes
   are the right remedy.
7. **Error handling and observability** — expected failures are explicit, while
   logs, traces, and diagnostics remain useful.
8. **Testability** — pure logic becomes easier to test and integration behavior
   remains covered.
9. **Simplicity and deletion** — prefer deleting indirection or narrowing scope
   over adding a framework, DSL, or generic abstraction.

## Conflict resolution

When aspect recommendations conflict, use this priority order:

1. Preserve behavior, data formats, and public API contracts.
2. Match the language and repository idiom.
3. Reduce complexity and improve locality.
4. Improve testability and observability.
5. Improve dataflow, immutability, and declarative structure.
6. Add abstraction only when it clearly reduces repeated same-shaped code.

FP, DSLs, patterns, and architecture vocabulary do not win by default. A smaller
idiomatic function can be cleaner than a generalized pipeline. A direct match or
switch can be cleaner than a transition table. A clear loop can be cleaner than a
chain of combinators.

## Refactoring rules

- Prefer the smallest change that removes a real maintenance hazard.
- Keep functions small by extracting named concepts, not by scattering every
  line into a helper.
- Reduce complexity at the source: remove flags, nested conditionals, duplicate
  branches, temporal coupling, and mixed responsibilities before adding an
  abstraction.
- Do not introduce new dependencies, frameworks, public APIs, persistence
  changes, or behavior changes without explicit authorization.
- Stop and ask when the cleanest fix requires a product decision or incompatible
  API change.

## Completion evidence

Report:

- the highest-priority smell addressed;
- the invariant preserved;
- the aspect tradeoffs considered, including any FP/DSL vetoes;
- files changed;
- focused and broad verification results;
- deferred risks or follow-up recommendations.
