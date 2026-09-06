# Rendering, replay and resume obligations

Read for private machine transport, explicit replay/resume, or qualification of
those guarantees. These correctness requirements are not optional merely
because graph display is hidden. Debug presentation itself remains opt-in via
[review-boundaries.md](review-boundaries.md).

The host may perform manual structural review during an ordinary or native
speculative interview, but manual review does not prove automated validation.
This source package provides no universal graph validator/replay engine.
`gptengage grill` provides ordered private call checkpoints and a structural
public projection only; it has no graph delta replay, semantic question validator,
or guaranteed suppression of private input echoed in model text. Verify an
actual implementation and its checks before offering stronger guarantees.
If a selected resumable profile requires unavailable checks, preserve the
checkpoint/unknown status and stop dependent resume; never invent a passing
validator command. Continue independent work allowed by the selected scope.

## Enforce rendering on weak instruction-following models

Require channel separation at the display boundary. A model instruction alone
does not enforce it; apply available structural checks and review the intended
prose. No denylist proves that model text contains no paraphrase of private input.

### Put human prose first

Generate the complete human channel before generating any agent-machine
structure. If the runtime carries both channels in one stream, the human prose
must come first, followed by the control payload. Never place identifiers,
schemas, routing metadata, state, or ledgers before or inside the human prose.
The renderer must remove the trailing control payload before presenting the
turn to the user.

### Give machine content a zero-token visible budget

The machine-content budget for every user-facing turn is exactly **0 tokens**.
Question-list numbering and ordinary quantities or dates inside a question are
human prose; identifiers, field names, envelopes, ledgers, state labels, and
transport delimiters are machine content. Keep any permitted control payload
private and outside the rendered turn.

### Keep graph ownership outside the griller

The orchestrator exclusively owns the decision graph, dependency edges,
branch state, revision counters, resumability data, and question-to-identifier
mapping. The griller receives only the current question frontier and the
minimum ancestry needed to ask the next questions. Never ask the griller to
print, restate, synchronize, summarize, or repair the graph or ledger.

### Reject identifier leakage before display

Validate every candidate user-facing turn before display. The turn is invalid
if it contains any internal identifier or machine field, including:

- a token matching `\b(?:Q|A|B|D|U|R|W|T)-\d+\b`;
- a run or human-turn identifier such as `G-\d+`, `H-\d+`, `R-\d+`,
  `run`, or `human_turn`;
- any control-envelope field: `v`, `base_rev`, `rev`, `mode`, `add`,
  `update`, `remove`, `frontier`, `ancestry`, `recompute`, `deps`,
  `content_ref`, `from_nr`, `nr`, `id`, `targets`, or `depends-on`; and
- any `lattice` (gradient) envelope field: `lattice`, `shape`, `axis`, `n`,
  `branch`, `depth`, `keep`, `zones`, `beam`, `path_ref`, `value`, `zone`,
  `status`, `wave`, `worker_status`, `last_frontier_rev`, `budget`, `executed`,
  `cap`, `tokens_cap`, `tokens_used`, `time_cap_secs`, `time_used_secs`,
  `merge_keys`, `scoring`, `params`, or `tie_break`; and
- any machine-structure marker: a JSON/YAML object or array literal, a
  key-value mapping outside a numbered question list, a code fence,
  `BEGIN`/`END` transport delimiters, or an HTML `<details>`/`<summary>`
  diagnostic block.

The denylist above is the visible subset of a complete machine-token
classification: every field name, identifier family, and delimiter shown
anywhere in this skill's transport examples is machine content by default.
These matches are **schema-key matches** — they flag the fields only where
they appear as control-envelope keys (a quoted field in an envelope or a key
in a JSON/YAML object), not as bare words. Short generic tokens such as `n`,
`zone`, `value`, `status`, `shape`, or `budget` are ordinary English and must
not be banned when they appear in human prose. A validator should match a
quoted identifier or a mapping key at envelope depth, never every occurrence
of the word.
If any such content appears, do not show any part of the turn. Re-render it
from the question prose and validate the complete replacement.

### Map visible question numbers privately

The displayed question numbers are the only protocol numbers the user sees.
They are turn-local labels starting at `1`; they are not stable graph
identifiers. Maintain the private mapping
`(human_turn, displayed_item) -> internal_question_id`, and use that mapping
when the user answers “1,” “2,” or another displayed item. Never ask the user
to quote or interpret an internal identifier. This rule does not prohibit
ordinary quantities, dates, or measurements inside question prose.

## Evidence required for the offered profile

- A user can complete the interview without seeing or learning any internal identifier.
- Every visible question is plain prose with only a turn-local question number.
- An automated zero-machine-content claim requires an implemented validator
  and observed results for the selected transport; otherwise report manual
  review and its limits. Structural checks never establish semantic privacy.
- If replay/resume is offered, execute the actual reconstruction check and
  verify the same graph, frontier, branches and ratification state. Without that
  evidence, do not offer or claim verified replay/resume.
- Upstream revisions invalidate exactly their dependency subtrees while preserving independent work and the longest valid accepted prefix.
