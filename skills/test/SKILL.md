---
name: test
description: Run focused tests with available supervision or the native project runner, preserving output, timeouts and required coverage. Use when running test suites (npm test, pytest, playwright, etc.)
argument-hint: "<test-command>"
---

# Test Runner with Overwatch

## Intent and applicability

Run the selected project checks and report actual results. Prefer an existing
working `overwatch` service when supervision improves the run; use the native
runner for ordinary tests when the service is unavailable or adds no useful
control. Explicitly requested supervision must be preserved or reported unavailable.

## Inputs and local bindings

Resolve the project command, working directory, interpreter/environment and
required coverage. A daemon may have a different PATH: use explicit executable
paths or a reviewed subprocess environment for required dependencies. Do not
dump credentials while diagnosing environment differences.

## Non-goals

Testing does not select tool/daemon installation, full-suite repetition after
every edit, or fixes beyond the active task. Necessary diagnosis and authorized
local repairs remain autonomous.

## Must not

Do not start/install a daemon merely because this skill loaded, run a test twice
because a launched supervised task's state is unknown, or claim cancelled,
timed-out, partial or unobserved output as a passing suite.

## Interaction and authority

Use existing test authorization and choose routine runner details. If supervision
is unavailable before launch, run ordinary tests natively and explain the fallback.
If a launch may have succeeded, inspect its task state before any retry. Missing
required infrastructure blocks its dependent check, not independent preparation.

## Procedure

## Why Use This

- **Streaming output**: See test progress in real-time instead of waiting for completion
- **Early exit**: Stop on first failure to save time (optional)
- **Timeouts**: Prevent hung tests with configurable timeouts
- **Consistent behavior**: Same execution policy across all test runs

## Command Format

```bash
overwatch run --profile <profile> --stream [options] -- <test command>
```

## Profiles

| Profile | Max Runtime | Silent Timeout | Use For |
|---------|-------------|----------------|---------|
| `pytest` | 20 min | 2 min | Python tests |
| `npm_test` | 30 min | 5 min | JS/TS tests, Playwright |
| `generic` | 30 min | 10 min | Other test frameworks |

## Key Options

- `--stream`: Show real-time output (recommended)
- `--cancel-on-output "pattern"`: Stop when pattern appears in output
- `--soft-timeout N`: Override max runtime (seconds)
- `--silent-timeout N`: Override no-output timeout (seconds)
- `--quiet`: Only show summary, not full output

## Cancel Patterns (Choose Carefully)

Pick patterns that won't false-positive on variable names or log strings:

| Framework | Good Pattern | Why |
|-----------|--------------|-----|
| Playwright/Jest | `" failed"` | Matches "1 failed" (lowercase, space-prefixed) |
| pytest | `"FAILED "` | Matches "FAILED tests/..." (trailing space) |
| Go | `"--- FAIL:"` | Go test failure prefix |
| Cargo | `"test result: FAILED"` | Rust test summary |

## Examples

### Run E2E tests with streaming (let all tests complete)
```bash
overwatch run --profile npm_test --stream -- npm run test:e2e
```

### Run pytest, stop on first failure
```bash
overwatch run --profile pytest --stream --cancel-on-output "FAILED " -- pytest tests/
```

### Run with custom timeout (5 minutes max)
```bash
overwatch run --profile generic --stream --soft-timeout 300 -- go test ./...
```

### Quick check - just see if tests pass
```bash
overwatch run --profile npm_test --quiet -- npm test
```

## When NOT to Cancel Early

Don't use `--cancel-on-output` when:
- You need to see all failures (not just the first)
- The test output might contain the pattern in non-failure context
- You're debugging and need full output

## Completion and evidence

Record the command, scope, exit status and relevant failures/coverage limits.
Use task cancellation/status APIs when supervised; with a native runner retain
process identity and output and use the host's timeout/cancellation mechanisms.
A wrapper exit or disconnected stream alone does not prove all child processes
stopped. Confirm termination where it matters before retrying heavy work.
Run the narrowest reliable checks and actual required gates. Broaden or repeat
only for changed risk, missing/stale coverage or a diagnosed failure.
