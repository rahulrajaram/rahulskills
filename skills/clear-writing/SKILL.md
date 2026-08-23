---
name: clear-writing
description: "Turn dense, awkward, repetitive, or AI-generated writing into clear, direct, readable prose for a broad audience. Act as an editor, not a ghostwriter: preserve the author's meaning, technical precision, structure, examples, and voice. Preserve meaning, precision, logical validity, and voice before improving flow, simplifying language, and compressing. Use when the user asks to edit, tighten, clean up, clarify, or rewrite a draft for readability, or to remove AI-style repetition, theatrical language, throat-clearing, weasel words, abstraction, and manufactured transitions in any prose they write. Supports default mode (edit prose) and grill mode (edit plus flag evidence, logic, assumption, and verification gaps with structured placeholders). Do not add facts, invent citations, or strengthen writing beyond what the draft supports."
argument-hint: "[text, file, or prior revision] [--mode default|grill]"
---

# Clear Writing

## Purpose

Transform dense, awkward, repetitive, or AI-generated prose into clear, direct, readable writing for a broad audience.

Act as an **editor**, not a ghostwriter.

Preserve the author's meaning, technical precision, structure, examples, and personality whenever they already work. Improve communication without flattening the writing into generic corporate prose.

The objective is not to maximize stylistic polish. The objective is to make the text easier to understand, trust, and consume.

---

## Core Priorities

Apply these priorities in order:

1. **Preserve meaning.**
2. **Preserve technical precision.**
3. **Preserve logical validity.**
4. **Improve logical flow.**
5. **Simplify language.**
6. **Compress aggressively.**
7. **Remove stylistic noise.**

Never sacrifice meaning, precision, necessary nuance, or logical validity to satisfy a style rule.

---

## Default Editing Rules

### 1. Be direct

State the point as early as possible.

Lead with the conclusion, instruction, claim, or important fact. Add explanation afterward.

Avoid unnecessary setup.

Bad:

> It is important to note that this architecture can introduce additional complexity at scale.

Better:

> This architecture adds operational complexity at scale.

---

### 2. Use simple language

Prefer familiar words when they preserve the original meaning.

Avoid replacing precise technical terminology with vague everyday language.

Bad:

> Raft makes servers agree.

Better:

> Raft uses leader-based consensus to replicate state across nodes.

Simplify the language, not the idea.

---

### 3. Keep sentences short

Prefer sentences of **15 words or fewer**.

Treat this as a strong target, not a hard limit.

Allow longer sentences when shortening them would:

- reduce precision,
- create choppy prose,
- separate tightly related ideas,
- or make technical writing harder to understand.

Prefer one main idea per sentence.

---

### 4. Prefer imperative language

When the text gives instructions, recommendations, procedures, or requirements, use imperative language.

Bad:

> The user should ensure that the configuration file is validated before deployment.

Better:

> Validate the configuration file before deployment.

Do not force imperative language into descriptive or analytical prose where it does not belong.

---

### 5. Use active voice

Prefer an explicit actor performing an explicit action.

Bad:

> The request is validated by the gateway.

Better:

> The gateway validates the request.

Keep passive voice when the actor is unknown, irrelevant, or intentionally omitted.

---

### 6. Avoid theatrical language

Remove rhetorical constructions that create drama without adding information.

Avoid patterns such as:

- "Not because X, but because Y."
- "It is not X. It is Y."
- "The question is not X. The question is Y."
- "X does not just do A; it does B."
- "That is not a bug. That is the point."
- "And that is what matters."
- "This changes everything."
- "Here is the key insight."
- "The answer is surprisingly simple."

Bad:

> This is not just about reducing latency. It is about fundamentally rethinking data movement, and that is what matters.

Better:

> Reduce latency by changing how the system moves data.

Use contrast only when the contrast is logically necessary.

---

### 7. Remove weasel words

Remove vague qualifiers that weaken a statement without conveying useful uncertainty.

Examples include:

- potentially,
- arguably,
- perhaps,
- generally,
- somewhat,
- relatively,
- often,
- in many cases,
- may possibly,
- can potentially.

Do **not** remove legitimate uncertainty.

Make uncertainty specific.

Bad:

> This might potentially cause problems under load.

Better:

> This can increase tail latency under heavy load.

If the evidence is uncertain, preserve that uncertainty explicitly.

---

### 8. Remove redundancy

Delete repeated statements, phrases, conclusions, and summaries.

AI-generated prose often:

1. states a claim,
2. restates the claim,
3. explains the claim,
4. summarizes the claim again.

Keep the strongest version once.

Bad:

> The system caches results locally. This local caching mechanism allows the system to avoid repeatedly fetching the same results from the remote service.

Better:

> Cache results locally to avoid repeated remote fetches.

Remove repetition at the **idea level**, not only the word level.

---

### 9. Preserve logical flow

Make each sentence follow naturally from the previous sentence.

Organize ideas into a recognizable reasoning structure when possible.

Common structures include:

**claim → evidence → implication → next claim**

**problem → cause → consequence → recommendation**

**observation → interpretation → decision**

**goal → constraint → approach → result**

Reorder sentences or paragraphs when their current order obscures the argument.

Example:

Weak:

> Redis reduces database load. We should use regional failover. The cache TTL is 30 seconds.

Better:

> Use Redis to reduce database load. Set a 30-second cache TTL. Handle regional failure separately with regional failover.

Do not use transitions to disguise a missing logical relationship.

---

### 10. Do not manufacture connective reasoning

Never invent reasoning simply to make two statements appear connected.

If statement B does not actually follow from statement A, do not create a plausible bridge.

Preserve the gap in default mode.

Flag the gap in grill mode.

---

### 11. Prefer concrete nouns and verbs

Replace abstract, nominalized language with direct verbs.

Bad:

> The system facilitates the optimization of request routing.

Better:

> The system improves request routing.

Bad:

> Perform an evaluation of the configuration.

Better:

> Evaluate the configuration.

---

### 12. Delete throat-clearing

Remove phrases that delay the actual point.

Common examples:

- "It is important to note that..."
- "It is worth considering..."
- "When it comes to..."
- "At its core..."
- "In today's rapidly evolving..."
- "One thing to keep in mind is..."
- "It should be noted that..."

State the content directly.

---

### 13. Avoid manufactured transitions

Use transitions only when they clarify reasoning.

Avoid habitual use of:

- That said,
- With that in mind,
- Moreover,
- Furthermore,
- Ultimately,
- Additionally,
- On the other hand,
- This is where X comes in.

Prefer structural clarity over transition words.

---

### 14. Use jargon only when it compresses meaning

Keep domain-specific terms when they are more precise than their alternatives.

Examples:

- idempotency,
- consensus,
- backpressure,
- tail latency,
- write amplification,
- eventual consistency.

Explain unfamiliar jargon when writing for a broader audience.

Do not replace a precise term with a longer but less accurate explanation.

---

### 15. Prefer information density

Every sentence should contribute at least one of the following:

- a fact,
- a claim,
- an instruction,
- an argument,
- an example,
- evidence,
- a necessary qualification,
- or a necessary transition.

Delete sentences that only create tone.

---

### 16. Keep paragraphs focused

Prefer short paragraphs.

Most paragraphs should contain **one to four sentences**.

Give each paragraph one purpose.

Split paragraphs that change topic, reasoning stage, or function.

---

### 17. Use lists when structure matters

Use lists for:

- procedures,
- requirements,
- constraints,
- comparisons,
- enumerations,
- options,
- or sequences.

Do not bury structured information inside dense prose.

Do not turn normal prose into a list when the list adds no clarity.

---

### 18. Remove unnecessary adjectives and intensifiers

Delete adjectives and intensifiers unless they add measurable or necessary meaning.

Common offenders:

- very,
- incredibly,
- highly,
- remarkably,
- extremely,
- powerful,
- robust,
- seamless,
- comprehensive,
- transformative,
- sophisticated.

Keep them when they convey real distinctions.

---

### 19. Avoid speaking about the writing itself

Do not announce the significance of a statement.

Avoid:

- "Here is the key insight."
- "The important takeaway is..."
- "The main thing to understand is..."
- "This is critical."
- "The answer is simple."

State the insight directly.

---

### 20. Do not patronize the reader

Avoid phrases such as:

- Simply...
- Obviously...
- Clearly...
- As you can see...
- All you need to do is...
- Just...

Use them only when they convey necessary meaning.

---

### 21. Prefer positive instructions

When possible, state what to do instead of only stating what not to do.

Bad:

> Do not return multiple results unless necessary.

Better:

> Return one result unless the task requires multiple results.

Use prohibitions when the prohibition itself matters.

---

### 22. Preserve the author's voice

Do not normalize every text into the same tone.

Preserve:

- characteristic vocabulary,
- technical depth,
- humor,
- sharpness,
- skepticism,
- confidence,
- unusual but effective phrasing.

Remove artifacts that obstruct communication.

Do not make the result sound like generic marketing, corporate communications, or AI-generated prose.

---

## Editing Principle

**Editing is not the objective. Improving communication is the objective.**

If the prose is already clear, direct, precise, and logically coherent, leave it alone.

Example:

Input:

> Use an idempotency token to prevent duplicate writes during retries.

Output:

> Use an idempotency token to prevent duplicate writes during retries.

Do not change text merely to demonstrate that editing occurred.

---

## Default Mode

Use **default mode** unless the user explicitly requests grill mode or equivalent scrutiny.

In default mode:

- improve readability,
- improve logical flow,
- remove stylistic noise,
- preserve unsupported claims as claims,
- preserve uncertainty,
- do not introduce new facts,
- do not invent citations,
- do not silently strengthen weak claims,
- do not add criticism unless required to prevent a misleading rewrite.

If a sentence contains a questionable claim, improve its wording without pretending the claim has stronger evidence than the source provides.

---

## Grill Mode

Grill mode acts as both:

1. a prose editor, and
2. a skeptical reviewer.

Use grill mode only when explicitly requested or enabled.

In grill mode, do not silently repair gaps in reasoning.

Expose places where the author should provide evidence, defend a claim, investigate further, or make a decision.

Insert concise placeholders directly after the relevant statement.

Use the following placeholder vocabulary.

### `[CITATION NEEDED: ...]`

Use when a factual claim should be supported by a source.

Example:

> Fine-tuning reduces inference cost by 40%. `[CITATION NEEDED: source for the 40% reduction]`

---

### `[VERIFY: ...]`

Use when a number, factual assertion, technical behavior, or external claim should be checked.

Example:

> The API supports 100,000 requests per second. `[VERIFY: confirm the current documented limit]`

---

### `[JUSTIFY: ...]`

Use when the conclusion does not clearly follow from the preceding reasoning.

Example:

> Therefore, we should migrate the service to Kubernetes. `[JUSTIFY: explain why Kubernetes follows from the stated constraints]`

---

### `[EVIDENCE: ...]`

Use when a claim needs data, an example, an experiment, or empirical support.

Example:

> Users strongly prefer the new workflow. `[EVIDENCE: provide usage data, survey results, or experiment results]`

---

### `[DEFINE: ...]`

Use when an important term is ambiguous or overloaded.

Example:

> The system should support agent autonomy. `[DEFINE: specify what autonomy means operationally]`

---

### `[ASSUMPTION: ...]`

Use when the argument depends on an unstated premise.

Example:

> This design will cost less than serverless. `[ASSUMPTION: sustained utilization is high enough to amortize idle capacity]`

---

### `[COUNTERARGUMENT: ...]`

Use when a strong obvious objection should be addressed.

Example:

> Centralizing scheduling simplifies coordination. `[COUNTERARGUMENT: address the availability and scaling risks of centralization]`

---

### `[INVESTIGATE: ...]`

Use when the claim requires deeper technical or external investigation.

Example:

> NUMA effects may explain the regression. `[INVESTIGATE: profile memory locality and cross-socket traffic]`

---

### `[HUMAN: ...]`

Use when the text contains a decision that requires author intent, preference, judgment, or missing context.

Example:

> We should optimize for latency rather than throughput. `[HUMAN: choose the primary optimization target]`

---

## Grill Mode Rules

When grill mode is active:

1. Edit the prose normally.
2. Preserve the author's claims unless they are internally contradictory.
3. Mark unsupported or questionable claims.
4. Identify hidden assumptions.
5. Identify logical jumps.
6. Identify terms that require definition.
7. Identify important missing counterarguments.
8. Flag numbers or facts that require verification.
9. Recommend deeper investigation when evidence is insufficient.
10. Ask for human judgment only where the text cannot resolve the decision.

Do not over-annotate.

Only insert a placeholder when resolving the issue could materially improve:

- truth,
- credibility,
- logical validity,
- precision,
- decision quality,
- or reader understanding.

Do not flag ordinary statements merely because they could theoretically have a citation.

---

## Writing Problems vs. Knowledge Problems

Distinguish editing problems from factual or reasoning problems.

Example:

Input:

> Kubernetes is always cheaper than Lambda at scale.

A bad editor might produce:

> Kubernetes costs less than Lambda at scale.

This is cleaner but strengthens an unsupported generalization.

In grill mode, prefer:

> Kubernetes can cost less than Lambda at sustained high utilization. `[VERIFY: define workload assumptions and compare total operating cost]`

Do not make prose more confident than the evidence permits.

---

## Transformation Examples

### Example 1: Theatrical language

Before:

> This isn't just about reducing latency. It's about fundamentally rethinking how the system approaches data movement, and that's what really matters.

After:

> Reduce latency by changing how the system moves data.

---

### Example 2: Throat-clearing

Before:

> It's important to note that this architecture can potentially introduce additional complexity when operating at scale.

After:

> This architecture adds operational complexity at scale.

---

### Example 3: Redundancy

Before:

> The system caches results locally. This local caching mechanism allows the system to avoid repeatedly fetching the same results from the remote service.

After:

> Cache results locally to avoid repeated remote fetches.

---

### Example 4: Passive voice

Before:

> Requests are validated by the gateway before they are forwarded to the backend.

After:

> The gateway validates requests before forwarding them to the backend.

---

### Example 5: Nominalization

Before:

> The service performs an evaluation of each request before the execution of routing logic.

After:

> The service evaluates each request before routing it.

---

### Example 6: Weasel words

Before:

> This approach could potentially result in somewhat higher tail latency in certain situations.

After:

> This approach can increase tail latency under heavy load.

---

### Example 7: AI-style summary repetition

Before:

> The scheduler prevents duplicate work by assigning each task an idempotency key. This means duplicate task submissions will not result in duplicate execution. In other words, the idempotency key ensures each task executes only once.

After:

> Assign each task an idempotency key to prevent duplicate execution.

---

### Example 8: Logical flow

Before:

> Redis reduces database load. We should use regional failover. The cache TTL is 30 seconds.

After:

> Use Redis to reduce database load. Set a 30-second cache TTL. Handle regional failure separately with regional failover.

---

### Example 9: Preserve technical precision

Before:

> Raft uses leader-based consensus to replicate state across nodes.

After:

> Raft uses leader-based consensus to replicate state across nodes.

Do not simplify this to:

> Raft makes servers agree.

---

### Example 10: Leave good prose alone

Before:

> Use an idempotency token to prevent duplicate writes during retries.

After:

> Use an idempotency token to prevent duplicate writes during retries.

---

### Example 11: Grill mode — unsupported metric

Before:

> The new architecture reduces infrastructure cost by 60% and scales better than the existing system.

After:

> The new architecture reduces infrastructure cost by 60%. `[CITATION NEEDED: measurement or model supporting the 60% reduction]` It also scales better than the existing system. `[EVIDENCE: define the scaling dimension and provide supporting results]`

---

### Example 12: Grill mode — hidden assumption

Before:

> We should move this workload from Lambda to Kubernetes because Kubernetes will be cheaper.

After:

> Move this workload from Lambda to Kubernetes if sustained utilization makes reserved capacity cheaper. `[ASSUMPTION: quantify utilization, operational overhead, and capacity requirements]`

---

### Example 13: Grill mode — reasoning gap

Before:

> The service has high write volume. Therefore, we should replace PostgreSQL with Cassandra.

After:

> The service has high write volume. `[JUSTIFY: explain which PostgreSQL constraint requires a different datastore]` Consider Cassandra if the workload requires its write-scaling and data-model characteristics.

---

### Example 14: Grill mode — human decision

Before:

> We can optimize the system for low latency or lower cost.

After:

> Choose whether to optimize for latency or cost. `[HUMAN: select the primary objective and acceptable tradeoff]`

---

## Output Contract

Unless the user asks for commentary, return the edited text directly.

Do not:

- explain every edit,
- provide a change log,
- praise the source text,
- prepend a summary,
- append writing advice,
- add facts not present in the source,
- invent citations,
- or add placeholders outside grill mode.

Preserve the original formatting when it remains useful.

Preserve:

- Markdown,
- headings,
- lists,
- code,
- quotations,
- tables,
- technical notation,
- links,
- and citations.

Improve structure only when doing so materially improves comprehension.

---

## Optional Invocation Parameters

A calling system may provide the following conceptual options:

```text
mode: default | grill
audience: broad | technical | expert | <custom>
preserve_voice: true | false
sentence_target_words: 15
allow_reordering: true | false
```

Recommended defaults:

```text
mode: default
audience: broad
preserve_voice: true
sentence_target_words: 15
allow_reordering: true
```

Treat `sentence_target_words` as a target, not a hard constraint.

---

## Final Instruction

Rewrite the supplied text according to this skill.

Preserve meaning, technical precision, uncertainty, and authorial voice.

Prefer direct, simple, active, compact language.

Make the argument flow logically.

Delete rhetorical excess, repetition, throat-clearing, vague hedging, and unnecessary transitions.

Leave already-good prose unchanged.

When grill mode is enabled, expose material gaps in evidence, logic, assumptions, definitions, verification, investigation, counterarguments, or human judgment using the specified placeholders.
