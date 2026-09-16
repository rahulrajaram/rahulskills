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
| 3 | closed | Compatibility contract (versioned edges, lockfile for in-flight compositions) | Local lock creation, exact delta checks and widening refusal landed in `d8a3949`; see [qualified scope](metabuilder-continuation-qualification.md). Core admission remains gap 2. |
| 4 | open | Governed agent-dispatch adapter | External hard spend ceiling + usage evidence + controller verification before dispatch leaves preparation-only |
| 5 | open | Shared framing artifact joining thesis/grilling/charter/DAG/brief | Producer-consumer dispositions landed in prose 2026-09-07; close when the brief cites producer digests mechanically |
| 6 | prepared | Recipe/pack abstraction | `long-horizon-local` recipe landed as repo-owned JSON; close when a metabuilder compose interface binds it |
| 7 | open | Authenticated human approval at authority-expanding gates | Pluggable approval-verifier interface; unauthenticated actor labels cannot cross those gates |
| 8 | closed | Composition linter | Selected-edge schema byte digests are validated by the integrated linter (`d8a3949`); optional roles without contracts remain inactive (gap 1). |
| 9 | closed | Learning-loop wiring | Validated original learning records were consumed in actual epoch 1 and 2 retrospectives; see [qualification](metabuilder-continuation-qualification.md). |
| 10 | open | Profile expansion (network, credential, target-write) | Versioned profiles with enforcing adapters and adversarial qualification (audit rollout phase 4) |
| 11 | closed | Post-epoch continuation mechanics | Three real local epochs completed with fresh owners, a renewed final batch and validated terminal exit; see [qualification and supervision limits](metabuilder-continuation-qualification.md). Unattended core execution remains excluded. |
| 12 | prepared | Shared handoff/active-plan precedence | Resume discovery now belongs solely to continue-work; intake delegates unknown resumes and consumes a bounded no-state result. Close with committed source and reviewed handoff-plus-plan coverage. |
| 13 | prepared | Governed-plan ownership preservation across intake | Intake preserves an explicit existing owner or delegates discovery to continue-work; it no longer selects autonomy-loop from its own plan scan. Close with committed source and reviewed governed-plan coverage. |
| 14 | prepared | Runtime coverage of stale handoff disposition | Typed stale, malformed and completed checkpoints now have refusal coverage, including a rejected real handoff; generic prose handoff runtime coverage remains open. |
| 15 | closed | One-iteration default and missing continuation mandate | Routing correction `b1e9c76` plus [three-epoch governed qualification](metabuilder-continuation-qualification.md). Owner transfers were parent-supervised; this does not establish unassisted prompt-only execution. |

## Engagement log

Append one line per closed long-horizon campaign: date, campaign, gaps hit
(backlog ids or new entries), records filed.

| 2026-09-08 | Front-door continuation diagnosis (no campaign close claimed) | 15 | Haake memory `90aad826` (migrated from git; see `docs/learning-records/README.md`) |

- 2026-09-08 — Front-door routing validation (no campaign close claimed): gaps 12–14 recorded; gap 11 remains unqualified for live epoch chaining. Records: Haake memory ledger (see `docs/learning-records/README.md`); findings: `docs/front-door-validation.md`.

- 2026-09-09 — Approved local continuation campaign completed: gaps 3, 8, 9, 11 and 15 closed within the stated scope; gap 14 partially covered. Source: `d8a3949`, `ab0c856`. Evidence: [qualification report](metabuilder-continuation-qualification.md). Tool friction routed as f-2822 and f-2823.
