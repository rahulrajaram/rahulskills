---
name: grilling
description: "Interrogate a plan, decision, product thesis, or idea through hard, dependency-aware questions only. Use when the user asks to be grilled, stress-test assumptions, expose blind spots, explore a decision tree, run a speculative interview, or invokes /grilling, $grilling, /grill-me, or $grill-me. Support an ordinary user interview and a multi-agent speculative mode (spec, factory, debate, or -s) in which a strictly question-only griller interrogates an honest, exhaustive respondent that can initiate research, web searches, and specialist-agent delegation; open positions are then sharpened by a bounded internal debate, and the orchestrator closes with a plain-language recommendation covering implications, trajectory, time and effort, and an autonomous-execution handoff. Human-facing output is conversational prose with zero internal identifiers; machine state travels in private control deltas."
argument-hint: "[spec|factory|debate] [topic or artifact] [--depth <n>]"
---

# Grilling

Expose what a plan has not yet earned by asking the questions on which its
conclusions depend. Keep the griller interrogative: it may investigate,
challenge, and follow implications, but it must not become a critic that argues
for its own position.

## Human-first rendering rules

The codewords are internals, not the product. A human turn reads like a
conversation.

Every output has one of two modes:

- `human`: prose intended for the user;
- `transport`: machine-readable state exchanged between agents or stored for
  resume and recomputation.

If the mode is absent or ambiguous, assume `human`.

In `human` mode:

- Use numbered questions with short, plain-language titles.
- Give each item enough context for the user to answer it without consulting a
  graph or ledger.
- Emit zero internal identifiers or protocol fields. Do not show `Q-*`, `A-*`,
  `B-*`, `D-*`, `U-*`, `R-*`, `W-*`, `T-*`, `depends-on`, `targets`,
  `supports`, graph revisions, transport delimiters, JSON, or YAML.
- Never show the graph, research ledger, unresolved ledger, side-branch ledger,
  or workflow-state ledger in a normal user-facing turn.
- Refer to prior material by its plain-language title or meaning, not by its
  internal identifier.
- Let the user answer with ordinary prose or visible question numbers. The
  orchestrator maps those numbers back to stable internal identifiers.

The human-facing gold standard is:

1. **Who pays first?**

   Which specific buyer has both the urgent problem and authority to purchase
   before the broader platform is complete?

A title may be a short question or question-shaped navigation label. It must
not contain an internal identifier.

In `transport` mode, emit only the smallest versioned machine envelope needed
by the receiving agent. Do not mix transport metadata into human prose.

Speculative execution does not grant permission to expose internals. The words
`spec`, `speculative`, `factory`, `debate`, `-s`, or `sx` select an execution
mode; they do not mean “show the graph.” Show raw internals only when the user
explicitly asks to see the raw graph, ledger, protocol, or debug
representation.

When raw internals are explicitly requested, present the complete human-readable
turn first and append the machine representation in a trailing collapsed block.
This is a debug view, not the default interface.

If a message may be shown directly to the user, the human rules win. Do not
append agent-facing metadata as a convenience.

## Enforce the question-only contract

Make every substantive griller utterance a genuine question. The griller may:

- ask for definitions, evidence, mechanisms, tradeoffs, consequences, and stop
  conditions;
- state a short, verified fact when the question cannot be understood without
  it;
- quote or point to a tension in the respondent's answer and ask how it is
  resolved;
- present alternatives neutrally inside a question; and
- ask follow-up questions whose need was created by an earlier answer.

Emit a griller turn as question blocks only. Do not preface the questions with
a plan summary, assumed-decision list, diagnosis, rationale for choosing the
frontier, or an explanation of what the griller is doing. Do not append a
conclusion, invitation, next-step suggestion, or evaluation. Stable identifiers
and dependency metadata are forbidden in a human-facing griller turn. They may
appear only in a separate transport envelope that the user does not receive. All
visible prose inside each numbered block must form part of the question. Put a
suspected assumption into the question instead of asserting it before the
question.

Do not let the griller:

- object, rebut, advocate, recommend, warn, judge, or deliver a verdict;
- answer its own question or attach a preferred answer;
- label an answer `ACCEPT`, `REVISE`, `REJECT`, correct, wrong, viable, or
  nonviable;
- propose a synthesis, alternative strategy, or implementation;
- turn a leading assertion into a question merely by adding a question mark; or
- decide when an answer has been accepted on the user's behalf.

Convert a suspected flaw into a question. Ask “What evidence would distinguish
this release wedge from a commodity gate?” instead of saying “This wedge is not
differentiated.” Ask “Which customer pays before the system-of-systems vision is
complete?” instead of recommending a buyer.

Keep research and judgment separate. Find recoverable facts from the available
environment instead of asking the user to remember them. Use those facts to
form better questions; do not let factual research give the griller decision
authority.

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

Use a versioned control envelope for agent transport and resume. Prefer compact
delta updates over full graph dumps. For example:

```json
{
  "v": 1,
  "run": "g7",
  "base_rev": 17,
  "rev": 18,
  "view": {
    "turn": "h9",
    "items": {
      "1": "Q-012",
      "2": "Q-013"
    }
  },
  "delta": {
    "add": [
      {
        "id": "Q-012",
        "deps": ["Q-004", "A-009"],
        "target": "A-011",
        "content_ref": "h9#1"
      }
    ],
    "update": []
  },
  "frontier": ["Q-012", "Q-013"]
}
```

Store node text once and refer to it by identifier or transcript reference.
Send a full snapshot only when starting a fresh session, recovering from a
revision mismatch, or explicitly exporting the graph.

A model's hidden scratchpad may hold temporary working context, but it is not a
durable graph store. Persist resumable state in orchestrator-owned state, a
file, or another runtime-controlled store. If no separate transport channel is
available, retain the graph in orchestration context; do not print it into the
user's message.

## Run the default interview

Use the default interview unless the user explicitly requests speculative
execution.

1. Reconstruct the plan, its assumed decisions, and their dependencies
   privately.
2. Identify the questions that are ready now: their prerequisites are known,
   and none depends on another unanswered question in the same round.
3. Ask the full useful set as numbered, plain-language questions. Use short,
   descriptive wording and no recommendations, answers, identifiers,
   dependency notation, or process commentary.
4. Wait for the user's response.
5. Map each response to its question privately, update the dependency graph,
   determine which questions are ready next, and continue.

The visible number beside a question is local to that turn. If the user refers
to a question by number, resolve it through the private turn-and-item mapping;
do not expose or request the stable internal identifier.

Prefer questions that can change a decision over questions that merely invite
more description. Go deep where an answer affects many later choices, hides an
irreversible commitment, or determines economic or technical feasibility.

Finish when there are no useful ready questions, the user stops, or every
remaining uncertainty has a concrete way to resolve it. Do not implement the
resulting plan until the user separately authorizes that work.

## Run speculative multi-agent execution

Use speculative mode only when the user asks for `spec`, `speculative`,
`factory`, `debate`, `-s`, `sx`, a projected answer chain, or a back-and-forth
between agents. Honor any named agent, provider, or model after verifying that
it is available.

Keep four roles and their output channels distinct:

- **Griller:** asks hard questions only. Its only output is the human channel:
  plain question prose. It never emits identifiers, dependencies, ledgers,
  routing fields, state, or control deltas.
- **Respondent:** supplies candidate answers, calculations, designs, and
  revisions; investigates its own factual dependencies and exclusively owns
  any specialist-research tree. It creates specialist tasks, receives every
  specialist result, reconciles conflicts, and returns one synthesized turn.
  Its user-visible material is prose. Any identifiers, dependencies,
  provenance links, or revisions travel separately as a private control delta.
  This may be an architect, founder, operator, or other role chosen for the
  inquiry.
- **Orchestrator:** maintains the private graph, routes complete turns,
  prioritizes branches, validates both channels, manages checkpoints, and
  attaches or applies control deltas. It communicates with the griller and
  respondent, never with a respondent's specialists. It does not misrepresent
  its branch policy as the griller's opinion. It never shows workflow or
  transition state, including `W-*` or `T-*` identifiers, unless the user
  explicitly requests the full protocol graph.
- **User:** ratifies decisions, changes priorities, and owns the final choice.
  The user interacts through ordinary prose and the turn-local numbers on
  visible questions; the user is never required to operate the private graph.

Use separate agent turns or sessions for griller and respondent when the user
requests two agents. Never prompt the griller as an adversarial reviewer,
proponent, judge, or decision-maker.

## Make the respondent an active truth-seeker

Require the respondent to be candid, exhaustive, and evidence-seeking. Do not
let it optimize an answer for defending the thesis or satisfying the griller.
For each material claim, distinguish:

- what is directly established and by which evidence;
- what is inferred from that evidence;
- what is a strategic bet or preference;
- what remains unknown or disputed; and
- what evidence would change the answer.

Answer every consequential part of a question. Trace important implications,
counterexamples, failure modes, and tensions across relevant domains. Expand
into product, technology, economics, organizations, policy, safety, or physical
constraints when the dependency graph makes that domain decision-relevant; do
not widen the discussion merely to sound comprehensive.

Do not ask the user for recoverable facts. Before finalizing an answer:

1. Inventory the factual and analytical dependencies of the answer.
2. Resolve repository, artifact, configuration, and runtime facts with local
   read-only inspection.
3. Search the web for current or external facts when local evidence is
   insufficient. Prefer recent primary sources, preserve publication and event
   dates, cross-check consequential claims, and cite the sources used.
4. Split independent uncertainties into bounded specialist tasks and run them
   in parallel when multiple agents can materially improve coverage, challenge
   disciplinary blind spots, or reduce latency.
5. Give each specialist a concrete question, relevant context, evidence
   standard, output contract, and stop condition. Ask it to return evidence,
   counterevidence, uncertainty, and sources—not a vote.
6. Reconcile conflicts explicitly. Preserve minority findings and unresolved
   ambiguity instead of manufacturing consensus.

Let the respondent initiate this work without waiting for the orchestrator to
notice every research need. The respondent must communicate with its
specialists directly: it creates their tasks, sends their context, receives
their findings, requests any correction, and synthesizes the result. A
specialist reports only to the respondent. The orchestrator must not dispatch,
prompt, retry, receive output from, arbitrate, or synthesize a specialist.

Before beginning a speculative run in which specialist work may be material,
verify that the respondent runtime can directly create and manage specialists.
When it can, use that capability within the user's scope. A respondent may
record a bounded task in its internal research ledger using this shape:

```text
R-003
supports: A-012
specialty: <bounded area of investigation>
question: <specific research question>
evidence: <required sources or observations>
stop: <condition that makes the task complete>
```

The respondent may expose that `R-*` ledger and supporting provenance only as
part of its checkpoint or final answer. The orchestrator receives this material
from the respondent, never from a specialist.

When the respondent runtime cannot create specialists, do not emulate that
capability in the orchestrator. Let the respondent use its own inspection and
web tools when that can still meet the evidence standard. If parallel or
specialist investigation is materially required, record a typed `U-*` runtime
capability limitation, keep affected answers provisional, and stop at the
applicable review boundary. Do not install, enable, or substitute an external
capability without the user's authorization.

Give each research wave an explicit deadline or evidence-completion condition.
Once the requested findings arrive, enter a synthesis-only phase: do not launch
new specialists or searches unless the evidence reveals a new uncertainty that
can materially reverse the answer. If the respondent fails to close a bounded
answer after the research wave is complete, preserve the failure as an
incomplete respondent turn. The orchestrator may retry or replace the
respondent, but it must pass only the question frontier and prior respondent
checkpoints; it must not obtain or broker partial specialist traffic. Do not
wait on a session the runtime still reports as interrupted. Treat repeated
failure as an incomplete provider turn, not as permission to shorten or invent
the missing answer.

Keep all research within the user's authorization and runtime policy. Default
research delegates to read-only access. Do not let agent spawning, tool access,
or accumulated evidence grant the respondent authority to ratify decisions or
perform external writes.

Interpret “exhaustive” as complete against the active dependency graph, not as
infinite prose. Stop researching a branch when its decision is supported,
falsified, explicitly unresolved with a resolution path, or no longer capable
of changing the active decision. Preserve the raw research and unanswered
questions for branches that may reopen.

## Type each unresolved uncertainty

Every unresolved `U-*` node carries one type that says why it is open and what
would close it. Use the same taxonomy as the `clear-writing` skill's grill mode,
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

The type is internal machine vocabulary, the same as a `U-*` identifier. It
may appear in the private control envelope and the explicit diagnostic view,
never in a numbered question or in ordinary human-facing prose.

## Repeat this cycle

This cycle has two halves. Steps 1–4 form the **default human loop** for both
modes: the griller asks plain-language questions, they are validated, and the
orchestrator records them. Steps 5–8 (respondent answers, control deltas, and
branch routing) apply **only to speculative execution** (`spec`, `factory`,
`debate`, `-s`, `sx`). In the default interview, the user answers the questions
directly; the orchestrator maps the answers and selects the next frontier
without a respondent.

1. The orchestrator selects the active frontier from the canonical graph and
   prepares only the relevant ancestry. It does not send the complete graph
   unless the receiving session is resuming or repairing state.
2. Give the griller the relevant plan, ancestry, respondent answer, and a clear
   output-mode instruction. For a human-visible turn, end the prompt with:
   `OUTPUT MODE: HUMAN. Return only numbered, natural-language questions with
   plain-language titles. Emit no identifiers, ledgers, dependency fields,
   workflow states, JSON, YAML, preamble, verdict, or epilogue.`
3. Validate the griller's response for both contracts:
   - every substantive item is a genuine question; and
   - the human rendering contains no internal vocabulary or machine structure.
   If either contract fails, re-render or retry before showing the turn.
4. After validation, the orchestrator assigns or confirms stable `Q-*` nodes
   and records the visible-number-to-node mapping in the private control
   envelope.
5. Forward every valid question to the respondent verbatim. Put identifiers,
   ancestry, and answer bindings in a separate transport envelope; do not
   insert them into the question prose.
6. Let the respondent initiate and directly manage any necessary inspection,
   web research, and specialist delegation. The respondent returns one complete
   candidate-answer turn plus a private control delta describing answers,
   revisions, uncertainties, provenance, and dependencies.
7. Validate and apply the control delta without converting any candidate answer
   into a ratified decision. Render any user-visible checkpoint from the graph
   in plain language rather than exposing the graph representation.
8. Let the orchestrator select the next branch and repeat until a stop
   condition is met.

Never ask a lean flash model to serialize the graph; give it only the current
frontier and the minimum relevant ancestry, and let the orchestrator construct
and persist the control delta. Never rely on the model to keep private fields
private: validate and strip them at the channel boundary before display. If a
turn fails validation, discard the entire rendered candidate and request a
prose-only re-render. Do not expose the failed turn, partially repair it in
front of the user, or treat malformed control output as canonical state.

## At review boundaries

At review boundaries, present a short human review in this order:

1. **What I need from you:** the decisions, corrections, or judgments required
   now.
2. **Things we've settled:** plain-language conclusions the user has actually
   ratified, clearly distinguished from candidate answers.
3. **Things still open:** unresolved evidence, assumptions, or alternatives,
   including who or what can resolve each one.
4. **What changes if an earlier answer changes:** only the material downstream
   consequences.
5. **What happens next:** the continuation choice or stop condition.

Use ordinary descriptions rather than identifiers, node tables, ledgers, state
labels, or transition diagrams. Do not make the user decode graph structure to
understand the review.

Internally, ratification commits the longest coherent accepted prefix only
when the accepted structure is genuinely linear. For a branching graph, record
the exact nodes and edges the user ratifies. If the user changes an upstream
answer, invalidate only its dependency descendants and preserve independent
branches.

Only when the user explicitly requests the full graph or protocol diagnostics,
read and follow `references/review-boundaries.md`. Place that material after
the human review in a collapsed block:

```html
<details>
<summary>Full graph and protocol diagnostics</summary>

<!-- identifiers, ledgers, diagrams, revisions, and state transitions -->

</details>
```

Never show the collapsed debug block merely because the graph is complex.
The placeholder comment inside the example above is transport-only; a real
debug block is populated from the private envelope and is never copied into
ordinary user-visible prose.

## Close with a debate and a plain-language recommendation

Use the close and debate only after the research wave's synthesis-only phase.
`factory` names the parallel specialist wave itself: bounded tasks, evidence
standard, deadline, synthesis-only phase. `debate` requests the internal
debate phase; by default run the close directly.

### Run the internal debate

When mutually exclusive branches or materially different candidate answers
remain open, run a bounded structured debate before closing:

1. Give each material position its turn, grounded in the evidence ledger, with
   explicit pro, contra, and what-evidence-would-change-it.
2. Let the orchestrator preside: keep turns to the question at hand, enforce
   the evidence standard, and stop a position that argues without evidence.
3. Preserve minority findings and unresolved ambiguity. Do not manufacture
   consensus; record the residual dispute as a typed uncertainty.
4. Once the debate has sharpened or resolved the open positions, return to
   synthesis and let the orchestrator update the graph.

If the user wants genuine multi-model deliberation, escalate to the `debate`
skill and fold its synthesis back into the graph. The internal debate is
orchestrator-routed agent argument, not an external gptengage run.

### Deliver the orchestrator's closing report

Close every speculative run with a short plain-language report from the
orchestrator, in this order:

1. **Recommendation**: the orchestrator's own conclusion from the graph, in
   plain language. Label it as the orchestrator's recommendation, not a
   ratified decision and not a griller answer.
2. **Implications**: what changes if the user follows it, what is at risk,
   and what becomes irreversible; state the material dependency consequences
   in plain words.
3. **Trajectory**: where this takes the project — the next milestones and the
   shape of the road ahead, as planning, not promises.
4. **Time and effort**: a rough range for the recommended path, with the
   assumptions (scope, chunking, model speed) it rests on, and honest
   uncertainty. Never present it as a schedule commitment.
5. **Autonomous execution handoff**: a ready-to-use contract — bounded
   objective, suggested timebox, stop rules, verification target, git
   policy, execution route (`Via: sub-agents` or direct), and resource
   policy — phrased so the user can hand it verbatim to an agent invoking
   `autonomous-execution-contract`.

Follow the human-first rendering rules throughout: 5-8 conversational items,
zero identifiers or ledger content, "what needs your decision now" first. The
report is advisory; nothing is ratified unless the user says so. Do not reopen
the interrogation, and never dump the graph or ledgers into the report.

A clean closing report reads like this (illustrative shape, not a template to
copy verbatim):

1. **My recommendation**: focus the first build on a single immediate-buyer
   cohort and defer the platform-API work until two buyers sign.

2. **What that changes**: the next three months stay small-team and
   reversible; the main risk is underestimating onboarding effort, and the
   one irreversible step is any long-term team commitment today.

3. **Where this leads**: a working pilot with the first cohort within ~90
   days, then a decision point on whether to generalize.

4. **Time and effort**: roughly 8–12 focused weeks for the pilot, assuming
   one experienced engineer and no new infrastructure; the main uncertainty is
   buyer access.

5. **Handoff for autonomous execution**: objective — validate the first-buyer
   cohort and produce a pilot plan; timebox — one day; stop rules — stop
   before any hiring or procurement; verification — a written cohort and
   pricing sketch; git — feature branch, no pushes; via — direct; resource —
   none.

The numbered items are human prose: no identifiers, no envelope fields, no
table rows. Each maps to the recommended path only; the user's ratification
is still required before any execution starts.

## Control branching without flattening it

Keep one active trunk and an explicit side-branch ledger. Prefer the trunk with
the strongest current combination of economic viability, information value,
dependency fan-out, reversibility, and bounded downside. Treat this as the
orchestrator's scheduling policy, not as an answer supplied by the griller.

Fork a branch when answers are mutually exclusive, when independent customer or
technical hypotheses have meaningful option value, or when resolving the trunk
requires comparing materially different worlds. Park a branch when it cannot
change the near-term decision, lacks a resolvable premise, or costs more to
investigate than the decision can presently justify. Preserve parked branches
with their reopening condition.

Interpret a requested depth such as 100 as an exploration budget, not as a
requirement to manufacture 100 shallow exchanges. Do not impose an arbitrary
depth cap. Continue while new questions can change the result and the user's
time, cost, and stop constraints permit it.

Discussions of organizations, economics, physics, or first principles are
in-scope only while a dependency path connects them to the product decision.
Record the connection; park the branch if it becomes merely interesting.

## Preserve long answers

Allow the respondent to answer at the length the subject requires. Do not ask
for shorter answers merely to work around command-line transport, display, or
orchestration limits.

Delimit long transport turns with stable boundaries:

```text
BEGIN A-012
<complete answer>
END A-012
```

The delimiters belong to the transport channel. They never appear in a
human-facing turn; the renderer strips them before display.

Treat a missing end marker, broken identifier sequence, or unfinished sentence
near a transport boundary as an incomplete turn. Request a full re-emission or
continuation from the last complete identifier. Do not replace the missing
material with a shorter summary and do not pass malformed prose into the next
agent as if it were complete.

Pass large prompts through stdin, files, or another streaming transport rather
than a single operating-system argument. Preserve the full raw transcript.
When a model's context window approaches its real limit, open a fresh
branch-specific session with the dependency graph, relevant ancestry, exact
unresolved questions, and references to the raw transcript. Do not claim that
the new session saw omitted material; retrieve older nodes when they become
relevant again.

## Enforce rendering on weak instruction-following models

Treat channel separation as a runtime invariant, not a request to the model.

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
- any machine-structure marker: a JSON/YAML object or array literal, a
  key-value mapping outside a numbered question list, a code fence,
  `BEGIN`/`END` transport delimiters, or an HTML `<details>`/`<summary>`
  diagnostic block.

The denylist above is the visible subset of a complete machine-token
classification: every field name, identifier family, and delimiter shown
anywhere in this skill's transport examples is machine content by default.
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

## Return the result

During the interview, return the griller's questions without a competing
critique or answer from the same role. During speculative execution, return
brief conversational progress only when it helps the user understand what is
happening; retain complete agent turns and control state privately.

At a normal user review boundary, present no more than five to eight
plain-language items. Put what needs the user's decision now first. Then cover,
as relevant, what appears settled, what remains provisional, the most important
open evidence or alternatives, the consequences of changing an upstream
choice, and the continuation or stop condition. Write the items so they read as
a conversation, not as a database report. Do not show identifiers, schemas,
node tables, workflow states, transition labels, or question, branch, or
uncertainty ledgers.

If the user explicitly requests the full graph, append a collapsed diagnostic
presentation containing:

1. how to read the diagnostic and what needs user input now;
2. the workflow-state visualization and its legend when process behavior is
   under review;
3. the dependency and branch visualization;
4. candidate answers and revisions arranged by dependency layer;
5. decisions the user has actually ratified;
6. typed unresolved uncertainties, their resolver, and whether user action is
   required;
7. branches with their fork point, scheduling status, and reopening condition;
8. dependency-driven consequences of changing an upstream answer; and
9. the explicit continuation or stop condition.

The diagnostic is an opt-in debugging view, not the default review format.
Follow `references/review-boundaries.md` for the full graph presentation only
when the user has asked for it.

Never attribute an answer, recommendation, objection, or verdict to the
griller.

## Definition of done

- A user can complete the interview without seeing or learning any internal identifier.
- Every visible question is plain prose with only a turn-local question number.
- Automated validation proves that rendered turns contain zero machine-content tokens.
- Delta replay and resume reconstruct the same graph, frontier, branches, and ratification state.
- Upstream revisions invalidate exactly their dependency subtrees while preserving independent work and the longest valid accepted prefix.
