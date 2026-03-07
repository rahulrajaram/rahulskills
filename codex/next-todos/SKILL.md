---
name: next-todos
description: "Generate concise next-step to-do lists with each item capped at 20 words."
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# Next To-Dos

Use when the user asks for the next set of prioritized actions.

## Trigger
- User asks for "next tasks", "what should I do next", or equivalent planning output.

## Workflow
1. Inspect context from repo status, recent edits, and user intent.
2. If `yarli.toml` exists in project root, run `yarli plan validate` before drafting tasks.
3. Produce a prioritized ordered list of executable tasks.
4. Keep each item at 20 words or fewer.
5. Make each item specific and testable, with filenames or commands where useful.
6. If intent is unclear, ask one focused clarifying question.
7. If `yarli.toml` exists, enqueue **every** drafted task as an incomplete tranche:
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
8. Run `yarli plan validate` again after enqueuing all tranches.

## Output contract
- Return only a numbered list.
- Each list item must be 20 words or fewer.
- No extra commentary outside the list.
