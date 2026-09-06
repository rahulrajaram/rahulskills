# Live code-review contract

Use this contract for the read-only code phase of `check-antipatterns`.

## Reviewer stance and scope

Act as a reviewer, not as the author while this phase runs. If you wrote the
change being reviewed, disclose that the pass is self-review rather than
independent review. Do not edit files during the pass.

Treat a diff as a focus hint, not the complete program. Read the changed code,
the nearest callers and sibling implementations, relevant configuration, and
tests that claim to cover the behavior. For a user-supplied path, review the
smallest complete package or component containing that path. Never infer a code
target when the repository is clean and none was supplied.

Do not repeat mechanical lint, line-length, TODO, or complexity-threshold output
unless it exposes a deeper defect. Review behavior that requires reasoning.

## Review lenses

Apply the lenses that are relevant to the change:

1. **Intent alignment** — trace important behavior from entry point to output
   and verify it serves the stated request without unauthorized scope.
2. **Correctness** — inspect invariants, boundaries, malformed and empty input,
   state transitions, error paths, concurrency, and partial failure.
3. **Safety and security** — inspect trust boundaries, injection, traversal,
   credentials, unsafe deserialization, privilege, and destructive operations.
   For deletion, a non-empty variable guard is not proof: resolve the target,
   prove exact identity and containment, reject roots and unexpected symlinks,
   and prefer a recoverable move or backup.
4. **Test quality** — distinguish missing coverage from tautological tests.
   Ask which realistic mutation or defect would still pass the current test.
5. **Proximity consistency** — compare validation, defaults, error shapes,
   lifecycle, serialization, and naming with nearby code and callers.
6. **Idiomaticity and cleanliness** — flag accidental duplication, dead paths,
   misleading comments, needless indirection, or non-idiomatic APIs only when
   they create a concrete maintenance or correctness cost.
7. **Complexity and data flow** — identify branch clusters, hidden temporal
   coupling, avoidable mutation, implicit state machines, and unsuitable data
   structures. Respect deliberate imperative I/O boundaries.

Actively check for recurring semantic defects that shallow scanners miss:

- meaningful zero values replaced by defaults through falsy coercion;
- behavior selected by matching formatted exception strings;
- domain values fabricated outside the documented vocabulary;
- hard slices that discard overflow without a cursor or truncation signal;
- unguarded numeric coercion of parsed or untrusted data;
- production-dead helpers kept alive only by tests;
- duplicated construction whose branches have drifted semantically;
- protocol or version literals that bypass an authoritative constant; and
- duplicate serialization or digest logic that can diverge across modules.

Use an already-present source index when it provides trustworthy call-site
evidence. If no index exists, follow imports and call sites directly and state
that limitation only when it materially lowers confidence. Do not install,
build, or activate an index as part of this check.

## Finding contract

Every finding must contain:

- `file:line` or the narrowest available symbol;
- severity: critical, high, medium, or low;
- the applicable review lens;
- the concrete defect and a minimal failure scenario;
- expected versus observed behavior;
- a focused remediation or test; and
- exactly one miss-cause tag:
  - `static_ceiling` — semantic or runtime reasoning is required;
  - `lens_gap` — a useful static signal could be added to the checker;
  - `threshold_too_high` — an existing signal saw the site but filtered it;
  - `noise_threshold` — latent or low-impact unless combined with other facts.

Do not manufacture consensus or confidence. Separate observation from
assumption, never expose a discovered secret, and say explicitly when no
supported finding remains after reviewing the evidence.
