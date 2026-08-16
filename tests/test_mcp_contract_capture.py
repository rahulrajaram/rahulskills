from pathlib import Path
import argparse
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "mcp_contract_capture.py"
SPEC = importlib.util.spec_from_file_location("mcp_contract_capture", MODULE_PATH)
assert SPEC and SPEC.loader
mcp_contract_capture = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mcp_contract_capture
SPEC.loader.exec_module(mcp_contract_capture)


class McpContractCaptureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_capture_session_collects_initialize_and_tool_schemas(self) -> None:
        server = self.root / "fake_mcp.py"
        server.write_text(
        """\
import json
import sys
for line in sys.stdin:
    request = json.loads(line)
    if request.get("method") == "initialize":
        print(json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": {
            "protocolVersion": "2024-11-05", "instructions": "safe test server",
            "capabilities": {"tools": {}}, "serverInfo": {"name": "fake", "version": "1"}}}), flush=True)
    elif request.get("method") == "tools/list":
        print(json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": {"tools": [{
            "name": "inspect", "description": "[safety: readonly] inspect",
            "inputSchema": {"type": "object", "properties": {}}}]}}), flush=True)
""",
        encoding="utf-8",
    )

        capture = mcp_contract_capture.capture_session([sys.executable, str(server)], 5)

        self.assertEqual(capture.initialize["result"]["instructions"], "safe test server")
        self.assertEqual(capture.tools_list["result"]["tools"][0]["name"], "inspect")
        self.assertEqual(len(capture.transcript), 2)

    def test_compare_artifacts_hashes_and_diffs_text(self) -> None:
        source = self.root / "source.txt"
        runtime = self.root / "runtime.txt"
        source.write_text("new contract\n", encoding="utf-8")
        runtime.write_text("old contract\n", encoding="utf-8")

        result = mcp_contract_capture.compare_artifacts(
            mcp_contract_capture.Artifact("server", source),
            mcp_contract_capture.Artifact("server", runtime),
        )

        self.assertFalse(result["equal"])
        self.assertEqual(result["changed_paths"], ["@file"])
        self.assertIn("new contract", result["text_diffs"]["source.txt"])
        self.assertIn("old contract", result["text_diffs"]["source.txt"])

    def test_write_report_normalizes_volatility_and_records_rollback(self) -> None:
        output = self.root / "capture"
        capture = mcp_contract_capture.Capture(
            initialize={"id": 1, "result": {"timestamp": "volatile", "instructions": "stable"}},
            tools_list={"id": 2, "result": {"tools": []}},
            transcript=({"id": 1, "pid": 123},),
            stderr="",
            returncode=-15,
        )

        mcp_contract_capture.write_report(
            output,
            "demo",
            ["demo", "mcp"],
            capture,
            {},
            {"server": "rollback/server"},
        )

        initialize = json.loads((output / "initialize.json").read_text())
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertNotIn("timestamp", initialize["result"])
        self.assertEqual(manifest["rollback_artifacts"]["server"], "rollback/server")

    def test_artifact_labels_reject_path_traversal(self) -> None:
        for raw in ("../outside=/tmp/source", "nested/label=/tmp/source"):
            with self.assertRaises(argparse.ArgumentTypeError):
                mcp_contract_capture.parse_artifact(raw)

    def test_duplicate_artifact_labels_are_rejected(self) -> None:
        artifact = mcp_contract_capture.Artifact("server", self.root)
        with self.assertRaisesRegex(ValueError, "source artifact labels must be unique"):
            mcp_contract_capture.paired_artifacts([artifact, artifact], [artifact])

    def test_staging_creation_preserves_predictable_sibling(self) -> None:
        output = self.root / "capture"
        legacy_staging = self.root / "capture.staging"
        legacy_staging.mkdir()
        sentinel = legacy_staging / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")

        staging = mcp_contract_capture.create_staging_dir(output)
        try:
            self.assertNotEqual(staging, legacy_staging)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
        finally:
            shutil.rmtree(staging)
