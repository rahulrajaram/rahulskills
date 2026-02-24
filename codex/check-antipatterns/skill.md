---
name: check-antipatterns
description: Real-time checking of current conversation against known anti-patterns
author: system
version: 1.0.0
---

# Anti-Pattern Checker

Monitors current conversation for anti-patterns and provides immediate warnings and suggestions.

## Usage

`/check-antipatterns`

Analyzes the CURRENT conversation up to this point and provides:
- ⚠️ **Warnings**: Anti-patterns detected
- ✅ **Good Practices**: Positive behaviors observed
- 📊 **Compliance Score**: Percentage of rules followed
- 💡 **Recommendations**: Actionable next steps

## What It Checks

### 1. Retry-Without-Diagnosis
**Detection**: Same command run 2+ times in last 10 messages without diagnostic commands between attempts

**Warning Example**:
```
⚠️ Retry-Without-Diagnosis (Message 45-48)
   - Command 'pytest tests/e2e/' run 2 times
   - No diagnostic commands between attempts
   → Suggestion: Check logs before retrying:
     kubectl logs deployment/control-plane --tail=50
```

### 2. Credential Usage Without Verification
**Detection**: Message contains PASSWORD/SECRET/KEY/TOKEN but no `kubectl get secret` in last 20 messages

**Warning Example**:
```
⚠️ Potential Credential Assumption (Message 30)
   - Used PASSWORD env var without reading from K8s secret
   → Suggestion: Read from K8s secret:
     kubectl get secret <name> -o jsonpath='{.data.key}' | base64 -d
```

### 3. Scope Expansion
**Detection**: Creating new files in directories not mentioned in original request

**Warning Example**:
```
⚠️ Potential Scope Expansion (Message 55)
   - Creating new service 'myproject-discovery' not in original task
   → Suggestion: Confirm with user:
     "This expands scope to include service discovery. Should I proceed?"
```

### 4. Missing Preflight Checks
**Detection**: About to run pytest with "integration" or "e2e" but no cluster/pod status checks in last 10 messages

**Warning Example**:
```
⚠️ Missing Preflight Check (Message 50)
   - About to run E2E test
   - No environment validation in last 10 messages
   → Suggestion: Run preflight validation:
     myproject-preflight --test e2e
     OR manually verify: clusters running, pods ready, services healthy
```

### 5. Tool Discovery Gap
**Detection**: Conversation length > 50 messages but never ran `ls ~/.local/bin` or `ls ./scripts/`

**Warning Example**:
```
⚠️ Tool Discovery Gap (Message 75)
   - 75 messages without checking for existing tools
   → Suggestion: Check for existing tools:
     ls ~/.local/bin ~/bin ./scripts/
     cat TOOLS.md (if exists)
```

### 6. Unverified External Values
**Detection**: Using IP addresses or URLs without running verification commands

### 7. Error Message Skimming
**Detection**: Command failed but next action doesn't reference the error message

### 8. All 15 Universal Rules
Checks compliance with all infrastructure work rules:
1. Never hardcode credentials
2. Always diagnose before retry
3. Stop and ask when scope expands
4. Verify entire dependency chain
5. Discover tools before reinventing
6. External values must be verified
7. Read error messages completely
8. Verify prerequisites before complex operations
9. Document assumptions explicitly
10. One command, one purpose
11. Check pod events on K8s failures
12. Verify ConfigMap/Secret exists before using
13. Background services require health checks
14. Cross-cluster operations need network verification
15. Integration tests are not unit tests

## Example Output

```
Analyzing current conversation for anti-patterns...

⚠️  WARNINGS (2 found):

1. Retry-Without-Diagnosis (Message 45-48)
   - Command 'pytest tests/e2e/' run 2 times
   - No diagnostic commands between attempts
   → Suggestion: Check logs before retrying:
     kubectl logs deployment/control-plane --tail=50

2. Missing Preflight Check (Message 50)
   - About to run E2E test
   - No environment validation in last 10 messages
   → Suggestion: Run myproject-preflight --test e2e

✅ GOOD PRACTICES (3 found):

1. Credential Retrieved from Secret (Message 30)
   - Used kubectl get secret instead of hardcoding
   ✓ Follows Rule 1: Never hardcode credentials

2. Diagnostic Before Retry (Message 35-38)
   - Ran kubectl describe before retrying failed command
   ✓ Follows Rule 2: Diagnose before retry

3. Scope Confirmation (Message 40)
   - Asked user before expanding scope
   ✓ Follows Rule 3: Stop and ask when scope expands

RECOMMENDATIONS:
  - Fix 2 warnings before proceeding
  - Consider implementing myproject-preflight tool
  - Current anti-pattern score: 2/15 (87% compliance)

📊 COMPLIANCE SCORE: 87% (Target: 95%+)
```

## How It Works

This skill analyzes the last N messages (default: 50) of the current conversation and runs multiple pattern detectors:

1. **Load Conversation**: Reads current conversation JSONL file
2. **Extract Recent Messages**: Focuses on last 50 messages for performance
3. **Run Detectors**: Each detector checks for specific anti-pattern
4. **Identify Good Practices**: Also recognizes positive behaviors
5. **Generate Report**: Shows warnings, good practices, and compliance score

## Implementation

Located in `~/.claude/skills/check-antipatterns/`:

- **checker.py**: Main checker that coordinates all detectors
- **detectors/**: Individual pattern detectors
  - `retry.py`: Retry-without-diagnosis detector
  - `credentials.py`: Credential assumption detector
  - `scope.py`: Scope expansion detector
  - `preflight.py`: Missing preflight check detector
  - `tools.py`: Tool discovery gap detector
- **rules.json**: 15 universal rules for infrastructure work

## When to Use

- **Periodically**: Every ~50 messages during long conversations
- **Before major operations**: Before running E2E tests, deployments, or complex multi-step operations
- **When feeling stuck**: If repeatedly encountering failures
- **After significant work**: Before wrapping up a feature or task

## Benefits

- **Real-time feedback**: Catch anti-patterns while working, not after
- **Learning tool**: Reinforces good practices through positive recognition
- **Course correction**: Adjust behavior before wasting too much effort
- **Prevents bad habits**: Consistent checking builds better reflexes

## Related Skills

- `/analyze-conversation`: Post-mortem analysis of completed conversations
- Both skills work together in a learning loop:
  1. `/check-antipatterns` prevents issues during work
  2. `/analyze-conversation` identifies what wasn't caught
  3. Learnings improve both skills over time

## Configuration

The checker can be tuned via `~/.claude/skills/check-antipatterns/config.json`:

```json
{
  "lookback_messages": 50,
  "retry_threshold": 2,
  "tool_discovery_threshold": 50,
  "preflight_lookback": 10,
  "credential_lookback": 20,
  "severity_levels": {
    "credential": "HIGH",
    "retry": "MEDIUM",
    "scope": "MEDIUM",
    "preflight": "HIGH",
    "tools": "LOW"
  }
}
```

## Future Enhancements

- **Auto-fix suggestions**: Generate exact commands to fix detected issues
- **CI/CD integration**: Run as pre-commit hook or in CI pipeline
- **Custom detectors**: Allow users to define project-specific anti-patterns
- **Metrics tracking**: Store compliance scores over time
- **Learning from violations**: Update detectors based on new anti-patterns discovered by `/analyze-conversation`
