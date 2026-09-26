---
name: metabuilder-progressive-harness
description: Select and evolve the smallest MetaBuilder harness that can prove one index-grounded analysis objective. Use when a harness is becoming complex, when starting an analysis-program calibration case, or when deciding whether evidence justifies another workflow, reviewer, epoch, ledger, or authority mechanism.
argument-hint: "<analysis objective or existing harness>"
---

# MetaBuilder Progressive Harness

## Harness state diagrams

When work in this skill concerns a harness's states or transitions, follow [harness state diagrams](../metabuilder/references/harness-state-diagrams.md) and include the required Mermaid and ASCII diagrams in the final response.

Build the smallest useful index-grounded analysis first. Increase analysis capability and harness governance independently, and only from observed evidence that the current rung is insufficient.

This skill produces a bounded harness recommendation, calibration case, or graduation decision. It does not approve a brief, activate an epoch, grant effects, install a harness, or execute a campaign unless those actions are separately authorized.

## Core rule

> Complexity must be purchased by a demonstrated failure of the simpler system.

Do not add a workflow stage, independent reviewer, retry, epoch, continuation ledger, schema, or campaign mechanism merely because a later system may need it.

## Bind the case

Identify:

- the user-visible analysis outcome;
- the smallest claim that would be independently useful;
- exact source and index identities when available;
- known ground truth and allowed uncertainty;
- required query/evidence families;
- effect and authority boundaries;
- latency, memory, model-call, and artifact ceilings;
- the maximum allowed analysis and harness rungs.

Separate observed facts, assumptions, desired claims, and unavailable evidence. An index-grounded analysis may correctly conclude `insufficient_evidence`.

## Select two independent rungs

### Analysis capability

- `A0 retrieval`: definitions, symbols, references, callers, callees, and types.
- `A1 structure`: impact, dependency, cycle, coupling, documentation, and complexity assessment.
- `A2 coverage`: testing or documentation gap hypotheses.
- `A3 localized_defect`: distinguish a bounded known defect and fix.
- `A4 cross_file_defect`: resource lifetime, stale state, path boundary, or propagation analysis.
- `A5 temporal_defect`: race or TOCTOU hypotheses requiring ordering or lifecycle evidence.
- `A6 composed_program`: LLM-selected composition of bounded analyses.

### Harness governance

- `H0 probe`: read-only expressibility check; no durable semantic claim.
- `H1 single_run`: one frozen bounded workflow and result.
- `H2 evidence_packet`: exact source/index/query/manifest identities and deterministic replay.
- `H3 independent_challenge`: separate analyzer and challenger or verifier over one packet.
- `H4 improvement_epoch`: one finite assess-repair-rerun cycle.
- `H5 campaign`: multiple bounded epochs or corpora with continuation, recovery, and resource accounting.

Choose the lowest rung that preserves the current claim and risk boundary. A difficult read-only analysis does not automatically require H4/H5. External effects may require stronger governance even for a simple analysis.

## Produce the minimum case card

Return:

```text
Objective:
Analysis rung:
Harness rung:
Claim under test:
Ground truth:
Required evidence:
Allowed effects:
Evaluation method:
Performance budget:
Model-call budget:
Complexity budget:
Graduation trigger:
Stop/abstain trigger:
Explicitly deferred:
```

Then describe the smallest finite workflow. Keep campaign policy outside the Harness Module. Keep model narrative outside controller-observed facts.

## Run or assess the case

When execution is authorized:

1. Freeze exact source, binary, index, query, and evaluator identities required by the selected rung.
2. Execute only the minimum workflow.
3. Preserve unsupported, ambiguous, truncated, failed, timed-out, and Unknown outcomes.
4. Evaluate against ground truth rather than rhetorical plausibility.
5. Record latency, resource use, query count, model-call count, and artifact size when applicable.
6. Do not graduate automatically after success.

## Classify failure before adding capability

Choose exactly one primary class while preserving alternative hypotheses:

- `index_gap`: the required fact is absent or represented incorrectly;
- `query_gap`: the fact exists but no bounded supported query retrieves it;
- `evidence_gap`: identity, coverage, provenance, or replay is inadequate;
- `reasoning_gap`: the evidence is sufficient but analysis misses or invents conclusions;
- `evaluation_gap`: ground truth or scoring cannot distinguish quality;
- `runtime_gap`: execution, durability, confinement, or recovery fails;
- `governance_gap`: authority, effects, activation, or continuation is ambiguous.

Route the smallest repair to that owner. Do not patch MetaBuilder to solve a Cultivar query gap, add reviewers to solve an evaluator gap, or add campaign machinery to solve a prompt gap.

## Graduate conservatively

A graduation proposal must state:

- the failed acceptance criterion and evidence;
- why the current rung cannot satisfy it;
- the single capability being added;
- the verification that proves the addition works;
- the mechanisms still deferred;
- any new authority required.

Graduation is refused when an existing mechanism already satisfies the invariant, the failure has not reproduced, the proposed mechanism does not address the primary gap, or the change would expand effects without approval.

## Complexity review

Before accepting a harness, count its meaningful mechanisms: workflows, actions, branches, repeats, external reviewers, approval gates, effect grants, run roots, ledgers, and recovery paths. Require a one-sentence justification for each. Remove any mechanism whose deletion leaves all current acceptance criteria and invariants satisfied.

## Completion

Report the selected two-axis rung, minimum case, evidence and budgets, explicit deferrals, graduation/stop rules, and either:

- `run_minimum_case` when current authority covers execution;
- `repair_one_gap` when a measured deficiency has a bounded owner;
- `seek_authority` when the next capability changes effects or governance; or
- `stop` when the evidence cannot safely support the requested claim.
