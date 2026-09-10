---
name: metabuilder-harness-improvement
description: Improve an already qualified MetaBuilder harness from concrete consumer shortfalls while preserving the exact objective, prior qualification evidence, and gap lineage. Use for `$metabuilder repair existing harness`; do not use for fresh design or first qualification.
---

# MetaBuilder harness improvement

Use this package adapter when an existing harness has an exact agreed brief,
bundle, run, and qualification report, and the consumer wants a bounded repair
and matched requalification. The exact objective remains the complete agreed
brief identity. Preserve the prior qualification evidence and distinguish
per-run source facts from the enduring objective.

## Bind the authoritative workflow

Resolve the MetaBuilder package root from the user's explicit path or config;
when none is supplied, use `~/Documents/metabuilder`. Do not clone, install,
activate, or substitute another checkout. Read the authoritative local skill
at:

`<package-root>/.agents/skills/metabuilder-harness-improvement/SKILL.md`

Read its linked iteration guide when classifying the shortfall or explaining
the revision. Execute only the permitted, currently supported CLI workflow
specified by that skill. Inspect current CLI help/source before using any
operation whose availability matters. Resolve the retrospective schema from the current runtime scaffold; do not
invent assessment flags or commands here.

## Inputs and assessment

Require the exact agreed brief and complete brief-obligation mapping, the
intent/module/bundle and source identities, the exact prior qualification
subject/report, consumer attestations, and the prior coverage and gap ledger.
If the agreed brief or design bindings are absent, return to
`metabuilder-harness-design`; if the prior qualification subject/report is
absent, return to `metabuilder-consumer-qualification`. Hold repair and delta
authoring until those inputs exist, while continuing independent inspection.
Use `metabuilder-assess` as the assessor for the consumer's semantic adequacy
assessment when that role is selected by the governing workflow. Keep the
consumer's assessment separate from controller observations and qualification
evidence.

State the exact objective, expected versus observed behavior, missing evidence,
and proposed bounded change. Classify every shortfall as a skills gap, prompt
gap, harness gap, runtime gap, target gap, authority gap, or evidence gap as
applicable. Route it according to ownership:

- known target-specific harness, test, or evidence shortfall → improvement;
- missing generic capability or runtime operation → `metabuilder-assess` for
  assessment and the authorized maintainer path;
- missing permission → the named authority;
- missing qualification evidence or an unclear exact run/environment →
  `metabuilder-consumer-qualification`;
- changed objective, brief constraint, or required design commitment →
  `metabuilder-harness-design` with the prior evidence and lineage preserved.

Do not treat a brief change as a same-objective delta. Do not drop a gap,
reuse old evidence for a new candidate, or silently repair the design. If the
same objective and approval already cover a routine revision, do not insert a
human confirmation per iteration; retain the real approval and authority
boundaries.

## Completion

Return the bounded repair plan or executed repair, the new candidate identity,
matched requalification delta, prior-gap dispositions, newly discovered gaps,
assessor evidence, unresolved authority/evidence limits, and the next exact
dependency-ready action. Stop with a resumable checkpoint when the objective
changes, bounds or authority are exceeded, infrastructure is unavailable, or
an unsupported/destructive/external effect is required. Never call an
ungoverned bypass a qualified improvement.
