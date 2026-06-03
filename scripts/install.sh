#!/usr/bin/env bash
# Copy the TYF skills into a harness skills directory.
# Usage:
#   bash scripts/install.sh                 # interactive: pick a harness
#   bash scripts/install.sh claude          # ~/.claude/skills
#   bash scripts/install.sh codex           # ~/.agents/skills
#   bash scripts/install.sh /custom/path    # any explicit directory

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/skills"

resolve_target() {
  case "${1:-}" in
    claude)  echo "$HOME/.claude/skills" ;;
    codex)   echo "$HOME/.agents/skills" ;;
    cursor)  echo "$HOME/.cursor/skills" ;;
    "")      echo "" ;;
    *)       echo "$1" ;;
  esac
}

TARGET="$(resolve_target "${1:-}")"

if [ -z "$TARGET" ]; then
  echo "Pick a harness: claude | codex | cursor | <explicit path>"
  read -r choice
  TARGET="$(resolve_target "$choice")"
fi

if [ -z "$TARGET" ]; then
  echo "No target resolved. Aborting." >&2
  exit 1
fi

mkdir -p "$TARGET"
echo "Installing TYF skills into: $TARGET"

count=0
for dir in "$SRC"/*/; do
  name="$(basename "$dir")"
  rm -rf "${TARGET:?}/$name"
  cp -R "$dir" "$TARGET/$name"
  echo "  installed: $name"
  count=$((count + 1))
done

echo
echo "Done. $count skills installed."
echo "Also place the matching context file (CLAUDE.md / AGENTS.md / GEMINI.md) where your harness reads session context."
echo "Verify by asking the agent to list its TYF skills; it should route through using-tyf first."
