---
name: fp-refine
description: "Transform imperative code toward explicit data flow, immutable state, typed outcomes, exhaustive dispatch, and declarative domain rules. Use for targeted FP-style refactoring; use clean-code-refine for broad clean-code review where FP may conflict with simplicity, idiom, function size, or complexity."
argument-hint: "[file, module, or repo path]"
---

# FP Refine

Refactor existing imperative code toward explicit data flow, immutable state,
typed outcomes, exhaustive dispatch, and declarative domain rules. Preserve
observable behavior unless the user explicitly authorizes a behavior change.

FP is a lens, not the final judge of code quality. Apply it only when the
resulting control flow, state ownership, and domain rules become easier to
inspect than the original code.

## Core workflow

1. Read repository instructions, nearby code, tests, and dependency manifests.
2. Identify the language and read the relevant language adapter if one exists:
   - Python: [references/languages/python.md](references/languages/python.md)
   - Rust: [references/languages/rust.md](references/languages/rust.md)
   - TypeScript/JavaScript: [references/languages/typescript.md](references/languages/typescript.md)
   - Java: [references/languages/java.md](references/languages/java.md)
   - Common Lisp: [references/languages/common-lisp.md](references/languages/common-lisp.md)
3. Identify the highest-leverage imperative pressure point:
   - mutable state machine;
   - long workflow with hidden data dependencies;
   - string or type-test dispatch;
   - scattered validation;
   - exception-driven expected control flow;
   - deep mutation of shared collections.
4. State the intended invariant, target shape, and clean-code risks before
   editing.
5. Make one coherent transformation at a time.
6. Run the narrowest reliable tests after each transformation.
7. Run the subsystem's broader verification once focused tests pass.

## Clean-code vetoes

Stop, choose a smaller change, or switch to `clean-code-refine` when the FP
transformation would likely:

- make functions longer or raise cyclomatic/cognitive complexity;
- replace obvious code with framework, macro, type-level, or point-free
  cleverness;
- fight the language's idioms or the repository's established style;
- obscure error paths, logging, tracing, or debugging;
- introduce dependency, performance, allocation, or API costs that the task did
  not justify;
- split code into so many tiny functions that the domain story becomes harder
  to follow.

When a broader review is requested, or when FP conflicts with small functions,
idiomatic style, testability, or simplicity, use `clean-code-refine` as the
orchestrator and treat this skill as one aspect pass.

## Target shapes

- Model state transitions as `transition(state, event) -> Result[new_state, error]`
  backed by an explicit transition table or an idiomatic exhaustive match.
- Model workflows as named, typed stages composed by a small executor only when
  the original workflow has real hidden dependencies.
- Replace open-ended string dispatch with enums, algebraic data types, tagged
  unions, or sealed hierarchies and exhaustive handling.
- Express validation as small pure rules returning typed results, then collect
  failures declaratively.
- Reserve exceptions for exceptional faults; represent expected domain outcomes
  explicitly in the language's idiom.
- Return new immutable values instead of mutating shared structures in place
  when that improves local reasoning.
- Represent stable business policy as validated data when that makes changes
  local, reviewable, and exhaustive.

## Selection rules

- Prefer the smallest transformation that removes a real hidden dependency.
- Follow existing functional libraries and house style before introducing a new
  abstraction.
- Do not add a bespoke FP framework when plain functions, frozen/readonly
  records, enums, tagged unions, and explicit tables are sufficient.
- Keep names explicit. Avoid point-free style, deep transformer stacks, opaque
  macros, and type-level machinery that obscures the domain.
- Do not refactor working imperative code merely for aesthetic purity.
- Stop and ask before changing a public API, persistence format, or user-visible
  behavior that cannot be inferred from repository context.

## Detailed patterns

Read [references/pattern-catalog.md](references/pattern-catalog.md) only for the
specific transformation being applied. It defines the language-neutral pressure
points, target shapes, anti-patterns, and sequencing. Then read only the
language adapter that matches the target code when syntax, idiom, or verifier
choice matters.

## Completion evidence

Report the imperative pressure point removed, the invariant now made explicit,
the language-specific idiom used, the clean-code vetoes checked, the focused and
broad verification results, and any intentionally deferred areas. Do not claim
improvement solely from introducing functional vocabulary; the resulting code
must be easier to inspect, test, and modify.
