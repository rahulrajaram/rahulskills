---
name: humanize
description: "Rewrite analytical, technical, product, strategy, architecture, or agent-generated prose into clear, natural language for its intended human audience while preserving meaning, evidence, uncertainty, commitments, and important distinctions. Use after frame-goals-constraints or when the user asks to humanize text, make it readable, make it less agent-like or robotic, translate it into plain English, or turn a rigorous analysis into a customer-, executive-, or practitioner-facing narrative. Do not use to evade AI-detection systems or misrepresent authorship."
argument-hint: "[text, file, or prior response] [--audience <audience>]"
---

# Humanize

Turn a rigorous source artifact into writing that helps a real person understand,
care, decide, or act. Preserve the source's truth while changing its center of
gravity from the system's internal concepts to the reader's world.

Humanization is not decoration and is not simplification at any cost. Do not
make the writing warmer by making it less accurate.

## Scope and authority

Adapt the supplied claims for their audience; original business-case authorship
belongs to `whitepaper`, while `clear-writing` defaults to preserving the draft's
working structure. A user-selected light edit or exact wording/structure always
outranks this skill's recomposition default.

Do not select research, new promises, publication, or file changes beyond the
requested artifact. Necessary source inspection and audience-oriented reordering
remain autonomous. Reuse settled source/audience choices; ask only about a
material unresolved meaning, promise, or audience decision after preparing the
available alternatives. Keep independent rewriting moving within known bounds.

## Resolve the source and audience

Use the source in this order:

1. text or a file named by the user;
2. text quoted in the request;
3. the most recent relevant narrative in the conversation.

Honor a named audience and reading context. Otherwise infer them from the
request and artifact. When neither is discoverable, write for an informed
non-specialist who has a practical stake in the decision.

Infer the document's job: explain, persuade, align, support a decision, invite
action, or establish shared language. Ask only when choosing incorrectly would
materially change the promise, audience, or decision.

Choose the transformation depth:

- **Polish** only when the user asks for a light edit or exact structural
  preservation.
- **Rewrite** ordinary prose around the intended reader while retaining its
  useful shape.
- **Recompose** an analytical frame, taxonomy, architecture narrative, or
  multi-audience source into a new human-facing document. Treat the source as
  the meaning to preserve, not as the outline to preserve.

Default to recomposition for customer-facing output derived from a strategy or
systems frame, including output from `frame-goals-constraints`.

## Create a semantic checksum

Before rewriting, identify the source elements that must survive:

- material facts, numbers, names, and chronology;
- claims and their strength of confidence;
- strategic bets, preferences, and unresolved questions;
- commitments, prohibitions, conditions, and exceptions;
- causal relationships and important distinctions;
- who acts, who decides, who benefits, and who bears risk;
- the intended outcome and requested next action.

Use this as an internal checksum. Do not print it unless the user requests an
audit, comparison, or annotated rewrite.

## Find translation failures

Look for prose that makes sense to the system producing it but not to the person
reading it:

- abstractions introduced before the human problem;
- several technical nouns stacked into a category label;
- principles written as commands from one agent to another;
- passive constructions that hide who acts or decides;
- internal taxonomies presented without explaining why they matter;
- implementation mechanisms substituted for customer value;
- repeated qualifications that interrupt the main thought;
- long inventories where a narrative or a few meaningful groups would work;
- slogans that sound impressive but do not create a concrete picture.

Do not merely replace difficult words with easier synonyms. Recover the human
meaning underneath them.

For customer-facing prose, do not preserve the source's headings, bullet count,
or taxonomy by default. Consolidate related mechanisms into the three to five
outcomes the reader will actually experience. Move distinctions that still
matter but would interrupt the story into a supporting paragraph or later
technical layer.

Do not publish a section named “operating principles,” “trust model,” or a
similar internal label merely because the source contains one. Integrate its
meaning into the promise, explanation, customer control, and honest boundary;
use a customer-facing list only when the list itself helps the reader decide.

## Build the human spine

Organize the rewrite around the smallest useful sequence:

1. **Recognizable situation** — what is changing or difficult in the reader's
   world?
2. **Human consequence** — why does that matter to this reader or to people
   affected by the decision?
3. **Promise or position** — what becomes possible, safer, clearer, or easier?
4. **Credible explanation** — how does it work at the level the audience needs?
5. **Honest boundary** — what remains uncertain, unproven, conditional, or in
   the reader's control?
6. **Next thought or action** — what should the reader understand, decide, or do?

This is a guide, not a mandatory section template. A short passage may need only
the first three elements.

## Translate mechanisms into experiences

Lead with what the reader can see, know, choose, or rely on. Introduce the
mechanism only when it explains the promise or supports a decision.

Examples are conditional translations, not evidence of product capabilities.
Use one only when the source establishes its added actors and concrete meaning;
otherwise retain a narrower explanation. For example:

- “Evidence precedes authorization” becomes “Review the evidence before
  authorizing the action.”
- “Bounded and revocable autonomy” becomes “You decide what the system may do,
  how far it may go, and when it must stop.”
- “Failure classes remain distinct” becomes “When something goes wrong, know
  whether the problem is the product, the test, or the surrounding service.”
- “Learning cannot self-authorize” becomes “The system cannot quietly change
  its own rules.”
- “Local sovereignty” becomes “Scale without giving up control of your own
  systems.”
- “Portable evidence” becomes “The proof follows the work across teams and
  tools.”

Prefer concrete subjects and active verbs. Name people or roles when the source
supports them. Use technical vocabulary where it helps the audience; explain it
where necessary and remove it where it merely signals expertise.

Use “you” when it makes the reader's control or benefit concrete, but do not
turn every sentence into sales copy. Challenge words such as “authority,”
“admissible,” “bounded,” “sovereignty,” “orchestration,” and “provider”: retain
them only when this audience uses them or when a simpler phrase would lose an
important distinction.

## Preserve truth and agency

- Do not strengthen a claim, erase a caveat, or turn a bet into a fact.
- Do not imply customer proof, safety, compliance, maturity, or universality
  that the source does not establish.
- Do not remove a technical distinction when doing so changes a decision.
- Do not hide who retains authority or who bears consequences.
- Do not turn safeguards into fear-based marketing.
- Do not present the reader as passive when the product depends on their
  judgment, policy, or consent.
- Do not add fake anecdotes, testimonials, emotions, personal experience, or
  artificial verbal quirks.
- Do not optimize for AI-detector evasion or claim that a human wrote the text.

## Compose with other skills

When humanizing output from `frame-goals-constraints`, treat that frame as the
source of truth. Preserve its horizon, wedge, facts, bets, principles,
constraints, unknowns, maturity, and revision rules, but do not reproduce its
internal taxonomy merely because the analysis used one.

Translate the customer-facing portion first. Put practitioner or technical
precision later, or in an appendix, only when the intended reader needs it. A
single document may serve several audiences through progressive disclosure;
it should not speak to all of them in the same vocabulary.

When composing with formatting skills, humanize the meaning before applying
length, column, slide, or document-format constraints.

## Return the artifact

By default, return the rewritten artifact rather than a critique of the source
or a list of edits. Preserve an explicitly requested format, approximate
length, voice, and call to action when they remain compatible with clarity and
truth. Otherwise, let the selected transformation depth determine the new
structure.

If a rewrite cannot preserve both readability and a material distinction,
prefer accuracy and add the minimum explanation needed. If the source itself is
contradictory, surface the contradiction instead of smoothing it away.

Provide a preservation note only when:

- the user requests one;
- a consequential ambiguity required an assumption;
- the requested tone would materially overstate the evidence; or
- important technical detail was moved to another layer rather than retained
  inline.

## Read it as a person

Before returning, verify that:

- the opening gives the intended reader a reason to continue;
- the reader can tell why the subject matters to them;
- each paragraph advances one recognizable thought;
- actors, decisions, consequences, and uncertainty remain clear;
- customer-facing structure reflects human outcomes rather than the source's
  internal taxonomy;
- no sentence exists only to impress, classify, or instruct another agent;
- the rewrite can be repeated in ordinary language without changing its claim;
- the semantic checksum still matches the source.
