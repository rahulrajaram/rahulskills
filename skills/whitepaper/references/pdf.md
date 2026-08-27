# Rendering the PDF

Turn the Markdown whitepaper + CSS into a styled, self-contained PDF with
pandoc + weasyprint and locally embedded fonts.

## Commands

Check tools: `pandoc`, `weasyprint`, `pdfinfo`.

Download fonts (modern UA returns variable fonts; specific weights per weight
via an old-style UA). Put font files in a `fonts/` dir next to the `.css`.

Build:

```bash
pandoc whitepaper.md -o whitepaper.pdf \
  --pdf-engine=weasyprint --css style.css --metadata title=""
```

`--metadata title=""` suppresses pandoc fabricating a title from the file
name (weasyprint shows a benign "nonempty title" warning; harmless).

Verify: `pdfinfo whitepaper.pdf | grep Pages`, and
`pdffonts whitepaper.pdf` to confirm the expected fonts are embedded (no
DejaVu fallback beyond a stray glyph count).

## The stylesheet essentials

- `@page { size: A4; margin: ...; }` plus a footer page counter.
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
- **Tables:** the repo's default stripe/header styling change the page count
  by ~10%; check pagination after adding CSS.

## Diagrams

Graphviz `dot` PNGs embed cleanly. Build at higher DPI (`-Gdpi=150`) for a
sharp PDF. Keep labels short; name edges on the arrows where possible.

## Open / deliver

Open the PDF in the default viewer with `xdg-open`. Report page count and the
output path. Keep the `.md` and `.css` next to the `.pdf` so it stays
editable.