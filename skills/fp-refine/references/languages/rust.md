# Rust FP Refine Adapter

Use this adapter when applying `fp-refine` to Rust code.

## Rust-specific bias

Rust already gives you many FP-refine targets by default: algebraic data types,
pattern matching, ownership, immutability-by-default bindings, `Option`,
`Result`, and the `?` operator. In Rust, the danger is usually
**over-abstraction**, not insufficient functional vocabulary.

Good default tools:

- `enum` variants carrying state-specific data.
- Exhaustive `match` without a wildcard when new variants should force review.
- `Result<T, E>` and `Option<T>` with domain-specific error enums.
- Ownership and borrowing to make mutation local and explicit.
- Small pure functions with concrete domain types.

## What to avoid

- Do not replace clear `match` or a clear `for` loop with iterator cleverness
  merely to look functional.
- Do not add generic traits, associated-type machinery, macros, or typestate
  encodings unless they remove a proven class of errors and remain readable.
- Do not clone large values to satisfy an immutable-looking design; prefer
  ownership-aware structures and measured copy costs.
- Do not hide domain flow behind blanket trait implementations that are hard to
  grep.

## Recommended transformations

### State machines

Prefer an `enum` where each state variant owns only the data valid in that
state. A direct `match (state, event)` is often clearer than a table because the
compiler enforces coverage. Use a table only when the workflow is large,
configuration-like, or edited as policy data.

### Workflows

A Rust pipeline can be an ordinary function using `?`:

```rust
fn process_order(input: RawOrder) -> Result<FulfilledOrder, OrderError> {
    let validated = validate_order(input)?;
    let priced = calculate_pricing(validated)?;
    let charged = charge(priced)?;
    fulfill(charged)
}
```

This is often better than a custom pipeline abstraction. Introduce stage traits
or executors only when several workflows share the same machinery.

### Dispatch

Replace stringly dispatch with enums at parse boundaries. Avoid wildcard arms in
core domain matches when adding a variant should trigger compiler errors.

### Validation and rules

Use simple functions or arrays/slices of rule functions for repeated same-shaped
rules. If rules carry names, priorities, or messages, use a concrete struct. Do
not build a generic rule engine before the domain needs one.

### Error handling

Use domain error enums. Convert external errors at the boundary with `From`,
`thiserror`, or the repository's established style. Avoid `anyhow` in library or
domain code when callers need to handle specific cases.

## Clean-code checks

- Prefer concrete domain types over highly generic helpers.
- Keep lifetime complexity below the value of the refactor; sometimes an owned
  value is clearer than an intricate borrow graph.
- Run available checks: `cargo fmt`, focused tests, `cargo test`, and `cargo
  clippy` when used by the project.
