## Pi model routing

- Use `llmctl-gateway/Qwen/Qwen3.8-27B` by default. It is served from a
  self-hosted B300 through the guest's loopback gateway; the B300 may be off or
  disconnected. A healthy `/healthz` proves only that the local gateway runs.
- When Qwen inference is unavailable after a bounded readiness check or retry,
  use `zai/glm-5.3` through the Z.ai **Coding Plan** subscription for coding
  work. This fallback is authorized by the sandbox owner. Use the Coding Plan
  endpoint and credential, not a direct-pay Z.ai route or OpenRouter. Note the
  fallback in the task report.
- If the Coding Plan credential or route is not installed, report that exact
  prerequisite gap and continue independent work. Never print, commit, or
  transmit the credential through `/shared`.
