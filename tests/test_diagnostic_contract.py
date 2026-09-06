import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]
sys.path[:0] = [str(ROOT / "skills/check-antipatterns"), str(ROOT / "skills/analyze-conversation")]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_shared_taxonomy_has_stable_ids_and_evidence_categories():
    taxonomy = json.loads((ROOT / "references/diagnostic-taxonomy.json").read_text())
    rules = taxonomy["rules"]
    assert len({rule["id"] for rule in rules}) == len(rules)
    assert all(rule["id"].startswith("DIAG-") for rule in rules)
    assert all(rule.get("evidence_category") for rule in rules)


def test_checker_marks_empty_and_unsupported_coverage():
    checker = load("diagnostic_checker", ROOT / "skills/check-antipatterns/checker.py")
    assert checker.normalize_events([]).coverage == "empty"
    data = checker.normalize_events([{"type": "unrelated_event"}])
    assert data.coverage == "unsupported"
    assert not data.messages


def test_current_item_completed_stream_is_detected_and_normalized():
    checker = load("diagnostic_checker_current", ROOT / "skills/check-antipatterns/checker.py")
    events = [{"type": "event_msg", "payload": {"type": "item_completed", "item": {
        "type": "UserMessage", "content": [{"type": "text", "text": "Inspect this"}]
    }}}]
    data = checker.normalize_events(events)
    assert data.source_format == "codex-item-completed"
    assert data.coverage == "observed"
    assert data.messages[0]["type"] == "user"


def test_shared_taxonomy_maps_legacy_rule_ids_to_stable_ids():
    checker = load("diagnostic_checker_mapping", ROOT / "skills/check-antipatterns/checker.py")
    rules = checker.load_rules()["universal_rules"]
    assert next(rule["stable_id"] for rule in rules if rule["id"] == 2) == "DIAG-002"


def test_analyzer_rejects_empty_and_unsupported_codex_transcripts(tmp_path):
    analyzer = load("diagnostic_report", ROOT / "skills/analyze-conversation/generate_report.py")
    empty = tmp_path / "empty.jsonl"
    empty.write_text("")
    unsupported = tmp_path / "unsupported.jsonl"
    unsupported.write_text(json.dumps({"type": "session_meta", "payload": {}}) + "\n")
    for path, marker in ((empty, "empty transcript"), (unsupported, "unsupported transcript")):
        try:
            analyzer.normalize_codex_conversation(str(path))
        except ValueError as error:
            assert marker in str(error)
        else:
            raise AssertionError("unsupported coverage was reported as success")
