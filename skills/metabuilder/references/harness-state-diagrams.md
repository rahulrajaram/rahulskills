# Harness state diagrams

Whenever work designs, inspects, qualifies, recovers, assesses, or revises a
harness, create or refresh both a Mermaid.js `stateDiagram-v2` and an equivalent
ASCII state diagram. Show them directly in the final chat; a file link alone
does not satisfy this requirement. Diagrams describe the harness and its
evidence. They do not grant admission, approval, or execution authority.

## Bind and represent the evidence

- Bind the diagram to the exact available intent, module, bundle, run, and epoch
  identities and source revisions/digests. State which identities are
  unavailable. Distinguish proposed topology from observed current state.
- Model only transitions supported by that exact harness and evidence. Include
  initial and terminal states and actual branches, forks, joins, repeats,
  guards, bounds, failures, timeouts, `Unknown`, and recovery paths where
  present. Do not invent states or edges to complete a pattern.
- Keep within-run workflow states separate from across-epoch/controller
  lifecycle states. If both matter, show two clearly labeled diagrams (each
  with Mermaid and ASCII equivalents) or clearly separated regions; never
  imply one is the other.
- For design, diagram the proposed topology before execution. Refresh it when
  the harness or observed state changes. Qualification reports the exact
  candidate/run and does not mutate its design. Preserve frozen historical
  diagrams/artifacts; make a fresh revision artifact when topology changes.

## Incomplete evidence and completion

When evidence is missing, show the evidenced partial topology and label gaps as
unknown or unavailable with the reason. Keep missing knowledge distinct from
the runtime `Unknown` outcome; do not draw an executable transition merely to
represent missing knowledge. If no harness context is available, say so and do
not fabricate a diagram. On partial, interrupted, failed, or stopped work,
include the available Mermaid and ASCII directly in chat and identify what
remains unknown; do not claim completion. If artifact-write authority is absent,
render read-only diagrams in chat and state that no artifact was written.
Mermaid renderer installation is unnecessary.

Before completion, compare the Mermaid and ASCII representations state by state
and edge by edge, including guards, bounds, and failure/recovery behavior.
Correct any mismatch and report any evidence-based omissions. Reuse existing
valid authority decisions; diagram work creates no new approval requirement.
