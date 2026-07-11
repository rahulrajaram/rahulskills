---
name: next-todos
description: "Generate imperative next-step to-do lists as full sentences with clear objectives."
argument-hint: ""
---

# Next To-Dos

Use when the user asks for the next set of prioritized actions.

## Autonomy Routing

This skill produces executable work, not a workflow-selection checkpoint.
After generating todos, if the user selects an item, says to tackle them, or
otherwise signals execution, proceed with the selected or top-priority todo by
default. Do not ask whether to use `/goal`, Yarli, or direct execution unless
that choice materially changes durability, shared state, safety, or user-visible
behavior.

## Trigger
- User asks for "next tasks", "what should I do next", or equivalent planning output.

## Workflow
1. Inspect context from repo status, recent edits, and user intent.
2. Treat planning as read-only. Repository tooling may inform tasks, but its
   presence never authorizes mutation or enqueueing.
3. Produce a prioritized ordered list of executable tasks.
4. Write each item as a full imperative sentence that states a clear objective (e.g. "Add input validation to the /login endpoint so malformed emails are rejected before hitting the database.").
5. Start every item with an imperative verb (Add, Fix, Remove, Update, Extract, Replace, Wire, Validate, etc.).
6. Each item must be a complete sentence — no sentence fragments, bare noun phrases, or shorthand labels.
7. Keep each item to one sentence, 30 words or fewer.
8. Make each item specific and testable, with filenames or commands where useful.
9. If intent is unclear, ask one focused clarifying question.
10. Enqueue only when the user explicitly asks to queue/enqueue the tasks. Route
    that separate mutation through the shared Yarli enqueue primitive in
    [`../../references/yarli-primitives.md`](../../references/yarli-primitives.md);
    preview keys and summaries, use idempotent adds, and validate afterward.

## Output contract
- Return only a numbered list.
- Each item is a full imperative sentence starting with a verb, 30 words or fewer.
- No fragments, no bare labels, no shorthand — every item must read as a clear directive.
- No extra commentary outside the list.
