"""The independently installable skills must satisfy the same redaction contract."""

import importlib.util
import json
from pathlib import Path
import unittest


def load_redactor(skill):
    path = Path(__file__).parent / "skills" / skill / "redaction.py"
    spec = importlib.util.spec_from_file_location(skill, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REDACTORS = tuple(
    (skill, load_redactor(skill))
    for skill in (
        "analyze-conversation",
        "check-antipatterns",
    )
)


def synthetic_url(userinfo):
    return f"https://{userinfo}@host.invalid"


class RedactionTests(unittest.TestCase):
    def test_complete_quoted_and_concatenated_values(self):
        values = (
            r'{"password": "prefix\"SYNTHETIC_TAIL"}',
            r'PASSWORD="prefix\"SYNTHETIC_TAIL"',
            r'deploy --password "prefix\"SYNTHETIC_TAIL"',
            'PASSWORD="prefix"SYNTHETIC_TAIL',
            r"PASSWORD=prefix\ SYNTHETIC_TAIL",
            r"PASSWORD='prefix'\''SYNTHETIC_TAIL'",
            "password: 'prefix''SYNTHETIC_TAIL'",
            '"Authorization": "Bearer SYNTHETIC_TAIL"',
            'PASSWORD="prefix\nSYNTHETIC_TAIL"',
            synthetic_url("user:token=SYNTHETIC_TAIL"),
            "env 'PASSWORD=prefix SYNTHETIC_TAIL' deploy",
            'export "PASSWORD=prefix SYNTHETIC_TAIL"',
            'deploy "--password=prefix SYNTHETIC_TAIL"',
            "env 'PASSWORD=prefix 'SYNTHETIC_TAIL deploy",
            r'export "PASSWORD=prefix\" SYNTHETIC_TAIL"',
        )
        for skill, redactor in REDACTORS:
            for value in values:
                with self.subTest(skill=skill, value=value):
                    output = redactor.redact_sensitive_text(value + " visible-context")
                    self.assertNotIn("SYNTHETIC_TAIL", output)
                    self.assertIn("[REDACTED]", output)
                    self.assertIn("visible-context", output)
                    self.assertEqual(output, redactor.redact_sensitive_text(output))

    def test_json_escapes_and_backslash_parity(self):
        for skill, redactor in REDACTORS:
            for count in range(5):
                with self.subTest(skill=skill, count=count):
                    value = "prefix" + "\\" * count + '"SYNTHETIC_TAIL'
                    source = json.dumps({"api_key": value, "safe": "visible-context"})
                    output = redactor.redact_sensitive_text(source)
                    self.assertNotIn("SYNTHETIC_TAIL", output)
                    self.assertIn('"safe": "visible-context"', output)

    def test_unterminated_values_do_not_reveal_the_remainder(self):
        for skill, redactor in REDACTORS:
            for source in (
                'PASSWORD="prefix\nSYNTHETIC_TAIL',
                "password: 'SYNTHETIC_TAIL\\",
            ):
                with self.subTest(skill=skill, source=source):
                    self.assertNotIn(
                        "SYNTHETIC_TAIL", redactor.redact_sensitive_text(source)
                    )

    def test_excerpt_can_start_and_end_inside_a_credential(self):
        source = synthetic_url("u:SYNTHETIC_TAIL.more")
        start = source.index("SYNTHETIC_TAIL")
        end = start + len("SYNTHETIC_TAIL")
        for skill, redactor in REDACTORS:
            with self.subTest(skill=skill):
                self.assertEqual(
                    "[REDACTED]", redactor.redact_sensitive_excerpt(source, start, end)
                )
                self.assertEqual(
                    "", redactor.redact_sensitive_excerpt(source, end, start)
                )
                self.assertEqual(
                    "invalid", redactor.redact_sensitive_excerpt(source, -7)
                )

    def test_plain_text_and_non_sensitive_fields_survive(self):
        source = (
            'name="example"; endpoint: https://host.invalid/path\nNothing sensitive.'
        )
        for skill, redactor in REDACTORS:
            with self.subTest(skill=skill):
                self.assertEqual(source, redactor.redact_sensitive_text(source))
                masked = redactor.redact_sensitive_text('PASSWORD="value"')
                self.assertEqual(masked, redactor.redact_sensitive_text(masked))


if __name__ == "__main__":
    unittest.main()
