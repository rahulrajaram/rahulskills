# Codex Notes

- Keep the core Yarli workflow exactly as written in `SKILL.md`.
- The agent is the supervisor. A repo-local `scripts/yarli_supervisor.py` is only a one-shot launcher unless you explicitly choose otherwise.
- When a run is already active, keep a long-lived watch session open at a 60-second cadence and summarize deltas instead of raw tail spam.
- After `3` flat ticks, run a deeper pulse check with run-list state, process health, and the latest meaningful log note.
- Prefer short, operational retries after a refusal: smaller scope, fewer paths, or one verification command at a time.
- Treat repeated helper or test failures as an intervention trigger. Inspect the exact failing command and decide whether to patch, retry, or enqueue follow-up work.
- If Codex refuses or stops after the first execution step, do not treat that as terminal. Convert it into a narrowed retry, a durable follow-up tranche, or `stop-and-summarize`.
- Re-run the inspect script after each material command so the next decision is grounded in Yarli state, not chat memory.
- If no supervisor exists and `yarli run continue` refuses because of drift, switch to `yarli run --fresh-from-tranches` instead of retrying the same command.
- When memory or checkpoint tooling is available, record run ID, active tranche, last completed tranche, health, and intervention reason.
