---
name: frame-goals-constraints
description: Frame a complex problem or system decision before solutioning by separating goals, environment, actors, constraints, competing concerns, trust boundaries, assumptions, risks, success criteria, and decision boundaries. Use when a user asks for the big picture, says several concerns are competing, wants goals and constraints laid out plainly, questions whether a design is becoming too complicated, or needs a shared operating model before planning or implementation.
argument-hint: "<problem or decision>"
---

# Frame Goals and Constraints

Build a shared model of the problem before recommending constructs or work.
Prefer plain language, explicit distinctions, and the smallest design that
satisfies the actual constraints.

## Framing workflow

1. State the situation in one paragraph without proposing a solution.
2. Separate what is known from assumptions, preferences, and unknowns.
3. Identify the actors, systems, resources, and external dependencies in the
   environment. State who controls, trusts, observes, or can modify each one.
4. Extract the goals:
   - primary outcome,
   - supporting outcomes,
   - non-goals,
   - measurable success conditions.
5. Extract the constraints:
   - hard prohibitions and authorization limits,
   - safety and security invariants,
   - compatibility and environmental limits,
   - time, cost, resource, and operational limits,
   - softer preferences that may be traded off.
6. Name the competing concerns. For each tension, explain what both sides
   protect and what fails if either side is optimized alone.
7. Define trust, authority, and evidence boundaries when relevant. Distinguish:
   - identity: which actor or work item a record names,
   - authority: who may permit an effect,
   - capability: what can technically perform the effect,
   - evidence: what proves an event or outcome occurred.
8. Identify invariants that every acceptable design must preserve.
9. Compare the smallest plausible operating models against the framing. Do not
   add a component unless it resolves a named concern or invariant.
10. Recommend the simplest adequate model, its residual risks, its stop rules,
    and the condition that would require graduating to a stronger design.

Make reasonable assumptions and continue unless an unknown would change the
authorization boundary, threat model, public behavior, or irreversible scope.

## Output shape

Adapt detail to the request, but normally present:

1. **Situation** — the problem in plain language.
2. **Goals and non-goals** — outcomes and exclusions.
3. **Environment and actors** — the operating context and ownership map.
4. **Constraints and invariants** — hard limits before preferences.
5. **Competing concerns** — tensions and failure modes.
6. **Unknowns and assumptions** — facts still needing validation.
7. **Recommended operating model** — the minimum sufficient design.
8. **Decision and graduation rules** — when to proceed, stop, or strengthen the
   architecture.

Use a compact table or small flow diagram only when relationships would be
harder to understand in prose.

## Reasoning discipline

- Do not confuse the current implementation with the underlying requirement.
- Do not turn audit metadata or self-asserted fields into authority.
- Do not describe an application convention as a security boundary.
- Do not invent infrastructure before testing whether an existing mechanism
  already satisfies the concern.
- Do not hide a tradeoff inside implementation language; state it explicitly.
- Do not flatten hard constraints, preferences, risks, and unknowns into one
  undifferentiated list.
- Show where simplicity is safe and where stronger enforcement becomes
  necessary.

## Handoff to planning

Stop at the shared operating model unless the user asks for execution planning.
When implementation is requested, use the accepted frame as input to an issue
tree, execution DAG, or bounded execution contract. Preserve the goals,
constraints, invariants, and unresolved decisions during that translation.

## Quality check

Before returning, verify that:

- every proposed component answers a named concern;
- every hard constraint appears in the recommendation;
- actors with identity are not automatically treated as authorities;
- the trust and threat model is explicit;
- success, stop, and graduation conditions are observable;
- the recommendation is simpler than rejected alternatives for a stated
  reason, not merely because it has fewer parts.
