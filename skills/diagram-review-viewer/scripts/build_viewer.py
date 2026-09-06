#!/usr/bin/env python3
"""Assemble the local viewer without interpreting diagram text as HTML or JS."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from urllib.parse import urlparse
from pathlib import Path


TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "template.html"
TOKEN = re.compile(r"\{\{([A-Z_]+)\}\}")


def script_json(value: str) -> str:
    # HTML raw-text parsing precedes JavaScript/JSON parsing, even for JSON scripts.
    return json.dumps(value, ensure_ascii=True).replace("<", "\\u003c")


def required_text(config: dict, key: str) -> str:
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a nonempty string")
    return value


def build(source_bytes: bytes, config: dict, runtime_uri: str, template: str) -> tuple[str, str]:
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
    render_id = config.get("render_id", "diagram-" + digest[:16])
    if not isinstance(render_id, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", render_id):
        raise ValueError("render_id must be a lowercase kebab-case identifier")
    sections = config.get("sections", [])
    if not isinstance(sections, list):
        raise ValueError("sections must be a list")
    rail = ['<div class="where-we-are"><p>' + html.escape(summary) + '</p></div>']
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
        document, digest = build(args.source.read_bytes(), config, runtime.as_uri(),
                                 TEMPLATE.read_text(encoding="utf-8"))
        with args.out.open("w" if args.replace else "x", encoding="utf-8", newline="") as output:
            output.write(document)
    except (OSError, ValueError) as error:
        parser.exit(2, f"build_viewer: {error}\n")
    print(json.dumps({"output": str(destination), "source_sha256": digest,
                      "runtime": str(runtime), "packaging": "local-runtime-reference"}))


if __name__ == "__main__":
    main()
