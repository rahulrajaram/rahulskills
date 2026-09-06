---
name: markdown-to-pdf
description: "Convert markdown to PDF via pandoc + weasyprint. Use when the user asks to generate a PDF from markdown or says /markdown-to-pdf."
argument-hint: "<input.md> [--css <style.css>] [--output <output.pdf>]"
---

# Markdown to PDF Conversion Skill

Convert a markdown file to a styled PDF using pandoc with the weasyprint engine.

## Workflow

1. **Check dependencies** — verify `pandoc` and `weasyprint` are installed. If
   either is missing, report the missing command and stop. Do not install it or
   recommend an unpinned privileged/global install unless the user asks for
   installation and approves the source, destination, and command.

2. **Parse arguments** from the user's request:
   - `<input.md>` — required, the markdown file to convert.
   - `--css <style.css>` — optional, path to a CSS stylesheet.
   - `--output <output.pdf>` — optional, path for the output PDF.

3. **CSS discovery** — if `--css` was given, use that file. Otherwise use an explicitly project-declared stylesheet for this document type. A nearby `resume.css` is not a generic document style; proceed without CSS if no relevant style is selected.

4. **Output path** — if `--output` was given, use that. Otherwise, replace the `.md` extension on the input file with `.pdf`.

5. **Handle an existing PDF** — if the output exists, show the path and ask
   before replacing it only when existing authority does not already cover regeneration
   of that exact output. Reuse ongoing regeneration/overwrite authorization. Preserve
   the old file until the new PDF has been generated and validated, then replace
   atomically where possible.

6. **Convert** — run:
   ```bash
   pandoc <input> -o <output> --pdf-engine=weasyprint [--css <css>] --metadata title=""
   ```
   Always pass `--metadata title=""` to suppress pandoc generating a title from the filename.

7. **Validate and report** — inspect the generated PDF; use `pdfinfo` for page count
   when installed, otherwise an available PDF reader. Report unavailable layout/page
   checks explicitly; do not install an extra tool solely to count pages.

8. **Show output path** — tell the user where the PDF was written.

## Options Reference

| Option     | Description                        | Default                              |
|------------|------------------------------------|--------------------------------------|
| `--css`    | Path to CSS stylesheet             | Explicit or project-declared relevant CSS |
| `--output` | Output PDF path                    | Input path with `.md` replaced by `.pdf` |

## Examples

```bash
# Explicit CSS and output
/markdown-to-pdf ~/docs/resume.md --css ~/docs/resume.css --output /tmp/resume.pdf

# Use a project-declared style if available
/markdown-to-pdf ~/docs/resume.md

# No CSS, custom output
/markdown-to-pdf README.md --output docs/readme.pdf
```

## Guardrails

- Always check that the input file exists before running pandoc.
- Always use `--metadata title=""` to prevent duplicate title generation.
- Report observed page count when available and identify unverified layout; never invent a page count.
- Never modify the input markdown file.
