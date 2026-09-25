---
name: translate-output
description: "Simplify the language of the most recent LLM response, or supplied text, into plain language with clean formatting. Use when the user asks to simplify, translate, or clarify the last answer or recent output, says 'in plain English', 'what does that mean', or 'dumb it down'."
argument-hint: "[text or file] [strong]"
---

# Translate Output

Rewrite recent agent output so a tired, non-specialist reader understands it on
one pass. Preserve what the source claimed; change only how it is said.

## Source selection

- No arguments: use your most recent response in this conversation. If none
  exists, ask for the text to simplify.
- Argument is text: simplify that text.
- Argument names a readable file: load it and simplify its prose.
- Optional `strong`: simplify further, for a smart newcomer; every rule below
  still applies.

## Summary first

Open the output with a one- or two-sentence summary of the point, then the
simplified text. State the outcome itself; do not announce that a summary or a
rewrite follows. When the request is only for a summary, deliver the summary
alone.

## Rewrite rules

- Lead with the answer or outcome; then the reasons.
- One idea per sentence; target 20 words or fewer. Split longer sentences.
- Plain words first. Replace jargon with the common word; keep a necessary
  technical term only with a short plain-language gloss at first use.
- Active voice. Delete filler and hedges ("simply", "it is worth noting",
  "crucially"); keep real uncertainty, stated plainly ("we do not know X").
- Keep every claim, caveat, number, and commitment from the source. Add none.

## Untouchables

Leave exactly as written: code blocks, inline code, commands, flags, file
paths, identifiers, quoted errors, numbers with units, and URLs.

## Formatting

- Wrap wrappable prose at or below 80 display columns unless the user set
  another width.
- Paragraphs of at most four sentences; convert lists of three or more items
  into bullets.
- Bold only the key answer. No emojis. Keep a heading only when the result
  still needs sections.

## Non-goals

Editing the user's own drafts is `clear-writing`; restoring a natural human
voice is `humanize`; reading aloud is `speak`. Do not combine unless asked.

## Completion

Deliver the summary followed by the rewritten text, or the summary alone when
that is all that was asked for. Name any part left technical when a plain gloss
cannot carry it.
