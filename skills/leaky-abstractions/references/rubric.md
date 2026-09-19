# Leaky-abstraction review rubric

This rubric operationalizes the skill's standard: ordinary consumers should
reason in domain terms and stable, uniform contracts, not implementation
mechanics. It is a judgment aid, not a score that can prove quality.

## Dimensions and probes

| Dimension | Look for a consequential leak when | Healthy evidence |
|---|---|---|
| Consumer and boundary mapping | A caller, operator, or document reader must know an internal layer's topology, storage, scheduling, encoding, vendor, or protocol to complete an ordinary task. | Roles and trust boundaries are explicit; domain inputs and outcomes cross the boundary. |
| Information hiding and volatility | A detail likely to change is represented in public types, names, sequencing rules, or mandatory configuration. | Parnas-style information hiding localizes design decisions and replacement affects a small boundary. |
| Substitution and change locality | Valid implementations, providers, or subtypes cannot substitute without caller branches, casts, retries, or special cases. | Behavioral promises remain valid for substitutes; changes stay behind the boundary. |
| Uniformity | Similar operations require different verbs, envelopes, errors, pagination, auth, or lifecycle rules without a domain reason. | Related operations share predictable semantics and conventions. |
| Common path and progressive disclosure | The common task requires advanced knobs, internal vocabulary, setup choreography, or a long caveat trail. | Simple cases are simple; advanced power is available behind explicit, discoverable escape hatches. |
| Failure, performance, lifecycle | Consumers must infer retries, partial failure, ordering, backpressure, caching, latency, cleanup, or ownership from implementation behavior. | Observable semantics are documented and stable, with safe defaults and actionable errors. |
| Escape hatches | No escape exists when a real advanced use case is foreseeable, or the escape requires abandoning the abstraction and importing internals. | A bounded lower-level path is intentional, documented, and does not contaminate ordinary consumers. |

## Finding threshold

Require all four before calling something a material leak:

1. **Boundary:** identify what abstraction claims to hide and who crosses it.
2. **Mechanism:** name the implementation detail that crossed the boundary.
3. **Burden:** show consumer learning, branching, coordination, operational, or
   change-locality cost on a reachable path.
4. **Consequence:** explain why the cost is consequential for this scope.

Classify as a design trade-off or non-finding when the exposed behavior is a
stable domain fact, a measured performance/resource requirement, an explicit
advanced capability, or an honest limitation that consumers can handle through
a uniform contract. Escalate when the leak is undocumented, surprising,
volatile, repeated across consumers, or causes every consumer to reconstruct
the same hidden mechanism.

## Concrete examples

### Usually non-leaky

- A repository's `UserStore.get(id)` returns a domain result and normalizes
  database errors into documented outcomes. Switching SQL engines does not
  require callers to learn SQL state codes.
- A media API exposes `play`, `pause`, and a documented `ended` event while
  hiding decoder and buffer implementation. It exposes a separate advanced
  buffer-control API for clients that genuinely need it.
- A REST resource uses the same representation, method semantics, cache rules,
  and self-descriptive errors across resource types. A proxy can intervene
  without clients knowing the service topology.
- A queue client offers `publish` with explicit delivery guarantees and a
  separate tuning surface for batching. Consumers do not need to know shard
  assignment for the common path.

### Usually leaky

- A “reliable” network client makes callers understand TCP retransmission,
  packet-size limits, connection pooling, and retry timing to avoid ordinary
  data loss or latency surprises, while exposing raw socket exceptions.
- A storage abstraction returns ORM/driver-specific query objects, requires
  callers to manage transactions and connection lifetimes, or changes behavior
  based on a backend-specific isolation level that is not in the contract.
- A cloud object API claims provider neutrality but makes callers branch on
  provider error codes, regions, eventual-consistency windows, and pagination
  tokens for every operation.
- A wrapper has a simple `send()` name but requires callers to set hidden
  thread affinity, event-loop ownership, serialization order, and cleanup
  callbacks that vary by implementation.
- A design document says “the service handles retries” while its examples and
  incident procedures require consumers to distinguish timeout, accepted-but-
  not-visible, and duplicate states through undocumented timing assumptions.

These examples are prompts for evidence, not automatic verdicts. TCP, storage
engines, cloud providers, and event loops have real semantics; exposing a
necessary constraint can be justified if it is explicit, uniform, and scoped.

## Source-grounded principles

- Joel Spolsky, [The Law of Leaky Abstractions](https://www.joelonsoftware.com/2002/11/11/the-law-of-leaky-abstractions/): non-trivial abstractions leak; use this to avoid an impossible leak-free standard.
- David Parnas, [On the Criteria to be Used in Decomposing Systems into Modules](https://doi.org/10.1145/361598.361623): hide design decisions likely to change so comprehension and flexibility improve.
- John Ousterhout, [Designing Abstractions](https://web.stanford.edu/~ouster/CS349W/lectures/abstraction.html): prefer a small interface that hides substantial complexity and isolates change.
- W3C, [Web Platform Design Principles](https://www.w3.org/TR/design-principles/): make common cases simple, keep high- and low-level APIs on a gradual power curve, and be consistent; lower-level APIs can be deliberate escape hatches.
- Barbara Liskov and Jeannette Wing, [A Behavioral Notion of Subtyping](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf): judge whether substitutes preserve specified behavior, not merely whether types line up.
- Jakob Nielsen, [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/): prioritize primary features and reveal advanced detail when needed to reduce learning and error burden.
- Roy Fielding, [REST dissertation, Chapter 5](https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm): uniform interfaces and layered constraints improve visibility, independent evolution, and substrate independence, with explicit efficiency trade-offs.

## Related practice, not copied instruction

API design guides and architecture-review checklists overlap with this lens,
especially around consistency, versioning, and common paths. For comparison,
see [Google API Design Guide](https://cloud.google.com/apis/design) and
[Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines).
They are adjacent references, not dependencies or templates for this skill;
the distinguishing output here is evidence of consumer-facing abstraction
leakage and its change-locality consequence across code and design artifacts.
