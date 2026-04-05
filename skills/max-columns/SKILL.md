---
name: max-columns
description: "Keep output within a user-specified column width. Use when the user asks for N-column, 72-column, 80-column, wrapped, terminal-width, or narrow output."
argument-hint: "[columns]"
---

# Max Columns

Honor the requested column budget.

- Treat the argument or user-stated `N` as a hard maximum.
- Keep every line at or below `N` visible characters.
- Wrap prose early and prefer short bullets.
- Prefer vertical layouts over side-by-side layouts or wide tables.
- Reformat code, commands, and examples so each line still fits.
- If something cannot fit without losing meaning, say so briefly and give the narrowest useful version.
