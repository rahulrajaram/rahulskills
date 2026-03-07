---
name: postmortem
description: Generate Amazon COE-style 5-whys postmortem reports for incidents and failures. Use when user says "postmortem", "COE", "5-whys", "incident report", or asks to analyze why something failed.
author: claude
version: 1.0.0
allowed-tools: Bash, Read, Grep, Glob, Task
---

# Postmortem Generator (Amazon COE 5-Whys Style)

Generate comprehensive Correction of Error (COE) postmortem reports following Amazon's 5-whys methodology.

## When to Use

- User asks for a "postmortem" or "incident report"
- User wants to analyze why something failed
- User mentions "COE" or "5-whys" analysis
- After a significant failure that needs root cause analysis
- When deriving action items from an incident

## Usage

`/postmortem [incident-description-or-id]`

## Arguments

- `incident-description-or-id` (optional): Description of the incident or an identifier (orchestration ID, PR number, etc.)

## Report Structure

The postmortem follows this structure:

### 1. Header
```markdown
# Correction of Error (COE) Report

## Incident: [Title]
**Date:** YYYY-MM-DD
**Duration:** X minutes/hours
**Severity:** Critical/High/Medium/Low
**Affected Systems:** [list]
```

### 2. Executive Summary
2-3 sentences describing what happened and the business impact.

### 3. Timeline
Chronological table of events:
```markdown
| Time (UTC) | Event |
|------------|-------|
| HH:MM:SS | Event description |
```

### 4. 5-Whys Analysis

For each problem identified, drill down with 5 levels of "why":

```markdown
### Problem N: [Problem Statement]

**Why did X happen?**
→ Because Y

**Why did Y happen?**
→ Because Z

**Why did Z happen?**
→ Because A

**Why did A happen?**
→ Because B

**Why did B happen?**
→ Because C (ROOT CAUSE)
```

### 5. Root Causes Table
```markdown
| # | Root Cause | Category |
|---|------------|----------|
| RC1 | Description | Category (Infrastructure/Code/Process/etc.) |
```

### 6. Impact Assessment
```markdown
| Metric | Value |
|--------|-------|
| Affected users | N |
| Failed operations | N |
| Data loss | Yes/No |
| Revenue impact | $X or N/A |
```

### 7. Action Items

Prioritized by urgency:

```markdown
### Immediate (P0) - Completed ✅
| # | Action | Owner | Status |
|---|--------|-------|--------|

### Short-term (P1) - This Sprint
| # | Action | Owner | Status |
|---|--------|-------|--------|

### Medium-term (P2) - Next Sprint
| # | Action | Owner | Status |
|---|--------|-------|--------|

### Long-term (P3) - Backlog
| # | Action | Owner | Status |
|---|--------|-------|--------|
```

### 8. Lessons Learned
Numbered list of key takeaways that should inform future work.

### 9. Appendix
- Files changed
- Related PRs/commits
- Links to logs/dashboards

## Investigation Process

When generating a postmortem, follow this process:

### Step 1: Gather Evidence
- Check logs: `kubectl logs`, application logs, system logs
- Check database: Query relevant tables for state/events
- Check metrics: Dashboards, error rates, latencies
- Check git: Recent commits, PRs, deployments

### Step 2: Build Timeline
- Identify the first sign of trouble
- Map out each significant event
- Note when the issue was detected vs when it started
- Note when resolution actions were taken

### Step 3: Perform 5-Whys
- Start with the observable symptom
- Ask "why" and answer with facts, not assumptions
- Continue until you reach systemic/process root causes
- Multiple branches are normal (different failure modes)

### Step 4: Categorize Root Causes
Common categories:
- **Infrastructure Gap**: Missing automation, tooling, monitoring
- **Code Bug**: Logic error, edge case, regression
- **Schema Issue**: Database design flaw
- **Configuration**: Misconfiguration, stale config
- **Process Gap**: Missing procedure, unclear ownership
- **Observability Gap**: Missing logs, metrics, alerts
- **Testing Gap**: Missing test coverage
- **Documentation Gap**: Missing or outdated docs

### Step 5: Generate Action Items
For each root cause, generate at least one action item:
- Make them specific and measurable
- Assign clear ownership (even if TBD)
- Set realistic priority based on recurrence risk and impact
- Track status (TODO/In Progress/Done)

## Example Queries

For Striation orchestration failures:
```sql
-- Get orchestration status
SELECT id, status, current_phase, created_at, updated_at
FROM orchestration_runs WHERE id = 'UUID';

-- Get event timeline
SELECT type, message, created_at
FROM orchestration_events
WHERE orchestration_run_id = 'UUID'
ORDER BY created_at;

-- Get failure details
SELECT type, message, data::text
FROM orchestration_events
WHERE orchestration_run_id = 'UUID' AND type LIKE '%failed%';
```

For Kubernetes issues:
```bash
# Pod events
kubectl describe pod <pod> -n <ns> | grep -A20 Events

# Recent logs with errors
kubectl logs deploy/<deploy> -n <ns> --tail=500 | grep -i error

# Resource status
kubectl get pods,svc,deploy -n <ns>
```

## Output Location

Reports can be:
1. Output directly in the conversation (default)
2. Saved to file: `~/.claude/postmortems/YYYY-MM-DD_<incident-slug>.md`

## Tips for Good Postmortems

1. **Blameless**: Focus on systems and processes, not individuals
2. **Fact-based**: Use logs, metrics, and evidence - not assumptions
3. **Actionable**: Every root cause should have a corresponding action item
4. **Proportional**: Depth of analysis should match severity of incident
5. **Timely**: Write while details are fresh
6. **Shareable**: Should be useful for others who weren't involved

## Related Skills

- `/analyze-conversation`: Analyze conversation patterns (complementary)
- `/check-antipatterns`: Real-time anti-pattern detection
