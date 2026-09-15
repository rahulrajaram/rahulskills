import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "skills" / "handoff" / "scripts" / "validate_handoff_claims.py"

spec = importlib.util.spec_from_file_location("validate_handoff_claims", SCRIPT)
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator  # dataclasses requires the module to be registered
spec.loader.exec_module(validator)


class HandoffClaimValidatorTests(unittest.TestCase):
    def test_existing_artifact_claimed_missing_is_suspect(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            repo = Path(raw_dir)
            (repo / "evidence").mkdir()
            (repo / "evidence" / "proof.json").write_text("{}")
            text = "- R-001 exit evidence is still missing: `evidence/proof.json`\n"

            claims = validator.find_claims(text, repo, repo)

            self.assertEqual(1, len(claims))
            self.assertEqual("SUSPECT", claims[0].status)
            handoff = repo / "NEXT_SHELL_PROMPT.md"
            handoff.write_text(text)
            self.assertEqual(2, validator.main([str(handoff), "--repo", str(repo)]))

    def test_named_absent_path_is_confirmed(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            repo = Path(raw_dir)
            text = "- The closure report is missing: `evidence/report.md`\n"

            claims = validator.find_claims(text, repo, repo)

            self.assertEqual(1, len(claims))
            self.assertEqual("CONFIRMED", claims[0].status)

    def test_pathless_evidence_claim_is_unresolved_and_strict_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            repo = Path(raw_dir)
            handoff = repo / "NEXT_SHELL_PROMPT.md"
            handoff.write_text("- The joint-refusal evidence is still missing.\n")

            claims = validator.find_claims(handoff.read_text(), repo, repo)

            self.assertEqual(1, len(claims))
            self.assertEqual("UNRESOLVED", claims[0].status)
            self.assertEqual(0, validator.main([str(handoff), "--repo", str(repo)]))
            self.assertEqual(
                2, validator.main([str(handoff), "--repo", str(repo), "--strict"])
            )

    def test_dir_ish_token_without_extension_stays_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            repo = Path(raw_dir)
            text = (
                "- R-001 exit conditions still missing: merged-branch "
                "full-suite/Clippy evidence + joint-refusal artifact.\n"
            )

            claims = validator.find_claims(text, repo, repo)

            self.assertEqual(1, len(claims))
            self.assertEqual("UNRESOLVED", claims[0].status)

    def test_guardrail_prose_is_not_a_claim(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            repo = Path(raw_dir)
            text = "Guardrails: never substitute models; no pushes; no secrets.\n"

            self.assertEqual([], validator.find_claims(text, repo, repo))


if __name__ == "__main__":
    unittest.main()
