"""Pure redaction helpers for transcript-derived report text."""

from __future__ import annotations

import re


_ASSIGNMENT = re.compile(
    r"(?i)(\b[A-Z0-9_]*(?:password|secret|token|api_?key|credential)"
    r"[A-Z0-9_]*\s*=(?!=)\s*)"
    r"(?:\"[^\"\n]*\"|'[^'\n]*'|[^\s;|&]+)"
)
_MAPPING_FIELD = re.compile(
    r"(?i)((?:\"|')?[A-Z0-9_-]*(?:password|secret|token|api_?key|credential)"
    r"[A-Z0-9_-]*(?:\"|')?\s*:\s*)"
    r"(?:\"[^\"\n]*\"|'[^'\n]*'|[^\s,;}]+)"
)
_COMMAND_FLAG = re.compile(
    r"(?i)(--(?:password|secret|token|api[-_]key|credential)(?:=|\s+))"
    r"(?:\"[^\"\n]*\"|'[^'\n]*'|[^\s;|&]+)"
)
_AUTHORIZATION = re.compile(r"(?i)(\bauthorization\s*:\s*(?:bearer|basic)\s+)[^\s,;]+")
_URL_USERINFO = re.compile(r"(?i)(\b[a-z][a-z0-9+.-]*://)[^/@\s]+@")


def redact_sensitive_text(value: object) -> str:
    """Redact common credential-bearing forms without echoing their values."""
    text = str(value)
    text = _ASSIGNMENT.sub(r"\1[REDACTED]", text)
    text = _MAPPING_FIELD.sub(r"\1[REDACTED]", text)
    text = _COMMAND_FLAG.sub(r"\1[REDACTED]", text)
    text = _AUTHORIZATION.sub(r"\1[REDACTED]", text)
    return _URL_USERINFO.sub(r"\1[REDACTED]@", text)
