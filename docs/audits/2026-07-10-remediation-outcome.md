# Skills and MCP Remediation Outcome

Date: 2026-07-10

This document records the implementation wave following the independent audit
at `docs/audits/2026-07-10-skills-mcp-second-review.md`. All changes remain
local and uncommitted. No dependency, push, runtime rebuild, restart, reload, or
process cleanup was performed.

## Implemented locally

- Reordered `handoff` so canonical documents are reconciled before the shared
  `commit` workflow, with explicit-path staging and clean-tree verification.
- Removed `commit` authority to edit global ignores or untrack files as routine
  housekeeping; repository policy now outranks generic heuristics.
- Made `next-todos` read-only unless enqueue intent is explicit.
- Added approval boundaries and dry-run/confirmed paths for Yarli cancellation,
  repair, launch, and relaunch.
- Added push, PR-create, and version-change approvals to `pr-lifecycle`.
- Replaced TTS source interpolation with a stdin-based Python helper.
- Corrected and shortened per-process and system memory diagnostic prompts.
- Added shared history-rewrite, GPTEngage, and Yarli primitive references and
  assembly/install support.
- Repaired conversation-analysis paths/contracts and the Yore LLM filter's full
  prompt, JSON validation, dry-run, backend, and write gates.
- Upgraded capability metadata to schema v2 multi-effects/approval boundaries;
  OpenAI Docs is now available-but-degraded without its preferred MCP.
- Hardened Haake destructive confirmations, limited-snapshot disclosure,
  importance persistence, metadata-only updates, schema parity, deterministic
  pagination/cursors, restore cache invalidation, structured operation metadata,
  and stable error envelopes. Large global pages now fetch backend pages beyond
  the previous 50-result truncation.
- Hardened selfimprove discovery, effects, Literal schemas, error envelopes, and
  list pagination across Claude/agent/Codex roots and MCP configuration.
- Added GPTQueue idempotent delivery, bounded timeouts, structured results,
  stable unavailable errors, and server-level control-plane guidance.
- Centralized Cultivar tool naming/dispatch, corrected advertised routing and
  artifact-handle schemas, documented all hidden tools, and deprecated `slice`
  in favor of `query.neighborhood`.

## Verification

- Rahulskills: 11 Python tests; all five shell packaging suites; 46 loaded
  definitions/46 unique names; zero collisions, oversized prompts, personal
  paths, or undeclared skills.
- Haake: full `cargo test`; 43 MCP integration tests; hotspot ratchet; format,
  compile, and diff checks.
- Selfimprove: Ruff; 59 focused tests plus repeated 13-test hardening slice. The
  full suite reached 492 passes before an unrelated pre-existing import-cycle
  inventory failure for three already-absent modules.
- GPTQueue: TypeScript typecheck and 29/29 Vitest tests.
- Cultivar: 42 unit tests, 4 stdio smoke tests, and warning-free Clippy.
- Every repository passes `git diff --check`.

## Upstream submission packets

These system-owned changes were not applied locally because no upstream issue
tracker or submission destination was specified and external writes require a
separate destination decision.

1. **Merge overlapping Figma skills and gate setup.** Consolidate the duplicate
   implementation workflow, require approval before MCP activation/login, and
   remove token echo/persistence guidance.
2. **Reduce ImageGen prompt context and align output rules.** Move setup/model
   recipes to references and resolve the prompt's post-generation report against
   the runtime tool's no-text-after-generation contract.
3. **Make OpenAI Docs fallback-only when Docs MCP is absent.** Remove automatic
   MCP installation/escalation and deduplicate official-source fallback policy.
4. **Harden Plugin Creator external writes.** Gate marketplace/cachebuster/plugin
   activation operations and resolve contradictory top-level `hooks` rules.
5. **Shrink and correct Skill Creator.** Add plugin-routing precedence, qualify
   portable frontmatter guidance, and add semantic safety/output validation.
6. **Harden Skill Installer provenance and rollback.** Require exact-source
   approval, ref pinning, pre-install review, validation, transactional cleanup,
   removal guidance, and protection for system-owned skills.

## Remaining approval-gated work

- Reload the currently stale Haake, GPTQueue, and Cultivar MCP processes only
  after explicit authorization. Source and tests are updated; loaded runtime
  descriptions may remain stale until then.
- Choose upstream destinations before submitting the six packets above.
- Decide whether to commit the five repository worktrees; nothing was committed
  or pushed by this remediation contract.

## Known residual limitations

- Haake snapshots intentionally restore memories and relationships only; access
  logs, revisions, enrichment/entity rows, source rows, channel messages, and
  external provenance removed by cascading deletes are not recoverable.
- Haake success envelopes now expose stable operation/pagination identifiers,
  but versioned domain schemas for full memory/search arrays remain a future
  compatibility project.
- Some legacy Haake errors are still classified at the MCP boundary from
  internal string errors; the wire codes are stable, but a full typed internal
  error migration remains desirable.
