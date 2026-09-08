# MetaBuilder Maturity Backlog

Date opened: 2026-09-07

Running ledger of gaps that block or bound long-horizon autonomy around
MetaBuilder. Seeded from [`skill-composition-audit.md`](skill-composition-audit.md);
each real long-horizon engagement appends what it actually hit (see the
metabuilder skill's improve-through-use path and
[`skill-overlap-dispositions.md`](skill-overlap-dispositions.md) for the
composition context).

Entry shape: status (open | prepared | in-progress | closed), the gap, the
triggering evidence, and the exit condition. Do not close an entry without
citing the commit, contract, or qualification that removed it.

## Seeded from the 2026-08-30 audit

| # | Status | Gap | Exit condition |
| --- | --- | --- | --- |
| 1 | prepared | Skill function signatures (registry Phase 0) | Contract registry + linter landed 2026-09-07 for the first five phases; close when every recipe-referenced skill has a contract |
| 2 | open | Authority-safe composition rule | Compiler refuses any composition that widens the ratified envelope; enforced in metabuilder admission |
| 3 | open | Compatibility contract (versioned edges, lockfile for in-flight compositions) | `update-module`-style re-resolution with exact delta and refusal on widening |
| 4 | open | Governed agent-dispatch adapter | External hard spend ceiling + usage evidence + controller verification before dispatch leaves preparation-only |
| 5 | open | Shared framing artifact joining thesis/grilling/charter/DAG/brief | Producer-consumer dispositions landed in prose 2026-09-07; close when the brief cites producer digests mechanically |
| 6 | prepared | Recipe/pack abstraction | `long-horizon-local` recipe landed as repo-owned JSON; close when a metabuilder compose interface binds it |
| 7 | open | Authenticated human approval at authority-expanding gates | Pluggable approval-verifier interface; unauthenticated actor labels cannot cross those gates |
| 8 | prepared | Composition linter | `scripts/lint_skill_composition.py` wired into `audit-skills.sh check` 2026-09-07; close when it also validates edge schema digests |
| 9 | open | Learning-loop wiring | Shared learning-record shape landed 2026-09-07; close when metabuilder retrospectives consume records mechanically |
| 10 | open | Profile expansion (network, credential, target-write) | Versioned profiles with enforcing adapters and adversarial qualification (audit rollout phase 4) |
| 11 | prepared | Post-epoch continuation mechanics | Orchestrator-side loop landed 2026-09-08: continuation handoff at qualification close, work-intake fast path, charter standing delegation with batch M and renewal policy. Core-side unattended multi-epoch remains intentionally excluded (`define-intent-capabilities.md`: convergence never creates continuation authority). Close when a real multi-epoch engagement chains epochs through the fast path and the renewal/exit edges both fire correctly. |

## Engagement log

Append one line per closed long-horizon campaign: date, campaign, gaps hit
(backlog ids or new entries), records filed.
