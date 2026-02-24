---
name: test
description: Run tests with overwatch for streaming output, early failure detection, and timeout management. Use when running test suites (npm test, pytest, playwright, etc.)
allowed-tools: Bash
---

# Test Runner with Overwatch

Run test commands through `overwatch` for better visibility and control.

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

## Prerequisites

The overwatch daemon must be running:
```bash
overwatch serve  # In a separate terminal, or use systemd
```
