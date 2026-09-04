---
name: grill-me
description: "A shortcut to run the grilling skill on a plan, decision, or idea. Use when the user says /grill-me or $grill-me."
argument-hint: "[spec|factory|debate|gradient] [topic or artifact] [--n <stems>] [--branch <b>] [--depth <n>] [--keep <k>] [--zones <z>] [--cap <nodes>]"
disable-model-invocation: true
---

Call the Skill tool with `grilling`, preserving any arguments.

For Pi: invoke `grilling` via the Skill tool. For other CLIs, run the
`grilling` skill directly; this alias exists only as a convenient trigger
name so `/grill-me` and `$grill-me` resolve to the full grilling skill.
