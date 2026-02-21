---
allowed-tools: Bash(python3:*)
argument-hint:
description: Real-time checking of current conversation against known anti-patterns
---

# Anti-Pattern Checker

Analyze the CURRENT conversation for anti-patterns and provide immediate warnings.

## Instructions

Run the anti-pattern checker on the current conversation:

```bash
PROJECT_DIR=$(pwd | sed 's|/|-|g')
CONV_FILE=$(ls -t ~/.claude/projects/${PROJECT_DIR}/*.jsonl 2>/dev/null | head -1)
python3 ~/.claude/skills/check-antipatterns/checker.py "$CONV_FILE"
```

**Note:** The project directory is derived from `pwd` with slashes replaced by dashes. If the conversation file is not found, check `~/.claude/projects/` for the correct JSONL file.

The checker will analyze the conversation and provide:
- ⚠️ **Warnings**: Anti-patterns detected
- ✅ **Good Practices**: Positive behaviors observed
- 📊 **Compliance Score**: Percentage of rules followed
- 💡 **Recommendations**: Actionable next steps

## What It Checks

1. **Retry-Without-Diagnosis**: Same command run 2+ times without diagnostics
2. **Credential Usage Without Verification**: Using PASSWORD/SECRET/KEY without reading from K8s secret
3. **Scope Expansion**: Creating files/services not in original request
4. **Missing Preflight Checks**: Running E2E/integration tests without environment validation
5. **Tool Discovery Gap**: Long conversation without checking for existing tools
6. **Unverified External Values**: Using IPs/URLs without verification
7. **Error Message Skimming**: Command failed but error not referenced
8. **All 15 Universal Rules**: Checks compliance with infrastructure work rules

## After Running

Review the output and:
1. Address any HIGH severity warnings immediately
2. Consider MEDIUM warnings before proceeding
3. Note good practices to reinforce positive behaviors
4. Aim for 95%+ compliance score

## Related

- `/analyze-conversation`: Post-mortem analysis of completed conversations
