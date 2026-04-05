# Codex Notes

- Keep the core Yarli workflow exactly as written in `SKILL.md`.
- Prefer short, operational retries after a refusal: smaller scope, fewer paths, or one verification command at a time.
- If Codex refuses or stops after the first execution step, do not treat that as terminal. Convert it into a narrowed retry, a durable follow-up tranche, or `stop-and-summarize`.
- Re-run the inspect script after each material command so the next decision is grounded in Yarli state, not chat memory.
- If `yarli run continue` refuses because of drift, switch to `yarli run --fresh-from-tranches` instead of retrying the same command.
