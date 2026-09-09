# Local continuation qualification

Three finite MetaBuilder consumer epochs completed on source commit
`ab0c8569b9c15a9e0fc9263ebf270097a6760eb5`. Each executed exactly one
controller-observed action, passed 37 component tests, recorded both required
retrospectives, and produced a checked qualification report. All three reports
reconstructed byte-for-byte without redispatch.

The first epoch used the parent owner; the next two used fresh native Codex
contexts. The two-epoch scenario batch was consumed after epoch two. Its
already-approved renewal permitted a final batch of one, preserving total
consumption at two before the third action. Terminal validation then reported
`complete`, total consumption three, and no next action.

Exact action, output, report and journal identities are in the
[evidence summary](qualification/larger-move-2026-09-09.json). The
[contract guide](metabuilder-continuation-contracts.md) documents the maintained
CLIs, source binding and reproduction steps.

## What was verified

- Continuation binds source, controller identities, owner, grant, predecessor,
  budget and next action. Ten controlled negative checkpoint variants refused
  execution or reported terminal completion, with no dispatch.
- An actual proposed handoff with a future timestamp was rejected before the
  third epoch. The owner corrected its controller identities and predecessor
  using retained evidence. A malformed terminal summary was also replaced by
  a complete validated terminal state.
- An old checkpoint without a post-dispatch result produced `unknown`. Reading
  the completed third-run journal resolved it to `duplicate_replay`; its action
  count stayed one and its journal stayed unchanged. This was a controlled
  stale-owner scenario, not a fabricated controller Unknown event.
- The real selected recipe admits three typed edges and retains five inactive
  optional edges. Changed identities produce a review-required lock delta.
- Eight original learning records were ingested per epoch. Epochs one and two
  explicitly included their learning-document digests in recorded retrospectives;
  epoch three referenced the enclosing declared output.

The final source also passed 44 focused tests. Changes after the frozen live
checkpoint tightened malformed optional-field rejection and clarified the
schema and guidance; the valid-input execution path remained unchanged.

An independent acceptance review accepted all four deliverables within this
local, controller-backed scope.

## Evidence and limits

Run roots are retained under
`$HOME/.local/state/rahulskills/metabuilder/larger-move/`, with baseline runs
named `baseline-epoch-1` through `baseline-epoch-3`. The earlier `epoch-1` run
failed because the exported sandbox source had no Git metadata. That evidence
is retained separately; the correction binds the exact source commit before
compiling a module and executes from a clean checkout.

Local owner evidence, grants, rejected handoffs, attestations and reports are
retained in `.agent/larger-move/`. Controller command observations, native
session metadata and consumer semantic judgments remain distinct. Actor labels
are not authentication. The parent supervised the owner transfers and corrected
bad handoff artifacts; this evidence does not establish unassisted agent
execution, governed model dispatch, distributed ownership or a MetaBuilder
self-rebuild loop.

Optional preparation-role contracts, authenticated approvals, provider spending
controls and broader execution profiles remain separate backlog items. No
skills were installed or synced to OpenCode, and no branch was pushed.
