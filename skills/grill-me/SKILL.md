---
name: grill-me
description: "A shortcut to run the grilling skill on a plan, decision, or idea. Use when the user says /grill-me or $grill-me."
argument-hint: "[spec|factory|debate|gradient|linear-runtime] [topic or artifact] [--n <stems>] [--branch <b>] [--depth <n>] [--keep <k>] [--zones <z>] [--cap <nodes>]"
disable-model-invocation: true
---

Invoke the available `grilling` skill, preserving the topic, arguments,
selected mode, existing decisions and authority. This alias inherits that
skill's intent, boundaries, interaction policy and completion contract; it adds
no backend calls, approval gate or speculative mode. With no mode selected,
start the ordinary user interview.

Use the host's actual skill-loading mechanism. A Skill tool is one supported
route when present; otherwise read the available `grilling/SKILL.md` directly.
Do not invent a host tool or install a missing skill. If the target is
unavailable, report the missing binding instead of claiming the alias ran it.
