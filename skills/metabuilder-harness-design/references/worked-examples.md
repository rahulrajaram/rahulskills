# Worked mappings

These examples use source programs already exercised by MetaBuilder's public
CLI and product tests. They show how discovered domain facts become an agreed
brief and then an authority-free intent program. The later Harness Module adds
the executable commitments; the final consumer assessment remains separate.

## Small: one delivery and one assurance

Source: `crates/mb-core/tests/fixtures/intents/hello_world.mb.ts`.

Domain facts:

- The consumer wants one runnable greeting implementation.
- Completion means independently observing the exact expected greeting.
- The brief does not authorize a language, command, toolchain, or filesystem
  write merely because those will eventually be needed.

Mapping:

| Brief statement | Program commitment |
| --- | --- |
| Produce a runnable greeting | `achieve` obligation with id `app` |
| Prove the exact greeting is emitted | `establish` obligation with id `hello-output` |
| Finish only after that proof | `established("hello-output")` |

The Harness Module may later bind the delivery and check to direct commands.
A successful `intent check` proves only that the meaning is well-formed and
authority-free. A successful run records the command outcome; the consumer
still judges whether the check establishes the intended greeting behavior.

Validate:

```bash
metabuilder intent check \
  --input crates/mb-core/tests/fixtures/intents/hello_world.mb.ts --json
```

## Medium: exact artifacts through a sequential pipeline

Source: `crates/mb-core/tests/fixtures/intents/typed_artifact_pipeline.mb.ts`.

Domain facts:

- A candidate JSON artifact must be created before a bundle can consume it.
- The bundle must remain the exact subject of an independent verification.
- Canonical bytes, media types, and size ceilings matter across steps.

Mapping:

| Brief statement | Program commitment |
| --- | --- |
| Candidate, bundle, and verification are durable evidence objects | Three typed `artifact` declarations |
| Packaging depends on the exact candidate | Sequential `produces`/`consumes` edge |
| Verification depends on the exact bundle | Final `establish` consuming `bundle` |
| No later step may run early | `sequence` around all three obligations |

The module must implement each artifact as a declared file with a byte bound;
stdout is only a diagnostic. Compiler and run digests support exact identity
and replay claims, not the semantic claim that the verifier is adequate.

Validate:

```bash
metabuilder intent check \
  --input crates/mb-core/tests/fixtures/intents/typed_artifact_pipeline.mb.ts \
  --json
```

## Complex: staged parallel production, synthesis, and verification

Source: `crates/mb-core/tests/fixtures/intents/parallel_agent_synthesis.mb.ts`.

Domain facts:

- Two analyses must be produced independently.
- Synthesis can start only after both exact analysis artifacts exist.
- One named synthesis obligation coordinates that stage.
- An independent assurance checks the exact synthesis and emits separate
  verification evidence.

Mapping:

| Brief statement | Program commitment |
| --- | --- |
| Production, synthesis, and verification are separately reviewable phases | Root `stages` |
| Analyses cannot depend on each other | Named `parallel` arms |
| Synthesis requires both exact inputs | One `achieve` consuming both analysis artifacts |
| Synthesis coordinates its stage | Stage-local `orchestrator` identity |
| Assurance distinguishes subject from evidence | `verification { subject, evidence }` |
| Completion requires independent assurance | `established("verify-synthesis")` |

Generation may choose command, agent, MCP, or mixed adapters only after those
commitments are exposed for semantic approval and admitted by the relevant
controller boundary. An agent response is not execution evidence. A receipt
binds the selected bytes and observations but does not prove reviewer identity,
provider honesty, or production readiness.

Validate:

```bash
metabuilder intent check \
  --input crates/mb-core/tests/fixtures/intents/parallel_agent_synthesis.mb.ts \
  --json
```

## Complexity rule

Use the smallest topology that preserves the approved dependencies. Do not add
parallelism, stages, waits, cases, or repeats because the task sounds complex.
Add them only when the domain facts require independent work, reviewable phase
boundaries, controller decisions, observed gates, or bounded convergence.
