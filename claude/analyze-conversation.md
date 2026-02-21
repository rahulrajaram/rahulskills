---
allowed-tools: Bash(python3:*)
argument-hint: [conversation-id]
description: Analyze completed conversations for anti-patterns, tooling gaps, and learnings
---

# Conversation Analyzer

Performs comprehensive post-mortem analysis of conversations to extract systemic anti-patterns, tooling opportunities, and recommendations.

## Instructions

**If conversation-id is provided:**
```bash
python3 ~/.claude/skills/analyze-conversation/generate_report.py "$ARGUMENTS"
```

**If no arguments (analyze current conversation):**

First, find the current conversation ID:
```bash
PROJECT_DIR=$(pwd | sed 's|/|-|g')
CONV_ID=$(ls -t ~/.claude/projects/${PROJECT_DIR}/*.jsonl | head -1 | xargs basename -s .jsonl)
python3 ~/.claude/skills/analyze-conversation/generate_report.py "$CONV_ID"
```

## What It Analyzes

The analyzer will extract and report on:

### Anti-Patterns
1. **Credential Anti-Patterns**: Hardcoded passwords, assumed credentials, env vars without verification
2. **Retry-Without-Diagnosis**: Commands retried without checking logs/events
3. **Scope Drift**: Task expansions beyond original request without asking
4. **Tool Blindness**: Existing tools not discovered or used
5. **Verification Gaps**: Unverified external values, tests without preflight checks
6. **Command Repetition**: Same command 3+ times (automation opportunity)

### Tool Opportunities
- Commands repeated 3+ times that should be automated
- Manual sequences that should be scripts
- Missing tools that would improve workflow

### Universal Rules
- Which of the 15 infrastructure rules were violated
- Frequency and impact of each violation

### Recommendations
- Priority-ranked action items (HIGH/MEDIUM/LOW)
- Specific tools to build
- Process improvements
- System prompt updates

## Output

Report is generated at: `~/.claude/retrospectives/[conversation-id].md`

The script will output:
```
Analyzing conversation: [conversation-id]
Loading messages...
Analyzing anti-patterns...
Detecting tool opportunities...
Checking universal rules...
Generating report...

Report saved to: ~/.claude/retrospectives/[conversation-id].md
```

## After Running

1. Read the generated report: `cat ~/.claude/retrospectives/[conversation-id].md`
2. Review HIGH priority recommendations
3. Consider implementing suggested tools
4. Update processes based on learnings

## Related

- `/check-antipatterns`: Real-time detection during active work
- Both skills form a learning loop for continuous improvement
