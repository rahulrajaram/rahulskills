"""Pure redaction of complete source fields and excerpts derived from them."""

from __future__ import annotations

from itertools import accumulate
import re


# Keep quoting rules distinct: shell words can concatenate quoted and unquoted
# segments; mapping strings can contain escaped or doubled quotes. Unterminated
# quoted values consume the remainder rather than revealing a credential tail.
_DOUBLE_QUOTED = r'"(?:\\[\s\S]|[^"\\])*(?:"|\\?\Z)'
_SHELL_SINGLE_QUOTED = r"'[^']*(?:'|\Z)"
_MAPPING_SINGLE_QUOTED = r"'(?:\\[\s\S]|''|[^'\\])*(?:'|\\?\Z)"
_SHELL_WORD = rf"""(?:{_DOUBLE_QUOTED}|{_SHELL_SINGLE_QUOTED}|\\[\s\S]|[^\s;|&'"\\])+"""
_MAPPING_VALUE = (
    rf"""(?:\[REDACTED\]|{_DOUBLE_QUOTED}|{_MAPPING_SINGLE_QUOTED}|[^\s,;}}'"\]]+)"""
)
_ASSIGNMENT_NAME = r"[A-Z0-9_]*(?:password|secret|token|api_?key|credential)[A-Z0-9_]*"
_CREDENTIAL_FLAG = r"--(?:password|secret|token|api[-_]key|credential)"

# Every pattern captures the identifying prefix as group 1 and only the
# sensitive value as group 2 (the prefix is empty for a whole quoted word).
# Match all patterns on the ORIGINAL source:
# replacing one value must not hide a boundary needed by another recognizer.
_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        # Quoting can begin before the key: env 'PASSWORD=two words'. Mask the
        # whole word so removing its closing quote cannot leave a dangling one.
        rf"""()((?=["'](?:{_ASSIGNMENT_NAME}\s*=(?!=)|{_CREDENTIAL_FLAG}(?:=|\s))){_SHELL_WORD})""",
        rf"(\b{_ASSIGNMENT_NAME}\s*=(?!=)\s*)({_SHELL_WORD})",
        r"""((?:"|')?[A-Z0-9_-]*(?:password|secret|token|api_?key|credential)"""
        rf"""[A-Z0-9_-]*(?:"|')?\s*:\s*)({_MAPPING_VALUE})""",
        rf"({_CREDENTIAL_FLAG}(?:=|\s+))({_SHELL_WORD})",
        r"""(\bauthorization["']?\s*:\s*["']?(?:bearer|basic)\s+)([^\s,;"']+)""",
        r"(\b[a-z][a-z0-9+.-]*://)([^/@\s]+)@",
    )
)


def redact_sensitive_excerpt(
    value: object, start: int = 0, end: int | None = None
) -> str:
    """Select a source span, masking credentials identified in the complete field.

    Offsets refer to the original source, so a regex capture or context window
    inside a credential remains redacted even if its key/terminator is outside
    that window. Raw input stays available to callers for detection and counts.
    """
    text = str(value)
    start, stop, _ = slice(start, end).indices(len(text))
    if stop <= start:
        return ""
    spans = tuple(
        sorted(
            (max(start, match.start(2)), min(stop, match.end(2)))
            for pattern in _PATTERNS
            for match in pattern.finditer(text)
            if match.start(2) < stop and match.end(2) > start
        )
    )
    covered_ends = tuple(accumulate((right for _, right in spans), max, initial=start))
    return (
        "".join(
            text[previous:left] + "[REDACTED]"
            for (left, right), previous in zip(spans, covered_ends)
            if right > previous
        )
        + text[covered_ends[-1] : stop]
    )


def redact_sensitive_text(value: object) -> str:
    """Redact common credential-bearing forms without echoing their values."""
    return redact_sensitive_excerpt(value)
