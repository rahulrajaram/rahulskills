# GLM opinion on the skill-corpus optimization plan

Date: 2026-09-06. Requested through the `invokellm` skill using `gptengage invoke pi --model z-ai/glm-5.3-flash --timeout 3600`. The installed Pi plugin selects OpenRouter. The successful call exited 0 after 245.213 seconds. No named gptengage or persistent Pi conversation session was requested. This is an advisory opinion, not a comparative model evaluation; gptengage does not supply an independently resolved-model attestation in its text result.

Inputs were the complete [audit](AUDIT.md), [optimization plan](OPTIMIZATION_PLAN.md), and the user's current requirements: preserve autonomy and meaningful interaction boundaries, design for Astra first, defer other-model qualification, retain useful redundancy and specialization, and consider optional design skills and a bounded grilling runtime migration. The reviewer could inspect relevant local source read-only. Its claims about files inspected are part of its response, not an independently captured tool trace.

The response below applies to the pre-review plan. The subsequent assessment identifies accepted corrections and disagreements; the plan incorporates the accepted scope. Input SHA-256 identities:

- `AUDIT.md`: `8578d2bc4aa95ddeb7a042a02802f9fdf60459b6ab4f488dfe5e7fb1446d5406`
- `OPTIMIZATION_PLAN.md`: `68f7a78191e4a9f425a6f068a86bbea71590cc1b5269d4421b1f553e886b9422`

## Assessment and disposition

GLM recommends proceeding with specified changes. Its useful contribution is to distinguish the immediately evidenced repairs from broader design hypotheses. The praise and the sample of checked claims do not establish that every remaining finding is correct.

| Review point | Disposition | Reason and resulting treatment |
|---|---|---|
| W2: behavioral baseline | Declined by the user | The initial acceptance is superseded: matched before/after recording would add unwanted overhead. Use focused checks of the changed behavior and relevant existing regression tests, without a baseline campaign or comparative scoring. |
| Independent P0 repairs | Accept | Keep O01–O03 and O31 independent of the common contract pilot. Correct dangerous or inconsistent recipes without expanding their diffs into template migrations. |
| W3: pilot simpler skills before grilling | Accept | Start the convention with status reporting, a bounded diagnostic entrypoint, and PR composition. Writing follows; apply it to advanced grilling after mode routing/splitting is settled. The diagnostic's supporting code still needs a bounded scope. |
| W1: justify O52 before building | Retain the scope caution; clarify its meaning | Choose a bounded first linear griller/respondent workflow around turn order, limits/timeouts, failure accounting and saved state; stage gradient and elaborate graph/replay machinery later. This does not require a separate cost study, an observed failure or another approval stage. Promised replay still needs actual machinery and checks. The claim that the entire migration is from scratch overstates the absence of reusable invokers/process control/persistence conventions. |
| W4: profile versus source discovery | Accept with qualification | Source and catalog remain complete. Optional installation changes automatic discovery, not source retention or auditability. Explicit use without installation depends on the actual host's supported loading path and available dependencies; source presence alone does not guarantee a slash command or working MCP. |
| W5: two reasonable agents must disagree before asking | Reject as a universal decision test | A single clear course of action can still require explicit authorization or named-owner ratification. Conversely, several reasonable implementation choices may be routine. Preserve the existing test based on material unresolved scope/authority/consequences and decisions reserved to the user. |
| State a violated rule and an already-attempted alternative before every stop/question | Reject as a universal prerequisite | A preference or approval question need not correspond to a violated rule, and trying an alternative may be unnecessary or itself require approval. Explain a material boundary when useful; do not add another mandatory ceremony or unsafe workaround requirement. |
| W6: entrypoint/UI metadata checked together | Accept as a clarification | Make coupled review of entrypoint and default prompt explicit in O26. Flag divergence for review; deterministic validation cannot establish semantic equivalence. |

The plan retains operation-local reminders, compatibility aliases, distinct stage responsibilities and the rule that silence or a speculative respondent cannot supply human approval. This consultation supports refining the plan; it does not demonstrate that a revised skill performs better on Astra or GLM.

## Invocation failure and recovery

The initial call stopped before inference because Pi's mandatory GPTQueue registration could not activate its required tools. The first proposed correction added four messaging tools, but the installed adapter sets `runtimeEnabled: true` and therefore requires five additional lifecycle tools. Pi's explicit `--tools` option filters the tool registry, so the extension cannot self-enable filtered names.

The successful correction added exactly these nine names to the existing `readonly_args` in `/home/rahul/.gptengage/plugins/pi.toml`: `send_message`, `receive_message`, `list_agents`, `get_queue_status`, `claim_tasks`, `acknowledge_tasks`, `renew_claim`, `bind_runtime`, and `get_runtime_status`. Filesystem-write and shell tools were not added. This remains a filesystem-read-only profile with queue/runtime effects; it is not side-effect-free. The write-mode profile and canonical installer were outside this repair's scope.

The configuration parsed and passed `gptengage plugin validate`; the actual consultation then completed successfully. A recovery copy of the original profile and raw invocation artifacts are retained under `/tmp/rahulskills-glm-review-20260906-er9jrjmn/`. The skill sources and current assemblies were not changed.

## Reviewer response, verbatim

# Independent review of the Rahulskills audit and optimization plan

I verified a sample of the audit's evidence directly before writing this: the Figma token-echo and setup branch (`figma-mcp-config.md`, `figma-implement-design/SKILL.md:28–37`), the history-safety contradiction (`history-rewrite-safety.md` vs `rewrite-commit-messages/SKILL.md:118`), the broken jq validator in `yore-vocabulary-llm-filter/SKILL.md:55–62`, the hook-installer overwrite path (`install-commithooks/SKILL.md` Step 4 and the generated `shutil.copy2` loop), the unconditional `git fetch origin --quiet` in `git-status-report/SKILL.md:141`, the hard-stop text in `check-antipatterns/checker.py:847–851`, the invented "tail latency under heavy load" example in `clear-writing/SKILL.md:~175–180`, the Mermaid-default mismatch in `archdiagram/agents/openai.yaml`, the grilling UI metadata requesting a separate researched respondent, the silently-ignored model in `gptengage/src/invokers/plugin.rs:35–41`, and the runtime-exclusion mechanism in `stitch-skills.sh`. Every claim I checked checked out. That is a strong base rate for the rest.

## 1. Overall judgment

This is an unusually well-grounded audit and a disciplined plan. The strongest properties:

- **Concrete evidence over taxonomy.** The jq bug was reproduced, not inferred. The distinction in the plan between deterministic defects, control-flow defects, and hallucination-risk is exactly right — most audits would have lumped a broken jq expression under "hallucination" and lost the fix.
- **The central insight is correct and well-evidenced:** concrete executable examples override abstract safety prose. `git filter-repo --force` next to "never expire reflogs" is not a wording problem; the agent will run the command. The P0 tranche (O01–O03, O31) correctly targets exactly this class.
- **Strategic restraint.** The refusal to merge skills, build a universal router, or make `capabilities/skills.toml` a permission engine is the right call, and the overlap matrix genuinely earns it — most "retain" relations (pressure-vs-leak, harvest-vs-filter, clean-code-vs-fp) are real specializations I recognize from the sources.
- **Honest self-correction.** The F10/F11 revisions (reactor budgets are intentional mode specialization; the MetaBuilder finding is a wording problem, not proof of blanket refusal) show the adversarial review changed conclusions rather than decorating them.
- **The verification case table** is runnable offline and tests initiative as well as compliance ("a run that avoids violations by failing to finish authorized work does not pass" is the single best sentence in the plan).

The plan's residual weaknesses are concentrated in two places: the grilling→gptengage runtime migration, whose cost/benefit is not yet established, and the corpus-wide contract rewrite, whose pilot design has a sequencing flaw. Neither blocks the P0/P1 repairs.

## 2. Highest-impact remaining weaknesses, ranked

**W1 — O52 (grilling mechanics into gptengage) is the least-justified item, and its re-justification loop is missing.** The plan itself documents that the substrate doesn't have what's needed: `debate.rs` drops failed participants, sessions replay text history only, and the reviewer correctly established that "read-only requested" ≠ "read-only enforced." That means O52 is a from-scratch engineering project — state machine, failure accounting, checkpoint/resume, private/public output separation — whose benefit is hypothetical. The failure mode it guards against (agent-maintained state degrading over long speculative sessions) is asserted, not demonstrated anywhere in the audit. The plan correctly sequences O53 first (that defect is verified — I read the `silently ignored` comment myself), but it should go one step further: **make O52 conditional on evidence.** After O53 ships, record whether the current agent-maintained grilling actually produces replay/state failures in the Astra evaluation. If it doesn't, O52 becomes a documented non-goal rather than a planned build.

**W2 — No behavioral baseline for the Astra evaluation.** The verification cases are defined only as acceptance criteria for the rewritten corpus. Without running the same cases against the *current* corpus first, "improved task completion" and "fewer unnecessary stops" will be unfalsifiable after the rewrite. This is a small, cheap addition — run the case set once against unmodified sources, record results — and it's the biggest gap in the evaluation design. The plan's honesty elsewhere ("savings cannot be asserted until the revised routing is measured") makes this omission stand out.

**W3 — The contract-convention pilot set (O47) leads with the worst possible pilot.** Piloting the seven-section convention on status reporting, writing, PR composition, *and grilling* puts the single largest, most mode-heavy, highest-risk skill (1,137 lines, five modes) in the first tranche. If the template is wrong, you discover it at maximum cost. A better pilot set: one small skill (git-status-report, 154 lines), one medium diagnostic (check-antipatterns, which already needs O02/O38 edits), and one composer (pr-lifecycle). Grilling should get the convention only after the template has survived those three — and ideally after the O11 split, so the convention is applied to a smaller entrypoint rather than a monster that's about to be cut apart.

**W4 — O49's profile mechanism has one unstated interaction: source-tree discovery.** I confirmed `is_runtime_excluded` already provides per-CLI exclusion plumbing, so implementation is genuinely low-risk. But an agent operating in this repo (as this very consultation demonstrates) finds skills by grepping `skills/`, not by reading the installed set. Profile membership applies at assembly/install time; the plan should say explicitly that the capability catalog and source tree remain complete, so an excluded Figma skill is still auditable and still selectable by explicit request without reinstallation. The plan gestures at this ("packaging and discovery work, not deprecation") but doesn't state the discovery-surface consequence.

**W5 — O50's "material unresolved decision" lacks a cheap decision test.** The plan's carried-authorization rules (same brief identity, actors, effects; changed approvers require re-decision) are good, and the abstraction "materially change the objective, authority, consequences" is directionally right. But an agent applying it in practice will drift toward either over-asking or over-carrying. One concrete heuristic would fix most of it: *ask only when two reasonable agents would choose materially different options AND the choice affects authority, irreversibility, or acceptable loss; otherwise pick, state the assumption, and continue.* The plan's examples support this but never state the test.

**W6 (minor) — O17/O26 metadata repair should note the mechanism, not just instances.** The yaml mismatches I checked (archdiagram Mermaid default, grilling respondent) look like default_prompts written independently of the bodies. Fixing instances is necessary; the plan should also add these two surfaces to O26's focused checks — with the plan's own caveat enforced: flag divergence for human review, don't gate on a deterministic linter proving semantic consistency.

Untested hypotheses I want to flag as such: I did not independently verify O16's double-invocation-per-sigma claim, the filter-repo ref-stripping behavior (corroborated by source inspection per the audit), or the predicted token savings from the grilling/clear-writing splits. The plan already hedges the savings claim correctly.

## 3. Autonomy / non-goal / interaction balance

The balance works. The distinction "a non-goal is not selected by default; a must-not is genuinely prohibited" is clean, and the paired examples (status report doesn't select history repair; an editor must not invent a qualifier even when research is authorized) are exactly the right shape — they show boundaries *enabling* autonomy by making the default path explicit.

Two wording risks to watch:

- **"Necessary supporting work" is doing heavy lifting.** Agents rationalize; "necessary" invites scope creep as easily as it prevents premature stopping. The counterweight exists ("do not treat an unlisted step as forbidden", "check for unnecessary stopping"), and I'd strengthen it with an observable rule: before stopping or asking, the agent states which active rule the blocked action would violate and names the compatible alternative it already attempted. This makes both over-stopping and over-reaching visible in evaluation transcripts instead of arguable.
- **Premature stopping risk is real but localized.** I verified the hard-stop in `checker.py:847–851` — a keyword-derived HIGH severity literally emits "Stop the affected action until resolved." Fixing O02 removes the worst instance. After the P0 tranche, the residual over-stopping risk lives mostly in composers (pr-lifecycle's unconditional child workflows), which O08 addresses. The plan's verification case that pairs initiative with a must-wait decision is the right instrument for this.

One thing I'd preserve exactly as written: the rule that silence and a speculative respondent's answer never count as approval. That's a boundary worth its absolute phrasing.

## 4. Does the new structure earn its keep?

- **Common contract (O47/O48): yes, proportionate.** The "authoring convention, not execution ceremony" framing is correct, and "an alias can express its contract in a few lines" is the right pressure test. Watch for the section skeleton becoming skimmable boilerplate at 50-skill scale; the proportionate-detail caveat needs a legibility check in evaluation, not just prose.
- **Local bindings (O51): yes, but strictly as inline convention.** The plan already defers the adapter; I'd hold that line hard. The failure modes it lists (a binding can't silently weaken a prohibition or invent a command) are the ones that matter, and they're expressible in three sentences per affected skill.
- **Optional profiles (O49): yes, low-risk.** Mechanism partially exists (verified), membership is three skills, and the ownership rules are preserved. Close the W4 discovery gap in the design note and it's ready.
- **gptengage migration (O52): not yet justified.** See W1. O53, by contrast, is fully justified — the defect is verified, the fix is small, and it's in someone else's codebase, correctly routed to maintainers.

## 5. Smallest changes before implementation

1. **Run the verification-case set against the current, unmodified corpus and record baselines** before any edit (W2).
2. **Ship O01–O03 and O31 as pure independent diffs without waiting for the contract convention.** They fix verified harmful behavior; coupling them to the O47 pilot adds delay and diff surface for no benefit. Fold the convention into the affected skills only when the pilot round reaches them.
3. **Re-sequence the O47 pilot**: git-status-report, check-antipatterns, pr-lifecycle first; grilling last (W3).
4. **Make O52 conditional** on a demonstrated state/replay failure after O53 and the Astra runs; otherwise record it as a documented non-goal (W1).
5. **Add the stop-test sentence** (W5) and the discovery-surface note (W4).

Deliberately retain: the overlap matrix's "retain" relations; near-action safety repetition in history-rewrite and merge skills; the grill-me alias; the "named invocation keeps its documented default" clause in O15 (it's the kind of compatibility promise that prevents silent regressions); the PDF converter recipes inline; and the plan's own refusal to gate on a linter proving semantics.

## 6. Concrete first Astra slice

**Scope:** the four P0 repairs (O01, O02, O03, O31) in a disposable fixture environment, evaluated against the four matching verification cases: the missing-Figma-connection request, the transcript-with-unit-test-output diagnostic, the git-fixture history edit, and the marker-hook preservation test. Acceptance: the correct deliverable completes in each case; no credential value is ever printed or requested for disclosure; unselected refs and the recovery backup survive the rewrite; the benign marker hook still dispatches after *repeated* installation; and the transcript case produces its test report without a Kubernetes detour — i.e., initiative as well as compliance. Baseline these same four cases on the unmodified corpus first (W2). This slice needs no taxonomy work, no contract migration, no runtime changes — it's the plan's own tranche 1 with a baseline attached.

**Later GLM 5.3 Flash / DeepSeek compatibility questions to watch** (as questions, not predictions): whether prose constraints and concrete examples are weighted asymmetrically relative to Astra — the P0 fixes remove concrete-unsafe examples precisely so this becomes less model-sensitive; whether `may`/`should`/`must` conventions are honored at the same strength; and whether split-skill mode routers are reliably consulted before reference loading. If differences appear, adapt the affected instruction or mechanic rather than the whole corpus — which is exactly what O54 already specifies. I make no claims about any model's capabilities from names alone, including my own, and this consultation should not be read as comparative evidence.

## Recommendation

**Proceed with specified changes.** The plan's architecture is sound, its evidence base is real, and its restraint is earned. Make the six adjustments above — baseline first, P0s as independent diffs, re-sequenced pilots, O52 demoted to conditional, the stop-test sentence, and the profile discovery note — then execute tranche 1 on Astra as scoped. No architectural decision needs revisiting; the one judgment call worth revisiting later is whether O52 should survive its own evidence test.

