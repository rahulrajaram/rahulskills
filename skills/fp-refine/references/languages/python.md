# Python FP Refine Adapter

Use this adapter when applying `fp-refine` to Python code.

## Python-specific bias

Python benefits from explicit data flow, but it does not enforce ADTs,
immutability, or exhaustiveness as strongly as Rust or TypeScript. Prefer simple,
idiomatic Python before importing FP vocabulary.

Good default tools:

- `@dataclass(frozen=True)` or an existing `attrs`/Pydantic model for domain
  values.
- `Enum`, `StrEnum`, `Literal`, or small tagged dataclasses for finite cases.
- `tuple`, `frozenset`, and read-only mappings for stable domain collections.
- `typing.Protocol`, `TypedDict`, `NewType`, and named dataclasses when they
  clarify boundaries.
- `typing.assert_never` or `typing_extensions.assert_never` with mypy/pyright
  when approximating exhaustive matches.

## What to avoid

- Do not add a `Result` dependency, pipe library, persistent collection package,
  or validation framework unless the repository already uses it or the user
  approves the new dependency.
- Do not turn direct Python into Haskell cosplay. A named helper function is
  usually better than nested `map`, `filter`, `partial`, and combinators.
- Do not assume `match` is exhaustive. Python will not prove this without type
  checker support and careful shapes.
- Do not replace ordinary boundary exceptions, such as file or network errors,
  with custom results throughout the call stack unless that makes domain error
  handling clearer.

## Recommended transformations

### State machines

Use enums or tagged frozen dataclasses for states and events. Choose a transition
table when adding states should be a local data edit. Choose `match` when the
state-specific data is easier to see in a direct branch.

Keep effects separate from the pure transition function. A transition may return
`(new_state, effects)` where `effects` are command values interpreted elsewhere.

### Workflows

Extract named stages from long functions only where mutable temporaries hide
real dependencies. A good Python pipeline often remains a plain top-to-bottom
function with well-named intermediate values and small stage helpers.

Use a small executor only if multiple workflows share error-threading or effect
collection.

### Dispatch

Replace repeated string dispatch with `Enum`/`StrEnum` or a tagged dataclass
family. If using `match`, avoid a broad `case _:` inside domain logic; parse and
reject unknown values at the boundary instead.

### Validation and rules

Use frozen rule records when there are several same-shaped checks:

```python
T = TypeVar("T")

@dataclass(frozen=True)
class Rule(Generic[T]):
    name: str
    check: Callable[[T], bool]
    message: str
```

Return all validation failures when the caller can act on a complete list. Use
short-circuit validation only when later rules depend on earlier normalized data.

### Expected failures

Prefer repository idiom. Options include:

- a small local `Ok`/`Err` union when many domain functions compose;
- domain-specific return dataclasses such as `Accepted`/`Rejected`;
- ordinary exceptions at I/O or framework boundaries;
- `None` only for truly optional values, not for multi-reason failure.

## Clean-code checks

- Keep transformed functions short enough to read without jumping through many
  helpers.
- Watch import weight: a refactor that adds a framework must pay for itself.
- Run available Python checks: focused tests first, then `pytest`, `ruff`,
  `mypy`, or `pyright` if the project already uses them.
