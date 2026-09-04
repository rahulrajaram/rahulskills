# TypeScript / JavaScript FP Refine Adapter

Use this adapter when applying `fp-refine` to TypeScript or JavaScript code.

## TypeScript-specific bias

TypeScript is strongest when finite domain shapes are represented as discriminated
unions and when data tables are checked with `as const`/`satisfies`. Prefer
plain functions and repository idiom before importing an FP framework.

Good default tools:

- Discriminated unions with a stable `kind` or `type` tag.
- Exhaustive `switch`/`match` helpers using `never` checks.
- `readonly` fields, `ReadonlyArray<T>`, and immutable update helpers.
- `as const` and `satisfies` for declarative tables.
- Lightweight local `Result<T, E>` unions when expected domain failures compose.

## What to avoid

- Do not introduce `fp-ts`, `effect`, `neverthrow`, or a pipe library unless the
  codebase already uses it or the user approves the dependency.
- Do not hide simple promise flow behind deep effect stacks.
- Do not use `any`, broad index signatures, or catch-all defaults in code whose
  purpose is exhaustive domain modeling.
- In JavaScript-only projects, do not write TypeScript-shaped abstractions that
  the runtime cannot enforce unless JSDoc/checking is already in use.

## Recommended transformations

### State and dispatch

Use discriminated unions for states and events. In TypeScript, a missing switch
case should produce a `never` error. In JavaScript, co-locate the allowed strings
in a frozen object and validate unknown values at boundaries.

### Workflows

Use named functions and explicit data types. A simple top-to-bottom `async`
function with extracted pure helpers can be cleaner than a generic pipeline.
Introduce `pipe`/`andThen` only when many stages share the same result-threading
shape.

### Validation and rule DSLs

Use readonly rule arrays checked by `satisfies`:

```typescript
const rules = [
  { name: 'has_items', check: hasItems, message: 'Order must have items' },
] as const satisfies readonly ValidationRule<Order>[]
```

Make priority, ordering, and conflict behavior explicit when they matter.

## Clean-code checks

- Keep type-level programming shallow enough that the domain is visible.
- Avoid callback nesting that raises cognitive complexity.
- Run available checks: focused tests, then `npm test`/`pnpm test`, `tsc --noEmit`,
  eslint, or the package's own scripts when present.
