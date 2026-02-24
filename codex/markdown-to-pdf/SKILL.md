---
name: markdown-to-pdf
description: "Convert markdown to PDF via pandoc + weasyprint. Use when the user asks to generate a PDF from markdown or says /markdown-to-pdf."
---

# Markdown to PDF Conversion Skill

Convert a markdown file to a styled PDF using pandoc with the weasyprint engine.

## Workflow

1. **Check dependencies** — verify `pandoc` and `weasyprint` are installed. If either is missing, print install instructions and stop:
   - pandoc: `sudo apt install pandoc`
   - weasyprint: `pip install weasyprint`

2. **Parse arguments** from the user's request:
   - `<input.md>` — required, the markdown file to convert.
   - `--css <style.css>` — optional, path to a CSS stylesheet.
   - `--output <output.pdf>` — optional, path for the output PDF.

3. **CSS discovery** — if `--css` was given, use that file. Otherwise, look for `resume.css` in the same directory as the input file. If found, use it automatically. If not found, proceed without CSS.

4. **Output path** — if `--output` was given, use that. Otherwise, replace the `.md` extension on the input file with `.pdf`.

5. **Remove old PDF** — if a file already exists at the output path, delete it.

6. **Convert** — run:
   ```bash
   pandoc <input> -o <output> --pdf-engine=weasyprint [--css <css>] --metadata title=""
   ```
   Always pass `--metadata title=""` to suppress pandoc generating a title from the filename.

7. **Report** — run `pdfinfo <output> | grep Pages` and display the page count.

8. **Show output path** — tell the user where the PDF was written.

## Options Reference

| Option     | Description                        | Default                              |
|------------|------------------------------------|--------------------------------------|
| `--css`    | Path to CSS stylesheet             | Auto-discover `resume.css` in input dir |
| `--output` | Output PDF path                    | Input path with `.md` replaced by `.pdf` |

## Examples

```bash
# Explicit CSS and output
/markdown-to-pdf ~/docs/resume.md --css ~/docs/resume.css --output /tmp/resume.pdf

# Auto-discover resume.css in same directory
/markdown-to-pdf ~/docs/resume.md

# No CSS, custom output
/markdown-to-pdf README.md --output docs/readme.pdf
```

## Guardrails

- Always check that the input file exists before running pandoc.
- Always use `--metadata title=""` to prevent duplicate title generation.
- Always report page count after conversion so the user can verify layout.
- Never modify the input markdown file.
