#!/usr/bin/env python3
"""Bind a committed source identity into a qualification module template."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re

SOURCE_MARKER = "SOURCE_COMMIT_TO_BIND"


@dataclass(frozen=True)
class Binding:
    module_json: str | None
    error: str | None = None


def bind_source(template: object, source_commit: str) -> Binding:
    """Return a fresh module rendition; do not infer or authorize its source."""
    if not isinstance(source_commit, str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", source_commit):
        return Binding(None, "Expected an exact Git commit identity.")
    try:
        module = json.loads(json.dumps(template, allow_nan=False))
        actions = module["actions"]
        if len(actions) != 1:
            return Binding(None, "Expected one qualification action.")
        argv = actions[0]["command"]["argv"]
        if argv.count(SOURCE_MARKER) != 1 or argv.count("--source-commit") != 1:
            return Binding(None, "Expected exactly one unbound source argument.")
        index = argv.index("--source-commit") + 1
        if argv[index] != SOURCE_MARKER:
            return Binding(None, "Source marker is not the source argument.")
        actions[0]["command"]["argv"] = [source_commit if i == index else value for i, value in enumerate(argv)]
        return Binding(json.dumps(module, sort_keys=True, indent=2, allow_nan=False) + "\n")
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        return Binding(None, f"Invalid qualification template: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = bind_source(json.loads(Path(args.template).read_text()), args.source_commit)
    if result.error:
        parser.error(result.error)
    Path(args.output).write_text(result.module_json, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
