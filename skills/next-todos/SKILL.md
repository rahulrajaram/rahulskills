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
2. If `yarli.toml` exists in project root, run `yarli plan validate` before drafting tasks.
3. Produce a prioritized ordered list of executable tasks.
4. Write each item as a full imperative sentence that states a clear objective (e.g. "Add input validation to the /login endpoint so malformed emails are rejected before hitting the database.").
5. Start every item with an imperative verb (Add, Fix, Remove, Update, Extract, Replace, Wire, Validate, etc.).
6. Each item must be a complete sentence — no sentence fragments, bare noun phrases, or shorthand labels.
7. Keep each item to one sentence, 30 words or fewer.
8. Make each item specific and testable, with filenames or commands where useful.
9. If intent is unclear, ask one focused clarifying question.
10. If `yarli.toml` exists, enqueue **every** drafted task as an incomplete tranche:
   - Determine the next numeric prefix from existing `NXT-<NNN>` keys:
   ```bash
   next_index=$(rg 'key = "NXT-[0-9]{3}"' .yarli/tranches.toml | sed -E 's/.*NXT-([0-9]{3}).*/\1/' | sort -n | tail -n1)
   next_index=$((next_index + 0))
   ```
   - For each drafted item (in final numbered output order), add sequentially:
   ```bash
   idx=1
   while IFS= read -r task; do
      key="NXT-$(printf '%03d' "$((next_index + idx))")"
      yarli plan tranche add --key "$key" --summary "$task" --group "next-todos"
      idx=$((idx + 1))
   done <<< "<raw_task_lines>"
   ```
   - Set `next_index` to `0` when no prior `NXT` keys exist.
   - Use exact quoted task summaries without truncation.
   - Example: `yarli plan tranche add --key NXT-009 --summary "..." --group "next-todos"`.
   - Do not skip any drafted item.
11. Run `yarli plan validate` again after enqueuing all tranches.

## Output contract
- Return only a numbered list.
- Each item is a full imperative sentence starting with a verb, 30 words or fewer.
- No fragments, no bare labels, no shorthand — every item must read as a clear directive.
- No extra commentary outside the list.
