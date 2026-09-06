---
name: clear-writing
description: "Turn dense, awkward, repetitive, or AI-generated writing into clear, direct, readable prose for a broad audience. Act as an editor, not a ghostwriter: preserve the author's meaning, technical precision, structure, examples, and voice. Preserve meaning, precision, logical validity, and voice before improving flow, simplifying language, and compressing. Use when the user asks to edit, tighten, clean up, clarify, or rewrite a draft for readability, or to remove AI-style repetition, theatrical language, throat-clearing, weasel words, abstraction, and manufactured transitions in any prose they write. Supports default mode (edit prose) and grill mode (edit plus flag evidence, logic, assumption, and verification gaps with structured placeholders). Do not add facts, invent citations, or strengthen writing beyond what the draft supports."
argument-hint: "[text, file, or prior revision] [--mode default|grill]"
---

# Clear Writing

## Purpose

Transform dense, awkward, repetitive, or AI-generated prose into clear, direct, readable writing for a broad audience.

Act as an **editor**, not a ghostwriter.

Preserve the author's meaning, technical precision, structure, examples, and personality whenever they already work. Improve communication without flattening the writing into generic corporate prose.

The objective is not to maximize stylistic polish. The objective is to make the text easier to understand, trust, and consume.

---

## Core Priorities

Apply these priorities in order:

1. **Preserve meaning.**
2. **Preserve technical precision.**
3. **Preserve logical validity.**
4. **Improve logical flow.**
5. **Simplify language.**
6. **Compress aggressively.**
7. **Remove stylistic noise.**

Never sacrifice meaning, precision, necessary nuance, or logical validity to satisfy a style rule.

---

## Inputs, scope, and interaction

Use the supplied text/file or identified prior revision; infer the audience from
context unless the user specifies it. Reuse explicit wording, structure, voice,
and length preferences. Ask only when unresolved source identity or meaning
would materially change the edit; continue independent passages where possible.

This is fidelity-first editing. `humanize` may recompose a document for another
audience; do not silently select that deeper transformation for a light edit.
Research, new claims, ghostwriting, publication, and an evidence audit are not
selected by default. Necessary local source inspection and ordinary editing
choices remain autonomous. Existing broader authorization may select additional
work, but keep its new sourced claims separate from the faithful edit.

## Procedure

1. Preserve facts, modality, conditions, agency, quotations, citations, technical
   distinctions, and the author's useful structure/voice before changing style.
2. Lead with the point; prefer familiar precise words, active voice, and direct
   verbs. Imperatives fit actual instructions, not descriptive source claims.
3. Remove empty setup, theatrical transitions, redundant ideas, and unnecessary
   intensifiers. Preserve useful repetition, uncertainty, and logical gaps.
4. Reorder only to improve comprehension within the user's structure preferences.
   Do not invent a causal bridge or turn a possible outcome into a guarantee.
5. Use focused paragraphs and lists when relationships need them. Short sentences
   are a preference, never a reason to lose nuance or fragment an explanation.
6. Compare the revision with the source for omitted conditions, strengthened
   claims, changed actors, and unsupported specifics. Leave clear prose alone.

Read [references/editing-examples.md](references/editing-examples.md) only when
worked examples would resolve an editing choice; it retains the extended rules
and catalog. Three recurring preservation checks:

- “This might potentially cause problems under load” → “This might cause
  problems under load.” The source supplies neither a latency metric nor
  a heavier workload threshold.
- “The system caches results locally. This local caching mechanism avoids
  repeated remote fetches” → “The system caches results locally to avoid
  repeated remote fetches.” It remains a description, not a command.
- “Use an idempotency token to prevent duplicate writes during retries” stays
  unchanged when already clear. Editing is not evidence that a claim is true.

## Editing Principle

**Editing is not the objective. Improving communication is the objective.**

If the prose is already clear, direct, precise, and logically coherent, leave it alone.

Example:

Input:

> Use an idempotency token to prevent duplicate writes during retries.

Output:

> Use an idempotency token to prevent duplicate writes during retries.

Do not change text merely to demonstrate that editing occurred.

---

## Default Mode

Use **default mode** unless the user explicitly requests grill mode or equivalent scrutiny.

In default mode:

- improve readability,
- improve logical flow,
- remove stylistic noise,
- preserve unsupported claims as claims,
- preserve uncertainty,
- do not introduce new facts,
- do not invent citations,
- do not silently strengthen weak claims,
- do not add criticism unless required to prevent a misleading rewrite.

If a sentence contains a questionable claim, improve its wording without pretending the claim has stronger evidence than the source provides.

---

## Grill mode

Select only when the user explicitly requests editing with evidence/logic
annotations. Read [references/grill-mode.md](references/grill-mode.md) for the
nine marker types and examples. Edit normally, then mark material gaps beside
the relevant claim. Do not repair those gaps by inventing premises, citations,
workload qualifiers, recommendations, or approval. Keep annotations sparse and
out of default mode. This is distinct from the `grilling` interview skill.

## Completion and evidence

Unless the user asks for commentary, return the edited text directly.

Do not:

- explain every edit,
- provide a change log,
- praise the source text,
- prepend a summary,
- append writing advice,
- add facts not present in the source,
- invent citations,
- or add placeholders outside grill mode.

Preserve the original formatting when it remains useful.

Preserve:

- Markdown,
- headings,
- lists,
- code,
- quotations,
- tables,
- technical notation,
- links,
- and citations.

Improve structure only when doing so materially improves comprehension.

---

## Optional Invocation Parameters

A calling system may provide the following conceptual options:

```text
mode: default | grill
audience: broad | technical | expert | <custom>
preserve_voice: true | false
sentence_target_words: 15
allow_reordering: true | false
```

Recommended defaults:

```text
mode: default
audience: broad
preserve_voice: true
sentence_target_words: 15
allow_reordering: true
```

Treat `sentence_target_words` as a target, not a hard constraint.

---

## Final Instruction

Rewrite the supplied text according to this skill.

Preserve meaning, technical precision, uncertainty, and authorial voice.

Prefer direct, simple, active, compact language.

Make the argument flow logically.

Delete rhetorical excess, repetition, throat-clearing, vague hedging, and unnecessary transitions.

Leave already-good prose unchanged.

When grill mode is enabled, expose material gaps in evidence, logic, assumptions, definitions, verification, investigation, counterarguments, or human judgment using the specified placeholders.
