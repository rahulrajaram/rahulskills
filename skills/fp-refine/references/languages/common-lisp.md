# Common Lisp FP Refine Adapter

Use this adapter when applying `fp-refine` to Common Lisp code.

## Common Lisp-specific bias

Common Lisp already supports functional style, generic functions, conditions,
macros, and data-driven programming. The main risk is hiding domain logic behind
macros or dynamic behavior that an agent cannot inspect locally.

Good default tools:

- Small pure functions over explicit data.
- `defstruct`/CLOS objects with read-only or conventionally immutable fields
  when state ownership matters.
- Keywords or typed structures for finite domain states, with centralized
  transition definitions.
- Conditions and restarts used deliberately, not as invisible ordinary control
  flow.
- Simple data tables for rule families.

## What to avoid

- Do not create opaque macros whose expansions must be understood before the
  domain can be edited.
- Do not rely on dynamic variables for hidden dependencies in domain logic.
- Do not turn a small function into a mini-language before the rule family is
  large and regular enough to justify it.
- Do not obscure expected outcomes inside broad `handler-case` forms.

## Recommended transformations

### State machines and dispatch

Centralize the transition topology as data or as explicit generic methods. Use a
table when policy review matters; use generic dispatch when behavior genuinely
belongs to variant-specific methods. Keep effects separate from pure transition
choice.

### Workflows

Prefer named functions and explicit threading of values. Macros that define
pipelines are acceptable only when the emitted structure is simple, documented,
and the workflow definition remains readable as domain data.

### Validation and rules

Use lists/vectors of rule records or simple structs when many rules share a
schema. Make rule names, messages, and ordering explicit.

### Error handling

The condition system can be clearer than ad hoc result objects when restarts are
part of the domain interaction. For ordinary pure validation, explicit `ok`/`err`
values may be easier to compose. Choose the shape that exposes all expected
outcomes at the call site.

## Clean-code checks

- Keep macro expansion and dynamic scope from becoming prerequisites for domain
  understanding.
- Preserve REPL-debuggability.
- Run available checks through the project's test runner, ASDF system tests, and
  style/lint tools when configured.
