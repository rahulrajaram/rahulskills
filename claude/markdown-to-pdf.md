---
allowed-tools: Bash(pandoc:*), Bash(weasyprint:*), Bash(rm:*), Bash(pdfinfo:*)
argument-hint: <input.md> [--css <style.css>] [--output <output.pdf>]
description: Convert markdown to PDF via pandoc + weasyprint with optional CSS stylesheet
---

Convert a markdown file to PDF using pandoc with the weasyprint engine.

## Workflow

1. **Check dependencies** — verify `pandoc` and `weasyprint` are installed. If either is missing, print install instructions (`sudo apt install pandoc` / `pip install weasyprint`) and stop.

2. **Parse arguments** from `$ARGUMENTS`:
   - `<input.md>` — required, the markdown file to convert.
   - `--css <style.css>` — optional, path to a CSS stylesheet.
   - `--output <output.pdf>` — optional, path for the output PDF.

3. **CSS discovery** — if `--css` was given, use that file. Otherwise, look for `resume.css` in the same directory as the input file. If found, use it. If not found, proceed without CSS.

4. **Output path** — if `--output` was given, use that. Otherwise, replace the `.md` extension on the input file with `.pdf`.

5. **Remove old PDF** — if a file already exists at the output path, delete it with `rm`.

6. **Convert** — run:
   ```
   pandoc <input> -o <output> --pdf-engine=weasyprint [--css <css>] --metadata title=""
   ```
   Always pass `--metadata title=""` to suppress pandoc generating a title from the filename.

7. **Report** — run `pdfinfo <output> | grep Pages` and display the page count to the user.

8. **Show output path** — tell the user where the PDF was written.
