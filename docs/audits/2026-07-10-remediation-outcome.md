# Skills and MCP Remediation Outcome

Date: 2026-07-10
Status refreshed: 2026-07-11

This is the corrected outcome of the implementation wave following
`2026-07-10-skills-mcp-second-review.md`. The earlier version incorrectly said
the work was uncommitted and the MCP runtimes had not been reloaded. The source
work is committed, the configured MCP artifacts were rebuilt, and fresh
processes were verified as described below. No repository was pushed.

## Committed source state

| Repository | Branch | Remediation commits | Current remediation HEAD |
|---|---|---|---|
| Rahulskills | `master` | `e174ff8` workflow safety contracts; `39523bd` MCP capture harness and cache-safe assembly | `39523bd` |
| Haake | `master` | `59e9e33` context/effects; `fbd3411` destructive, pagination, and structured contracts; `297ccde` migration repair; `d014325` canonical ID round trips | `d014325` |
| Selfimprove | `master` | `2551eb3` discovery, effects, schemas, errors, and pagination | `2551eb3` |
| GPTQueue | `feat/session-aware-architecture` | `8f51dd3` coordination safety; `44e9156` idempotency, timeout, and error contracts | `44e9156` |
| Cultivar | `master` | `d29ee59` safety metadata; `ae835ed` registry, routing, and artifact schemas | `ae835ed` |

DeepMetrics remained a workspace anchor. No tracked DeepMetrics file was
changed, staged, or committed by this remediation. Its substantial product work
remains pre-existing and untouched. Cultivar `stash@{0}` also remains untouched.

## Runtime outcome

- GPTQueue was rebuilt, its user service was restarted, and the fresh runtime
  was verified for server instructions, safety metadata, caller idempotency,
  stable errors, and bounded timeout schemas.
- Cultivar and Haake were rebuilt. Fresh stdio clients advertised the committed
  instructions, safety labels, routing/input schemas, output schemas, and
  artifact or recovery fields.
- Selfimprove's configured source symlink already exposed the committed code; a
  fresh process verified the current contract.
- The Rahulskills bundle from `39523bd` was installed with explicit approval on
  2026-07-11 after a hash-verified backup. Both runtime roots now match the
  reviewed 39-Codex/40-Claude assembly, and fresh Codex verification confirmed
  that `next-todos` treats planning as read-only unless enqueue intent is explicit.
- New processes therefore match the committed runtime sources through
  `44e9156`, `ae835ed`, `297ccde`, and `2551eb3`. Haake commit `d014325` is a
  later source-only follow-up and has not been installed or used to restart an
  existing MCP process.
- Existing Codex-owned stdio children were deliberately not killed or pruned.
  Long-lived sessions may retain their prior process metadata until their owner
  exits or an approved lifecycle operation is performed.

## Haake data migration

The DeepMetrics Haake database was backed up before migration at:

`$DEEPMETRICS_ROOT/.haake-data/backups/pre-schema21-20260710T2212.db`

The main backup SHA-256 is
`e51bf6fda2cd43f5a32573aeace25f02983a960417beb34de9dddcc3928edcbe`.
The live database migrated from schema 19 to schema 21 after `297ccde` repaired
legacy databases missing `memory_access_log`. Read-only verification on
2026-07-11 reported schema 21, `PRAGMA integrity_check = ok`, no foreign-key
violations, 32 memories, and 2 scopes. The first 31 memories survived migration;
the 32nd records runtime-remediation completion. The required follow-on outcome
memory recorded on 2026-07-11 then brought the live count to 33.
The approved skill-activation outcome was recorded afterward, bringing the
count to 34.

## Follow-on implementation

- Haake `d014325` closes f-1212/f-1641 without rewriting either friction
  record. Query/list results now expose full canonical IDs and structured
  `memory_id`, `display_id`, `project_id`, and `scope_id` fields. Mutation and
  citation inputs accept exact IDs or unique prefixes of at least eight
  characters; ambiguity returns canonical candidates without mutation.
- Rahulskills `39523bd` adds a reusable, standard-library MCP capture harness
  for initialize instructions, tool schemas, normalized transcripts,
  source/runtime hashes, text diffs, stderr, and rollback artifacts. Assembly
  now excludes Python runtime caches from capability bundles.
- The six system-skill packets, Codex lifecycle issue, exact Rahulskills install
  packet, and repository publication options are prepared in adjacent audit
  documents. Preparation made no external write.

## Verification evidence

- The original remediation passed the Rahulskills packaging/catalog suites,
  Haake full Rust suite, Selfimprove focused hardening suite, GPTQueue typecheck
  and 29 tests, and Cultivar unit/stdio/Clippy checks recorded during the wave.
- Haake `d014325` passed the repository commit hook: `cargo check`, Clippy, 256
  library tests, 8 binary tests, 44 MCP tests, 75 REST tests, all other enabled
  integration tests, doc tests, and the hotspot ratchet.
- Rahulskills `39523bd` passed 3 capture-harness tests and the complete stitch
  assembly test with 40 Claude and 39 Codex repository skills. Codex excludes
  the repository `skill-creator` because the system-owned skill is authoritative.
- Every changed repository passed `git diff --check` before commit.

## Remaining approval gates

The approved Rahulskills installation is complete. Its retained rollback backup
and verification evidence are recorded in
`2026-07-11-rahulskills-install-approval.md`.

The following also remain approval-gated and were not performed: pushing any
branch, creating or updating a pull request, creating or commenting on an
external issue, installing a dependency, restarting another service, pruning a
process, or rebuilding/reloading Haake for `d014325`.
