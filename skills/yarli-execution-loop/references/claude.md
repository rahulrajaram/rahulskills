# Claude Notes

- Keep the core Yarli workflow exactly as written in `SKILL.md`.
- Claude may generate more planning prose than Codex; keep queue updates in Yarli, not in narrative text.
- Before long tool-use sequences, restate the single next Yarli command you intend to run.
- If Claude encounters a permission or safety refusal, convert it into a narrowed retry, a durable follow-up tranche, or `stop-and-summarize`.
- If `yarli run continue` refuses because of drift, switch to `yarli run --fresh-from-tranches` instead of retrying the same command.
