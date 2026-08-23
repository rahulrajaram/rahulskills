---
name: frame-goals-constraints
description: Frame a complex product, platform, or system direction into a living product thesis before solutioning. Work backward from the future change and customer job; connect an ambitious design horizon to a credible first wedge; separate facts, bets, preferences, constraints, actors, trust boundaries, tradeoffs, and unknowns; and produce aligned customer, product, and technical language with measurable success, stop, and revision rules. Use when the user asks for the big picture, north star, product worldview, positioning, strategic direction, goals and constraints, an approachable expression of a technical vision, or a shared operating model before planning or implementation.
argument-hint: "<problem, product direction, or decision>"
---

# Frame Goals, Constraints, and Direction

Create a **living product thesis**: a lightweight, versioned, falsifiable
decision artifact that connects customer value, product direction, operating
principles, architecture, and evidence.

Do not call the result a doctrine unless the user requests that word. Prefer
language such as **product thesis**, **north star**, **operating story**,
**principles**, **playbook**, or **design horizon**. Make the artifact feel
native to a fast-moving software company: ambitious, testable, revisable, and
useful for making the next decision.

## Select the depth

- Use a **decision frame** for a bounded architecture or operating decision.
- Use a **living product thesis** when the request concerns identity, vision,
  positioning, a long-range horizon, a product wedge, or several connected
  decisions.

If the request spans customer meaning and technical architecture, use the full
living-product-thesis workflow. Do not force one vocabulary on every audience.

## Work backward from the artifact

Before analyzing the system, identify what the resulting frame must enable:

- A customer should understand the problem, value, and first useful product.
- A product team should know what to prioritize and reject.
- An architect should know which boundaries must remain true as implementation
  changes.
- An operator should know what evidence permits progress or requires stopping.
- A future revision should be able to identify which fact, bet, or constraint
  changed.

Use those decisions to determine the necessary depth. Avoid sections that do
not help one of these audiences act.

## Living-product-thesis workflow

1. **Start at the destination.** Describe the observable change in the world if
   the product succeeds at its intended horizon. State whose life or work is
   different and how. Do not begin with components, category language, or an
   implementation.
2. **Return to the customer.** Identify the first customer, painful job,
   current workaround, consequence of inaction, buying trigger, and outcome
   they would recognize. Express the value before introducing technical nouns.
3. **Establish why now.** Name the external shifts that make the problem newly
   urgent or newly solvable. Separate durable forces from temporary release
   excitement and unsupported market claims.
4. **Build a truth ledger.** Classify consequential statements as:
   - observed fact,
   - supported inference,
   - strategic bet,
   - preference,
   - known unknown,
   - protection against unknown unknowns.
   Bind current product claims to evidence or maturity where available.
5. **Connect horizon to wedge.** Define the long-range destination, the first
   independently valuable product cell, and the expansion path between them.
   Explain what structural idea recurs at each scale. Do not let the wedge erase
   the ambition or let the ambition obscure the first buyer.
6. **Define product identity.** State:
   - who the product helps,
   - what outcome it creates,
   - why this product is distinct,
   - what it is now,
   - what it may become,
   - what it will not become.
7. **Map the operating world.** Identify actors, systems, resources, external
   dependencies, and institutions. State who controls, trusts, observes,
   modifies, pays for, benefits from, or bears risk from each relevant part.
8. **Extract goals and measures.** Separate the primary outcome, supporting
   outcomes, non-goals, and observable success measures. Include customer,
   product, system, and learning measures when relevant.
9. **Extract constraints and enduring principles.** Separate:
   - hard prohibitions and authorization limits,
   - safety, security, privacy, and integrity invariants,
   - compatibility and environmental limits,
   - time, cost, resource, and operational limits,
   - product principles that guide tradeoffs,
   - preferences that may be revised.
10. **Expose the tensions.** For each competing concern, explain what both sides
    protect, what fails when either is optimized alone, and the choice or rule
    that resolves the tension for now.
11. **Define trust, authority, and evidence.** When relevant, distinguish:
    - identity: which actor or work item a record names,
    - capability: what can technically perform an effect,
    - permission: what that actor is allowed to do,
    - authority: who may approve or commit the effect,
    - evidence: what demonstrates an event or outcome occurred,
    - judgment: who interprets the evidence and with what confidence.
12. **Compare plausible operating models.** Include the current model when it
    exists, the smallest credible alternative, and at least one materially
    different model. Challenge each with an adversarial example. Add no
    component that does not resolve a named concern or invariant.
13. **Choose the simplest adequate model.** State why it is sufficient now,
    what remains risky, what would falsify it, and which condition requires a
    stronger design.
14. **Make the thesis live.** Define what happens now, what becomes possible
    next, what remains horizon, and which evidence or environmental change
    should trigger revision.

Make reasonable assumptions and continue unless an unknown would change the
authorization boundary, threat model, public promise, buyer, or irreversible
scope.

## Produce a language ladder

When the subject is a product or platform, express the same truth at multiple
altitudes. Lead with the customer layer.

1. **Customer promise** — one plain sentence about the problem and outcome.
2. **Product story** — who it serves, why now, the first useful product, and the
   credible path to the larger opportunity.
3. **Practitioner explanation** — what the product does in operational terms
   and what the user receives or can decide.
4. **Technical precision** — the architecture, trust model, and invariants
   needed by builders and agents.

The layers may use different words but must not make different promises.
Translate heavy internal abstractions rather than deleting their meaning. For
example:

- “constitutional rules” may become “rules that stay true as the system grows”;
- “evidentiary fabric” may become “proof customers can inspect”;
- “federated systems” may become “many teams and systems working together
  without one of them taking control.”

Use precise terms in the technical layer when precision matters. Do not put
them in the customer headline merely because they are architecturally central.

## Default output shape

Adapt the detail to the request. A full living product thesis normally contains:

1. **Customer promise** — one approachable sentence.
2. **Situation and why now** — the problem and external change.
3. **Customer and job** — first user, pain, workaround, and desired outcome.
4. **Destination, wedge, and expansion path** — ambition connected to an
   independently useful first product.
5. **Product identity** — what it is, is not, and will not become.
6. **Goals, principles, and constraints** — outcomes and enduring decision
   rules.
7. **Operating world** — actors, incentives, trust, authority, and evidence.
8. **Strategic tensions and chosen posture** — explicit tradeoffs.
9. **Bets and unknowns** — what is factual, assumed, falsifiable, or protected
   against.
10. **Success and stop signals** — observable evidence for continuing,
    changing, or stopping.
11. **Now / next / horizon** — a direction map, not an implementation backlog.
12. **Language ladder** — customer, product, practitioner, and technical forms.
13. **Decision filters and revision triggers** — how the thesis changes daily
    choices and when it should itself change.

For a bounded decision frame, compress this to situation, goals, actors,
constraints, tensions, unknowns, operating-model comparison, recommendation,
and graduation rules.

Use a compact table or small diagram only when it makes relationships easier to
understand.

## Reasoning discipline

- Do not confuse the current implementation, first product, and long-range
  destination.
- Do not reduce a bold horizon to the nearest sale; do not use the horizon to
  avoid naming the first buyer and useful product.
- Do not turn architecture language into customer copy without translation.
- Do not create a marketing promise stronger than the supporting evidence.
- Do not hide strategic bets inside statements of fact.
- Do not turn audit metadata or self-asserted fields into authority.
- Do not describe an application convention as a security boundary.
- Do not mistake technical capability for permission or legitimacy.
- Do not invent infrastructure before testing whether an existing mechanism
  already satisfies the concern.
- Do not hide a tradeoff inside implementation language; state it explicitly.
- Preserve plural perspectives and affected parties when the intended scale
  crosses teams, institutions, jurisdictions, or communities.
- Treat unknown unknowns through containment, reversibility, diversity,
  observation, and revision—not by pretending to list them exhaustively.

## Handoff to planning and communication

Stop at the shared product thesis or operating model unless the user requests
planning, copy, or implementation.

When planning is requested, preserve the customer outcome, horizon-to-wedge
logic, principles, constraints, bets, maturity, and unresolved decisions in the
issue tree or execution DAG.

When marketing language is requested, derive it from the customer and product
layers. Keep the technical layer as the truth source and flag any claim whose
evidence is not yet strong enough for external use.

## Quality check

Before returning, verify that:

- a plausible customer can understand and repeat the opening promise;
- the first product is valuable without requiring the full horizon to exist;
- the expansion path preserves a recurring structural advantage;
- the team can use the principles to reject attractive but off-direction work;
- architects can identify the trust and authority boundaries;
- facts, bets, preferences, and unknowns remain visibly distinct;
- success, stop, falsification, and revision conditions are observable;
- external and internal language express the same underlying truth;
- the artifact feels revisable and operational rather than ceremonial.
