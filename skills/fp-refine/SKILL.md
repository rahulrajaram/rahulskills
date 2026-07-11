---
name: fp-refine
description: "Transform imperative code into functional-programming-first, immutable, DSL-oriented structures optimized for agent-amenability. Diagnose mutable state machines, long imperative workflows, string dispatch, scattered validation, exception control flow, and deep mutation, then apply declarative refactoring patterns. Use when the user says /fp-refine, 'make this functional', 'refactor to FP', or asks to make code more declarative or agent-friendly."
argument-hint: "[file, module, or repo path]"
---

# FP Refine

Refactor existing imperative code toward explicit data flow, immutable state,
typed outcomes, exhaustive dispatch, and declarative domain rules. Preserve
observable behavior unless the user explicitly authorizes a behavior change.

## Core workflow

1. Read repository instructions, nearby code, tests, and dependency manifests.
2. Identify the highest-leverage imperative pressure point:
   - mutable state machine;
   - long workflow with hidden data dependencies;
   - string or type-test dispatch;
   - scattered validation;
   - exception-driven expected control flow;
   - deep mutation of shared collections.
3. State the intended invariant and target shape before editing.
4. Make one coherent transformation at a time.
5. Run the narrowest reliable tests after each transformation.
6. Run the subsystem's broader verification once focused tests pass.

## Target shapes

- Model state transitions as `transition(state, event) -> Result[new_state, error]`
  backed by an explicit transition table.
- Model workflows as named, typed stages composed by a small executor.
- Replace open-ended string dispatch with enums or algebraic data types and an
  exhaustive match.
- Express validation as small pure rules returning typed results, then collect
  all failures declaratively.
- Reserve exceptions for exceptional faults; return `Result`/`Either` for
  expected domain outcomes.
- Return new immutable values instead of mutating shared structures in place.
- Represent stable business policy as validated data when that makes changes
  local, reviewable, and exhaustive.

## Selection rules

- Prefer the smallest transformation that removes a real hidden dependency.
- Follow existing functional libraries and house style before introducing a
  new abstraction.
- Do not add a bespoke FP framework when plain functions, frozen records, and
  explicit tables are sufficient.
- Keep names explicit. Avoid point-free style, deep transformer stacks, opaque
  macros, and type-level machinery that obscures the domain.
- Do not refactor working imperative code merely for aesthetic purity.
- Stop and ask before changing a public API, persistence format, or user-visible
  behavior that cannot be inferred from repository context.

## Detailed patterns

Read [references/pattern-catalog.md](references/pattern-catalog.md) only for the
specific transformation being applied. It contains complete before/after
examples for transition tables, typed pipelines, exhaustive dispatch,
composable validation, result types, immutable updates, and rule DSLs. Use its
heading index to load only the relevant section rather than the entire file.

## Completion evidence

Report the imperative pressure point removed, the invariant now made explicit,
the focused and broad verification results, and any intentionally deferred
areas. Do not claim improvement solely from introducing functional vocabulary;
the resulting control flow and state ownership must be easier to inspect.
