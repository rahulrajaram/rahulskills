# Claude Notes

- Keep the core Yarli workflow exactly as written in `SKILL.md`.
- The agent is the supervisor. A repo-local `scripts/yarli_supervisor.py` is only a one-shot launcher unless you explicitly choose otherwise.
- Claude may generate more planning prose than Codex; keep queue updates in Yarli, not in narrative text.
- When a run is already active, watch it at a 60-second cadence and summarize deltas rather than replaying raw logs.
- Before long tool-use sequences, restate the single next Yarli command you intend to run.
- After `3` flat ticks, do a deeper pulse check before concluding the run is stuck.
- If Claude encounters a permission or safety refusal, convert it into a narrowed retry, a durable follow-up tranche, or `stop-and-summarize`.
- If no supervisor exists and `yarli run continue` refuses because of drift, switch to `yarli run --fresh-from-tranches` instead of retrying the same command.
- Treat repeated helper or test failures as intervention points that require concrete inspection, not just another retry.
