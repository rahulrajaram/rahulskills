# Rahulskills agent guidance

## Delegate the bulk of the work to LUNA

Use **LUNA (`gpt-5.6-luna`) subagents for the bulk of substantive analysis and
implementation**, including difficult work. The primary agent owns the global
instruction architecture, task decomposition, integration, acceptance decisions
and communication with the user. Do not reserve LUNA only for trivial chores
while doing all substantial work in the primary agent.

- Give each LUNA agent a bounded objective, concrete files or a semantic cluster,
  relevant context, constraints and observable acceptance criteria.
- Delegate independent clusters in parallel when this saves time or improves
  quality. Assign one writer per file; use separate read-only reviewers where
  useful, rather than overlapping rewrites.
- Keep one synthesized global view. Review returned evidence and diffs, resolve
  cross-skill contradictions and verify integration before declaring completion.
- Prefer Medium reasoning for bounded LUNA work unless the task or user specifies
  otherwise. If an agent is stuck, first improve its context or decompose the task;
  use a stronger model for a specific unresolved problem when evidence warrants it.
- Delegate test execution to at most one agent at a time, or keep it with the
  primary agent. Avoid duplicate builds and test runs.
- Do small immediate edits directly when delegation would add more cost than
  value. Do not invent parallel work just to satisfy a delegation quota.
- If LUNA is unavailable in the current host, report that limitation and use the
  best available authorized path; do not claim another model was LUNA.

## Corpus work

Treat `skills/` and its metadata, examples, scripts and shared references as one
instruction system. Preserve user intent, autonomy, useful specialization and
repetition that improves reliability. Follow the shared authoring convention in
`references/skill-authoring-contract.md` when editing skills; executing skills
must remain locally sufficient without loading that authoring reference.

Use focused verification appropriate to each change. Do not require matched
before/after behavior recording or a model-comparison campaign. Preserve existing
work, keep source edits separate from installation or external capability
activation, and track active optimization notes in the ignored `.agent/` planning directory.

## Backup retention

Do not retain separate backup copies of content that can be reconstructed from
verified local Git history or reflog-referenced objects. Before pruning, verify
the recovery path and record the original path, Git object or commit, and any
required mode or generation recipe in a compact recovery manifest. A reflog
does not capture uncommitted working files. Keep only contents whose recovery
is not established; mixed backups may retain just that remainder. Do not create
new Git objects merely to justify deletion, or expire reflogs or prune Git
objects as part of backup cleanup. Apply this rule within the user's authorized
cleanup scope; it does not authorize deleting unrelated data.

## Temporary worktree cleanup

Remove temporary worktrees after their task is complete when their commits
remain recoverable from verified Git history or a retained Git ref. Do not keep
a worktree merely as a commit backup. Before removal, inspect tracked changes,
untracked files and ignored files; preserve unique work that still matters and
record any necessary recovery metadata. Use `git worktree remove` to remove the
checkout and its registration together. Do not create replacement backup copies
of content already recoverable from Git.
