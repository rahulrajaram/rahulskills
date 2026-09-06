# Archive cleanup review and execution

## Executed under the Git-recovery retention rule

The user superseded blanket backup retention: delete backup content reconstructible
from verified local Git history or reflog-referenced objects. LUNA performed
per-file recovery checks and guarded deletion; the primary agent verified the
results. This completed cleanup supersedes the initial recommendations below.

- Repository archives: **2,093 files / 10,637,847 bytes removed** from the March
  snapshot and `.git/rahulskills-backups/`; **248 unmatched files retained**.
- Runtime backups: **406 files / 1,998,615 bytes removed**. Retained: 82 unmatched
  regular files, 48 symlinks, and the prior binary whose exact reconstruction
  was not established. The primary activation backup is now a partial remainder,
  not a self-contained complete rollback tree.
- Total: **2,499 files / 12,636,462 bytes (about 12.1 MiB)** removed. Empty
  archive descendant directories were removed where possible.
- Active `build/`, canonical skills, installed skills, Git objects, refs and
  reflogs were not changed. Hash comparison confirmed canonical and installed
  trees unchanged. Sample files were restored from Git with their recorded modes
  in temporary directories and checked, then the temporary copies were removed.

Recovery records (metadata, not retained file copies):

- `.agent/git-recoverable-blob-census.json`: repository file paths, Git OIDs, modes
  and unmatched entries.
- `.agent/git-recoverable-prune-result.json`: exact repository removals.
- `.agent/git-recoverable-runtime-backups.json`: original absolute runtime backup
  paths, Git OIDs, modes and deletion results.

To recover a removed file, read its manifest row, obtain bytes with
`git -C <rahulskills> cat-file blob <OID>`, write them to the recorded original
path, and apply the recorded mode. The original backup path is authoritative;
the Git source path may differ because identical blobs occur under several paths.
Do not assume a partial backup directory alone still contains every original file.

The retention rule is recorded in `AGENTS.md`. No new Git objects were created
to manufacture recoverability, and no Git garbage collection or reflog expiry
was performed. Remaining unknowns can be reviewed later if exact generation
recipes become demonstrably reconstructible.

## Initial assessment before the deletion directive

Reviewed 2026-09-06 by the primary agent and three LUNA reviewers. This is an
assessment: no archives, backups, skills or build artifacts were deleted.
Sizes below are logical file bytes unless explicitly described otherwise.

## Recommended first cleanup

| Candidate | Recommendation | Evidence and consequence |
|---|---|---|
| `build/` | Remove the stale generated output; regenerate only when needed. | 259 files, 1,400,521 bytes. Canonical source and installed core packages remain intact. This old assembly still includes optional design outputs; their presence here does not mean they are installed. The assembler can recreate this directory. |
| `.git/rahulskills-backups/build-20260904T183627Z-2448559.mMPUY8/` | Remove the redundant snapshot. | 247 files, 1,317,481 bytes; same relative file paths, file contents and file modes as the retained snapshot named below. |
| `.git/rahulskills-backups/build-20260904T205931Z-2927783.YXeHfs/` | Remove the redundant snapshot. | Same exact duplicate group: 247 files, 1,317,481 bytes. |
| `.git/rahulskills-backups/build-20260904T183316Z-2430953.mzCOOY/` | Remove the empty backup tree. | Contains no files; it provides no file-content recovery. |
| `.ruff_cache/`, Python `__pycache__/` directories, empty `.benchmarks/` | Optional low-value housekeeping. | Regenerable or empty; exclude any active process's temporary work. This is not a skill architecture improvement. |

Retain `.git/rahulskills-backups/build-20260904T213425Z-3066963.zmCpy2/`
as the representative of the three identical snapshots. The comparison included
relative paths, file modes and contents; it does not assert identical original
creation timestamps. The three nonempty cleanup candidates above account for
4,035,483 bytes (about 3.85 MiB), before caches or redundant migration backups.

The other six nonempty build-backup snapshots have distinct content hashes.
Difference alone does not establish value, but we have not established that
their distinct historical contents are recoverable elsewhere. Keep them in this
first pass. `.git/rahulskills-backups/` contains custom generated backups;
this recommendation does not concern Git objects, refs, reflogs or repository
history.

## Redundant migration backups

The migration is already accepted and verified. Comparison against the primary
activation snapshot found these additional cleanup candidates:

| Backup cohort | Proven redundant subset | Logical bytes |
|---|---|---:|
| `/home/rahul/.codex/skill-backups/` | 47 migration directories containing skill copies | 749,009 |
| `/home/rahul/.claude/skill-backups/` | 46 migration directories containing skill copies | 614,775 |
| `/home/rahul/.pi/agent/skill-backups/migration-vhgrw5w9/` | The old charter skill, fully covered by the primary Pi snapshot | 8,075 |

These comparisons cover file contents, modes and symlinks, not simply names or
age. Exact per-directory candidates and their preserved counterparts are listed
in `.agent/archive-migration-candidates.json`; do not use a blanket
`migration-*` deletion. Together with the stale build and duplicate build
snapshots above, the proven candidates total 5,407,342 logical bytes (about
5.16 MiB), excluding caches.

**Retain these six shared-reference backups as part of the rollback set.** The
primary activation backup contains `skills/` only, so it does not cover them:

- `/home/rahul/.codex/skill-backups/migration-imira150/gptengage-invoke.md`
- `/home/rahul/.codex/skill-backups/migration-2mu4pb6m/history-rewrite-safety.md`
- `/home/rahul/.codex/skill-backups/migration-bnauc179/gptengage-invocation.md`
- `/home/rahul/.claude/skill-backups/migration-yas5rsfx/gptengage-invoke.md`
- `/home/rahul/.claude/skill-backups/migration-klnb9tdc/gptengage-invocation.md`
- `/home/rahul/.claude/skill-backups/migration-aehiy6we/history-rewrite-safety.md`

## Preserve unique historical material

`build.stale.20260325T1248/` has 81 files totaling 289,953 bytes. It includes
both archived `kokoro-tts` entrypoints; no canonical skill with that name exists,
and `speak` is the active replacement. The Codex and Claude archived TTS files
also differ from each other. Do not delete the whole tree as a generated cache.

If reducing search noise is the priority, move this snapshot intact into the
existing external archive/backup area, with a recorded origin and verified
contents. That relocation would preserve provenance while removing obsolete
instruction copies from ordinary worktree searches. It is a separate candidate
action, not something performed during this review.

Keep the older Pi `diagram-review-viewer.pre-pi-sync`, `grilling.pre-pi-sync`
and `grill-me.pre-pi-sync` snapshots for now. Their historical contents are not
identical to active files, and no complete substitute was established. They
already sit outside active skill discovery.

## Preserve current rollback and evidence

- Primary activation backup:
  `/home/rahul/.local/state/rahulskills-activation-backups/20260906T141719Z/`
  (242 files, 1,392,520 bytes).
- Prior installed gptengage binary:
  `/home/rahul/.local/bin/gptengage.backup-20260906T141427Z-b5ee17feaad4753f88d024b066ee1ae45611f918387df69b5e0078d67b9bad79`
  (2,282,696 bytes). It is the direct rollback from 1.2.1 to 1.1.2.
- `AUDIT.md`, `GLM_REVIEW.md`, `OPTIMIZATION_PLAN.md`,
  `INSTALLATION_PREVIEW.md`, `.agent/activation-review.*`, and gptengage's
  `.agent/activation-evidence/` and `activation-qualification.md`.
  These contain unique decisions, fingerprints and actual live qualification
  evidence. The source changes remain uncommitted.
- `NEXT_SHELL_PROMPT.md`, `docs/diagram-preview-v2/`, `v3/` and `v4/`.
  The handoff references the earlier previews; the newest bundle contains
  source/generation/verification assets. Untracked or locally ignored status
  does not establish that these are disposable.
- Existing project research, `agent_reports/`, and gptengage's unrelated plans.
  This cleanup review does not authorize discarding other project history.

gptengage's `target/` is a regenerable compiler cache, not a skill archive.
Cleaning it would primarily trade disk space for later rebuild time; it is not
recommended as part of this instruction-corpus cleanup.

## Review limitations and next action

Initial archive discovery missed the ignored March snapshot; explicit filesystem
enumeration corrected the census and recovered the TTS provenance. Tooling
friction f-2666 records the need for complete archive-root discovery. No claim of
absence in this report relies only on default ignore-respecting source search.

The useful first action is narrowly scoped removal of proven duplicate/generated
material while retaining one representative and the latest rollback snapshot.
Recheck candidate fingerprints immediately before deletion because this review
is a snapshot. Do not infer deletion authority for unrelated directories from
the fact that they are old, ignored or named `backup`.
