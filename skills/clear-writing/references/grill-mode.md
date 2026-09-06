# Evidence annotations for editing

Read only for explicitly requested grill/annotation mode. This edits and annotates
supplied prose; it does not start an interview or perform the proposed research.
Preserve claims and uncertainty even when flagging a likely error. A placeholder
asks for evidence; it does not establish a fact or supply human approval.

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

> This design will cost less than serverless. `[ASSUMPTION: identify the utilization and cost premises supporting this comparison]`

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
2. Preserve the author's claims and flag contradictions rather than resolving
   them through an invented premise.
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

This removes the explicit universal qualifier without establishing the claim.
Editing cannot settle the cost comparison.

In grill mode, prefer:

> Kubernetes is always cheaper than Lambda at scale. `[VERIFY: test the universal cost claim against workload assumptions and total operating cost]`

Do not make prose more confident than the evidence permits.

---

