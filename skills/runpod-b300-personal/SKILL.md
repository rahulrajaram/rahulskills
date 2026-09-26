---
name: runpod-b300-personal
description: Launch or recover the personal Qwen A1 service on a RunPod B300, including pinned chat bootstrap, sandbox gateway readiness, and a short throughput baseline. Use for this personal deployment; not for generic RunPod workloads.
---

# Personal Qwen B300 launch

## Intent and bindings

Bring the user's personal A1 chat endpoint to verified use by agents, then
leave the pod running unless the user changes that instruction. Locate the
`runpod-server` and `llm-runpod` checkouts and read the current
`docs/qwen-b300-launch.md`, `scripts/gpu_pod_bootstrap.sh`,
`docs/qwen-personal-b300-live.md`, and hardware profile before acting. These
project files own exact revisions, image digest, flags, ports, and commands;
do not rely on stale values in this skill.

## Operational decisions

- Prefer **US-WA-2** for this personal pod. The single-B300 Qwen profile is
  pinned there. If it lacks B300 capacity, wait or report the blocker rather
  than silently choosing another GPU or region. EU-NL-1 slowness was observed
  once, but a regional speed difference was not proven.
- Use the approved A1/NVFP4 chat configuration and pod-local disk; no network
  volume is needed. Check the actual create specification for region, disk,
  volume, runtime/image, and pod count before creation. Do not assume
  `llmctl up --ttl` is equivalent: it can attach a named volume and start a
  teardown watchdog.
- Record each launch phase with a UTC timestamp and pod identity: create
  request, allocation, SSH mapping, pinned chat stage, chat ready, tunnel
  ready, sandbox gateway ready, and optional embedding ready. Diagnose a
  stalled phase using its receipt/log before retrying or creating another pod.
- Use the script's chat-only first pass (`CHAT_ONLY=1`) so optional embedding
  download/load does not hold up chat readiness. Authenticate against
  `/v1/models` and make a short streamed chat request. A PID, SSH mapping,
  or gateway `/healthz` alone is insufficient.
- Verify the `development` Chasm gateway from an agent terminal shell with
  authenticated `/readyz` and `/v1/models`. Check access from the relevant
  sandbox agent shell context, not just the host. Keep tokens in private
  configs; never copy them into source or reports.
- If embedding is requested, bootstrap and verify it separately after chat
  serves. If the loader stalls on FUSE again, keep chat available and report
  embedding as unqualified rather than tearing down the pod.
- For a new baseline, run bounded C1/C8/C64 workloads with recorded prompt,
  output, warmup, duration, and concurrent background load. Separate client
  aggregate delivered tok/s and TTFT from vLLM prefill and decode counters;
  do not call a client post-first-token proxy an engine decode rate.

## Authority and completion

Honor the user's current authorization for provisioning, spending, and
keep-running behavior. A benchmark ending does not authorize teardown. If
capacity or credentials block launch, report the exact phase and smallest
needed action. Completion requires a chat response through the sandbox
gateway from an agent shell, clear status of optional embedding, a bounded
baseline if requested, and a pod that remains available for agent work.
