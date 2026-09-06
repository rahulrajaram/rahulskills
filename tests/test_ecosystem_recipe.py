"""Exercise the single-call-per-sigma ideation recipe with a fake CLI."""

import json
import os
import subprocess


def test_recipe_preserves_one_result_and_failure_per_sigma(tmp_path):
    fake = tmp_path / "gptengage"
    fake.write_text("""#!/bin/sh
sigma=
for arg in "$@"; do
  if test "$take_sigma" = 1; then sigma=$arg; take_sigma=; fi
  test "$arg" = --sigma && take_sigma=1
done
if test "$sigma" = 0.5; then
  echo "backend unavailable for sigma=$sigma" >&2
  exit 7
fi
printf '{\"sigma\":\"%s\",\"ideas\":[\"kept\"]}\n' "$sigma"
""", encoding="utf-8")
    fake.chmod(0o755)
    run_dir = tmp_path / "runs"
    script = r'''set -u
GPTENGAGE="$1"; RUN_DIR="$2"; mkdir -p "$RUN_DIR"
SEED="bounded seed"; DEPTH=2; CLI=claude; CALL_TIMEOUT=30; INDEX=0
for SIG in 0.25 0.5; do
  INDEX=$((INDEX + 1))
  if "$GPTENGAGE" ideate "$SEED" --sigma "$SIG" --depth "$DEPTH" \
      --output json --cli "$CLI" --timeout "$CALL_TIMEOUT" \
      > "$RUN_DIR/$INDEX.json" 2> "$RUN_DIR/$INDEX.stderr"; then
    status=0
  else
    status=$?
  fi
  printf '%s\n' "$status" > "$RUN_DIR/$INDEX.exit"
done
'''
    result = subprocess.run(["bash", "-c", script, "recipe", str(fake), str(run_dir)],
                            env=os.environ.copy(), capture_output=True, text=True)
    assert result.returncode == 0
    assert json.loads((run_dir / "1.json").read_text()) == {"sigma": "0.25", "ideas": ["kept"]}
    assert (run_dir / "1.stderr").read_text() == ""
    assert (run_dir / "1.exit").read_text() == "0\n"
    assert (run_dir / "2.json").read_text() == ""
    assert "sigma=0.5" in (run_dir / "2.stderr").read_text()
    assert (run_dir / "2.exit").read_text() == "7\n"
