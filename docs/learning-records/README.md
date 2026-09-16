# Learning records — now in local agent memory

The learning-record corpus that used to live here
(`front-door-routing-2026-09-08.json`, added 2026-09-08) has been migrated to
the local Haake memory ledger for the `opencode` agent in project
`rahulskills` (memory id `90aad826-a331-44b4-bf3f-1ed5ecb60614`, tags
`learning-records`, `migrated-from-git`).

Rationale: records are single-run claims whose value grows with volume and
whose natural operations (dedupe, recurrence counting, clustering) are
ledger operations, not git operations. Each record already carries its own
provenance (`source_commit`, `run_id`, digests), so version control added
redundant bookkeeping while accumulating session-specific detail.

What still belongs to the repository:

- `references/learning-record.schema.json` — the record contract.
- `references/retrospective-learning-input.schema.json` — the aggregate
  input contract consumed by retrospective tooling.
- `scripts/learning_ingest.py` — validation and deterministic digesting.

To reconstruct or re-enter migrated records, query Haake memory with tag
`migrated-from-git` in this project scope.
