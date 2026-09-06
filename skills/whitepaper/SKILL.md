---
name: whitepaper
description: "Author a whitepaper, business case, investor pitch, or product value proposition for the specified reader. Use for original product/value authorship; financial modeling, naming, branding, and PDF delivery apply when requested. Preserve evidence, assumptions, and the distinction between recommendations and approved commitments."
argument-hint: "[product or topic] [--investor] [--tone <ycombinator|neutral>] [--styling css] [--out <file>]"
---

# Whitepaper Authoring

## Intent and applicability

Make the case for a product or investment at the requested depth, from a value
paragraph to a full business case. Let the reader's decision determine what to
explain. For faithful editing of supplied prose use `clear-writing`; for
reorganizing existing claims for another audience use `humanize`.

## Inputs and local bindings

Use the supplied topic, reader, decision, evidence, product maturity, requested
length/format, existing name/style, and financial assumptions. Infer ordinary
omissions from context. A paragraph request selects prose; an investor audience
alone does not select naming, projections, or PDF. Preserve explicit preferences.

## Non-goals and must not

Do not automatically select rebranding, name/domain checks, font downloads,
financial research, charts, publication, or rendering. Necessary source inspection
and original drafting within the brief remain autonomous. Never invent facts,
citations, customer proof, measurements, market size, or ratification. Label bets,
proposed commitments, illustrative assumptions, and unverified claims distinctly.

## Interaction and authority

Reuse an established reader, name, output path, and still-valid decisions. Ask
only when a missing choice materially changes the audience, claim, product
positioning, financial premise, or authorized effect. Prepare the draft/options
and independent work first. A recommendation is not an approved product decision;
a document request does not authorize publication, tool installation, or paid
resources. Existing explicit authorization carries into regeneration and rendering.

## Procedure and conditional references

1. Open with the problem, proposed value, and first useful product. For a short
   value proposition, write that artifact directly without a full document shell.
2. For a full business case, read [references/structure.md](references/structure.md)
   and adapt the outline to the reader's decision. Keep technical explanation
   in the body when it is necessary to assess that decision; use an appendix for
   supporting detail in a longer investor/sales document.
3. For substantial investor-facing prose or a requested founder tone, read
   [references/tone.md](references/tone.md). Plain, precise language remains the
   default; product-specific analogies are optional and need supporting facts.
4. Add cost/revenue modeling when requested or already selected in the brief.
   State assumptions, units, calculation basis, time horizon, sensitivities,
   and evidence. Do not manufacture a five-year forecast for a short passage.
5. Read [references/branding.md](references/branding.md) only for requested naming
   or visual branding. Reuse the existing name and brand otherwise. Present
   unverified naming candidates as proposals; a collision check is not clearance.
6. Read [references/pdf.md](references/pdf.md) only for PDF delivery. Resolve the
   requested/project stylesheet and existing local fonts before rendering; keep
   editable sources with the output when creating a document package.

## Completion and evidence

Return the requested prose or artifact, with sources and assumptions close to
claims they support. For a financial model, verify calculations and distinguish
modeled figures from observations. For a PDF, report its path and observed
rendering/font checks. State missing evidence or unavailable rendering honestly;
a polished document does not establish the product's claims or authorize release.
