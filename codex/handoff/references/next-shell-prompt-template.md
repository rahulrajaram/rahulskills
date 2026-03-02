# Next-Shell Prompt Template

Use this template to produce the final copy-paste prompt for a new shell.
Every placeholder MUST be replaced with a concrete value or removed entirely.

```text
Continue work in <ABSOLUTE_REPO_PATH>.

Session handoff facts:
- Branch: <BRANCH>
- HEAD commit: <COMMIT_SHA> — <COMMIT_MESSAGE>
- Working tree: <CLEAN_OR_DIRTY_SUMMARY>

What was completed this session:
1. <DONE_ITEM_1>
2. <DONE_ITEM_2>
3. <DONE_ITEM_3>

Key decisions and context from this session:
- <DECISION_OR_CONCLUSION_1>
- <DECISION_OR_CONCLUSION_2>
- <DISCUSSION_TOPIC_WITH_OUTCOME>

What still needs to be done (priority order):
1. <NEXT_TASK_1>
2. <NEXT_TASK_2>
3. <NEXT_TASK_3>

Files touched this session:
- <FILE_1> (<ACTION: new/edited/deleted>)
- <FILE_2> (<ACTION>)

Canonical docs status:
- IMPLEMENTATION_PLAN.md: <UPDATED / NOT_FOUND>
- PROMPT.md: <UPDATED / NOT_FOUND>

Known risks and blockers:
- <RISK_OR_BLOCKER_1>
- <RISK_OR_BLOCKER_2>

Start by running:
1. <FIRST_COMMAND>
2. <SECOND_COMMAND>
```

## Template rules

- "Key decisions and context" is NOT optional. If the session involved any discussion,
  design exploration, feasibility assessment, or validated conclusions, they MUST appear
  here. This prevents the next shell from re-discovering context already established.
- "What still needs to be done" should include tasks surfaced in discussion, not just
  tasks from a formal plan document.
- Remove any placeholder lines that have no value rather than leaving them empty.
- Prefer factual, verifiable statements over narrative.
