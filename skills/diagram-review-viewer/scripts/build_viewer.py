#!/usr/bin/env python3
"""Assemble the local viewer without interpreting diagram text as HTML or JS."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import html
import json
import re
from urllib.parse import urlparse
from pathlib import Path


TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "template.html"
TOKEN = re.compile(r"\{\{([A-Z_]+)\}\}")
# The page is frozen at build time, so it must never assert a review verdict:
# an accepted diagram would keep saying "pending" forever (seen 2026-09-19).
VERDICT_WORDS = re.compile(
    r"\b(accepted|approved|rejected|not accepted|pending review|awaiting review|under review)\b",
    re.IGNORECASE)
MAX_DIFF_LINES = 200


def script_json(value: str) -> str:
    # HTML raw-text parsing precedes JavaScript/JSON parsing, even for JSON scripts.
    return json.dumps(value, ensure_ascii=True).replace("<", "\\u003c")


def required_text(config: dict, key: str) -> str:
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a nonempty string")
    return value


def change_section(config: dict, source: str, previous_bytes: bytes | None) -> str:
    """Plain-language meaning changes first, exact line changes behind a disclosure."""
    changes = config.get("changes")
    if previous_bytes is None and changes is None:
        return ""
    if previous_bytes is None:
        raise ValueError("changes require --previous so the exact line changes can be shown")
    if not isinstance(changes, dict):
        raise ValueError("a --previous revision requires a changes object with since and summary")
    since = required_text(changes, "since")
    summary = changes.get("summary")
    if not isinstance(summary, list) or not summary or not all(
        isinstance(item, str) and item.strip() for item in summary
    ):
        raise ValueError("changes.summary must be a nonempty list of plain-language strings")
    previous = previous_bytes.decode("utf-8").splitlines()
    lines = [line for line in difflib.unified_diff(previous, source.splitlines(), lineterm="", n=0)
             if line[:1] in "+-" and not line.startswith(("+++", "---"))]
    shown = lines[:MAX_DIFF_LINES]
    exact = "".join(
        '<li class="' + ("removed" if line[0] == "-" else "added") + '">'
        + ("− " if line[0] == "-" else "+ ") + html.escape(line[1:].strip()) + "</li>"
        for line in shown
    ) or "<li>No line changes.</li>"
    more = (f"<p>{len(lines) - len(shown)} more changed lines not shown.</p>"
            if len(lines) > len(shown) else "")
    bullets = "".join("<li>" + html.escape(item) + "</li>" for item in summary)
    return ('<details class="rail-section changes" open><summary>What changed since '
            + html.escape(since) + '</summary><div class="rail-content"><ul>' + bullets
            + '</ul><details class="exact-changes"><summary>Exact line changes ('
            + str(len(lines)) + ')</summary><ul class="line-changes">' + exact + '</ul>' + more
            + '</details></div></details>')


def build(source_bytes: bytes, config: dict, runtime_uri: str, template: str,
          previous_bytes: bytes | None = None) -> tuple[str, str]:
    source = source_bytes.decode("utf-8")
    parsed_runtime = urlparse(runtime_uri)
    if parsed_runtime.scheme != "file" or not parsed_runtime.path:
        raise ValueError("runtime URI must reference a local file")
    digest = hashlib.sha256(source_bytes).hexdigest()
    expected = config.get("expected_digest")
    if expected is not None and expected != digest:
        raise ValueError("expected_digest does not match exact Mermaid bytes")
    title = required_text(config, "title")
    summary = required_text(config, "summary")
    boundary = required_text(config, "boundary")
    revision = required_text(config, "revision")
    if VERDICT_WORDS.search(revision):
        raise ValueError("revision is a version label; review verdicts belong in the owner's record, "
                         "referenced through verdict_record")
    verdict_record = config.get("verdict_record")
    if verdict_record is not None and (not isinstance(verdict_record, str) or not verdict_record.strip()):
        raise ValueError("verdict_record must be a nonempty string when present")
    render_id = config.get("render_id", "diagram-" + digest[:16])
    if not isinstance(render_id, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", render_id):
        raise ValueError("render_id must be a lowercase kebab-case identifier")
    sections = config.get("sections", [])
    if not isinstance(sections, list):
        raise ValueError("sections must be a list")
    rail = ['<div class="where-we-are"><p>' + html.escape(summary) + '</p></div>']
    changes_html = change_section(config, source, previous_bytes)
    if changes_html:
        rail.append(changes_html)
    for section in sections:
        if not isinstance(section, dict):
            raise ValueError("each section must be an object")
        heading = required_text(section, "title")
        paragraphs = section.get("paragraphs")
        if not isinstance(paragraphs, list) or not paragraphs or not all(
            isinstance(paragraph, str) for paragraph in paragraphs
        ):
            raise ValueError("section paragraphs must be a nonempty list of strings")
        body = "".join("<p>" + html.escape(paragraph) + "</p>" for paragraph in paragraphs)
        rail.append('<details class="rail-section"><summary>' + html.escape(heading)
                    + '</summary><div class="rail-content">' + body + '</div></details>')
    rail.append('<p class="boundary">' + html.escape(boundary) + '</p>')
    rail.append('<p class="verdict">Acceptance is not recorded on this page, which is frozen when it is built. '
                + ('The current verdict lives in ' + html.escape(verdict_record) + '.'
                   if verdict_record else "Check the owner's review record for the current verdict.")
                + '</p>')
    rail.append('<div class="digest">Exact Mermaid digest: ' + digest + '</div>')
    values = {
        "VIEWER_TITLE": html.escape(title),
        "HEADER_TITLE": html.escape(title),
        "REVISION_LINE": html.escape(revision),
        "BADGE": html.escape(revision) + " · " + digest[:8] + "…" + digest[-6:],
        "DIAGRAM_ARIA": html.escape(title, quote=True),
        "MERMAID_SOURCE_JSON": script_json(source),
        "RENDER_ID_JSON": script_json(render_id),
        "STORAGE_KEY_JSON": script_json("diagram-rail-" + render_id),
        "RAIL_CONTENT": "\n".join(rail),
        "MERMAJS_PATH": html.escape(runtime_uri, quote=True),
    }
    tokens = TOKEN.findall(template)
    if set(tokens) != set(values) or len(tokens) != len(values):
        raise ValueError("template tokens must match the builder exactly once each")
    # One pass: token-shaped user content remains literal, never a second template.
    return TOKEN.sub(lambda match: values[match.group(1)], template), digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True,
                        help="Already-present mermaid.min.js; no download is performed")
    parser.add_argument("--previous", type=Path,
                        help="Earlier .mmd revision; requires a changes summary in the config")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--replace", action="store_true", help="Replace an authorized existing output")
    args = parser.parse_args()
    try:
        runtime = args.runtime.resolve(strict=True)
        if not runtime.is_file():
            raise ValueError("runtime must be an existing local file")
        destination = args.out.resolve()
        if destination in {args.source.resolve(), args.config.resolve(), runtime, TEMPLATE.resolve()}:
            raise ValueError("output must not overwrite an input or template")
        config = json.loads(args.config.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError("config must be an object")
        previous = args.previous.read_bytes() if args.previous else None
        document, digest = build(args.source.read_bytes(), config, runtime.as_uri(),
                                 TEMPLATE.read_text(encoding="utf-8"), previous)
        with args.out.open("w" if args.replace else "x", encoding="utf-8", newline="") as output:
            output.write(document)
    except (OSError, ValueError) as error:
        parser.exit(2, f"build_viewer: {error}\n")
    print(json.dumps({"output": str(destination), "source_sha256": digest,
                      "runtime": str(runtime), "packaging": "local-runtime-reference"}))


if __name__ == "__main__":
    main()
