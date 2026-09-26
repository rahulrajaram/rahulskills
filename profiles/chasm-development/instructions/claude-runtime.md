## Claude access and credentials

- In a `chasm shell NAME --with claude` session, start Claude with
  `claude-openrouter`. It reaches OpenRouter through the Chasm relay; the guest
  never holds the OpenRouter key. If the wrapper or relay is unavailable,
  report that prerequisite gap rather than substituting another route.
- In a plain `chasm shell NAME`, use `claude`, then `/login` only when the user chooses
  to sign in with a personal account inside this guest.
- Never copy host `~/.claude/.credentials.json` (or any host Claude auth or
  settings file) into a guest, `/shared`, a repository, or a chat. Sealed
  templates are scrubbed of it; do not reintroduce it.
- Claude discovers skills only at `~/.claude/skills/<name>/SKILL.md` (or under
  `$CLAUDE_CONFIG_DIR`). Host-synced entries are listed in
  `.chasm-skills-ownership.json`; edit them on the host, not in the guest.
  Guest-created skills beside them are preserved.
