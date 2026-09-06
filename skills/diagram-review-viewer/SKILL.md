---
name: diagram-review-viewer
description: "Create hand-authored Mermaid diagrams with an interactive HTML review viewer (pan/zoom viewport, zoom toolbar, resizable info rail, digest badge) for operator review. Use when asked for an architecture, state-transition, or design diagram meant for human review in a browser, or when asked to package a diagram as a reviewable artifact. Not for throwaway ASCII sketches or images embedded in docs."
argument-hint: "[diagram file or design brief] [--type state|flowchart|...] [--out DIR]"
---

# Diagram Review Viewer

Produce a Mermaid source (`.mmd`) for every requested Mermaid diagram. Produce
an HTML review viewer (`.html`) only when browser review or viewer packaging is
requested. The viewer renders with an already-installed local Mermaid runtime;
it is a review package, not a diagram format or a renderer service.

## Inputs to gather first

1. The diagram's subject and audience question (one viewer answers one
   question; make separate projections for separate questions).
2. Diagram kind: `stateDiagram-v2` for lifecycles, `flowchart TB` for
   architecture/compartments, others only with cause.
3. Rail content: 3–7 info sections. Required: a "Where we are" summary, a
   "Plain-language glossary" whenever jargon appears, an "Evidence boundary"
   section stating what the diagram does NOT prove, and a "Review status"
   section with the exact digest. For compartmented diagrams add one section
   enumerating the processes and what each owns, one on process boundaries
   (what may not cross), and a "Reading the shapes" legend.
4. Version label (e.g. `v1`, `v3 · corrected after walkthrough`).

## Mermaid source rules

- Start every file with the standard init header (theme `base`, transparent
  background, border `#111827`, line `#334155`); copy it from
  `assets/init-header.mmd`.
- Use the shared shape dialect from `assets/classdefs.mmd` (state, process,
  decision, data store, cross-process message, artifact, blocked/refused,
  note) and include a "Reading the shapes" legend in the rail when more than
  three kinds appear.
- Flowcharts have no `[*]` terminal: end with a labeled stadium node (for
  example `Done(["CAMPAIGN ENDS · report or nothing"])`).
- **Write every label in plain English first.** Assume the reader has no
  source-code familiarity; they rely on the diagram author to explain.
  Jargon may appear only after a plain gloss (e.g. "a sandboxed helper
  sub-process: it can read the code, it can never change it"). Terms like
  persistence, baseline, or controller must be defined in a glossary rail
  section.
- **Show the entry point and the exit.** How control enters the workflow
  (a typed request, an event) and what the terminal state produces.
- **Name the controller.** Identify which process drives the loop. When
  several compartments execute inside one runtime, nest them inside an outer
  box labeled for that runtime; keep humans and on-disk stores outside it,
  explicitly labeled.
- **Compartmentalize when the subject has distinct authorities.** One
  subgraph per process/role, each owning the lifecycle states that belong to
  it. Group states inside the process that owns them; separation of duties
  means each process may not exercise another's authority, and every
  cross-boundary edge is a message or artifact, never a shared shortcut.
  Passive or record-keeping compartments get dashed borders
  (`style X fill:transparent,stroke:#64748b,stroke-width:1.8px,
  stroke-dasharray:6 4`) while authoritative ones stay solid.
- Embed Mermaid source as JSON in the template's application/json script
  element. The builder must JSON-escape `<` and preserve backslashes so valid
  Mermaid escapes remain valid. Assert the decoded embedded value equals the
  exact source bytes before treating packaging as successful.
- Mermaid is hand-authored here: never generate diagram *meaning* from a
  tool; you are the designer. Structure it deliberately: group related
  states/components, label every transition with its trigger, use notes for
  standing rules rather than cluttering transitions.
- Where a state-transition view hides real entity kinds (processes, stores,
  artifacts vs. states), say so: either add a companion flowchart projection
  or note the collapse explicitly in the rail. Do not silently lose the
  distinction.
## Generate the viewer

Use `scripts/build_viewer.py` with `assets/template.html`; the builder performs
context-safe one-pass substitution, validates placeholder completeness, and
checks the exact source digest. Do not hand-assemble HTML when the builder is
available. Its template bindings are:

| Token | Content |
| --- | --- |
| `{{VIEWER_TITLE}}` | `<title>` text |
| `{{HEADER_TITLE}}` | `<h1>` headline |
| `{{REVISION_LINE}}` | e.g. `Revision 2 · corrected after review · pending review` |
| `{{BADGE}}` | `v1 · <digest8>…<digest6>` |
| `{{DIAGRAM_ARIA}}` | aria-label for the diagram host |
| `{{MERMAID_SOURCE_JSON}}` | full `.mmd` contents encoded as JSON for a script element |
| `{{RENDER_ID_JSON}}` | unique render id encoded as a JavaScript string |
| `{{STORAGE_KEY_JSON}}` | localStorage key encoded as a JavaScript string |
| `{{RAIL_CONTENT}}` | the `<aside>` inner HTML (use the classes below) |
| `{{MERMAJS_PATH}}` | URI for an already-installed `mermaid.min.js`; resolve it in the current environment and never encode a username or machine-specific path in tracked source |

Digest = sha256 of the exact `.mmd` bytes. Put the full digest in the review
status section (`<div class="digest">Exact Mermaid digest: …</div>`) and the
short form in the badge.

Rail section vocabulary (keep these classes):

- `<div class="where-we-are">` with `<p><strong>…</strong> …</p>` paragraphs;
- `<details class="rail-section"><summary>…</summary><div class="rail-content">…</div></details>`;
- `<p class="boundary">` inside a rail-content for evidence boundaries;
- `<div class="digest">` for exact digests.

## Placement and hygiene

- Write both files into one versioned directory, e.g.
  `<project>/<design-dir>/diagram-preview-v<N>/`. Prefer the current
  project's own directory over unrelated repos.
- If the target repo must stay clean for source-identity binding (e.g.
  MetaBuilder), prefer an authorized artifact path outside the repository. Use
  `.git/info/exclude` only when that ignore-policy mutation is explicitly
  selected or already covered by project policy, and report it.
- Never commit viewer files unless asked; they are review artifacts.
- Report to the user: both file paths, the digest, the single question the
  viewer answers, and what the evidence boundary excludes.

## Limitations

- Rendering requires a browser and a resolvable `mermaid.min.js`. The viewer
  does not bundle that runtime. A local file URI can support an offline review
  only when the referenced runtime remains available at that path; the HTML is
  not self-contained merely because it was built without a network request.
- The template assumes one diagram per viewer. For multi-projection bundles
  (MetaBuilder `diagrams preview` style), create one viewer per projection or
  extend the template deliberately.
- The template's evidence boundary does not make a draft artifact
  gate-bound; gate-bound bundles come only from MetaBuilder's
  `harness diagrams` machinery over an agreed brief.
