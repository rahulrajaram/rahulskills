import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import init_skill as init_skill_module
from quick_validate import parse_frontmatter, validate_skill


def write_skill(root: Path, frontmatter: str) -> Path:
    skill = root / "example-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        f"---\n{frontmatter}\n---\n\n# Example\n",
        encoding="utf-8",
    )
    return skill


class QuickValidateTests(unittest.TestCase):
    def test_rejects_non_string_or_unsupported_yaml_descriptions(self):
        for value in (
            "[one, two]",
            "{one: two}",
            "a: b",
            "false # note",
            "False",
            "null # note",
            "# only a comment",
            "'first' junk 'last'",
            "0xFF",
            "1e3",
            "1_000.0",
            ".1_0",
            "2026-09-04",
            "&anchor value",
            "*anchor",
            "!!str value",
        ):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as raw_dir:
                skill = write_skill(
                    Path(raw_dir), f"name: example-skill\ndescription: {value}"
                )
                self.assertFalse(validate_skill(skill)[0])

    def test_supported_scalar_comments_and_quotes_preserve_values(self):
        for value, expected in (
            ('"Describe: a # value" # comment', "Describe: a # value"),
            ("'Describe it''s behavior' # comment", "Describe it's behavior"),
            ("Describe behavior # comment", "Describe behavior"),
            ("See https://host.invalid/#anchor", "See https://host.invalid/#anchor"),
            ("1.0.0", "1.0.0"),
            ("5-whys analysis", "5-whys analysis"),
        ):
            with self.subTest(value=value):
                self.assertEqual(
                    expected, parse_frontmatter(f"description: {value}")["description"]
                )
        self.assertIs(
            False,
            parse_frontmatter("disable-model-invocation: False # comment")[
                "disable-model-invocation"
            ],
        )

    def test_null_is_not_a_valid_optional_boolean(self):
        with tempfile.TemporaryDirectory() as raw_dir:
            skill = write_skill(
                Path(raw_dir),
                "name: example-skill\ndescription: Example skill.\ndisable-model-invocation: null",
            )
            self.assertFalse(validate_skill(skill)[0])

    def test_parses_nested_metadata_without_third_party_yaml(self) -> None:
        self.assertEqual(
            {
                "name": "example-skill",
                "metadata": {"short-description": "Example"},
            },
            parse_frontmatter(
                "name: example-skill\nmetadata:\n  short-description: Example"
            ),
        )

    def test_accepts_package_frontmatter_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            skill = write_skill(
                Path(raw_dir),
                "\n".join(
                    (
                        "name: example-skill",
                        "description: Validate an example skill.",
                        'argument-hint: "[input]"',
                        "disable-model-invocation: true",
                        "author: example",
                        'version: "1.0.0"',
                    )
                ),
            )

            self.assertEqual((True, "Skill is valid!"), validate_skill(skill))

    def test_rejects_wrong_extension_type(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            skill = write_skill(
                Path(raw_dir),
                "\n".join(
                    (
                        "name: example-skill",
                        "description: Validate an example skill.",
                        "disable-model-invocation: sometimes",
                    )
                ),
            )

            valid, message = validate_skill(skill)
            self.assertFalse(valid)
            self.assertIn("'disable-model-invocation' must be bool", message)

    def test_rejects_unknown_frontmatter_key(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            skill = write_skill(
                Path(raw_dir),
                "\n".join(
                    (
                        "name: example-skill",
                        "description: Validate an example skill.",
                        "unexpected: true",
                    )
                ),
            )

            valid, message = validate_skill(skill)
            self.assertFalse(valid)
            self.assertIn("Unexpected key(s)", message)

    def test_rejects_malformed_quoted_value(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            skill = write_skill(
                Path(raw_dir),
                'name: example-skill\ndescription: "unterminated',
            )

            valid, message = validate_skill(skill)
            self.assertFalse(valid)
            self.assertIn("Invalid YAML frontmatter", message)

    def test_rejects_empty_required_fields(self) -> None:
        for field, frontmatter in (
            ("Name", 'name: ""\ndescription: Validate an example skill.'),
            ("Description", 'name: example-skill\ndescription: ""'),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as raw_dir:
                skill = write_skill(Path(raw_dir), frontmatter)

                valid, message = validate_skill(skill)

                self.assertFalse(valid)
                self.assertIn(f"{field} must not be empty", message)

    def test_rejects_directory_name_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            skill = write_skill(
                Path(raw_dir),
                "name: different-skill\ndescription: Validate an example skill.",
            )

            valid, message = validate_skill(skill)

            self.assertFalse(valid)
            self.assertIn("must match frontmatter name", message)

    def test_generator_runs_without_site_packages(self) -> None:
        script = Path(__file__).resolve().parent / "generate_openai_yaml.py"
        with tempfile.TemporaryDirectory() as raw_dir:
            skill = write_skill(
                Path(raw_dir),
                "name: example-skill\ndescription: Validate an example skill.",
            )

            result = subprocess.run(
                [sys.executable, "-S", str(script), str(skill)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((skill / "agents" / "openai.yaml").is_file())

    def test_initializer_rejects_interface_before_creating_destination(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            with contextlib.redirect_stdout(io.StringIO()):
                result = init_skill_module.init_skill(
                    "example-skill",
                    root,
                    [],
                    False,
                    ["short_description=too short"],
                )

            self.assertIsNone(result)
            self.assertFalse((root / "example-skill").exists())
            self.assertEqual([], list(root.glob(".example-skill.stage-*")))

    def test_initializer_failure_leaves_only_inspectable_staging(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            sentinel = root / "sentinel.txt"
            sentinel.write_text("preserve me", encoding="utf-8")
            with mock.patch.object(
                init_skill_module,
                "create_resource_dirs",
                side_effect=OSError("simulated failure"),
            ), contextlib.redirect_stdout(io.StringIO()):
                result = init_skill_module.init_skill(
                    "example-skill",
                    root,
                    ["scripts"],
                    False,
                    [],
                )

            self.assertIsNone(result)
            self.assertFalse((root / "example-skill").exists())
            self.assertEqual("preserve me", sentinel.read_text(encoding="utf-8"))
            stages = list(root.glob(".example-skill.stage-*"))
            self.assertEqual(1, len(stages))
            self.assertTrue((stages[0] / "SKILL.md").is_file())

    def test_initializer_does_not_overwrite_existing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            destination = root / "example-skill"
            destination.mkdir()
            sentinel = destination / "sentinel.txt"
            sentinel.write_text("preserve me", encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                result = init_skill_module.init_skill(
                    "example-skill", root, [], False, []
                )

            self.assertIsNone(result)
            self.assertEqual("preserve me", sentinel.read_text(encoding="utf-8"))
            self.assertEqual([], list(root.glob(".example-skill.stage-*")))

    def test_initializer_publishes_complete_skill_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            with contextlib.redirect_stdout(io.StringIO()):
                result = init_skill_module.init_skill(
                    "example-skill", root, ["references"], False, []
                )

            destination = root / "example-skill"
            self.assertEqual(destination, result)
            self.assertTrue((destination / "SKILL.md").is_file())
            self.assertTrue((destination / "agents" / "openai.yaml").is_file())
            self.assertTrue((destination / "references").is_dir())
            self.assertEqual([], list(root.glob(".example-skill.stage-*")))


if __name__ == "__main__":
    unittest.main()
