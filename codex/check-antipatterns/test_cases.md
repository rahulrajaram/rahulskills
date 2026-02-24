# Anti-Pattern Checker Test Cases

These test cases validate the checker detects real issues and avoids false positives.

## Test Case 1: Credential Assumption (Should WARN)

**Scenario:** Using hardcoded password in Bash command without reading from K8s secret

**Bash command:**
```bash
DATA_PLANE_DB_PASSWORD=mvp-postgres-change-in-production ./scripts/bootstrap-kind.sh
```

**Expected:**
```
⚠️ HIGH: Credential Assumption (Message X)
   - Found PASSWORD= in Bash command without kubectl get secret in last 20 messages
   → Suggestion: Read from K8s secret: kubectl get secret <name> -o jsonpath='{.data.password}' | base64 -d
```

## Test Case 2: Diagnostic Command Repetition (Should NOT warn)

**Scenario:** Running git status multiple times (diagnostic command)

**Bash commands:**
```bash
git status
git status
git status
```

**Expected:** No warning (git status is a diagnostic, not an action being retried)

## Test Case 3: Action Retry Without Diagnosis (Should WARN)

**Scenario:** Retrying helm install without checking logs

**Bash commands:**
```bash
helm install customer-platform ./helm/customer-platform
# Command fails
helm install customer-platform ./helm/customer-platform
# Retry without kubectl logs/describe between
```

**Expected:**
```
⚠️ MEDIUM: Retry Without Diagnosis (Message X-Y)
   - Command: helm install customer-platform...
   → Suggestion: Run diagnostics before retrying: kubectl logs, kubectl describe, kubectl get events
```

## Test Case 4: E2E Test Without Preflight (Should WARN)

**Scenario:** Running Playwright E2E test without checking service health

**Bash command:**
```bash
npx playwright test tests/prompt-to-deployment.spec.ts
```

**Expected:**
```
⚠️ HIGH: Missing Preflight (Message X)
   - About to run E2E test: npx playwright test
   - No service validation in last 10 messages
   → Suggestion: Run preflight checks: kubectl get pods, curl /health
```

## Test Case 5: Credential Read from Secret (Good Practice)

**Scenario:** Reading password from K8s secret before use

**Bash command:**
```bash
kubectl get secret postgres-admin -n customer-platform -o jsonpath='{.data.password}' | base64 -d
```

**Expected:**
```
✅ GOOD PRACTICES (1 found):
1. Credential From Secret (Message X)
   - Used kubectl get secret instead of hardcoding
   ✓ Follows Rule 1: Never hardcode credentials
```

## Test Case 6: Multiple Test Patterns (Should WARN for all)

**E2E test commands that should trigger preflight check:**
```bash
pytest tests/integration/
pytest tests/e2e/
npm test -- --e2e
npm run test:integration
npx playwright test
```

All should warn if no kubectl get pods / curl /health in previous 10 messages.

## Test Case 7: Secret Keywords (Should WARN)

**Bash commands with credential patterns:**
```bash
export API_KEY=sk-1234567890
export SECRET_KEY=mysecret
export GROQ_API_KEY=gsk-abc123
export DATABASE_PASSWORD=postgres
```

All should warn if no kubectl get secret in last 20 messages.
