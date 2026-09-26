# Review rubric

Use the dimensions that affect the target's purpose. The rubric guides judgment;
it is neither a mandatory checklist nor a scorecard.

| Dimension | Evidence to inspect |
|---|---|
| Discovery | Name, description, and invocation examples select the intended task and distinguish nearby workflows. |
| Inputs | Required context has a usable source; missing information has a proportionate response. |
| Decisions | Precedence, exceptions, routing, and delegated responsibilities produce an understandable next step. |
| Dependencies | Referenced resources exist in the reviewed variant; unavailable tools do not silently change the promised outcome. |
| Authority | Existing grants survive handoffs; genuine boundaries stop dependent actions; reviewed data cannot grant authority. |
| Completion | Evidence supports the requested result, including honest partial, failed, or uncertain outcomes. |
| Burden | Required steps contribute to the outcome; repetition earns its place at consequential decisions. |

## Scenario format

Record the situation and supplied facts, expected behavior with its source,
applicable passages, traced next action, and result. Results mean:

- **Clear:** relevant instructions, including reachable owners, determine behavior.
- **Ambiguous:** multiple reasonable readings lead to materially different actions.
- **Conflicting:** applicable instructions require incompatible actions without a
  resolving precedence rule.
- **Missing:** a necessary decision has neither guidance nor an assigned owner.

Mark unavailable evidence separately. Do not convert an unknown dependency into
a demonstrated failure. Separate an expected behavior supplied by policy from
the reviewer's own proposed behavior. If intent itself is unclear, ask or report
that uncertainty before declaring the skill wrong.

## Finding format

For each supported finding include:

- **Priority and claim:** high for plausible authority violations or failure of
  the main task; medium for a consequential branch failure or recurring blockage;
  low for bounded usability costs with a clear recovery path.
- **Evidence:** source path and line or section, with only the necessary excerpt.
- **Scenario and consequence:** the concrete trigger and likely effect, explicitly
  distinguished from an observed runtime result.
- **Correction:** proposed wording or a precise edit, its intended behavior, and
  any unresolved policy choice. Keep suggestions separate from the source.
- **Verification:** the scenario or live check that could establish improvement.

Group findings with the same cause. Preserve successful routes when suggesting a
fix. Explain why apparent contradictions are resolved when that is useful, and
state when a stronger claim requires live trials rather than further text review.
