---
name: leaky-abstractions
description: Review code, plans, and design documents for consequential abstraction leaks, excessive consumer burden, and non-uniform contracts; report evidence and calibrated findings without changing the target unless fixes are explicitly requested.
metadata:
  short-description: Detect consequential leaks in code and design artifacts
---

# Intent and applicability

Use this skill when a user asks whether an implementation, API, architecture,
plan, or design document hides its internals well enough for ordinary
consumers. It is a read-only review by default and applies to source code,
public interfaces, operational interfaces, plans, RFCs, ADRs, and design docs.

The governing question is: can the intended consumer reason in domain terms
and stable contract terms, or must they understand volatile implementation
mechanics to use, substitute, diagnose, or evolve the system? All non-trivial
abstractions leak to some degree. Report only leaks that impose consequential,
evidenced burden on a relevant consumer or boundary; do not treat every
exposed detail as a defect.

# Inputs and local bindings

Bind, from the request and repository evidence:

- the absolute target and scope (changed files, named components, or document);
- the intended consumer(s), their common path, expertise, and trust boundary;
- the abstraction's advertised purpose, contract, and lifecycle;
- the underlying implementation or dependency whose details might leak;
- available tests, examples, API specifications, error documentation, and
  design constraints.

If the consumer or intended scope is unclear, state the assumption and use the
most ordinary external consumer supported by the artifact. Ask only when the
choice would materially change the finding. Read
[references/rubric.md](references/rubric.md) for the review dimensions and
source-grounded examples.

# Non-goals

- Do not demand that every interface be minimal, generic, or equally simple.
- Do not equate low-level access, configuration, observability, or an escape
  hatch with a leak when it is explicit, bounded, and appropriate for its user.
- Do not review general correctness, security, performance, or style except
  where those facts establish abstraction leakage or consumer burden.
- Do not prescribe a particular architecture, programming language, or
  abstraction layer merely because it is fashionable.

# Must not

- Must not modify, format, commit, or install anything in the target during a
  default review.
- Must not claim that an abstraction is leak-free; use calibrated language and
  disclose unobserved paths.
- Must not infer a finding from naming or complexity alone. Tie every finding
  to a reachable consumer path, a concrete detail, and an observable burden or
  change-locality consequence.
- Must not hide uncertainty: distinguish observed facts, reasoned inferences,
  counterevidence, and proposed remedies.

# Interaction and authority

Reviewers have read-only authority unless the user explicitly requests fixes.
Routine selection of relevant rubric dimensions needs no extra approval. If a
requested fix would change a public contract, compatibility policy, or product
behavior, present the impact and wait for the user's decision before editing.

# Procedure

1. **Map the boundary.** Name the producer, abstraction boundary, underlying
   mechanisms, and each consumer. Trace one ordinary success path and one
   failure, slow, restart, or substitute path. For plans and design docs,
   treat stated actors, interfaces, operational steps, and assumptions as the
   evidence; mark absent implementation evidence as unknown.

2. **State the intended contract.** Summarize what a consumer should need to
   know, what should remain replaceable, and what complexity is deliberately
   exposed. Separate domain concepts from storage, transport, scheduling,
   serialization, vendor, topology, and other volatile details.

3. **Apply the rubric.** Check consumer/boundary mapping; information hiding
   and volatile details; substitution and change locality; interface
   uniformity; common-path burden and progressive disclosure; failure,
   performance, and lifecycle semantics; and escape hatches. Consider both
   call-site evidence (imports, branches, retries, casts, special cases,
   flags, leaked types) and document evidence (prerequisites, caveats,
   exception tables, sequence diagrams, and operational runbooks).

4. **Test the counterfactual.** Ask what changes when the implementation is
   replaced, deployed elsewhere, slower, partially unavailable, or given a
   new valid subtype. A leak is stronger when many consumers must change,
   learn internals, or coordinate out-of-band. It is weaker when the detail is
   stable, intentionally part of the domain contract, isolated to an advanced
   path, or justified by a measured trade-off.

5. **Calibrate severity.** Use `critical`, `high`, `medium`, or `low` only
   when the evidence supports it. Weight ordinary-path reach, consumer count,
   volatility, failure impact, and workaround cost. A sophisticated tool may
   have a sophisticated interface; judge whether complexity is progressive,
   uniform, and necessary rather than whether it is large.

6. **Write findings.** For each finding include:

   - `ID`, severity, and concise title;
   - exact location or document section and the affected consumer;
   - observed evidence (quote, call pattern, dependency, or stated rule);
   - the hidden mechanism that crossed the boundary;
   - concrete consumer burden and likely change/failure consequence;
   - counterevidence or why the complexity may be warranted;
   - a smallest useful remedy, framed as an option rather than an unauthorized
     patch; and
   - confidence (`high`, `medium`, or `low`) and what would verify it.

7. **Close with coverage.** Summarize boundaries examined, ordinary and
   exceptional paths, dimensions not observable, non-findings, and any
   unresolved questions. If no consequential leak is evidenced, say so and
   list the residual risks rather than manufacturing findings.

## Output shape

Use this compact structure:

```text
Verdict: [well-contained | mixed | materially leaky | insufficient evidence]
Scope and consumers: ...
Findings:
- [ID] [severity] Title
  Location/consumer: ...
  Evidence: ...
  Leak and burden: ...
  Counterevidence: ...
  Option: ...
  Confidence/verification: ...
Coverage and residual risk: ...
```

# Completion and evidence

Completion requires a bounded scope, named consumers, evidence-backed findings
or an explicit insufficient-evidence verdict, and counterevidence considered
for each material concern. The result is a review claim, not proof of semantic
correctness or usability. Keep source excerpts short and identify paths,
symbols, sections, or examples so another reviewer can reproduce the judgment.
