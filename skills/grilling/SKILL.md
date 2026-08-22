---
name: grilling
description: "Interrogate a plan, decision, product thesis, or idea through hard, dependency-aware questions only. Use when the user asks to be grilled, stress-test assumptions, expose blind spots, explore a decision tree, run a speculative interview, or invokes /grilling, $grilling, /grill-me, or $grill-me. Support an ordinary user interview and a multi-agent speculative mode in which a strictly question-only griller interrogates an honest, exhaustive respondent that can initiate research, web searches, and specialist-agent delegation."
argument-hint: "[spec] [topic or artifact] [--depth <n>]"
---

# Grilling

Expose what a plan has not yet earned by asking the questions on which its
conclusions depend. Keep the griller interrogative: it may investigate,
challenge, and follow implications, but it must not become a critic that argues
for its own position.

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
and dependency metadata are allowed; all reader-facing prose inside each block
must form part of the question. Put a suspected assumption into the question
instead of asserting it before the question.

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

## Map the decision graph

Represent the inquiry as a dependency graph rather than an unstructured list.
Give every question, answer, and decision a stable identifier:

```text
Q-012
depends-on: Q-004, A-009
targets: A-011
question: <one or more related questions, with no proposed answer>
```

Record separately:

- `Q-*`: a question the griller asked;
- `A-*`: the respondent's candidate answer;
- `D-*`: a decision explicitly ratified by the user;
- `U-*`: an unresolved uncertainty; and
- dependency edges showing what must be reconsidered when an upstream answer
  changes.

Do not treat an agent answer as a decision. Only the user can ratify a `D-*`
node unless the user explicitly delegates that authority.

## Run the default interview

Use the default interview unless the user explicitly requests speculative
execution.

1. Reconstruct the plan and the decisions it assumes.
2. Identify the current frontier: questions whose prerequisites are already
   known and that do not depend on another unanswered question in the same
   round.
3. Ask the full useful frontier as numbered questions, without recommendations
   or answers.
4. Wait for the user's response.
5. Record the answers, recompute the frontier, and continue.

Prefer questions that change a decision over questions that merely invite more
description. Go deep where an answer has broad dependency fan-out, hides an
irreversible commitment, or determines economic or technical feasibility.

Finish when the useful frontier is empty, the user stops, or every remaining
question is explicitly recorded as an uncertainty with a way to resolve it.
Do not implement the resulting plan until the user separately authorizes that
work.

## Run speculative multi-agent execution

Use speculative mode only when the user asks for `spec`, `speculative`, `-s`,
`sx`, a projected answer chain, or a back-and-forth between agents. Honor any
named agent, provider, or model after verifying that it is available.

Keep four roles distinct:

- **Griller:** asks hard questions only.
- **Respondent:** supplies candidate answers, calculations, designs, and
  revisions; investigates its own factual dependencies and initiates specialist
  research. This may be an architect, founder, operator, or other role chosen
  for the inquiry.
- **Orchestrator:** maintains the graph, routes complete turns, prioritizes
  branches, detects malformed output, and manages checkpoints. It does not
  misrepresent its branch policy as the griller's opinion.
- **User:** ratifies decisions, changes priorities, and owns the final choice.

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
notice every research need. When its runtime can spawn agents and browse within
the user's scope, use those capabilities directly. When it cannot, emit a
structured delegation request for the orchestrator to execute:

```text
R-003
supports: A-012
specialty: <bounded area of investigation>
question: <specific research question>
evidence: <required sources or observations>
stop: <condition that makes the task complete>
```

Treat a delegation request as an initiated action, not as a suggestion to the
user. The orchestrator should dispatch independent requests in parallel, return
their complete findings to the respondent, and let the respondent synthesize
them before closing the answer. If a tool, source, or specialist is unavailable,
record the limitation and keep the affected claim provisional.

Give each research wave an explicit deadline or evidence-completion condition.
Once the requested findings arrive, enter a synthesis-only phase: do not launch
new specialists or searches unless the evidence reveals a new uncertainty that
can materially reverse the answer. If the respondent fails to close a bounded
answer after the research wave is complete, preserve all findings, interrupt
only the stalled synthesis turn, and reissue the answer to a fresh
synthesis-only respondent session with no tools and no further delegation. Do
not wait on a session the runtime still reports as interrupted. Treat repeated
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

Repeat this cycle:

1. Give the griller the relevant plan, graph ancestry, and respondent answer.
2. Ask the griller for the next dependency-aware questions only.
3. Validate that the response contains only question blocks and structural
   metadata: no preamble, epilogue, verdict, objection, recommendation, or
   proposed answer. Discard and retry a violating turn.
4. Give the respondent the questions verbatim. Let it initiate any necessary
   inspection, web research, and parallel specialist delegation before
   returning complete candidate answers. Permit it to revise any dependent
   candidate answer.
5. Record each question, answer, revision, uncertainty, and dependency without
   silently converting any of them into a ratified decision.
6. Let the orchestrator select the next branch and repeat until a stop condition
   is met.

At review boundaries, show the user the candidate chain and unresolved question
ledger. Ratification commits the longest coherent accepted prefix. If the user
changes an upstream answer, invalidate only its dependent subtree and preserve
independent branches.

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

Delimit long turns with stable boundaries:

```text
BEGIN A-012
<complete answer>
END A-012
```

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

## Return the result

During the interview, return the griller's questions without a competing
critique or answer from the same role. During speculative execution, return
compact progress checkpoints only when useful, while retaining full agent
turns.

At a user review boundary, present:

1. candidate answers and revisions produced by the respondent;
2. decisions the user has actually ratified;
3. unresolved questions, uncertainties, and parked branches;
4. dependency-driven consequences of changing an upstream decision; and
5. the explicit continuation or stop condition.

Never attribute an answer, recommendation, objection, or verdict to the
griller.
