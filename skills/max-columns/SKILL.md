---
name: max-columns
description: "Keep output within a user-specified column width. Use when the user asks for N-column, 72-column, 80-column, wrapped, terminal-width, or narrow output."
argument-hint: "[columns]"
---

# Max Columns

Honor the requested column budget.

- Use the argument or user-stated `N` as the layout budget; preserve meaning and machine syntax when an indivisible atom cannot fit.
- Keep wrappable lines at or below `N` display columns; account for wide Unicode and tabs when relevant.
- Wrap prose early and prefer short bullets.
- Prefer vertical layouts over side-by-side layouts or wide tables.
- Wrap code/commands only at syntactically valid boundaries. Never insert breaks into identifiers, URLs, string values or machine-consumed records that change their meaning.
- If something cannot fit without losing meaning, say so briefly and give the narrowest useful version.

Non-goals: changing content or adding a formatter dependency. Must not: corrupt
syntax to meet width. Choose valid layouts autonomously; disclose an indivisible
overlong atom and preserve it intact. Completion: readable output at the selected
width except explicitly identified syntax/meaning-preserving exceptions.
