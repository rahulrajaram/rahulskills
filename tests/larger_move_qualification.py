"""Read-only qualification entry point for one larger-move epoch.

The controller supplies the process environment and output directory.  This
module only runs consumer-owned unittest suites, checks a separately frozen
trace fixture, and serializes the consumer result; it does not dispatch work
or infer authority from the result.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import sys
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
ORACLE = ROOT / "tests" / "fixtures" / "larger-move" / "trace-oracle.json"
SUITE_MODULES = (
    "tests.test_continuation_state",
    "tests.test_composition_lock",
    "tests.test_learning_ingest",
    "tests.test_bind_qualification_source",
)


def _digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_oracle(epoch: int) -> tuple[dict[str, Any], str]:
    raw = ORACLE.read_bytes()
    document = json.loads(raw)
    expected = next(item for item in document["baseline"] if item.get("epoch") == epoch)
    return expected, _digest_bytes(raw)


def _run_suites() -> dict[str, Any]:
    loader = unittest.TestLoader()
    result = unittest.TestResult()
    details: list[dict[str, Any]] = []
    for module_name in SUITE_MODULES:
        try:
            module = importlib.import_module(module_name)
            suite = loader.loadTestsFromModule(module)
            module_result = unittest.TestResult()
            suite.run(module_result)
            result.testsRun += module_result.testsRun
            result.failures.extend(module_result.failures)
            result.errors.extend(module_result.errors)
            details.append(
                {
                    "module": module_name,
                    "status": "passed" if module_result.testsRun > 0 and not module_result.failures and not module_result.errors else "failed",
                    "tests_run": module_result.testsRun,
                    "failures": len(module_result.failures),
                    "errors": len(module_result.errors),
                    "failure_tracebacks": [str(trace)[:4096] for _, trace in module_result.failures],
                    "error_tracebacks": [str(trace)[:4096] for _, trace in module_result.errors],
                }
            )
        except Exception as exc:  # retain an import/collection failure as evidence
            details.append(
                {
                    "module": module_name,
                    "status": "failed",
                    "tests_run": 0,
                    "failures": 0,
                    "errors": 1,
                    "failure_tracebacks": [],
                    "error_tracebacks": [],
                    "collection_error": f"{type(exc).__name__}: {exc}",
                }
            )
    return {
        "tests_run": result.testsRun,
        "failures": [str(name) for name, _ in result.failures],
        "errors": [str(name) for name, _ in result.errors],
        "modules": details,
        "passed": result.testsRun > 0 and not result.failures and not result.errors and all(
            item["status"] == "passed" for item in details
        ),
    }


def _learning_result(epoch: int, campaign_id: str, run_id: str, policy_digest: str, source_commit: str) -> dict[str, Any]:
    module = importlib.import_module("scripts.learning_ingest")
    source_path = ROOT / "docs" / "learning-records" / "front-door-routing-2026-09-08.json"
    source_bytes = source_path.read_bytes()
    records = json.loads(source_bytes.decode("utf-8"))
    value = module.ingest(records, {
        "campaign_id": campaign_id,
        "epoch": epoch,
        "run_id": run_id,
        "source_commit": source_commit,
        "policy_digest": policy_digest,
    }, previous=None)
    result = value.to_dict() if hasattr(value, "to_dict") else value
    if isinstance(result, dict):
        result["source_path"] = str(source_path.relative_to(ROOT))
        result["source_sha256"] = _digest_bytes(source_bytes)
    return result


def qualify(epoch: int, campaign_id: str, run_id: str, policy_digest: str, source_commit: str) -> tuple[dict[str, Any], int]:
    expected, oracle_digest = _load_oracle(epoch)
    suites = _run_suites()
    try:
        learning = _learning_result(epoch, campaign_id, run_id, policy_digest, source_commit)
        learning_status = "passed" if learning.get("accepted") is True else "failed"
        learning_error = None
    except Exception as exc:
        learning = None
        learning_status = "failed"
        learning_error = f"{type(exc).__name__}: {exc}"

    report = {
        "schema_version": 1,
        "qualification": "larger-move-epoch",
        "epoch": epoch,
        "oracle": {"path": "tests/fixtures/larger-move/trace-oracle.json", "sha256": oracle_digest, "expected": expected, "verification": "controller trace comparison is deferred to the owner run"},
        "consumer_suites": suites,
        "learning_ingestion": {"status": learning_status, "result": learning, "error": learning_error},
        "claims": {
            "controller_observed": False,
            "live_multi_epoch_execution": False,
            "semantic_assessment": "consumer-local qualification evidence only",
        },
        "passed": suites["passed"] and learning_status == "passed",
    }
    return report, 0 if report["passed"] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epoch", type=int, choices=(1, 2, 3), required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--policy-digest", required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args(argv)
    output_root = os.environ.get("METABUILDER_OUTPUT_DIR")
    if not output_root:
        raise SystemExit("METABUILDER_OUTPUT_DIR is required")
    report, status = qualify(args.epoch, args.campaign_id, args.run_id, args.policy_digest, args.source_commit)
    output_dir = Path(output_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "qualification.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return status


if __name__ == "__main__":
    raise SystemExit(main())
