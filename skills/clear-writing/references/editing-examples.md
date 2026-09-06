# Editing rules and examples

Read when an editing choice needs a worked example. These are fidelity checks,
not licenses to add a metric, workload, cause, actor, or stronger modality.
Preserve descriptive versus imperative force and useful authorial structure.

## Default Editing Rules

### 1. Be direct

State the point as early as possible.

Lead with the conclusion, instruction, claim, or important fact. Add explanation afterward.

Avoid unnecessary setup.

Bad:

> It is important to note that this architecture can potentially introduce additional complexity.

Better:

> This architecture can add complexity.

---

### 2. Use simple language

Prefer familiar words when they preserve the original meaning.

Avoid replacing precise technical terminology with vague everyday language.

Bad:

> Raft uses leader-based consensus in order to replicate state across nodes.

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

> This concerns reducing latency and rethinking how the system moves data.

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

> This might cause problems under load.

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

> The system caches results locally to avoid repeated remote fetches.

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

> Redis reduces database load. The cache TTL is 30 seconds. We should use regional failover.

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

> The system helps optimize request routing.

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

## Transformation Examples

### Example 1: Theatrical language

Before:

> This isn't just about reducing latency. It's about fundamentally rethinking how the system approaches data movement, and that's what really matters.

After:

> This concerns reducing latency and rethinking how the system moves data.

---

### Example 2: Throat-clearing

Before:

> It's important to note that this architecture can potentially introduce additional complexity.

After:

> This architecture can add complexity.

---

### Example 3: Redundancy

Before:

> The system caches results locally. This local caching mechanism allows the system to avoid repeatedly fetching the same results from the remote service.

After:

> The system caches results locally to avoid repeated remote fetches.

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

> This approach could increase tail latency in certain situations.

---

### Example 7: AI-style summary repetition

Before:

> The scheduler prevents duplicate work by assigning each task an idempotency key. This means duplicate task submissions will not result in duplicate execution. In other words, the idempotency key ensures each task executes only once.

After:

> The scheduler assigns each task an idempotency key to prevent duplicate execution.

---

### Example 8: Logical flow

Before:

> Redis reduces database load. We should use regional failover. The cache TTL is 30 seconds.

After:

> Redis reduces database load. The cache TTL is 30 seconds. We should use regional failover.

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

> We should move this workload from Lambda to Kubernetes because Kubernetes will be cheaper. `[VERIFY: compare costs for this workload, including utilization and operating overhead]`

---

### Example 13: Grill mode — reasoning gap

Before:

> The service has high write volume. Therefore, we should replace PostgreSQL with Cassandra.

After:

> The service has high write volume. Therefore, we should replace PostgreSQL with Cassandra. `[JUSTIFY: explain why the write volume warrants this replacement]`

---

### Example 14: Grill mode — human decision

Before:

> We can optimize the system for low latency or lower cost.

After:

> We can optimize the system for low latency or lower cost. `[HUMAN: identify the preferred objective if this choice is needed]`

---
