# Chasm instruction candidates

`policy.md` is the shared source. `scripts/render_chasm_instructions.py`
renders it with runtime-specific filenames. Generated candidates
are Codex `AGENTS.md`, Pi `AGENTS.md`, Claude `CLAUDE.md`, and an OpenCode
content candidate. Merge candidates into reviewed global instruction layers;
do not replace existing instructions wholesale. For OpenCode, inspect the
installed runtime's actual global-instruction configuration before selecting a
destination. These files do not establish runtime installation or capability.

When merging with an existing Pi global file in this guest, remove stale host
memory observations and old OpenRouter fallback instructions. Keep self-hosted
Qwen on the B300 as the default and use the owner's authorized Z.ai Coding Plan
`zai/glm-5.3` fallback only when its guest credential is installed. Preserve
unrelated user preferences and keep a copy of the prior guest file for rollback.
If the host operator supplies a private `~/.zaitoken` file, Pi can resolve it
at request time with `"apiKey": "!cat ~/.zaitoken"` under the built-in
`zai` provider in `~/.pi/agent/models.json`. An alternative for a guest without
that file is `python3 scripts/import_zai_coding_key.py`, which reads the key
through a hidden prompt into Pi's private auth file. Do not transmit the key
through chat or `/shared`.

Regenerate from the repository root with:

```sh
python3 scripts/render_chasm_instructions.py --output profiles/chasm-development/instructions/rendered
```
