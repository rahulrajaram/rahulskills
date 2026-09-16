---
name: objective-to-dag-decomposition
description: Decompose vague or complex objectives into a MECE issue tree, typed reasoning nodes, an execution DAG, and a phased implementation plan with verification.
argument-hint: "<objective>"
---

# Objective to DAG Decomposition

Use this skill when the user asks to reason hierarchically, get a 50K-foot view,
decompose a product or project, build an issue tree, create a work breakdown
structure, convert an objective into a DAG, or turn vague intent into actionable
implementation and verification work.

## Inputs, scope, and authority

Bind the requested objective, existing decisions, constraints, acceptance
criteria, and any project-native task/queue format from available evidence.
Reuse a supplied plan rather than assuming the work starts from nothing.
Decomposition does not by itself select implementation, queue writes, external
research, or a new governance workflow. Necessary local inspection and routine
planning choices remain autonomous within the request.

Prepare a provisional plan and concrete alternatives before asking about a
material unresolved scope, authority, public behavior, or irreversible choice.
Hold only the dependent decision/work; reuse still-valid user answers. Do not
invent requirements, evidence, estimates presented as measurements, or approval
from a graph. Mark inferred priorities and unknown dependencies explicitly.

## Purpose

Transform a root objective into:

1. a crisp objective summary,
2. a MECE decomposition tree for reasoning,
3. a typed execution DAG for sequencing,
4. a recommended execution plan with a critical path and first vertical slice.

This is not a generic task-list generator. Preserve causal structure,
abstraction levels, decisions, risks, artifacts, and verification paths.

## Default stance

- Be decisive and make reasonable assumptions when the objective is vague.
- Ask a clarifying question only when the answer would materially change scope,
  risk, public behavior, or irreversible execution.
- Prefer capability decomposition first for product-building work.
- Cross-check the capability split against user journey, architecture, data,
  integrations, risks, milestones, and verification.
- Do not flatten the hierarchy too early.
- Stop decomposing when leaves are small enough to implement, test, delegate,
  estimate, or consciously defer.

## Node taxonomy

Every node must use exactly one of these types:

- `objective`
- `capability`
- `requirement`
- `architecture_component`
- `design_decision`
- `implementation_task`
- `verification_task`
- `risk`
- `open_question`
- `artifact`
- `milestone`

Keep risks as risks, questions as questions, decisions as decisions, and tasks
as tasks. Do not disguise uncertainty as implementation work.

## Decomposition workflow

1. Define the root objective as a concrete outcome.
2. Capture explicit assumptions, constraints, unknowns, and success criteria.
3. Choose the primary decomposition lens:
   - user journey,
   - system capabilities,
   - architecture layers,
   - data model,
   - external integrations,
   - risks and unknowns,
   - milestones,
   - verification strategy.
4. Decompose top-down using MECE pressure:
   - sibling nodes are mutually distinct,
   - sibling nodes collectively cover the parent,
   - sibling nodes sit at the same abstraction level,
   - each split helps decision-making, implementation, or verification.
5. Recurse only until the leaves are actionable.
6. Convert the reasoning tree into an execution DAG:
   - add dependency edges between leaves and shared prerequisites,
   - separate `refines` edges from `depends_on` edges,
   - add `verifies`, `produces`, and `consumes` edges when useful.
7. Attach acceptance criteria to requirements, implementation tasks, and
   verification tasks.
8. Attach a verification method wherever possible.
9. Identify the critical path, first useful vertical slice, and deferrals.
10. Run the quality checks before answering.

## Output contract

For a full decomposition or an explicit/automated JSON consumer, return these
four sections and preserve the structured contract below. For a requested quick
overview, use the compact mode instead; do not impose JSON unless requested or
required by the consuming workflow.

### 1. Objective Summary

- Restate the root objective.
- List assumptions.
- List constraints.
- List success criteria if known or inferable.
- List important open questions, but keep going unless one is blocking.

### 2. Decomposition Tree

Present a readable top-down tree. Mark node types inline.

Example shape:

```text
Build product [objective]
├── User-facing workflow [capability]
│   ├── Upload input [requirement]
│   └── Review generated graph [requirement]
└── Verification strategy [capability]
    ├── Golden examples [verification_task]
    └── Schema conformance checks [verification_task]
```

### 3. Execution DAG

Return valid JSON in a fenced `json` block:

```json
{
  "nodes": [
    {
      "id": "string",
      "title": "string",
      "type": "objective | capability | requirement | architecture_component | design_decision | implementation_task | verification_task | risk | open_question | artifact | milestone",
      "description": "string",
      "parent_id": "string | null",
      "depends_on": ["string"],
      "inputs": ["string"],
      "outputs": ["string"],
      "acceptance_criteria": ["string"],
      "verification": {
        "method": "manual_review | unit_test | integration_test | e2e_test | golden_test | static_analysis | benchmark | none",
        "description": "string"
      },
      "risks": ["string"],
      "open_questions": ["string"],
      "estimated_complexity": "small | medium | large"
    }
  ],
  "edges": [
    {
      "from": "string",
      "to": "string",
      "type": "depends_on | refines | blocks | verifies | produces | consumes"
    }
  ]
}
```

The example above is a shape template: choose one actual enum value per field
and emit only actual nodes and references in the result.

`nodes[].depends_on` is the canonical execution prerequisite representation:
for node A, entry B means A waits for B. Keep `edges` for compatibility, with
exactly one `{"from":"A","to":"B","type":"depends_on"}` projection for each
canonical entry and no extra dependency projections. Reject missing IDs,
duplicate IDs/edges, self-dependencies, and cycles. `parent_id` and `refines`
express reasoning containment (child to parent), not execution precedence.
Other typed relations explain evidence/artifact relationships; they cannot hide
scheduling prerequisites. A real blocking prerequisite belongs in `depends_on`
even when also annotated as `blocks` (blocker to blocked node).

Execution dependencies are always acyclic. Represent iteration as a single
bounded task with its iteration limit, exit condition, and verification stated
in its description/acceptance criteria, or describe feedback separately from
the execution graph. Do not add a dependency back-edge and call it a DAG.

Use stable, readable node IDs such as `graph.schema`, `api.graph_read`, or
`frontend.graph_view`. Do not use opaque sequential IDs unless the objective has
no natural namespace.

### 4. Recommended Execution Plan

Group the DAG into phases. Include:

- the critical path,
- the first useful vertical slice,
- what to defer,
- suggested parallel workstreams when they are genuinely independent,
- the next 3 to 7 executable actions.

If the active project uses a queueing system and the user asks to enqueue
work, prepare the exact queue changes and use the applicable existing authority.
Reuse an accepted decomposition when still valid; ask only about unresolved
material scope or queue-write authority before the dependent write.

When the objective is long-horizon work routed to a MetaBuilder harness, the
execution DAG feeds `metabuilder-harness-design` directly: obligations come
from task and verification nodes, and workflow ordering follows the
`depends_on` projection.

## Quality checks

Before returning the result, validate:

1. No sibling group mixes wildly different abstraction levels.
2. Every major capability has at least one verification path.
3. Every implementation task has acceptance criteria.
4. Execution prerequisites are acyclic, all IDs resolve, and dependency edges
   exactly match the canonical `depends_on` projection. Iteration is bounded
   inside a node or recorded separately from execution dependencies.
5. The first vertical slice is small enough to build quickly.
6. Open questions are separated from tasks.
7. Risks are not disguised as implementation tasks.
8. The plan preserves the difference between the reasoning tree and the
   execution DAG.

If a quality check fails, revise the decomposition before answering. If a tradeoff
is intentional, call it out briefly.

## Compact mode

When the user asks for a quick view, a concise dependency list or diagram is
sufficient. Preserve the outcome, meaningful node types, prerequisites,
verification, critical path, first vertical slice, and unresolved decisions.
If JSON is explicitly requested or required by an automated consumer, keep the
JSON small while retaining its nodes/edges contract and projection checks.
