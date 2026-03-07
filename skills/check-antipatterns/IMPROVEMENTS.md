# Anti-Pattern Checker - Core Fixes Implemented

**Date:** 2026-01-11
**Version:** 2.0 (Core Fixes)

## Changes Made

### 1. Command Taxonomy (Eliminates False Positives)

**Problem:** `git status` run multiple times was flagged as "retry-without-diagnosis"

**Fix:** Added command classification:
```python
DIAGNOSTIC_COMMANDS = {'git status', 'kubectl get', 'kubectl describe', 'kubectl logs', ...}
ACTION_COMMANDS = {'pytest', 'helm install', 'kubectl apply', ...}
```

**Result:** Only ACTION commands trigger retry warnings. Diagnostic commands ignored.

**Test Case:**
```bash
git status
git status
git status
# Should NOT warn (diagnostic command)

helm install failed
helm install retry
# Should WARN (action command without diagnostics between)
```

---

### 2. Credential Detection in Bash Commands (Catches Real Issues)

**Problem:** Missed `DATA_PLANE_DB_PASSWORD=mvp-postgres-change-in-production`

**Fixes:**
1. Look specifically in Bash commands (not general content)
2. Fixed regex patterns:
   - Before: `r'\bPASSWORD\s*='` (failed with underscore)
   - After: `r'PASSWORD\s*='` (works with `_PASSWORD`)
3. Patterns: PASSWORD, SECRET, API_KEY, TOKEN, CREDENTIAL

**Result:** Now detects all credential assignments in Bash commands.

**Test Case:**
```bash
DATA_PLANE_DB_PASSWORD=hardcoded-value ./script.sh
# Should WARN HIGH: Credential Assumption
```

---

### 3. Broader E2E Test Detection

**Problem:** Only detected `pytest` with "e2e"/"integration"

**Fix:** Added patterns:
```python
E2E_TEST_PATTERNS = [
    r'pytest.*e2e',
    r'pytest.*integration',
    r'npx\s+playwright',      # NEW
    r'npm.*test.*e2e',         # NEW
    r'npm\s+run\s+test:e2e'    # NEW
]
```

**Result:** Catches Playwright, npm test, etc.

**Test Case:**
```bash
npx playwright test tests/e2e/
# Should WARN HIGH: Missing Preflight
```

---

### 4. Severity Indicators (Better UX)

**Problem:** All warnings looked the same

**Fix:** Added visual severity:
- 🔴 HIGH: Credentials, missing preflight
- 🟡 MEDIUM: Retry without diagnosis
- 🔵 LOW: Tool discovery gap

**Result:** Easy to prioritize fixes.

**Output:**
```
⚠️  WARNINGS (3 found):

1. 🔴 HIGH: Credential Assumption (Message 1645)
   - Found: _PLANE_DB_PASSWORD=mvp-postgres...
   → Suggestion: Read from K8s secret

2. 🟡 MEDIUM: Retry Without Diagnosis (Message 45-48)
   - Command: helm install...
   → Suggestion: Run diagnostics first
```

---

### 5. Differential Lookback Strategy (Best of Both Worlds)

**Problem:** 50-message window missed issues from earlier in conversation

**Fix:** Different windows for different patterns:
- **Full conversation**: Credentials, tool discovery (critical, one-time checks)
- **Last 50 messages**: Retries, preflight (recent context matters)

**Result:** Catches historical issues AND recent patterns efficiently.

**Code:**
```python
# Critical checks (full conversation)
warnings.extend(check_credential_usage(all_messages))
warnings.extend(check_tool_discovery(all_messages))

# Recent checks (last 50)
warnings.extend(check_retry_without_diagnosis(recent_messages))
warnings.extend(check_preflight_missing(recent_messages))
```

---

## Test Results

### Before Fixes
```
⚠️  WARNINGS (1 found):
1. Tool Discovery Gap
📊 COMPLIANCE SCORE: 93%
```
**Issues:** Missed 4 credential assumptions, false positive on git status

### After Fixes
```
⚠️  WARNINGS (5 found):
1. 🔴 HIGH: Credential Assumption (x4)
2. 🔵 LOW: Tool Discovery Gap
📊 COMPLIANCE SCORE: 66%
```
**Result:** Actually detecting real issues!

---

## What Works Now

✅ Detects hardcoded passwords in Bash commands
✅ No false positives on diagnostic commands
✅ Catches Playwright, npm test patterns
✅ Visual severity indicators
✅ Scans full conversation for critical issues
✅ Efficient (focused lookback for recent patterns)

## What's Still Missing (Phase 2)

- Error message tracking (detect ignored errors)
- Scope drift detection improvements
- Custom pattern definitions
- Historical metrics tracking
- Auto-fix suggestions

---

## Usage

```bash
# Via skill command
/check-antipatterns

# Direct invocation
python3 ~/.claude/skills/check-antipatterns/checker.py <conversation-file>
```

## Test Cases

See `test_cases.md` for comprehensive test scenarios.
