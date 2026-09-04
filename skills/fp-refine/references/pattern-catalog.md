# FP Refine Pattern Catalog

## Contents

- Identity and purpose
- Diagnostic patterns
- Transformation patterns
- Clean-code compatibility checks
- Harmful FP anti-patterns
- Decision heuristics and execution sequence

## Identity and Purpose

Use this catalog to transform code toward **explicit data flow, immutable state,
typed outcomes, exhaustive dispatch, and declarative domain rules**. The taste
criterion is agent-amenability: after the change, another agent should be able
to inspect the domain logic without simulating hidden mutation or irregular
control flow.

This catalog is language-neutral. For concrete syntax and idiom, read only the
adapter matching the target code:

- [Python](languages/python.md)
- [Rust](languages/rust.md)
- [TypeScript/JavaScript](languages/typescript.md)
- [Java](languages/java.md)
- [Common Lisp](languages/common-lisp.md)

## Diagnostic patterns

### Pattern 1: Mutable state machines

**Symptoms:** status/state fields reassigned over time; `if state == ...` or
`switch state` chains; transitions buried inside business logic; auxiliary
fields such as retries, flags, or last errors that alter the transition rules.

**Why it resists agents:** the transition topology is invisible. Adding a state
requires searching all state checks and mentally simulating execution.

**Severity:** critical.

### Pattern 2: Long imperative workflows

**Symptoms:** functions longer than roughly 30 lines; mutable intermediate
variables; comments like “step 1 / step 2” as the only structure; early returns,
throws, logging, I/O, and notifications interleaved with computation.

**Why it resists agents:** hidden data dependencies make each step depend on the
history of every previous assignment.

**Severity:** high.

### Pattern 3: Branching dispatch on strings or untyped values

**Symptoms:** `if/elif/else`, `switch`, or `case` dispatch on strings, integer
codes, magic constants, object type names, or loosely typed dictionaries; the
same dispatch value checked in multiple places; catch-all defaults that hide
unknown cases.

**Why it resists agents:** the complete case set is not represented in one
place, and the compiler or type checker cannot help.

**Severity:** high.

### Pattern 4: Scattered validation and business rules

**Symptoms:** duplicated validation checks; policy logic embedded in handlers or
I/O code; rules whose ordering or interaction is implicit; no boundary between
raw and validated data.

**Why it resists agents:** a rule change requires rediscovering every partial
copy and guessing which boundary owns validity.

**Severity:** medium-high.

### Pattern 5: Exception-based expected control flow

**Symptoms:** ordinary domain outcomes represented as exceptions; catch blocks
that perform business logic; signatures that hide expected failure modes.

**Why it resists agents:** exceptions create invisible edges between producers
and handlers.

**Severity:** medium.

### Pattern 6: Deep mutation of shared structures

**Symptoms:** functions modify objects passed by reference; multiple functions
mutate the same request/session structure; defensive copying appears as a
workaround for aliasing; bugs depend on call order.

**Why it resists agents:** local reasoning fails because any alias may have
changed the value.

**Severity:** medium.

## Transformation patterns

### Transform 1: State machine -> explicit transition model

**Target:** separate the topology of the machine from transition computation and
side effects.

Useful shapes include:

```text
State:       enumerated/tagged/sealed variants, each carrying needed data
Event:       enumerated/tagged/sealed variants
Transition:  (State, Event) -> Result<State, DomainError>
Effects:     separately declared commands or notifications emitted by a transition
Executor:    small interpreter, or an idiomatic exhaustive match if a table adds no clarity
```

Prefer a transition table when adding or reviewing states should be a data edit.
Prefer a direct exhaustive match when the language already makes the transition
space obvious and a table would add indirection.

### Transform 2: Imperative workflow -> named typed stages

**Target:** a sequence of named transformations where each stage has an explicit
input, output, and error shape.

```text
Stage:     named function, Input -> Result<Output, Error>
Pipeline:  ordered composition of stages
Executor:  minimal error-threading helper, only if it removes duplicated plumbing
```

Do not pipeline a simple linear function. Use this when mutable temporaries,
early exits, or interleaved effects make the data dependencies hard to see.

### Transform 3: Branching dispatch -> finite domain model + exhaustive handling

**Target:** replace open-ended strings, integer codes, and ad hoc type tests with
a finite representation and exhaustive handling.

```text
Variant set: enum / ADT / tagged union / sealed hierarchy
Handler:     match / switch / table that covers every variant
No catch-all: unknown values fail at the boundary, not inside business logic
```

The win is not merely fewer `if` statements. The win is that adding a case has a
single declaration site and reliable review or compiler pressure on all handler
sites.

### Transform 4: Scattered validation -> composable rule collection

**Target:** all rules for one domain concept live together, share a schema, and
return collected failures rather than throwing or short-circuiting accidentally.

```text
Rule:       name + predicate/function + typed failure
RuleSet:    ordered or unordered collection, with ordering explicit when it matters
Boundary:   RawInput -> Result<ValidatedInput, list<ValidationError>>
Consumer:   accepts ValidatedInput instead of rechecking raw data
```

Use a rule table when there are several same-shaped rules or when policy changes
frequently. Avoid hiding genuinely distinct logic behind a generic rule engine.

### Transform 5: Exception control flow -> explicit expected outcomes

**Target:** expected domain failures appear in the return type or result value.
Exceptions remain for programmer errors, infrastructure faults, cancellation,
and other exceptional conditions appropriate to the language.

```text
Result<T, E> = Ok(T) | Err(E)
Producer: returns explicit result for expected failures
Caller:   handles both success and failure locally
Boundary: translates infrastructure exceptions to domain errors once
```

Do not introduce noisy `Result` wrappers where the host language has a clearer
idiom for the same boundary.

### Transform 6: Mutable data -> immutable transformation functions

**Target:** values are created once; updates produce new values or explicitly
owned mutable builders whose lifetime is local and obvious.

```text
Input value -> pure transformation -> new output value
```

This is most useful for shared request/session/domain structures. It is less
useful in hot loops, builders, parsers, or places where local mutation is an
idiomatic performance implementation detail hidden behind a pure interface.

### Transform 7: Business rules as data

**Target:** repeated policy of the same kind becomes validated data, so adding a
case means adding an entry rather than editing control flow.

```text
Rule definition: name + applicability + action/decision + priority/conflict policy
Rule set:        data table reviewed as domain policy
Executor:        stable interpreter with tests
```

Use this for pricing, routing, permission, notification, eligibility, and other
families of repeated same-shaped rules. Do not invent a DSL for two unrelated
cases.

## Clean-code compatibility checks

Before editing, state how the target transform affects these dimensions:

- **Function size:** will this reduce long functions or merely move length into
  a new executor?
- **Cyclomatic/cognitive complexity:** will branches become finite and local, or
  will abstraction force readers to jump through more files?
- **Idiomatic language use:** does the target language already have a standard
  way to express this?
- **Naming and locality:** are stages/rules named in domain language, close to
  their use, and easy to search?
- **Debuggability:** can a failure still be logged, traced, and reproduced?
- **Testability:** are pure rules/stages now easier to unit-test, and are
  integration boundaries still covered?
- **API and performance cost:** does the change add allocation, dependencies,
  public API churn, or migration work that the problem does not justify?

If the transform fails these checks, shrink it or hand off to a broader
clean-code review.

## Harmful FP anti-patterns

Avoid these even when they are technically functional:

- **Point-free or tacit style** where the reader must decode combinators before
  seeing the domain operation.
- **Deep monad/effect stacks** that make an ordinary business change require
  understanding a framework.
- **Opaque macros or code generation** that hide the domain shape from the agent.
- **Excessively generic type-level programming** where concrete domain types
  would be clearer.
- **Pipeline theater** that wraps a short linear function in abstractions.
- **DSL sprawl** where rules are data but validation, schema, ordering, and
  conflict behavior are implicit.

Rule of thumb: if an agent must understand the abstraction mechanism before it
can understand the domain logic, the abstraction is hurting.

## Decision heuristics

### Do not transform when

1. The code is simple, short, and already locally obvious.
2. Performance is critical and the proposed immutable shape has not been
   measured or bounded.
3. The code is a leaf utility with no workflow, state, or rule-set character.
4. The repository's established style would make the new abstraction an island.
5. The domain has only a couple of genuinely unrelated cases.

### Strongly consider transforming when

1. There is an implicit state machine.
2. There are more than three same-shaped cases or rules.
3. Agents or humans will repeatedly modify the same workflow or policy surface.
4. Side effects are interleaved with pure domain decisions.
5. Expected outcomes are hidden in exceptions or sentinel values.

## Execution sequence

1. Inventory the target for the six diagnostic patterns and rank by severity.
2. Start with implicit state machines when present.
3. Separate side effects from pure decisions.
4. Replace untyped branching dispatch with finite domain models.
5. Co-locate repeated rules and validation boundaries.
6. Extract long workflows into named stages only where dependencies are hidden.
7. Make shared data immutable where aliasing blocks local reasoning.
8. Make expected outcomes explicit in the language's idiom.

After each step, re-run clean-code compatibility checks. A smaller, idiomatic
partial transform is better than a pure-looking design that is harder to read.
