---
name: analyze-conversation
description: Analyze completed conversations for anti-patterns, tooling gaps, and learnings
author: system
version: 1.0.0
---

# Conversation Analyzer

Performs comprehensive post-mortem analysis of conversations to extract:
- Systemic anti-patterns (retry-without-diagnosis, credential assumptions, scope creep, etc.)
- Tooling opportunities (repeated commands that should be automated)
- Universal rules violated (15 infrastructure work rules)
- Recommendations for improvement

## Usage

`/analyze-conversation [conversation-id]`

## Arguments

- `conversation-id` (optional): ID of conversation to analyze. If omitted, analyzes current conversation.

## Output

Generates a comprehensive retrospective report in markdown format at `~/.claude/retrospectives/[conversation-id].md`

## What It Analyzes

### Anti-Patterns Detected

1. **Credential Anti-Patterns**
   - Hardcoded passwords/secrets
   - Using env vars without reading from K8s secrets
   - Assumed credentials without verification

2. **Retry Patterns**
   - Commands retried without checking logs/events between attempts
   - Blind retries without diagnosis

3. **Scope Drift**
   - Task expansions beyond original request
   - Creating new services/components without asking user

4. **Tool Blindness**
   - Existing tools not discovered or used
   - Manual commands when automation exists

5. **Verification Gaps**
   - Unverified external values (IPs, URLs, endpoints)
   - Integration tests run without preflight checks

6. **Command Repetition**
   - Same command run 3+ times (tool opportunity)
   - Manual command sequences that should be scripted

### Report Sections

The generated report includes:

- **Executive Summary**: Top anti-patterns, tool needs, rule violations
- **Detailed Anti-Pattern Analysis**: Each instance with context and fix
- **Tool Opportunities**: Commands that should be automated
- **Universal Rules Violated**: Which of 15 rules were broken and how often
- **Recommendations**: Priority-ranked action items
- **Success Metrics**: Comparison with target behavior

## Example Output

```markdown
# Conversation Retrospective: 5e6380e9-fb47-493b-9944-b029d43dae40

## Summary
- Total turns: 532
- Duration: ~8 hours
- Commands executed: 162
- Anti-patterns found: 13

## Anti-Patterns Found

1. **Retry-Without-Diagnosis**: 10 instances
   - Example: `git status` retried 3 times without checking logs
   - Fix: Run `git status --verbose` or check git daemon logs

2. **Credential Assumption**: 1 instance
   - Example: Used DATA_PLANE_DB_PASSWORD without reading from K8s secret
   - Fix: `kubectl get secret postgres-admin -o jsonpath='{.data.password}' | base64 -d`

3. **Tool Blindness**: 5 tools not discovered
   - myproject-runtime, myproject-db, tool-a, tool-b, tool-c
   - Impact: 30-50 manual commands could have been avoided

## Tool Opportunities

- **Repeated 10x**: git status → Tool: myproject-status --git
- **Repeated 5x**: kubectl get pods → Tool: myproject-status --data-plane
- **Repeated 5x**: pytest → Tool: myproject-test e2e (with preflight)

## Universal Rules Violated

- **Rule 2** (diagnose before retry): 10 violations
- **Rule 1** (never hardcode creds): 1 violation
- **Rule 5** (discover tools first): 5 violations

## Recommendations

1. **HIGH**: Implement myproject-preflight (prevents 15+ failed test runs)
2. **HIGH**: Implement myproject-creds (prevents credential leaks)
3. **HIGH**: Implement myproject-diag (prevents blind retries)
4. **MEDIUM**: Create TOOLS.md for tool discovery
5. **MEDIUM**: Update system prompt with verification protocol
```

## Implementation

This skill uses Python scripts located in `~/.claude/skills/analyze-conversation/`:

- **analyzer.py**: Main analysis engine that parses JSONL conversations
- **patterns.py**: Pattern detectors for each anti-pattern type
- **templates/**: Markdown templates for report generation

The analyzer reuses the analysis scripts created during retrospective analysis and enhances them with:
- Report generation in structured markdown
- Severity ranking (HIGH/MEDIUM/LOW)
- Actionable recommendations
- Success metric tracking

## Benefits

- **Learn from past mistakes**: Identify patterns that led to wasted effort
- **Improve processes**: Generate actionable recommendations
- **Track progress**: Compare metrics across conversations
- **Build better tools**: Discover automation opportunities
- **Refine system prompts**: Identify rules that need enforcement

## Related Skills

- `/check-antipatterns`: Real-time anti-pattern detection during active work
- Both skills work together in a learning loop:
  1. `/check-antipatterns` prevents issues during work
  2. `/analyze-conversation` identifies what wasn't caught
  3. Learnings improve both skills over time
