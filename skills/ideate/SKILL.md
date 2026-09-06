---
name: ideate
description: "Generate a divergent idea tree from a seed through gptengage. Use for brainstorming, evolutionary ideation, or when the user says /ideate or $ideate."
argument-hint: "<seed> [--sigma 1.0] [--depth 2] [--cli claude] [--select]"
---

# Ideate

Read the shared
[`../../references/gptengage-invocation.md`](../../references/gptengage-invocation.md)
contract and the selected
[`../../references/gptengage-ideate.md`](../../references/gptengage-ideate.md)
recipe before calling a backend.

## Workflow

1. Parse the seed, creativity, depth, backend, selection, output, and timeout
   options using the operation recipe.
2. Resolve the authorized existing `gptengage` executable and run only its
   `ideate` operation. Keep the default sigma 1,
   depth 2, and Claude backend unless the user supplied alternatives.
3. Capture the full tree, validate JSON output when requested, and distinguish
   backend failure from partial tree generation.

## Boundaries

- Tree cost grows exponentially with depth; disclose unusually deep requests.
- Accept normal depth 1-5 and sigma 0-3. Use `--force` above those limits only
  when the user explicitly requested the out-of-range value and its cost.
- Use `--select` only when interactive selection is actually available.
- Never change the seed merely to produce more interesting output.
