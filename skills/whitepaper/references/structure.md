# Whitepaper structure

A proven outline for an investor/partner-focused whitepaper that makes the
case for building (or continuation of) a product. Reorder or prune freely;
this is the shape the reader expects, not a fixed template.

## Recommended section order

1. **Title block**
   - Existing product name; a styled brand mark only when branding is selected.
   - One-line subtitle (e.g. "High-Fidelity Decision-Making for the Enterprise")
   - Drop boilerplate metatags ("Draft vX", "Investor Edition", filenames).
     Keep a short disclaimer line only where it matters (e.g., assumption
     caveat).

2. **Overview** (section named plainly — avoid "Executive Summary", "What
   this is, in one line" reads too AI-ish)
   - One-line: what the product is and turns into value.
   - A short "problem" paragraph: the expensive failure the reader knows.
   - A short product paragraph explaining the actual customer outcome.
   - "Why this wins": 2–3 crisp differentiators.
   - "The ask" (if investor-facing): the funding wedge and how it expands.

3. **The Problem** — name the evidenced customer failure and its consequences.
   Include "why now" when supported.

4. **The Product** — what the user actually gets (outcomes, not internals),
   the relevant limitations and a diagram only when useful.

5. **Delivery / surfaces** — app, API, connectors; how it plugs into tools the
   buyer already runs.

6. **Where this wins / positioning** — supported differentiation and the
   buyer/economic-sponsor profile.

7. **The Market** — sizing stated honestly ("we'll report primary research
   after pilots"), the wedge-first TAM thesis, and the moat.

8. **Economics** — when modeling is selected: pricing, unit costs, the requested
   forecast horizon, and sensitivities. Label assumptions and observed inputs.

9. **Go-to-market** — wedge-first, bottom-up API, partner connectors, category.

10. **Risks and mitigations** — a table; risk on the left, response on right.

11. **The ask / capital** and **roadmap** — if investor-facing.

12. **Appendix** — the engineering; explicitly "not required reading for the
    value." Keep the mechanism (orchestration, graphs, models) here and out of
    the body.

## Diagrams

When diagrams help the selected document, possible views include:
- a one-product picture (inputs → engine → outputs),
- a before/after of the failure mode,
- a delivery map (one engine, three doors/sub-types).

Graphviz `dot` output clean PNGs; keep text short and label edges. Embed
high-res so the PDF stays sharp.

## Cost & revenue model

Use only when financial modeling is selected. Separate observed inputs from
illustrative assumptions; choose the horizon and model dimensions for the brief.
Verify arithmetic and units. Possible dimensions include:
- Price tiers (starter/growth/enterprise/API) with assumed prices.
- A unit-cost envelope (inference, infra, connectors, R&D, S&M, G&A).
- A table over the selected horizon: paying customers, enterprise accounts, net revenue range,
  gross margin, EBITDA proxy.
- A short "most sensitive to" list (attach rate, inference cost, churn,
  GTM velocity).
