# Skill Contract Registry

Phase 0 of the composition rollout from
[`docs/skill-composition-audit.md`](../../docs/skill-composition-audit.md).

- [`skill-contract.schema.json`](skill-contract.schema.json) is the canonical
  contract shape. `work-intake.contract.json` is the worked example; read it
  before authoring a new contract. Do not copy digest placeholders — compute
  the real `guidance_digest` (SHA-256 of the owning `SKILL.md`); the
  composition linter fails a stale digest.
- A contract covers one phase-sized unit: one meaningful result, one effect
  and authority envelope, one retry/recovery policy. A whole skill is one
  unit only when it truly has that shape.
- `authority.attenuate_only` is an invariant: composition may only attenuate
  the ratified envelope. Widening effect, authority, confinement, resource,
  recovery, or output meaning is a breaking change requiring human
  ratification even when data schemas stay compatible.
- Recipes live in [`../recipes/`](../recipes/) and resolve required roles
  against this catalog. The metabuilder `harness compose` interface remains
  conceptual: recipes are repository-owned artifacts today, and any CLI
  binding goes through the improve-through-use path, not assumed features.

## Verification

`scripts/lint_skill_composition.py` (invoked by `audit-skills.sh check`)
validates: schema conformance of every contract, guidance digest freshness,
recipe role resolution, edge port matching against contract inputs/outputs,
catalog overlap symmetry, and `overlap_kind` presence wherever `overlaps`
is declared.
