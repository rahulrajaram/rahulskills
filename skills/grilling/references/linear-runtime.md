# Explicit bounded linear runtime profile

Use only when the user or authorized parent selects `linear-runtime` / the
`gptengage grill` execution profile. Do not silently map native `spec`, `factory`,
`debate`, or `gradient` onto it. This profile mechanically sequences a griller
and respondent; it does not reproduce the native graph or specialist topology.

## Bind the actual binary and effects

Read the shared
[`../../../references/gptengage-invocation.md`](../../../references/gptengage-invocation.md)
contract for outbound data, backend/model selection, access and persistence.
Resolve the actual approved executable and inspect its `grill --help` before
launch. The local `gptengage` source tree implements this
command, but source presence and successful source checks do not establish that
the installed `~/.local/bin/gptengage` exposes it. Conversely, an installed
binary must be checked rather than inferred from the source tree. Do not
rebuild, install, switch paths or substitute a profile without the applicable
authorization; reuse exact authorized source-binary use when it is already
present in context.

Bind both backends/models, complete topic, role-instruction files, exchange and
per-call timeout limits, and a new private run directory whose parent exists.
All topic/instruction/dialogue data is outbound to the applicable backends.
History shares prior successful dialogue with the next role; it excludes the
other role's instruction field and process diagnostics, but model text may echo
private input. Review data authority for that full route, not just the first
prompt. The two roles may select the same backend deliberately; never silently
substitute another model or provider.

The command creates a private run directory and immutable checkpoint files.
That persistence must be within the selected scope. It does not use a named
session or grant workspace-write authority to either backend. Read-only access
is requested; consult actual access observations rather than claiming it is
enforced. No `--write`, automatic resume or replay option exists in this slice.
The checkpoint schema version identifies the file format only; it is not proof
of native graph reconstruction, replay, or resumability.

## Invocation

Use an argument vector with actual supported flags. The current source contract
is:

```text
gptengage grill TOPIC
  --griller BACKEND --respondent BACKEND
  --griller-instructions FILE --respondent-instructions FILE
  --run-dir NEW_DIRECTORY
  [--griller-model MODEL] [--respondent-model MODEL]
  [--exchanges N] [--timeout SECONDS] [--show-dialogue]
```

The defaults are 3 exchanges and 120 seconds per direct call. Counts/timeouts
must be positive. At most `2 * exchanges` direct calls run, alternating griller
then respondent. This is not a token budget or a bound on provider-internal
research/tool calls. Very large topic/history arguments may exceed the actual
transport limits; diagnose and preserve full input instead of silently
summarizing it. If the selected runtime cannot carry the complete context,
report the limitation and use an explicitly authorized compatible transport or
profile. Do not claim a missing stdin/file flag exists.

Prepare role instructions from the requested topic and this skill's roles:
the griller asks genuine questions only; the respondent distinguishes evidence,
inference, bets, unknowns and what would change the answer. Instruct responses
to use plain prose. The code supplies turn mechanics, not a hardcoded theory of
good questions. No per-turn semantic validator or specialist dispatcher is
implemented here. In particular, the next role may receive a mechanically
successful but malformed model answer; do not describe these calls as the native
validated-frontier workflow.

Both participants' locally detectable model-option restrictions are checked
before any call. Backend authentication, actual provider model identity and
provider-side support still require observed reports and may fail at invocation.
A failed griller prevents its respondent call. Any invocation or persistence
failure stops the run. Each private checkpoint records the current state before
a call and its typed report afterward; an in-flight checkpoint after interruption
means the outcome is unknown. Never automatically resume/replay/retry it.

## Review, output and close

Default stdout reports status/counts and artifact paths, without raw prompts,
instructions or diagnostics. `--show-dialogue` explicitly includes intended
successful model questions/answers. Its structural projection excludes separate
control fields and diagnostics; it is not semantic redaction and cannot prevent
model-authored echo. The host should inspect the private dialogue before
presenting a skill-compliant human review; do not stream raw output directly
as if its question-only and evidence contracts had already passed.

Treat reaching the exchange limit as mechanical completion, not resolution of
the inquiry or user ratification. Preserve failed/partial/unknown outcomes and
unresolved evidence. The host owns evidence review, question quality, minority
findings and the advisory final recommendation. Apply the native closing
contract in [linear-speculative.md](linear-speculative.md): perform a bounded
internal debate when materially different positions remain, or explain why
none remains. That debate is separate host work, not an undocumented extra
phase implemented by `grill`. A full implementation handoff is included only
when that planning scope was selected.

Native graph revisions, invalidation, deterministic lattice merges, wave
scheduling, resumption, replay, nested-token enforcement and formal user
ratification are not implemented by this command. Do not infer those guarantees
from the separate checkpoint schema version or its ordered files.
