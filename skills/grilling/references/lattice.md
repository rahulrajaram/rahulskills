# Native gradient lattice

Read only for explicitly selected `gradient`. It extends
[linear-speculative.md](linear-speculative.md), with the shared question contract
and direct respondent-owned specialist topology. Read
[private-state.md](private-state.md) and
[rendering-and-replay.md](rendering-and-replay.md) before execution: private
consistency is required regardless of whether the user wants debug output.

## Bind capabilities before promising guarantees

The procedures below specify the required scheduler behavior; this skill file
is not an executable scheduler. The bounded `gptengage grill` runtime does not
implement lattice waves, merge keys, graph replay or hard nested token budgets.
Inspect the selected host's actual scheduler/state/checking support. Maintain
node and elapsed-time accounting with real observations; label estimates as
estimates. Hard aggregate token limits require enforceable admission/reservation
and accounting across nested calls, not a retrospective usage sum. Do not claim
a hard cap, atomic graph transaction or deterministic replay without a working
mechanism and relevant verification evidence.

If a required capability is missing, preserve the requested gradient objective,
prepare the axis/stems/evidence plan, and identify the exact blocked guarantee.
Ask only for a material change of budget or execution profile. Continue
independent authorized preparation; do not silently execute a linear substitute
or weaken a user-selected hard limit. Source presence does not prove that an
installed runtime supports a mechanism.

## Run gradient: a bounded, wave-parallel decision lattice

`gradient` is a distinct strategy for cases where the decision space should be
covered **widely and densely** — a smooth continuum of possibilities rather than
a few binary forks — with disciplined, bounded spend. It reuses the speculative
roles (griller, respondent, orchestrator, user) but changes the **topology** and
adds a **resource budget**. It is not a linear interview with a research wave; it
is a bounded branching lattice executed in parallel waves.

### Shape

The lattice is parameterized intentionally:

- **Level 1 is the root**: the single central question (for example "is this
the right base, and how firmly?"). It is not itself a position; it anchors
the axis.
- **The axis** is the one continuous dimension the lattice spans (for example
  confidence/discovery). It must be chosen and documented up front because it
defines what "adjacent" means.
- `n` stems at level 2 (one per major position). Each stem is a discrete,
  non-overlapping position along the axis; adjacent stems should differ by a
  small margin so the lattice is smooth. Enumerating the stems is a scoping
  decision the user sets (or the respondent wave proposes) before expansion;
  `n` is then fixed for the run.
- `b`-way branching per node thereafter.
- `d` maximum depth.
- Theoretical root→leaf paths = `n · b^(d-2)`. This number is a **frontier
  spec, never a build order** — the lattice is grown lazily and pruned, so the
executed cost is far below the theoretical count.
- `keep` (`k`) candidate paths carried as live; `zones` (`z`) divides the
  gradient into regions used to guarantee spread.

A “smooth gradient” is the organizing intent: the `n` stems deliberately span
one axis of the decision space (for example a confidence/discovery axis), so the
kept paths form a continuum of adjacent positions rather than clumping near the
current stance. Enforce this with explicit zone allocation, not by hoping the
top-value paths happen to spread.

### Execution rules

1. **Lazy expansion.** Never materialize a child you will not execute. A node's
   children are forked only when the parent's value-of-information gate passes.
2. **Value function.** Score each candidate node by its decision leverage, its
   shared fan-in (how many paths touch it), its gradient-diversity bonus, over
   an estimated cost:
   `V(n) = (decision_leverage(n) · fan_in(n) · diversity(n)) / cost(n)`.
3. **Beam + VOI prune.** Keep the top-`k` by accumulated value; stop a path the
   moment continuing it can no longer change the recommendation (supported,
   falsified, unresolved-with-a-path, or decision-fixed). Effective depth thus
   varies per path; `d` is a ceiling, not a target.
4. **DAG fan-in dedup.** When paths converge on a shared sub-node, execute it
   once and credit its result to every touching path. This is the single largest
   cost collapse: a huge theoretical lattice can cost a few hundred real nodes.
5. **Wave-parallel execution with barrier checkpoints (bulk synchronous).**
   Respondents run in parallel **per wave**; a serial orchestrator barrier sits
   between waves. **A wave worker is a complete respondent instance, not a
   specialist** — each independently answers its slot and may itself spawn
   bounded specialists (which report only to that worker, never to the
   orchestrator, per the respondent-specialist rules). The barrier does
exact-key clustering, near-duplicate recall, structured-field-confirmed
merges, re-scoring, pruning, and the next zone allocation **before any deeper
wave launches**. Parallelism (produce) and comparison (reconcile) never
overlap.

   **Barrier failure semantics.** The barrier advances only when every worker's
turn in the wave has finished and been validated. A worker that fails or
times out is isolated: its partial output is discarded, its slot is marked
failed (recorded in the ledger, not silently dropped), and the wave is
re-arranged — either retry that slot or, if the runtime is degraded, continue
with the valid workers and record the gap as an incomplete turn. A failed
slot is never merged half-valid into a shared node. If parallel workers finish
unevenly, the barrier waits for the slowest within the budget cap; if a worker
exceeds the wave deadline, that is a bounded failure handled here, not an
excuse to manufacture the missing answer.
6. **Similarity is recall, never merge authority.** BM25/embeddings recall
   candidate near-duplicates and drive MMR (maximal marginal relevance) cross-
   path selection so the kept set spans all zones. **Collapsing a node is gated
   on exact deterministic keys (canonicalized evidence tuples, structured
   fields), never on fuzzy similarity alone.** A fuzzy suggestion is only a
   candidate, always confirmed or reviewed before application. This guards the
   “looked equivalent, wasn't” failure.
7. **Budget caps.** Set an executed-node hard cap and a token/time envelope up
   front. If the beam would exceed the cap, tighten `keep`/`zones` rather than
   run more nodes. Insert a **stop-checkpoint** periodically (for example every
   ~40 executed nodes) so the user can steer before cost accumulates.
8. **Synthesis-only phase.** After the research/expansion waves close, stop
   launching new nodes and enter synthesis (reconcile, run the internal debate
   over the sharpest open split, then close).

### Close

Close `gradient` like any speculative run: user review boundary, the internal
debate over the sharpest open split **when materially different candidate
answers or mutually exclusive positions remain** (consistent with the mandatory
debate rule — it is only skipped when no materially different positions are
left), then the orchestrator's plain-language closing report (recommendation,
implications, trajectory, time and effort, autonomous-execution handoff).
Ratification stays with the user.

### Resumable state and graph mapping

Gradient's lattice is schedule state the orchestrator owns, and it must be
recorded in the same private control envelope as every other node so replay
reconstructs the same frontier (definition-of-done). Persist, per checkpoint:

- the **lattice shape** (`n`, `branch`, `depth`, `keep`, `zones`);
- the **beam**: every live path as a branch, with its accumulated value, its
  zone, and its scheduled/pruned/reopened status;
- the **wave/barrier state**: current wave number, per-slot worker status,
  and the last committed frontier;
- the **budget counters**: executed-node total against the hard cap, token and
  time consumed, and remaining envelope;
- the **deterministic merge keys** already assigned (so dedup is stable across
  replay, preventing a re-run from re-merging differently);
- the **scoring parameters and tie-break rule**, so two replays break ties
  identically.

Map the beam onto the canonical graph faithfully: each kept stem is a real
branch in the ledger; a pruned path has a parked branch with its reopening
condition; a fan-in convergence is recorded as shared-node edges so that
dependency invalidation still walks the same subgraph. The control delta may
carry a nested `lattice` block for this state; it is private and never shown
in human output.

### Typical parameters

A disciplined default is `--n 10 --branch 3 --depth 7 --keep 20 --zones 5`.
The theoretical lattice has 2,430 root-to-leaf paths, but that is a frontier
spec, never a build order. **Expected executed cost is a capped estimate, not
a guarantee:** under lazy expansion + DAG fan-in dedup + VOI pruning with
these parameters, an illustrative planning range is **120–200 executed
refinements**, not a measured benchmark or reliable forecast (not 2,430 materialized paths), always subject to the hard
executed-node cap (`--cap`), a token envelope, and a wall-clock envelope.
Set the hard `--cap` before launching (for example 200) and report actual vs
caps in the closing summary rather than asserting a fixed node count. Costs
are reported as executed refinements, token range, and wall-clock under the
stated parallel/serial assumptions and the explicit budget caps.

## Wave transaction and failure accounting

In the `gradient` strategy the loop is the same atomic contract at **per-wave**
granularity, not per-question: within one wave, each respondent runs steps 5-7
on its own slot in parallel; the orchestrator then runs one barrier checkpoint
that (a) validates each returned answer against the two rendering contracts,
(b) applies each control delta atomically, and (c) only after all valid turns
are applied, recomputes the frontier and selects the next wave. No parallel
worker's output is accepted until it has passed the same validation as a
serial turn; a failed worker turn is discarded and requests a fresh
re-render rather than merged half-valid. This keeps the definition-of-done
replay property (same frontier reconstructed) true under parallelism.

**Wave transaction.** All workers in one wave share the same `base_rev`. To
avoid revision conflicts and partial-wave commits, the orchestrator applies
one **composite wave delta**: it accumulates each validated worker's node
mutations onto a single envelope, applies them in a deterministic commit order
(materialized by `lattice.beam` order, then `path_ref`), and commits that one
delta as the next `rev`. No worker's delta is committed alone mid-wave; this
keeps the atomic "all-or-nothing" contract that the serial loop guarantees, and
a replay replays the whole composite wave as one step.

