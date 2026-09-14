# Conversation Retrospective: llm-runpod phase7-8 (manual)

**Provenance:** Authored manually by the session agent from complete session
context. The analyze-conversation tooling (`generate_report.py`) supports
Codex JSONL only; this opencode session lives in SQLite (`opencode.db`) and
is unsupported input — per skill contract this is a declared coverage
failure, not a silent no-findings pass. A tool-generated report for an
UNRELATED Codex session (rollout-2026-09-13T16-30-45) exists at
`~/.codex/retrospectives/` and is explicitly NOT this conversation's analysis.
Filed friction for an opencode adapter (see selfimprovemeta, f-1667-series).

**Session:** 2026-09-13 23:40Z → 2026-09-14 04:45Z (~5h wall) · llm-runpod
phase 7–8 · 13 commits · 53 tests · 4 pods · account zeroed at close.

## Anti-patterns observed (with evidence)

1. **Unverified value treated as ground truth** (HIGH, 3 instances)
   - `torch.cuda.get_arch_list()` read as "B300 cannot run" → over-broad
     manifest rewrite + wasted 433 GB download. Falsified by a 1-minute
     single-GPU probe.
   - "overswatch" assumed missing → was the Overwatch MCP all along.
   - pod "ssh key registered FAILED" doctor line assumed blocking → cosmetic.
   - Fix now institutionalized: README + handoff carry the empirical-probe
     rule; friction/COE record the cost.

2. **Retry-without-diagnosis** (HIGH, 3 cycles)
   - cooperative_topk → persistent_topk → both disabled: three restart
     iterations on error TEXT without reading the deepest stack frame. The
     "Invalid Argument" was our own pynvml patch, not a kernel.
   - Fix: handoff rule #10 — read the innermost frame before iterating.

3. **Verification gap before expensive action** (HIGH, 2 instances)
   - 433 GB download started before validating the image's kernel support.
   - Bench ran against a stale tunnel (endpoint dead) producing 7 error-only
     artifacts. No preflight in `bench`.
   - Fixes: TODO items 3–5 in the COE (recipe script, bench preflight,
     arch smoke test pre-download).

4. **Tool blindness** (MEDIUM, 3 instances)
   - Local docker arch check (free, no GPU) discovered late.
   - Single-GPU probe pattern discovered late.
   - `model start` vs `up` tunnel semantics undocumented until they bit.

5. **Command repetition** (LOW)
   - Pod-state ssh probes repeated ~10× in near-identical form → candidate
     for `llmctl probe` subcommand.

6. **Edit hygiene** (LOW, 2 instances)
   - replaceAll with wrong indentation silently fixed 1 of 2 call sites.
   - `git add -A` swept the handoff artifact into a code commit.

## Tool opportunities

- `llmctl bench` preflight (reachable endpoint + non-null window) — HIGH.
- `scripts/apply_b300_tp2_patches.sh` (recipe is 8 hand-typed commands) — HIGH.
- `llmctl probe` (ssh + torch op + nvidia-smi in one call) — MEDIUM.
- `llmctl wait-for-stock --model X` (formalize the ad-hoc zsh loop) — MEDIUM.
- analyze-conversation opencode adapter (SQLite → normalized JSONL) — MEDIUM,
  filed as friction.

## Autonomy/interaction notes

- 6 user re-prompts: 2 direction changes (Qwen addition, 1x-vs-2x policy),
  2 process asks (poll cadence, retrospective), 2 status questions. No
  workflow-routing stalls. Polling cadence ask (20s cycles) is now standing.

## What went right (keep doing)

- Standing autonomous contract + Overwatch supervision from the first pod.
- Handoff-driven resume with validated facts before acting.
- Honest-failure documentation instead of silent substitution (DeepSeek OOM
  path, opencode 8k-window bound).
- Friction records filed in-the-moment (4) rather than at close.

## Recommendations (priority order)

1. HIGH — bench preflight + recipe script + pre-download arch smoke test
   (COE actions 3–5; all mechanical).
2. MEDIUM — `llmctl probe` / `wait-for-stock` subcommands.
3. MEDIUM — opencode adapter for analyze-conversation.
4. MEDIUM — upstream vllm sm_103 DSA issue (user decision).
5. LOW — commit hygiene: explicit paths over `git add -A`.
