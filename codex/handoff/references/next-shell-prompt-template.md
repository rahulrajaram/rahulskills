# Next-Shell Prompt Template

Use this template to produce the final copy-paste prompt for a new shell.

```text
Continue work in <ABSOLUTE_REPO_PATH>.

Session handoff facts:
- Branch: <BRANCH>
- HEAD commit: <COMMIT_SHA>
- Latest commit message: <COMMIT_MESSAGE_OR_NONE>
- Files touched in this session: <FILES_OR_NONE>

What is already done:
1. <DONE_ITEM_1>
2. <DONE_ITEM_2>
3. <DONE_ITEM_3>

What still needs to be done (priority order):
1. <NEXT_TASK_1>
2. <NEXT_TASK_2>
3. <NEXT_TASK_3>

Canonical docs status:
- IMPLEMENTATION_PLAN.md: <UPDATED_OR_NOT_FOUND>
- PROMPT.md: <UPDATED_OR_NOT_FOUND>
- Any stale claims removed: <YES_NO_AND_NOTE>

Validation status:
- Commands run: <COMMANDS>
- Pass/fail summary: <SUMMARY>
- Known failing tests/checks: <FAILURES_OR_NONE>

Start by:
1. <FIRST_COMMAND>
2. <SECOND_COMMAND>
3. <THIRD_COMMAND>

Constraints:
- Preserve behavior; use helper extraction/decomposition unless instructed otherwise.
- Do not revert unrelated local changes.
- Report exact before/after lint-complexity counts after each batch.
```
