---
name: metabuilder-consumer-qualification
description: Run and assess an already designed Linux-local consumer harness with MetaBuilder while keeping controller evidence separate from consumer semantic judgment. Use after harness design when a target project is testing whether the resulting harness is suitable.
---

# MetaBuilder consumer qualification

Use the target's own instructions, source, and tests to execute an already
agreed Harness Module through MetaBuilder and produce an exact qualification
report. Initial repository discovery, task grilling, brief agreement, and
intent/program design belong to the upstream `metabuilder-harness-design`
skill. Do not silently reconstruct or change those decisions during
qualification; route design gaps back upstream.

This skill is guidance only. Rust admission, the compiled bundle, and the run
journal remain authority.

When this repository-local skill is unavailable, emit the same installed guide
with `metabuilder qualify guide`.

Use the installed `metabuilder` CLI for every governed operation. MetaBuilder
does not currently expose an MCP server, and this qualification does not
require one. Do not substitute an uncommitted development binary for the
installed consumer build unless the MetaBuilder maintainer has explicitly
admitted and identified those exact bytes.

## Entry and authority

Select inspection or execution from the user's request. An inspection request
permits relevant reads and assessment of existing artifacts; it does not select
a fresh run. Reuse the handed-off executable identity, help/guide evidence,
exact agreed brief, approvals, and grants when still valid. Recheck changed
inputs or constraints, and preserve named-owner ratification for any changed
formal design. Do not repeat a settled interview or approval merely because
qualification is a separate skill.

Before run authoring or effect application, verify that existing authority
covers the concrete artifacts, run root, processes, bounds, and effects. Brief
acceptance and a valid bundle establish design/admission facts, not these
execution grants. If a grant or consequential decision is missing, prepare the
concrete request and continue independent inspection; hold the dependent action.
A model's assessment or a passing report cannot supply human ratification.

## Contract boundary

- The Harness Module is the exact consumer config from the design handoff. Do
  not invent a second workflow or claims format. If no agreed module exists,
  stop and return to `metabuilder-harness-design`; the emitted module template
  is a design aid, not authority to fill product gaps during qualification.
- A requirement is the consumer's semantic claim. Its `acceptance` entries
  explain the intended meaning, and `evidence_actions` name the
  consumer-selected executable checks.
- Confirm that every claimed automated consumer test is a direct command
  action cited by the requirements it supports, with an exact toolchain and
  timeout. Report a design gap instead of adding a new check during
  qualification. Never hide execution in prose.
- Record manual review, external test artifacts, limitations, and untested
  conditions in consumer attestations after the run.
- Every module normalizes a required objective-bound epoch retrospective. A
  consumer may declare logical workers under `retrospectives.workers`, mapping
  each worker ID and intent to one or more reachable action IDs. The compiler
  alone creates digest-bound worker stages after each successful mapped action
  occurrence (including repeats), and an epoch stage after one successful root
  workflow incarnation. Failures, timeouts, and `Unknown` preserve existing
  semantics and do not trigger a failed-attempt retrospective. Only referenced
  built-in templates are embedded.

The v1 qualification profile is intentionally narrow: the current Linux host,
local sandboxed commands, read-only target source, no credentials, no network,
no external-state or target-source writes, no telemetry, and consumer-owned
artifacts. Authored commands may additionally use exact digest-bound sealed
snapshots of bounded repository-local auxiliary directories. MetaBuilder does
not establish production readiness. Stop and report an unsupported capability
when the target requires a broader effect; do not bypass the harness and call
the result governed.

Current toolchain admission supports absolute System executables under `/usr`
or `/bin` and bare Rustup executable names backed by explicit Rustup authority.
Arbitrary host executables and arbitrary host paths are not supported
resources. An authored command may declare `auxiliary_directories` only as
normalized paths below the already-bound target repository. Use
`metabuilder harness auxiliary-directory digest --repo PATH --path REL --json`
to obtain the exact declaration digest. Author and apply reobserve it; the
runtime copies the tree into private staging and mounts only that copy
read-only. This is not dependency installation or a live host bind, and fresh
untrusted generation cannot select it.

Static nested workflows are supported within one bundle through typed nested
nodes, acyclic `WorkflowRef` values, and bounded `RepeatUntil` nodes. Do not
describe this as dynamic child-harness execution: MetaBuilder does not yet
start a separate child harness with an independently governed run and journal.

Do not use `metabuilder maintain candidate ...` or
`metabuilder maintain improvement ...` for consumer qualification. Those are
internal maintainer workflows for proposing, reviewing, and integrating
changes to MetaBuilder itself. The bounded self-improvement campaign consumes
already-produced candidate, review, host-gate, retrospective, and integration
evidence; it neither dispatches workers nor integrates source. Neither command
family grants authority for target writes, consumer host execution,
unattended consumer looping, or production readiness.

Retrospective records are required, journaled interventions. They do not prove
outcomes, authorize effects, or decide continuation. Inspect the replay
projection, scaffold the exact pending intervention, save and edit that
complete object (not its nested `record` alone), then submit it:

```bash
metabuilder run retrospectives --run-root RUN --json
metabuilder run retrospectives scaffold \
  --run-root RUN --json
metabuilder run retrospectives record \
  --run-root RUN \
  --input retrospective-record.json --json
```

`scaffold` is canonical and read-only and exits 2 when no retrospective is
pending. `record` accepts only a complete `retrospective_recorded` intervention
and uses the existing workflow reducer, so selector, current-head, and replay
checks remain in force under the single-controller run-store contract.
Do not run concurrent controller writers against the same run root.

Operating notes verified in a real governed campaign:

- Every worker action is followed by a `retrospective_required` blocker that
  makes the workflow idle until its retrospective is recorded; the epoch
  retrospective is the last one. `record.actor_id` must be a valid tranche id
  (lowercase-hyphen slug such as `gptqueue-controller`); an empty string fails
  with "invalid retrospective id: invalid tranche identifier".
- Author runs with the run root OUTSIDE the target repository. The run's own
  journal dirties the worktree and `harness author` refuses a dirty tree.
- Attestation verdicts are `meets` / `does_not_meet` / `uncertain`, and each
  `consumer_evidence[].digest` must be a real SHA-256 digest (journaled action
  evidence digests are the natural choice).
- Bundle-backed runs need `--bundle BUNDLE` on `run workflow apply`.
- A finished consumer run rests at campaign state `awaiting_assessment` with
  the workflow selection `status: "complete"`; that is the normal resting
  state, not an error.
- Recompute every auxiliary-directory digest with the current binary
  immediately before authoring; `node_modules` drifts silently. An auxiliary
  directory may not overlap committed source.

Here “epoch” means one root-workflow incarnation; autonomous multi-epoch
self-rebuild remains deferred.

## Declared file outputs

Commands write canonical declared files only below `$METABUILDER_OUTPUT_DIR`
(mounted as `/outputs`); the target source workspace remains read-only. Declare
each normalized output path and byte bound in the action. MetaBuilder validates,
hashes, persists, and journals declared files. Standard output and standard
error are diagnostics, not canonical typed step inputs. A nonempty stream is
returned by `run workflow apply --json` as an optional bounded,
content-addressed `stdout_diagnostic` or `stderr_diagnostic` artifact; it does
not satisfy a declared output or worker-evidence requirement.

## Assess check adequacy

Read the target repository's authority and ordinary development workflow
and compare them with the handed-off module. Do not edit the module during
qualification. Assess the target-specific risks first, then check the relevant
usual suspects:

- build, test, lint, typecheck, and package integrity;
- negative and malformed-input behavior;
- interruption, recovery, replay, and retry behavior where state persists;
- declared-file output contracts and evidence tamper refusal;
- source immutability and sandbox confinement;
- declared auxiliary-directory visibility, digest mismatch refusal, and
  read-only enforcement when ignored or untracked dependencies are required;
- exact required toolchains and current-host assumptions;
- target-specific invariants that generic test suites may miss.

Passing commands show only that the declared checks produced the recorded
outcomes. Decide separately whether those checks are semantically adequate for
the target.

## Run the qualification

For an execution request with the required grants, use the installed binary.
Reuse an unchanged admitted bundle from the handoff; compile/check below only
when that evidence needs establishing or refreshing. Reuse current CLI/guide
verification rather than rerunning it solely for the phase change:

```bash
command -v metabuilder
metabuilder --help
metabuilder qualify guide
RUN_ROOT=/absolute/path/outside/the/repository/consumer-run
metabuilder harness compile \
  --input metabuilder.consumer.json > metabuilder.bundle.json
metabuilder harness check --input metabuilder.bundle.json
# Run root OUTSIDE the repository: the run journal would dirty the worktree
# and authoring requires a clean tree.
metabuilder harness author \
  --bundle metabuilder.bundle.json \
  --run-root "$RUN_ROOT" \
  --repo . \
  --harness-repo <clean-repository-containing-the-module> \
  --json
metabuilder run workflow preview \
  --run-root "$RUN_ROOT" --json
metabuilder run workflow effects \
  --run-root "$RUN_ROOT" \
  --bundle metabuilder.bundle.json --json
metabuilder run workflow apply \
  --run-root "$RUN_ROOT" \
  --bundle metabuilder.bundle.json \
  --workspace . --json
```

Repeat preview/apply only as permitted by the workflow state. After an
interrupted prepared or observed attempt, recover without redispatch. Never
blindly retry `Unknown`. If an authorized actor explicitly resolves `Unknown`,
the report records `action_resolved_after_unknown`; it never upgrades that
resolution to controller-observed success.

When a bounded repeat reaches its condition checkpoint, copy the exact node ID
and iteration from `run workflow preview --json` into an input file such as:

```json
{
  "kind": "repeat_observed",
  "node_id": "main.s0",
  "iteration": 0,
  "satisfied": false
}
```

Then apply the typed fact; repeat this only for the currently exposed
iteration:

```bash
metabuilder run workflow intervene \
  --run-root "$RUN_ROOT" \
  --input repeat-observed.json --json
```

Prepare the exact attestation subject after the run reaches the boundary being
assessed:

```bash
metabuilder qualify prepare \
  --bundle metabuilder.bundle.json \
  --run-root "$RUN_ROOT" \
  > metabuilder.qualification-preparation.json
```

Emit the attestation template, then copy the preparation's
`subject.subject_digest` into every requirement entry:

```bash
metabuilder qualify template \
  --kind attestations > metabuilder.attestations.json
```

Replace every `replace-me` value. Supply one attestation for every Harness Module
requirement. Use `meets`, `does_not_meet`, or `uncertain`; include an honest
rationale, limitations, untested conditions, and digests of consumer-owned
evidence. Actor labels are content-bound but unauthenticated.

Create and verify the MetaBuilder-owned report:

```bash
metabuilder qualify report \
  --bundle metabuilder.bundle.json \
  --run-root "$RUN_ROOT" \
  --attestations metabuilder.attestations.json \
  > metabuilder.report.json
metabuilder qualify check \
  --bundle metabuilder.bundle.json \
  --run-root "$RUN_ROOT" \
  --attestations metabuilder.attestations.json \
  --input metabuilder.report.json
```

If the run advances after preparation, regenerate the preparation and reassess;
stale attestations are refused. Exit zero from report construction means the
record was constructed, not that the product passed or is production-ready.
The subject binds the package version and digest of the MetaBuilder executable
that reconstructed the report. This identifies the reporter; it does not claim
that every earlier run command used those same executable bytes.

## Report back to MetaBuilder

Preserve `metabuilder.report.json` as the consumer's feedback artifact. Report
which requirements were useful, which checks were missing or awkward to
express, which effects were unsupported, and whether the harness changed the
consumer's semantic verdict. MetaBuilder owns structural traceability and
controller observations; the consumer owns test adequacy and product meaning.
Return the exact report and attestations through the agreed coordination
channel. Keep the artifacts in the consumer repository or discard them under
the consumer's own retention policy after the handoff; MetaBuilder does not
claim ownership of the target's retained harness artifacts.
