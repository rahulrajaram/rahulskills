# Rendering the PDF

Turn the Markdown whitepaper + CSS into a styled, self-contained PDF with
pandoc + weasyprint and locally embedded fonts.

## Commands

Check the tools actually used: `pandoc`, `weasyprint`, `pdfinfo`, and
`pdffonts`; check `dot` or `pdftoppm` only when their optional paths are selected.
Missing tools do not authorize installation. Report the unavailable step and
finish independent source/style preparation.

Resolve CSS from the explicit stylesheet or project-declared document style;
do not assume a generic `resume.css` is appropriate. Reuse existing local fonts.
New font downloads need the relevant source/path authority; see `branding.md`
only if font selection is part of the request. Honor the requested page size and
length; a paragraph or investor audience alone does not select PDF generation.

For regeneration, reuse existing output-replacement authority. Render to a new
temporary PDF beside the destination, verify it, then replace the authorized
output. Ask only when replacement authority is unresolved; do not overwrite
unrelated files or claim that rendering succeeded from command launch alone.

Build:

```bash
pandoc whitepaper.md -o whitepaper.preview.pdf \
  --pdf-engine=weasyprint --css style.css --metadata title=""
```

`--metadata title=""` suppresses pandoc fabricating a title from the file
name (weasyprint shows a benign "nonempty title" warning; harmless).

Verify: `pdfinfo whitepaper.preview.pdf`, and
`pdffonts whitepaper.preview.pdf` to confirm the expected fonts are embedded (no
DejaVu fallback beyond a stray glyph count).

## The stylesheet essentials

- `@page` with the selected paper size and margins; add a footer page counter
  when appropriate.
- `@font-face` for every weight/family with `src: url('fonts/…')`.
- A `.brand` span for the product name, `.tld` for the domain (so name and
  `.ai` can be styled independently). **Let the CSS drive styling**, not the
  Markdown: the `.md` holds `<span class="brand">…</span>` and the CSS in
  style.css colors/fonts it.
- An `h1 .brand` override so a brand in a title can match the h1 size while
  keeping its own letter-spacing.

## Pitfalls seen in practice

- **Gradients on text via `background-clip: text` don't render in WeasyPrint.**
  Either use a solid color, or an external `.svg` image whose gradient is
  defined in the *same* file, referenced via `<img>`.
- **A gradient or fill referenced by `url(#id)` defined in a separate hidden
  `<svg>` block renders blank/white.** Keep defs in the same `<svg>` as the
  use.
- **Variable fonts can collapse all weights to one file.** If a requested
  weight looks identical, request static weights with an old-style UA, or
  download the distinct per-weight file explicitly.
- **WeasyPrint warns** about `text-rendering: optimizeLegibility`, `@media
  (max-width:…)`, and `overflow-x: auto` from pandoc's default stylesheet —
  these are benign. Don't chase them.
- **Tables:** check pagination and clipping after applying the selected CSS;
  do not assume a fixed percentage change from another project.

## Diagrams

Graphviz `dot` PNGs embed cleanly. Build at higher DPI (`-Gdpi=150`) for a
sharp PDF. Keep labels short; name edges on the arrows where possible.

## Open / deliver

Open the PDF with `xdg-open` when opening is requested and the tool is available.
After verification, replace the authorized output. Report page count and the
output path. Keep the `.md` and `.css` next to the `.pdf` so it stays
editable.
