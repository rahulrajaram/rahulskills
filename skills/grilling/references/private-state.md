# Private graph state and uncertainty contracts

This is the skill-managed graph contract for native speculative execution or an
explicitly resumable interview. It is not the `gptengage grill` checkpoint
format: that runtime's separate `schema_version: 1` records sequential turns,
not this graph protocol. Bind any real validator/store before offering automated
validation or resume. The checks below remain obligations for a profile that
claims them; missing machinery is a visible limitation, never an inferred pass.

## Map the decision graph without exposing it

Maintain the inquiry as a canonical dependency graph owned by the orchestrator.
Preserve the internal vocabulary exactly:

- `Q-*`: a question the griller asked;
- `A-*`: the respondent's candidate answer;
- `B-*`: a mutually exclusive or option-preserving branch, including its fork
  point, scheduling status, and reopening condition;
- `D-*`: a decision explicitly ratified by the user;
- `U-*`: an unresolved uncertainty;
- `R-*`: a respondent-owned research task;
- `W-*` and `T-*`: workflow states and transitions; and
- dependency edges describing what must be reconsidered when an upstream node
  changes.

These identifiers belong to orchestration state, agent-agent transport, and
explicit debug views. They do not belong in ordinary human-visible prose.

An `A-*` graph is not necessarily the path the interview took, and a `B-*`
branch marked for investigation has not thereby been executed or ratified.
Use `selected-for-investigation`, `parked`, `executed`, and `ratified` precisely;
avoid ambiguous status labels such as `active` or `chosen` at review boundaries.

Do not treat an agent answer as a decision. Only the user can ratify a `D-*`
node unless the user explicitly delegates that authority.

The orchestrator assigns stable identifiers, records graph mutations, and maps
the visible question numbers in each human turn to their internal nodes. Do not
make the griller serialize or restate the full graph.

Use the single versioned control-envelope shape under “Persist compact private
control deltas” below. The earlier nested `view`/`delta` example is retired;
do not mix it with the flat `add`/`update`/`remove` fields at the same version.
Question-number bindings are recovered from each node's structured
`content_ref: {turn, item}` and the stored human-turn revision.

Store node text once and refer to it by identifier or transcript reference.
Send a full snapshot only when starting a fresh session, recovering from a
revision mismatch, or explicitly exporting the graph.

A model's hidden scratchpad may hold temporary working context, but it is not a
durable graph store. Persist resumable state in orchestrator-owned state, a
file, or another runtime-controlled store. If no separate transport channel is
available, retain the graph in orchestration context; do not print it into the
user's message.

## Type each unresolved uncertainty

Every unresolved `U-*` node carries a `type` describing its evidence/argument
gap and a separate `kind` describing how it can be resolved. Use the same taxonomy as the `clear-writing` skill's grill mode,
so a single vocabulary covers both editing and interrogation: the reason an
editor flags a sentence is the reason a plan's claim is unproven. Assign the
most specific. If several types apply, record the primary one and note the
others.

- **CITATION** — a factual claim should be supported by a source. Closed by finding the source.
- **VERIFY** — a number, fact, or external claim must be checked. Closed by confirming against a primary or otherwise documented source.
- **JUSTIFY** — a conclusion does not clearly follow from the preceding reasoning. Closed by stating the missing inference.
- **EVIDENCE** — a claim needs data, an example, an experiment, or other empirical support. Closed by producing it.
- **DEFINE** — an important term is ambiguous or overloaded. Closed by fixing its operational meaning.
- **ASSUMPTION** — the argument rests on an unstated premise. Closed by surfacing and testing the premise.
- **COUNTERARGUMENT** — a strong obvious objection goes unanswered. Closed by addressing it.
- **INVESTIGATE** — the claim requires deeper technical or external investigation. Closed by scoping and running that investigation.
- **HUMAN** — the text presents a choice only the user can decide. Closed by the user; never close it on their behalf.

Typing is not a license to over-flag. Mark only gaps whose resolution could
materially change truth, credibility, logical validity, decision quality, or
reader understanding. Do not type an ordinary statement merely because it
could theoretically cite a source.

The type maps to what the griller asks next and what the respondent resolves.
Filter the respondent's resolution precisely: it must close the stated type,
not restyle the claim to sound more confident or less exposed. Do not let a
clean restatement hide the evidence gap.

The diagnostic `kind` is a separate resolver axis:
`recoverable-fact`, `research-needed`, `experiment-needed`, `user-judgment`, or
`external-dependency`. For example, `EVIDENCE` may require either research or an
experiment; `VERIFY` may be a recoverable fact or depend on an external event;
`HUMAN` ordinarily maps to `user-judgment`. Preserve both axes, the specific
resolver and resolution path rather than collapsing them into one taxonomy.

The type is internal machine vocabulary, the same as a `U-*` identifier. It
may appear in the private control envelope and the explicit diagnostic view,
never in a numbered question or in ordinary human-facing prose.

## Persist compact private control deltas

Keep control state in a private, versioned envelope owned by the orchestrator.
This envelope is never part of the rendered user turn.

Use this delta shape:

```json
{
  "v": 1,
  "mode": "delta",
  "run": "G-004",
  "base_rev": 17,
  "rev": 18,
  "human_turn": {
    "id": "H-017",
    "rev": 1
  },
  "add": [],
  "update": [],
  "remove": [],
  "frontier": [],
  "ancestry": [],
  "lattice": {
    "shape": {
      "axis": "confidence-or-discovery",
      "n": 10,
      "branch": 3,
      "depth": 7,
      "keep": 20,
      "zones": 5
    },
    "beam": [
      {
        "path_ref": "B-012",
        "value": 0.0,
        "zone": 2,
        "status": "scheduled"
      }
    ],
    "wave": 0,
    "worker_status": {},
    "last_frontier_rev": 17,
    "budget": {
      "executed": 0,
      "cap": 200,
      "tokens_cap": null,
      "tokens_used": 0,
      "time_cap_secs": null,
      "time_used_secs": 0
    },
    "merge_keys": {},
    "scoring": {
      "params": {},
      "tie_break": "path_ref"
    }
  },
  "recompute": {
    "invalidate": {
      "roots": [],
      "scope": "dependency_subtree"
    },
    "accepted": {
      "paths": []
    }
  }
}
```

The first example is a shape illustration, not a launch-ready lattice budget.
`null` means the corresponding cap is unresolved, never unlimited or zero-cost.
Resolve selected budget constraints before executing dependent waves. Omit the
entire `lattice` field for a linear graph.

Interpret the fields as follows:

- `v` is the control-protocol version.
- `base_rev` is the canonical graph revision to which the delta applies.
- `rev` is the resulting canonical graph revision. Require
  `rev == base_rev + 1`.
- `human_turn.id` identifies the stored human-prose turn, and
  `human_turn.rev` distinguishes a re-rendered version of that turn.
- Every added node has `nr: 1`. Every update carries `from_nr` and the next
  `nr`; reject an update whose `from_nr` does not match canonical state.
- `add` contains new nodes and edges.
- `update` contains field-level `set` and `unset` changes.
- `remove` contains tombstones for nodes removed from the live graph. Removal
  never deletes the raw transcript, and identifiers are never reused.
- `frontier` contains only the internal references for questions currently
  eligible to be answered.
- `ancestry` contains only the minimum references needed to interpret that
  frontier. Do not send the full graph to the griller.
- `content_ref` points to stored human prose using `turn` and `item`. Do not
  repeat question or answer text in the control envelope. When one human item
  states multiple alternatives, an optional `part` ordinal may distinguish
  them without copying their prose.
- `lattice` (gradient only) carries scheduler state: the shape
  (`n`/`branch`/`depth`/`keep`/`zones`), the live beam, the current wave and
  per-slot worker status, and budget counters (executed vs cap, tokens, time).
  It is private and never shown in human output; replay accepts only
  monotonic, self-consistent lattice deltas (see the gradient section).

Apply a delta atomically:

1. Verify `v`, `run`, `base_rev`, envelope shape, node revisions, references,
   and authorization.
2. Compute invalidation against the graph at `base_rev`.
3. Invalidate every reachable dependency descendant of each invalidation root,
   while preserving nodes with no dependency path from those roots.
4. Apply explicit removals, updates, additions, and edge changes.
5. Recompute the eligible frontier from the resulting live graph rather than
   trusting the supplied `frontier`; reject the delta if the two differ.
6. Recompute ratification independently from candidate-answer validity.
7. Commit the envelope as `rev` only if every check succeeds.

Preserve longest-accepted-prefix semantics compactly. Each linear ratification
path is stored as an ordered `path` plus `through`, the last accepted node. If
invalidation reaches any node on that path, retain only the longest prefix
ending immediately before the first invalid node. In a branching graph, store
each explicitly ratified path separately and preserve exact ratified
cross-branch edges; never manufacture one global prefix for a non-linear
graph.

Use `mode: "snapshot"` only when opening a fresh session, resuming without the
required base revision, recovering from a revision mismatch, or compacting
state after durable checkpointing. A snapshot contains the current live nodes,
edges, frontier, minimum resumable ancestry, ratified paths and edges, branch
statuses, unresolved items, transcript references, and tombstones needed to
prevent identifier reuse. Do not emit a snapshot on ordinary turns. After a
snapshot is accepted, resume with deltas whose `base_rev` equals the snapshot's
`rev`.

For a three-question human turn with one two-way branch fork, the rendered
human channel could be:

1. What must be true about the first buyer for this to be worth funding?

2. What evidence would rule out that buyer before you build the product?

3. If direct sales and a channel partnership both remain plausible, what
   observation should determine which path we investigate first?

The corresponding private envelope is:

```json
{
  "v": 1,
  "mode": "delta",
  "run": "G-004",
  "base_rev": 17,
  "rev": 18,
  "human_turn": {
    "id": "H-017",
    "rev": 1
  },
  "add": [
    {
      "t": "q",
      "id": "Q-041",
      "nr": 1,
      "deps": ["A-038"],
      "content_ref": {"turn": "H-017", "item": 1}
    },
    {
      "t": "q",
      "id": "Q-042",
      "nr": 1,
      "deps": ["A-038"],
      "content_ref": {"turn": "H-017", "item": 2}
    },
    {
      "t": "q",
      "id": "Q-043",
      "nr": 1,
      "deps": ["A-039", "B-012", "B-013"],
      "content_ref": {"turn": "H-017", "item": 3}
    },
    {
      "t": "b",
      "id": "B-012",
      "nr": 1,
      "forks_from": "A-039",
      "status": "selected-for-investigation",
      "content_ref": {"turn": "H-017", "item": 3, "part": 1}
    },
    {
      "t": "b",
      "id": "B-013",
      "nr": 1,
      "forks_from": "A-039",
      "status": "parked",
      "content_ref": {"turn": "H-017", "item": 3, "part": 2}
    }
  ],
  "update": [
    {
      "id": "A-039",
      "from_nr": 1,
      "nr": 2,
      "set": {
        "status": "revised",
        "content_ref": {"turn": "H-016", "item": 2}
      },
      "unset": []
    }
  ],
  "remove": [
    {
      "id": "Q-040",
      "from_nr": 1
    }
  ],
  "frontier": ["Q-041", "Q-042", "Q-043"],
  "ancestry": ["A-038", "A-039"],
  "recompute": {
    "invalidate": {
      "roots": ["A-039"],
      "scope": "dependency_subtree"
    },
    "accepted": {
      "paths": [
        {
          "path": ["A-031", "A-038", "A-039"],
          "through": "A-038"
        }
      ]
    }
  }
}
```

The envelope records structure once, refers back to the human turn for content,
and sends the griller only the current frontier plus its minimum ancestry.

