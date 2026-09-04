# Clean Code Aspect Rubric

Use this rubric when a clean-code request needs more structure than a direct
local edit. It is a guide for ranking and tradeoffs, not a checklist that must
produce a finding in every category.

## Finding format

For each material finding, capture:

```text
Aspect: one primary aspect, with secondary aspects if relevant
Smell: concrete code shape, not a generic principle
Risk: how it makes changes, testing, or debugging harder
Preferred change: smallest behavior-preserving improvement
Vetoes: what would make the refactor worse
Verification: focused check plus broader check if needed
```

## Aspects

### Behavior and API safety

Look for public signatures, persistence formats, serialization shapes, CLI flags,
network payloads, error codes, and timing/ordering contracts.

Preferred changes preserve these surfaces. If changing them would be cleaner,
stop and ask.

### Language idiom

Look for code fighting the host language: Java written as Haskell, Python written
as Java, Rust hidden behind macros, TypeScript erased with `any`, or Common Lisp
logic hidden behind dynamic variables.

Preferred changes use common language mechanisms and house style.

### Function size and shape

Long functions are a symptom, not proof. Split when a region has a separate
reason to change, a separate invariant, or a reusable boundary. Do not split
purely to satisfy a line count.

Good extractions have names that explain domain intent and reduce the caller's
cognitive load.

### Cyclomatic and cognitive complexity

Look for deeply nested conditionals, flags that change meaning mid-function,
multiple exits with duplicated cleanup, catch-all dispatch, boolean parameter
modes, and temporal coupling through mutable variables.

Preferred changes flatten guard clauses, make finite cases explicit, extract
same-shaped branches, and remove mode flags. Avoid replacing visible branches
with invisible dynamic dispatch unless it improves locality.

### Cohesion and coupling

Look for modules that mix parsing, validation, persistence, UI, policy, and side
effects. Also look for rules duplicated across layers.

Preferred changes move responsibilities to existing homes or create the smallest
new boundary that matches the repository's architecture.

### Data flow and state ownership

Look for shared mutable request/session/domain structures, implicit state
machines, in-place mutation by callees, and hidden dependencies on call order.

Preferred changes make state transitions, ownership, and side effects explicit.
Use `fp-refine` when immutable values, typed outcomes, transition models, or
rule tables are the right remedy.

### Error handling and observability

Look for swallowed errors, broad catches, expected outcomes hidden as exceptions,
error strings with no type, logs too far from the failing decision, and refactors
that would remove diagnostic context.

Preferred changes expose expected outcomes while preserving useful logs, traces,
and operator messages.

### Testability

Look for logic that can only be tested through slow integration paths,
non-deterministic time/randomness, hidden global state, and side effects mixed
with pure decisions.

Preferred changes isolate pure logic and boundary adapters, then add or update
focused tests when the repository has a test pattern.

### Simplicity and deletion

Look for unused abstraction, over-generalized helpers, framework-shaped code for
one use case, and DSLs without validation or a clear owner.

Preferred changes delete, inline, or narrow abstractions before adding new ones.
Add a framework only when repeated same-shaped code and verification justify it.

## Ranking guidance

Rank findings highest when they combine high change frequency, high behavior
risk, and a small safe refactor. Rank style-only preferences low. If a proposed
change requires broad rewrites, dependency additions, or public API migration,
report it separately from safe local cleanup.
