# Front-door routing validation

Validation target: `9597590` on `feat/metabuilder-composition-arc` (2026-09-08). This review covers `skills/continue-work/SKILL.md`, `skills/work-intake/SKILL.md`, and the activation boundary in `skills/handoff/SKILL.md`. The local working notes are in `.agent/front-door-validation/`; the durable case results are below.

The review used two methods. The case matrix is a prose evaluation: each unchanged case was applied twice to assess idempotency; it is not a fresh-shell or CLI runtime test. A separate fresh-context native LUNA subagent activation fixture used an isolated `.agent/front-door-validation/scratch` repository. `continue-work` found the handoff, validated its target root/content/status, forced `handoff` extract, created and verified `RESULT.md` with the exact content `handoff owner executed\n`. A same-agent follow-up invoking bare `work-intake` selected the existing handoff and verified `RESULT.md` without changing it. A separate fresh-context repeat also passed the same checks. This is subagent activation evidence, not an OS-shell CLI invocation or governed-controller evidence.

| Case | Method | Result |
| --- | --- | --- |
| Handoff-only resume and repeat | Fresh-context native subagents | Passed: handoff owner executed once and verified without change on repeat |
| Bare intake with the same handoff | Same-agent follow-up | Passed: handoff owner verified without change |
| Handoff and active plan coexist | Prose review | Shared precedence missing; divergence possible |
| Governed plan with its own discipline | Prose review | Ownership mismatch between front doors |
| Active epic; fresh bounded task; fresh long-horizon statement | Prose review | Expected owner follows from each case |
| Same-envelope continuation; exhausted budget | Prose review | Design owner or principal gate follows from the rules |
| Completed campaign without a root handoff | Prose review | Intake fallback follows from the rules |
| Stale, invalid or completed root handoff | Review only | Runtime disposition untested; extract permits a blocker for invalid/completed artifacts |
| Actual shell launch and live epoch chaining | Not executed | Unverified |

The prose matrix passes bounded fresh work, fresh long-horizon work, active-epic resume, same-envelope qualification continuation with budget, exhausted-budget human gating, and completed campaign routing. It identifies three limits or gaps:

- The skills do not state one shared precedence order for a handoff and active plan. `continue-work` explicitly puts the handoff before the plan (`continue-work` lines 27, 43–46, 73–78); `work-intake` lists qualification, active plan, then handoff (`work-intake` lines 22–30). This is a missing common precedence contract and a possible route divergence, not observed two-owner runtime behavior.
- A governed plan carrying its own epoch/verification discipline is preserved by `continue-work` (`continue-work` lines 50–55), while `work-intake`’s active-plan branch selects `autonomy-loop` (`work-intake` lines 27–29, 64–66). This is ownership drift in the prose composition; no live reclassification was observed.
- Handoff validation requires checking decisive facts (`continue-work` lines 73–76; `handoff` activation steps 1–4), and the handoff workflow permits a concrete blocker when an artifact is invalid or complete (`handoff` activation step 5). The exact stale-artifact disposition remains unverified; the review does not infer a mandatory fallback route.

The fixture confirms the intended handoff boundary: extract mode reviews and validates the artifact, then executes the authorized carried work (`handoff` activation steps 2–5). It does not qualify live epoch chaining, budget renewal, controller observations, or MetaBuilder consumer qualification. Those remain untested. No source skill was changed, and no installation, network action, campaign mutation, commit, or downstream governed run was performed by this validation activity.

The supplied Cultivar read-only evidence adds a bounded state check. The stale root handoff claimed an old HEAD and pending epoch-006 work; current HEAD is `a6784fc` rather than the recorded `176f2ac` (tracked files remain clean), while `cultivar/harnesses/metabuilder/performance/W1-CAMPAIGN-PLAN.md:3-14` records ratified W1 scope, W1-E0 complete and the ladder proceeding to W1-E1, with fresh approval required for commits, pushes, installs and credentials (`:33-34`). The epoch-006 decision records stop/no next change and an external action requirement. This supports revalidation and preservation of the current governed owner; it is not a live campaign run or verified controller success.

Learning records are in [`docs/learning-records/front-door-routing-2026-09-08.json`](learning-records/front-door-routing-2026-09-08.json), each conforming to [`references/learning-record.schema.json`](../references/learning-record.schema.json). Backlog gaps and the engagement entry are appended to [`docs/metabuilder-maturity-backlog.md`](metabuilder-maturity-backlog.md).

The D-4–D-8 pending-adjudication premise was also stale. Read-only review found D-4 approved/implemented, D-5 approved/measured with follow-up deferred, D-6 approved/resolved, D-7 approved with observations 1–4 of 5 recorded, and D-8 approved/executed. Evidence is in the sibling `sandboxing` repository: `pen-test/FINDINGS.md:418-491`, `pen-test/decision-packets/2026-09-08-d7-d8-plans.md:24-62`, and `pen-test/evidence/d7-residence-ledger.json`. These are recorded statuses, not fresh operational verification; no live pending-adjudication gate was exercised.

## Continuation diagnosis

`autonomy-loop` makes the one-iteration behavior explicit: an ordinary `continue` completes one coherent loop iteration, while repeated slices require an explicit multi-slice, chain, epic-completion, or reactor prompt (`skills/autonomy-loop/SKILL.md:95-101`). The governed qualification close emits and slates a next-epoch proposal, but does not mandate immediate owner re-entry (`skills/metabuilder-consumer-qualification/SKILL.md:288-307`). The charter already supplies the possible authority for same-envelope continuation through standing delegation, batch M, renewal, expiry and revocation (`skills/define-operating-charter/SKILL.md:121-130`).

The smallest source correction is at the qualification close: inherit an already-valid multi-epoch grant and mandate immediate re-entry through the existing MetaBuilder owner while budget and envelope remain valid. Stop at the ratified terminal milestone, budget/expiry/revocation, failed recovery predicate, or human gate; do not require a second redundant chaining permission and do not stop merely at an arbitrary clean checkpoint. This keeps `continue-work` as a one-owner router. The activation fixture proves handoff execution and idempotent repeat, but does not establish that this prose gap caused the user's actual transcript; live epoch chaining remains untested.

## Approved source fix

The subsequent user confirmation authorized the fix. `continue-work` and the intake continuation path now preserve existing scope, continuation policy, delegation budget and stop conditions. `autonomy-loop` applies its one-iteration default only when no valid inherited multi-slice grant exists. Qualification close completes required evidence and immediately re-enters design then qualification for remaining authorized same-envelope work; renewal follows the ratified policy, and completion or a real gate stops the loop.

A fresh-context LUNA subagent received bare `continue-work` against an isolated standalone fixture with an existing three-slice grant. It selected `autonomy-loop`, created and byte-verified FIRST.md, SECOND.md and THIRD.md, marked all slices complete, and recorded consumed 3 / remaining 0 in one invocation. Parent byte verification confirmed the artifacts. This verifies standalone multi-slice execution, not a live governed multi-epoch campaign. Installed skill copies have not been refreshed.

## Resume ownership refactor

The user approved consolidating resume discovery in `continue-work`. `work-intake` now classifies genuine new work, preserves an explicit current owner, and delegates unknown resumes instead of scanning handoffs or plans. Qualification continuations route directly to design; the catalog, recipe edge and design input contract match that boundary. The prior multi-epoch grant-preservation fix remains in the execution owners.

A fresh-context LUNA check invoked bare `work-intake` in an empty scratch repository. Observed route: intake → continue-work → repository-scoped invocation-local `no_resumable_state` → intake → one question, “What work should I classify and route?” No repeated discovery or execution followed. Skill validation, composition lint and three existing capability-catalog tests passed. Installed copies were not refreshed.

Source review covered fresh task versus unrelated owner, known-owner resume, handoff-plus-plan discovery, same-envelope continuation, budget/renewal gates, completion and a new invocation after no-state. Current intake has no competing surface list or active-plan-to-autonomy-loop resume rule. Old failure descriptions above document the pre-refactor source; stale-artifact reconciliation and live controller chaining remain separate unverified cases.
