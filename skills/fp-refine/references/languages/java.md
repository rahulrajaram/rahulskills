# Java FP Refine Adapter

Use this adapter when applying `fp-refine` to Java code.

## Java-specific bias

Modern Java can express many FP-refine shapes with records, sealed interfaces,
enums, switch expressions, immutable collections, and small pure services. The
best Java refactor usually stays recognizably Java rather than importing a
foreign FP style.

Good default tools:

- `enum` for simple finite values.
- `sealed interface` plus `record` variants for states and domain outcomes.
- Switch expressions for exhaustive handling where the project's Java version
  supports them.
- Records and `List.copyOf`/`Map.copyOf` for immutable values.
- Repository-standard validation and error-handling libraries if already in use.

## What to avoid

- Do not introduce Vavr, custom Either monads, or a broad result framework unless
  the codebase already uses it or the user approves the dependency.
- Do not replace clear imperative Java with dense streams when a loop is more
  readable.
- Do not create sealed hierarchies in old Java projects where build targets or
  team style make them an isolated novelty.
- Do not flatten useful domain exceptions into generic errors when callers need
  typed handling.

## Recommended transformations

### State machines and dispatch

For growing finite domains, prefer `sealed interface` variants or enums with an
exhaustive switch expression. Keep state-specific data on the state variant
instead of nullable fields on one mutable object.

### Workflows

Extract long service methods into named private methods or package-level domain
functions with clear input/output types. Use a pipeline/result abstraction only
when it removes repeated error-threading across several workflows.

### Validation and rules

Use records for same-shaped rules when there are several business policies of
one kind. Make order and priority explicit. Keep validation near the raw-input
boundary and pass validated domain types inward when practical.

### Error handling

For expected domain failures, use sealed outcome types or repository-standard
result objects. Keep exceptions for exceptional faults and framework boundaries.

## Clean-code checks

- Respect the project's Java version and framework conventions.
- Prefer small cohesive methods over stream/combinator cleverness.
- Run available checks: focused tests, then Maven/Gradle test, formatting, and
  static analysis configured by the project.
