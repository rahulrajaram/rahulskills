# System-Skill Issue Routing Packets

Date: 2026-07-11
Status: destinations selected; no issue or comment submitted

All six findings belong to the system-owned Codex skill bundle, so the selected
destination is `openai/codex`. Five packets are new issues. The OpenAI Docs
finding is a comment on open issue #24239 to avoid duplicating its core report.
Each row is a separate external write and requires separate approval.

| Packet | Action | Proposed title / target |
|---|---|---|
| SYS-1 | new issue | Consolidate overlapping Figma skills and gate MCP setup |
| SYS-2 | new issue | Reduce ImageGen skill context and align its output contract |
| SYS-3 | comment | #24239, bundled OpenAI Docs skill assumes an optional MCP |
| SYS-4 | new issue | Gate Plugin Creator marketplace and reinstall side effects |
| SYS-5 | new issue | Clarify Skill Creator routing and frontmatter portability |
| SYS-6 | new issue | Add provenance, rollback, and system protection to Skill Installer |

## SYS-1 — Figma routing and setup

**Body draft:** The bundled `figma` and `figma-implement-design` skills encode
substantially the same design-context, screenshot, asset, translation, and
parity workflow. Please make `figma` the concise router and move the detailed
implementation recipe behind it. Setup instructions should not automatically
add/enable an MCP, log in, or echo/persist a token: show the exact source,
destination, permissions, disable/removal path, and request approval first.
Acceptance: one clear routing surface, no automatic activation, secret-safe
verification, and explicit recovery when the MCP is absent.

## SYS-2 — ImageGen prompt/output contract

**Body draft:** The bundled ImageGen skill carries setup and model-selection
context on every invocation and tells the agent to report after generation,
while the runtime contract requires no text after a successful generation.
Please move infrequent recipes to references and choose one authoritative
post-generation behavior. Acceptance: a compact raster-generation router,
unchanged safety/edit routing, and a test that the skill and tool output rules
cannot contradict one another.

## SYS-3 — OpenAI Docs comment on #24239

**Comment draft:** We reproduced the same bundled-skill/MCP availability gap in
a local multi-MCP setup. One additional safety concern is that the fallback
instructions should not auto-install or escalate to the Docs MCP merely because
it is preferred. Suggested resolution: check tool availability first; use the
local Codex manual helper and official OpenAI-domain web fallback when absent;
and present MCP installation as a separately approved capability change with
source, destination, permissions, and removal guidance. This preserves useful
fallback behavior without implying the optional MCP is bundled.

## SYS-4 — Plugin Creator side effects

**Body draft:** Plugin Creator's normal path can write outside the current
repository, update a personal marketplace, run a cachebuster, and reinstall or
activate a plugin. Those are distinct external/capability effects and should be
previewed and approved separately. The prompt also gives conflicting guidance
about top-level `hooks`. Acceptance: explicit dry-run manifest, exact paths and
rollback, approval before marketplace/reinstall operations, and one validated
manifest rule for hooks.

## SYS-5 — Skill Creator routing and portability

**Body draft:** Skill Creator is oversized for its routing role and its claim
that frontmatter may contain only `name` and `description` conflicts with
metadata used by bundled skills. Please route plugin bundles to Plugin Creator,
qualify which frontmatter subset is portable versus runtime-specific, and move
long examples to references. Acceptance: concise router, semantic validation of
safety/output claims, and tests for the documented portable metadata contract.

## SYS-6 — Skill Installer provenance and rollback

**Body draft:** Skill installation activates agent capabilities but the bundled
workflow needs a stronger provenance and rollback contract. Require the exact
repository/source and immutable ref, pre-install manifest review, destinations,
permissions/effects, collision/system-skill protection, transactional staging,
post-install validation, and removal guidance. Acceptance: a dry-run plan,
ref-pinned install, rollback on partial failure, and refusal to overwrite
system-owned skills without a separately explicit authority path.

## Submission checklist

Before any approved write, re-open the destination to detect a new duplicate,
remove local paths/private repository names from evidence, record the exact body
shown to the user, and verify the resulting URL. Approval for one packet does
not authorize any other packet or a follow-up comment.
