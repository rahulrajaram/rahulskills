# Native linear speculative modes

Use this for explicitly selected `spec`/`speculative`/`-s`/`sx`, `factory`, or
`debate`. Read the shared question/rendering rules in
[ordinary-interview.md](ordinary-interview.md), and
[private-state.md](private-state.md) when maintaining the candidate graph.
For machine transport or any offered resumability, also read
[rendering-and-replay.md](rendering-and-replay.md) before promising it.
These are the native role workflows; an installed gptengage command does not
silently replace their topology, per-turn review, or internal debate.

## Run speculative multi-agent execution

Use speculative mode only when the user asks for `spec`, `speculative`,
`factory`, `debate`, `gradient`, `-s`, `sx`, a projected answer chain, or a
back-and-forth between agents. Honor any named agent, provider, or model after
verifying that it is available.

`gradient` is a different shape from the others: `spec`/`factory`/`debate` keep
a linear interview and change who answers or how evidence runs; `gradient`
changes topology and resource discipline (it is the bounded wave-parallel
lattice defined in [lattice.md](lattice.md), which extends the
speculative roles). Select `gradient` when the goal is wide, smooth coverage of
a decision space with explicit cost caps, not a linear interrogation.

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

The direct topology above remains the named-workflow default. Only an
explicitly selected [mediated compatibility profile](compatibility-profile.md)
can change its transport, with respondent-owned questions/context/synthesis.
Host limitations alone do not select that profile.

When the respondent runtime cannot create specialists, do not silently emulate
that capability in the orchestrator. Let the respondent use its own inspection and
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

## Repeat this cycle

This cycle has two halves. Steps 1–4 form the **default human loop** for both
modes: the griller asks plain-language questions, they are validated, and the
orchestrator records them. Steps 5–8 (respondent answers, control deltas, and
branch routing) apply **only to speculative execution** (`spec`, `factory`,
`debate`, `gradient`, `-s`, `sx`). In the default interview, the user answers
the questions directly; the orchestrator maps the answers and selects the next
frontier without a respondent.

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

## Close with a debate and a plain-language recommendation

Use the close and debate only after the research wave's synthesis-only phase.
`factory` names the parallel specialist wave itself: bounded tasks, evidence
standard, deadline, synthesis-only phase. `debate` explicitly requests the internal debate phase. In every native
speculative mode, materially different candidate answers or mutually exclusive
positions require that bounded debate before closing. Skip it only when no
materially different positions remain, and say why; the earlier instruction to
close directly by default is superseded by this consistent rule.

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
5. **Autonomous execution handoff**, when the selected objective includes
   implementation planning: a ready-to-use contract — bounded
   objective, suggested timebox, stop rules, verification target, git
   policy, execution route (`Via: sub-agents` or direct), and resource
   policy — phrased so the user can hand it verbatim to an agent invoking
   `autonomous-execution-contract`.

For a comparison or personal decision, give the requested recommendation and
its decision-relevant implications; do not manufacture a software implementation
handoff, git policy or project schedule. In a selected implementation-planning
workflow, retain the complete handoff below. Use ranges only where evidence
supports them; leave unknown effort unresolved.

Follow the human-first rendering rules throughout: a small set of conversational items,
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
is still required for decisions or effects whose authority remains unresolved.
Existing authorization for the same concrete work remains valid.

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

