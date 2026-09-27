#!/usr/bin/env bash
# Install the Claude Code <-> gptqueue channel for the current user.
#   install.sh [--bin DIR] [--map DIR=NAME]... [--no-mcp] [--no-hooks]
# Copies the helper scripts to DIR (default ~/.local/bin), records optional
# directory->agent-name mappings, registers the user-scope "gptqueue" MCP server
# and adds SessionStart/Stop hooks to ~/.claude/settings.json (idempotent).
set -euo pipefail
here="$(dirname "$(realpath "$0")")"
bin="$HOME/.local/bin" mcp=1 hooks=1 maps=()
while [ $# -gt 0 ]; do
  case "$1" in
    --bin) bin="$2"; shift 2 ;;
    --map) maps+=("$2"); shift 2 ;;
    --no-mcp) mcp=0; shift ;;
    --no-hooks) hooks=0; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

mkdir -p "$bin"
for f in gptqueue-claude-name gptqueue-claude-mcp gptqueue-inbox-peek gptqueue-claude-hook gptqueue-claude-verify.mjs; do
  install -m 0755 "$here/$f" "$bin/$f"
done
echo "installed helpers into $bin"

names="${GPTQ_CLAUDE_NAMES_FILE:-${XDG_CONFIG_HOME:-$HOME/.config}/gptqueue/claude-agent-names.tsv}"
for m in "${maps[@]}"; do
  dir="$(realpath -m "${m%%=*}")" name="${m#*=}"
  mkdir -p "$(dirname "$names")"; touch "$names"
  grep -v -P "^\Q$dir\E\t" "$names" > "$names.tmp" || true
  printf '%s\t%s\n' "$dir" "$name" >> "$names.tmp"; mv "$names.tmp" "$names"
  echo "mapped $dir -> $name in $names"
done

if [ "$mcp" -eq 1 ]; then
  claude mcp remove -s user gptqueue >/dev/null 2>&1 || true
  claude mcp add -s user gptqueue -- "$bin/gptqueue-claude-mcp"
fi

if [ "$hooks" -eq 1 ]; then
  settings="$HOME/.claude/settings.json"
  [ -f "$settings" ] || echo '{}' > "$settings"
  cp "$settings" "$settings.bak-gptqueue"
  jq --arg s "$bin/gptqueue-claude-hook session-start" --arg t "$bin/gptqueue-claude-hook stop" '
    def ours: (.hooks // []) | any(.command | test("gptqueue-claude-hook"));
    def put(ev; cmd): .hooks[ev] = (((.hooks[ev] // []) | map(select(ours | not)))
      + [{matcher: "", hooks: [{type: "command", command: cmd, timeout: 10}]}]);
    put("SessionStart"; $s) | put("Stop"; $t)' "$settings.bak-gptqueue" > "$settings"
  echo "hooks written to $settings (backup: $settings.bak-gptqueue)"
fi
