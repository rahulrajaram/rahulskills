---
name: postmortem
description: Generate Amazon COE-style 5-whys postmortem reports for incidents and failures. Use when user says "postmortem", "COE", "5-whys", "incident report", or asks to analyze why something failed.
author: claude
version: 1.0.0
argument-hint: "[incident description]"
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

## Intent, inputs and local bindings

Explain the selected incident using supplied facts and relevant available logs,
metrics, source/history and operator accounts. Resolve actual systems, timezones,
access and evidence sources; example SQL/Kubernetes commands below apply only to
matching environments and authorized reads.

## Non-goals

Writing a postmortem does not select remediation, production/database changes,
new monitoring or a fixed-depth investigation. Necessary evidence gathering and
proposed actions remain in scope; depth should match impact and uncertainty.

## Must not

Do not invent a fifth cause, force a process failure as the root cause, fabricate
impact/timestamps/owners, or label a proposed action completed. Missing evidence
is unknown; distinguish supported causes, hypotheses and contributing conditions.

## Interaction and authority

Proceed from available evidence, recording uncertainty and focused follow-up
questions where answers change causal conclusions. Reuse access/decision context;
ask before dependent actions outside existing authority. A report is not approval
to perform its actions. Be blameless without hiding specific technical failures.

## Report structure

Use [templates/coe-template.md](templates/coe-template.md) as the single maintained
skeleton when a structured COE report is useful. Omit irrelevant placeholders;
for a short incident, a proportionate narrative can carry the same evidence.
Five whys is a technique: stop at a supported sufficient cause or explicit unknown,
continue deeper when useful, and branch when there are distinct causal paths.

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
- Continue while evidence supports a useful causal link; stop at a sufficient
  supported explanation or an explicit unknown, regardless of the number of whys.
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
For each supported cause, propose an action or explain why none is warranted:
- Make them specific and measurable
- Assign clear ownership (even if TBD)
- Set realistic priority based on recurrence risk and impact
- Track status (TODO/In Progress/Done)

## Example Queries

For orchestration failures:
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
3. **Actionable**: Tie proposed actions to supported causes and recurrence risk
4. **Proportional**: Depth of analysis should match severity of incident
5. **Timely**: Write while details are fresh
6. **Shareable**: Should be useful for others who weren't involved

## Related Skills

- `/analyze-conversation`: Analyze conversation patterns (complementary)
- `/check-antipatterns`: Real-time anti-pattern detection

## Completion and evidence

Deliver the report with provenance, uncertainty, impact coverage and actions whose
status reflects observed execution. Dates, counts and completed mitigations require
evidence. Unknown owners/dates remain explicitly unassigned; no forced root-cause
or action quota proves completeness.
