---
name: whitepaper
description: "Author an investor-facing enterprise whitepaper that makes the case for building a product (pre-solution, value/marketing/sales focused) with cost and revenue projections. Use when the user asks to write a whitepaper, business case, investor pitch document, product value proposition, or go-to-market whitepaper. Covers structure, Y Combinator-flavored but un-theatrical voice, naming/branding, and styling to a branded PDF with embedded fonts. Guardrails: keep technical detail in an appendix, lead with value, and never expose internal protocol identifiers in the prose."
argument-hint: "[product or topic] [--investor] [--tone <ycombinator|neutral>] [--styling css] [--out <file>]"
---

# Whitepaper Authoring

Produce a decision-grade whitepaper that makes the case for building a product
— aimed at investors, partners, or an internal green-light. The deliverable is
a narrative that proves the value proposition quickly and honestly, then
supports it with structure, a restrained voice, a clear brand, and a styled
PDF.

The approach distills a lot of hard-won conventions. Read the reference files
in order:
[`references/structure.md`](references/structure.md),
[`references/tone.md`](references/tone.md),
[`references/branding.md`](references/branding.md),
[`references/pdf.md`](references/pdf.md).

## When to use

- The user asks for a **whitepaper, business case, investor/partner pitch, or
  product value proposition** for something not yet built (or just built).
- They want cost and revenue projections framed as assumptions, not promises.
- They want a final styled document (PDF from Markdown/CSS), not just notes.

Do not use this for: technical design docs, code comments, API docs, or
internal engineering how-tos — those are not selling.

## Minimum viable workflow

1. **Clarify the reader and the intent.** An investor deck, a sales doc, and
   an internal green-light letter are all whitepapers but read differently.
   Confirm reader, and whether it needs cost/revenue projections, before
   writing.
2. **Expose the value now.** Open with a one-line "what this is" and a short
   synopsis that states the problem and the wedge. The reader must be alert
   to the value on the first page; do not bury it behind abstraction.
3. **Write a "war room" analogy, not a search analogy.** For a decision
   product, compare it to a virtual team that debates every angle and lands
   on a conclusion — not "Perplexity for X." Tune the analogy to the product.
4. **Keep the technology in the appendix.** What feels technical goes to an
   appendix ("How it works under the hood"). Keep the body at the value and
   outcome level.
5. **Add a cost-and-revenue model if asked** (investor/whitepaper). Present
   it as an illustrative snapshot with explicitly stated assumptions, price
   tiers, unit-cost envelope, a 5-year headcount/revenue table, and a short
   sensitivity list. Flag every figure as a model assumption.
6. **Brand and style it** (optional, but expected for investor-facing
   reads): a name, a brand font, a body font, an accent color, and a theme
   across the document. See [`references/branding.md`](references/branding.md).
7. **Render to a styled PDF** with embedded fonts. See
   [`references/pdf.md`](references/pdf.md).

## Naming, fonts, and delivery

Naming is a product decision, not a side note. Choose a name by **theme and
  allegory**, not by dictionary match. Read
  [`references/branding.md`](references/branding.md) entirely before committing
  to a name: check for negative real-world meanings (a disease, a failed common
  noun), run an availability/trademark/domain sanity check, and make the brand
  mark distinctive.

Deliver by default as a `.pdf` via pandoc + weasyprint with locally embedded
fonts (no runtime dependency on Google Fonts). Keep the `.md` and `.css`
alongside so the doc is editable.

## Guardrails

- **Never expose internals in the prose.** If a decision is grounded in a
  mechanism (e.g., an interrogation engine, a decision graph), describe the
  *fidelity* it buys the reader — attribution, typed blind spots, provenance,
  ratification stays human. Move the mechanism specifics to the appendix.
- **Distinguish a recommendation from a ratified decision.** The document may
  recommend a direction; nothing is a promise unless the user verifies.
- **Do not add facts or citations the evidence does not support.** If a claim
  is a model or a bet, say so. For uncertain numbers, prefer a range or a
  labeled model over a confident total.

## Tools

- `pandoc` + `weasyprint` (styled HTML/PDF)
- `curl` (download fonts)
- `dot`/graphviz (optional diagrams), `pdftoppm`/`pdfinfo`/`pdffonts` for verification