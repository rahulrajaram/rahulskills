# Shared Yarli primitives

Resolve `SKILLS_ROOT` to the active runtime's installed skills directory (for
example `~/.agents/skills`) and use these primitives instead of reimplementing
policy:

- Read-only diagnosis:
  `$SKILLS_ROOT/yarli-introspect/scripts/introspect.sh <project-root>`.
- Supervisor-only continuation drift:
  `$SKILLS_ROOT/yarli-execution-loop/scripts/yarli-loop-inspect.sh <project-root>`.
- Idempotent enqueue:
  `$SKILLS_ROOT/yarli-execution-loop/scripts/yarli-enqueue-tranche.sh ...`.

Inspection never authorizes mutation. Before enqueueing, preview the key,
summary, allowed paths, verification, completion evidence, and token budget; the
caller must already have explicit enqueue intent. A key collision with divergent
fields is an error, never an implicit update.

Cancellation, repair, launch, and relaunch retain the separate approval
boundaries in `yarli-execution-loop`.
