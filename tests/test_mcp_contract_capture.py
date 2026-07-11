from pathlib import Path
import importlib.util
import json
import sys


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "mcp_contract_capture.py"
SPEC = importlib.util.spec_from_file_location("mcp_contract_capture", MODULE_PATH)
assert SPEC and SPEC.loader
mcp_contract_capture = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mcp_contract_capture
SPEC.loader.exec_module(mcp_contract_capture)


def test_capture_session_collects_initialize_and_tool_schemas(tmp_path) -> None:
    server = tmp_path / "fake_mcp.py"
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

    assert capture.initialize["result"]["instructions"] == "safe test server"
    assert capture.tools_list["result"]["tools"][0]["name"] == "inspect"
    assert len(capture.transcript) == 2


def test_compare_artifacts_hashes_and_diffs_text(tmp_path) -> None:
    source = tmp_path / "source.txt"
    runtime = tmp_path / "runtime.txt"
    source.write_text("new contract\n", encoding="utf-8")
    runtime.write_text("old contract\n", encoding="utf-8")

    result = mcp_contract_capture.compare_artifacts(
        mcp_contract_capture.Artifact("server", source),
        mcp_contract_capture.Artifact("server", runtime),
    )

    assert result["equal"] is False
    assert result["changed_paths"] == ["@file"]
    assert "new contract" in result["text_diffs"]["source.txt"]
    assert "old contract" in result["text_diffs"]["source.txt"]


def test_write_report_normalizes_volatility_and_records_rollback(tmp_path) -> None:
    output = tmp_path / "capture"
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
    assert "timestamp" not in initialize["result"]
    assert manifest["rollback_artifacts"]["server"] == "rollback/server"
