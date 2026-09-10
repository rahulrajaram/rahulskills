---
name: code-review
description: Review source code or changes through the local codereview package, selecting only the perspectives and workflow stages needed. Use for code review, independent source assessment, or review packets; use check-antipatterns for agent-session execution.
metadata:
  short-description: Run selected independent code-review perspectives
---

# Intent and applicability

Use this skill for a read-only review of a repository or scoped change. Produce
controller-observed reviewer reports and, when all selected reports complete,
one aggregated packet. This skill routes review work; it does not patch the
target or run its tests.

# Inputs and local bindings

Resolve the package root from an explicit user or local configuration override
first; otherwise use `~/Documents/codereview`. The pipeline is
`<package-root>/review-pipeline`; its adapters require Python 3.11+, Git and
Linux. If that root is absent, report the missing
local capability and stop; do not download, install, or regenerate it.

Before preparing a run, bind:

- an absolute target repository path and explicit scope prefixes;
- a fresh absolute evidence directory outside the target;
- a concise review objective and the owner's authorization for the selected
  controller route;
- one or more unique perspective names selected for this review.

For a change review, retain the baseline and reviewed revision in the objective
and derive scope from the changed paths, including necessary callers. Do not
invent a `--baseline` flag for the native adapter; its CLI binds source and
scope, while the objective carries the comparison requested by the caller.

Read `<pipeline>/prompts/REVIEW-CONTRACT.md`,
`<pipeline>/prompts/REASONING-PROTOCOL.md`, and each selected
`<pipeline>/prompts/<perspective>.md`. These are the authoritative protocol,
reasoning method, and lens instructions. Load only the selected theme prompts.

# Non-goals and must-not

Review workers are read-only: they must not patch files, execute repository
programs or tests, install dependencies, access credentials, or perform
destructive operations. The parent/controller may separately verify an
authorized scope after review.

Do not silently commit, stash, clean, or otherwise alter user files. Require a
clean, committed source root (including untracked, staged, submodule, and
worktree state as checked by the pipeline); if it is dirty, do not silently review HEAD instead. For a review that must
include dirty work, use an exact isolated clean snapshot when existing authority
covers preparing local review artifacts; otherwise report that unmet binding.
Record the origin revision, included changes and exclusions, and snapshot
identity. Never commit or stash the original target to satisfy preparation; do not disguise a generic dirty-tree review as a
package execution. Preparation observes and binds the source identity; the
controller must preserve that same read-only source while workers run.

Always pass `--perspectives` explicitly to preparation and unbound-import
commands. Manifest-bound aggregation derives the exact selection from
`--manifest`; its CLI rejects combining that option with `--perspectives`. Never rely on `swarm_driver.py`'s thirteen-arm default, and never add
an advisory suggestion such as `cli-surface` automatically. Select only the
capabilities needed for the objective; optional lenses include
`boundary-contracts`, `resource-lifecycle`, and `cli-surface`.

# Interaction and authority

The controller owns provider execution, credentials, isolation, timeouts,
spend, and fresh worker/session identity. Use only a supported route and its
approved model. Reuse existing user/parent authorization; routine perspective
selection does not require another approval. A nonempty `--authorization` string
records that authority and does not create it. If a route is unavailable or
unapproved, report the exact boundary without substituting a provider. Native Codex currently admits exact `gpt-5.6-luna` with
`--reasoning low`; this low setting is required by the native adapter even if
the repository's general worker guidance says medium. The native adapter
records observations; it does not launch the native agent. Use the host's
native subagent tool (for example `collaboration.spawn_agent`), never a shell
`codex exec` or Claude CLI as a substitute. A delegated controller without that
tool returns the prepared manifest to its parent for dispatch under the same
authorization; it does not select another execution route. The opencode route
admits exact `zai-coding-plan/glm-5.3-flash` and requires the controller to run
one fresh `opencode run` session per perspective. Do not substitute providers,
models, or implicit defaults.

# Procedure

Select the operation before invoking tools. A focused source review uses the
smallest sufficient perspective set; name the objective and why each lens is
needed. Use the package registry or `review_doctor.py` to discover valid names
without loading every theme prompt. User-selected perspectives take precedence;
add a lens only for a concrete uncovered risk and explain the change. Examples:
`correctness` for behavior, `boundary-contracts` for producer/consumer invariants,
`resource-lifecycle` for ownership and termination, `test-tautologicalness` for
oracle independence, and `simplification` for capability-preserving reductions.
A general request is not permission to run all thirteen default perspectives.

- **New review:** choose an available, already-authorized controller route below.
- **Existing reports:** aggregate only the requested reports. With matching
  manifest and receipts, use the manifest-bound command below. Without execution
  provenance, run `distill_swarm.py --reviews-dir REPORTS --out NEW_PACKET
  --perspectives SELECTED_NAMES` and label the result an unbound import. Do not
  dispatch reviewers, invent receipts, or claim a fresh review for this mode.
  If the requested subset differs from a manifest's selection, explain that
  manifest-bound aggregation covers all its tasks; use an explicitly unbound
  subset only when acceptable to the caller. Never rewrite the manifest or
  silently broaden the requested subset.
- **Preparation only:** stop after preparing the selected manifest when requested;
  report dispatch-pending, not review completion.
- **Epoch gate:** use the final optional flow only when the caller requests it.
  Ordinary reviews do not select harness generation, worker retrospectives,
  harness self-improvement, or the full MetaBuilder lifecycle.


From the codereview package root, first inspect help or the package README if a
binding is unclear. For a native Codex review, use this sequence with fresh
absolute paths and the exact selected names:

```sh
python3 review-pipeline/scripts/native_codex_adapter.py prepare \
  --repo /absolute/clean/repo --prompts-dir review-pipeline/prompts \
  --out /absolute/new-evidence --perspectives <p1> <p2> \
  --scope <prefix1> <prefix2> --objective '...' \
  --model gpt-5.6-luna --reasoning low \
  --authorization 'owner authorization' --timeout-seconds 3600
python3 review-pipeline/scripts/native_codex_adapter.py dispatch \
  --manifest /absolute/new-evidence/manifest.json --perspective <p1> \
  --agent-id <controller-observed-fresh-agent-id> --out /absolute/new-evidence
python3 review-pipeline/scripts/native_codex_adapter.py complete \
  --manifest /absolute/new-evidence/manifest.json --perspective <p1> \
  --agent-id <same-agent-id> --terminal-status completed \
  --report /absolute/controller-captured-report.md --out /absolute/new-evidence
python3 review-pipeline/scripts/distill_swarm.py \
  --manifest /absolute/new-evidence/manifest.json \
  --reviews-dir /absolute/new-evidence --out /absolute/new-packet.md
```

After preparation, invoke the host's native agent tool with each exact
prepared prompt and the admitted model/effort, using a fresh context per
perspective. Record `dispatch` only after the tool returns its actual agent ID;
record `complete` only after its terminal report is observed and captured by the
controller outside the target. Serialize recording commands per evidence root;
reviewer work may run concurrently within the existing budget. Never synthesize
an agent ID or receipt from a proposed task name; workers must return the v2 report required by
the contract. A failed or incomplete terminal has no completion receipt and
cannot become a clean packet. Use a fresh evidence directory for retries.

For opencode, prepare with the same `--repo`, `--prompts-dir`, `--out`,
`--perspectives`, `--scope`, `--objective`, authorization, and timeout, plus:

```sh
python3 review-pipeline/scripts/opencode_adapter.py prepare \
  --repo /absolute/clean/repo --prompts-dir review-pipeline/prompts \
  --out /absolute/new-evidence --perspectives <p1> <p2> \
  --scope <prefix1> <prefix2> --objective '...' \
  --model zai-coding-plan/glm-5.3-flash \
  --authorization 'owner authorization' --timeout-seconds 3600
opencode run --model zai-coding-plan/glm-5.3-flash --format json \
  --title review-<p1> "$(cat /absolute/new-evidence/<p1>.prompt.md)" \
  > /absolute/new-evidence/<p1>.events.jsonl
python3 review-pipeline/scripts/opencode_adapter.py dispatch \
  --manifest /absolute/new-evidence/manifest.json --perspective <p1> \
  --session-id <controller-observed-session-id> --out /absolute/new-evidence
```

The controller extracts the final assistant report from the event stream, then
runs `opencode_adapter.py complete` with the same manifest, perspective,
session ID, `--terminal-status completed`, report path, and evidence output.
After every perspective completes, run `distill_swarm.py` as above. The
adapter binds event, source, prompt, report, and receipt digests; do not edit
those artifacts by hand.

If the requested workflow is an end-of-epoch gate for generated code, use the
optional `review-pipeline/scripts/epoch_review.py` flow: `init` with explicit
perspectives, scope, workers, authorization, objective, and epoch directory;
record each adapter dispatch/complete; aggregate to `<epoch-dir>/review/packet.md`;
then run the declared retrospective, decision, and `finalize` steps. Read the
package README's end-of-epoch section and the selected
`epoch_review.py <step> --help` before invoking this mode. The current epoch
initializer prepares the opencode route; do not relabel it as native Codex or
select it when that route lacks authorization.

# Completion and evidence

Report the selected perspectives, bound source HEAD/tree, controller route and
model, evidence/packet paths, and command exit results. A packet with missing,
failed, stale, or contract-invalid reports is incomplete; do not describe it as
a clean review. Structural aggregation does not prove finding truth,
coverage, worker independence, or provider attestation. Parent-side tests or
verification, when separately authorized, are distinct from worker review.
Before endorsing a finding, check its reachability and counterevidence. Keep
raw reports and receipts unchanged; record parent rejection or qualification
separately rather than rewriting a worker's report to manufacture agreement.

When a campaign requests learning ingestion, export the selected findings using
the shared [learning-record schema](../../references/learning-record.schema.json)
with report/source references. Preserve them as reviewer claims; the packet and
its receipts do not promote them into controller-observed correctness.
