# Local continuation and composition contracts

These repository tools make handoffs reviewable and reproducible. They use
Python 3.11's standard library and do not install skills, dispatch work, grant
effects, or replace MetaBuilder's controller. The campaign owner still decides
whether existing approval covers the next action and reconciles uncertain
attempts against the actual run journal.

## Continuation

`references/continuation-state.schema.json` binds the campaign, source commit,
owner, objective, run, module, bundle, policy, predecessor, grant, budget and
next action. Compute `state_id` as SHA256 of canonical JSON with `state_id`
omitted. Canonical JSON sorts keys, uses compact separators, preserves Unicode
and rejects nonfinite numbers. Identity-bearing timestamps stay in the digest.

```sh
python3 scripts/continuation_state.py \
  --state continuation-state.json --observation current-observation.json \
  --grant trusted-grant.json --as-of 2026-09-08T21:00:00Z
```

The caller obtains the grant independently from the trusted owner and obtains
observations from current source and controller inspection. Copying a proposed
state into those inputs cannot establish freshness or authority. The explicit
as-of timestamp makes expiry evaluation reproducible. The validator returns
eligibility or a refusal/reconciliation outcome and performs no dispatch or
file writes. A fresh owner repeats the check, preserves the approved policy,
and continues across checkpoints while work and authority remain.

Use the source checkpoint's actual controller `run_id`, canonical
`module_digest` and admitted `bundle_id`. Consumer logical run names and raw
file SHA256 values are different identities. The predecessor is the exact
previously consumed `state_id`. For this suite, the next action digest is the
raw SHA256 of the next bound module; verify it separately from the source
checkpoint identities. Read the clock for the as-of value. Never choose a
future timestamp to make a proposed handoff pass.

Batch consumption and total consumption are distinct. Renewal requires the
existing grant and its checkpoint evidence; it cannot reset total consumption.
Completion removes the next action. Interrupted, unknown, active or ambiguous
attempts require controller inspection before any retry. This is a
single-controller contract, not a distributed lease or actor authentication.

## Composition

```sh
python3 scripts/composition_lock.py create \
  --recipe capabilities/recipes/long-horizon-local.recipe.json \
  --catalog capabilities/skills.toml --contracts capabilities/contracts \
  --schema capabilities/contracts/skill-contract.schema.json --output current.lock.json
python3 scripts/composition_lock.py check --lock saved.lock.json --current current.lock.json
python3 scripts/composition_lock.py diff --lock saved.lock.json --current current.lock.json
```

The lock pins exact recipe, catalog, contract and schema bytes. Required roles
and selected optional roles must have typed boundaries. Unselected preparation
roles remain explicit inactive edges; selecting one requires supplying its
contract. Port schemas, cardinalities and epistemic classes must agree. A
routing diagnostic does not become a human objective or approval. Explicit
bounded lifecycle backedges preserve the qualification-to-design loop.

Recreate from the current files before checking a retained lock. Identity
changes require review, including effect, authority, confinement, resource,
recovery and output-meaning changes. Schema equality proves only declared
shape identity; the tools do not infer semantic equivalence or perform an
automatic migration.

## Learning and qualification

```sh
python3 scripts/learning_ingest.py --records learning-records.json --context context.json
```

Context contains `campaign_id`, positive `epoch`, `run_id`, exact
`source_commit` and SHA256 `policy_digest`. Records follow the existing
`references/learning-record.schema.json`; the whole selected batch either
passes or returns diagnostics. Repeated records deduplicate deterministically.
`--previous` merges only a verified ingestion document for the exact same
context. Original findings and references remain claims, including any source
disposition labels. Ingestion never performs their proposed actions.

The qualification owner retains the accepted document and cites its digest,
findings and original references in an actual MetaBuilder retrospective
answer before recording it. `tests/larger_move_qualification.py` produces a
declared consumer report for each module in
`harnesses/metabuilder/larger-move/`. The command requires explicit campaign,
logical-run, policy and source-commit bindings. The sandbox exports tracked
source without Git metadata, so the owner binds each module after committing:

```sh
python3 scripts/bind_qualification_source.py \
  --template harnesses/metabuilder/larger-move/epoch-1.module.json \
  --source-commit EXACT_COMMIT --output /tmp/epoch-1.bound.module.json
metabuilder harness compile --input /tmp/epoch-1.bound.module.json
```

Replace `EXACT_COMMIT` with the full verified commit used by `harness author`.
Retain the rendered module and bundle outside the target checkout; re-admit
the bundle and compare its source argument to the authored revision before
apply. The template marker is deliberately invalid as a commit identity, and
rebinding an already bound module is refused. The logical run label is bound separately to
the observed controller run identity in the owner's report.

The frozen trace fixture is an expected result, not evidence that an epoch ran.
Full qualification additionally needs three separate controller runs, two
fresh owner resumptions, actual renewal/refusal observations, retained journals
and checked attestations. Unit-test success alone cannot establish that result.
