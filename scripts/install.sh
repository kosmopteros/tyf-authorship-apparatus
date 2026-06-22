#!/usr/bin/env bash
# Install the TYF skills, and link the `tyf` helper onto your PATH.
# Usage:
#   bash scripts/install.sh                 # interactive: pick a harness
#   bash scripts/install.sh claude          # ~/.claude/skills
#   bash scripts/install.sh codex           # ${CODEX_HOME:-~/.codex}/skills
#   bash scripts/install.sh cursor          # ~/.cursor/skills
#   bash scripts/install.sh /custom/path    # any explicit skills directory
#
# Set BIN_DIR to choose where the `tyf` launcher is linked (default ~/.local/bin).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/skills"
BIN_DIR="${BIN_DIR:-$HOME/.local/bin}"

resolve_target() {
  case "${1:-}" in
    claude)  echo "$HOME/.claude/skills" ;;
    codex)   echo "${CODEX_HOME:-$HOME/.codex}/skills" ;;
    cursor)  echo "$HOME/.cursor/skills" ;;
    "")      echo "" ;;
    *)       echo "$1" ;;
  esac
}

ctx_file_for() {
  case "${1:-}" in
    claude) echo "CLAUDE.md" ;;
    codex)  echo "AGENTS.md" ;;
    cursor) echo "AGENTS.md" ;;
    *)      echo "CLAUDE.md / AGENTS.md / GEMINI.md" ;;
  esac
}

HARNESS="${1:-}"
TARGET="$(resolve_target "$HARNESS")"

if [ -z "$TARGET" ]; then
  echo "Pick a harness: claude | codex | cursor | <explicit path>"
  read -r HARNESS
  TARGET="$(resolve_target "$HARNESS")"
fi

if [ -z "$TARGET" ]; then
  echo "No target resolved. Aborting." >&2
  exit 1
fi

# 1. Skills
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
echo "  $count skills installed."

# 2. The tyf helper, linked (not copied) onto PATH. A symlink keeps `tyf check`
#    able to resolve the pack root; a loose copy could not.
echo
chmod +x "$ROOT/bin/tyf" 2>/dev/null || true   # a ZIP download can drop the exec bit
if mkdir -p "$BIN_DIR" 2>/dev/null && ln -sf "$ROOT/bin/tyf" "$BIN_DIR/tyf" 2>/dev/null; then
  echo "Linked helper: $BIN_DIR/tyf -> $ROOT/bin/tyf"
  case ":${PATH:-}:" in
    *":$BIN_DIR:"*) : ;;
    *) echo "  NOTE: $BIN_DIR is not on your PATH. Add it:"
       echo "        export PATH=\"$BIN_DIR:\$PATH\"" ;;
  esac
else
  echo "Could not symlink the helper. Add the bundled launcher to PATH instead:"
  echo "        export PATH=\"$ROOT/bin:\$PATH\"        # macOS / Linux"
  echo "        set PATH=$ROOT\\bin;%PATH%             # Windows (cmd)"
  echo "  If you copy the helper elsewhere, set TYF_PACK_ROOT=$ROOT so 'tyf check' finds the pack."
fi

# 3. Context guidance
echo
echo "Book workspace context:"
echo '  For a book workspace, run `tyf init` in the book folder, or `tyf init <book-folder>` near it.'
echo "  Use the generated context files."
echo "  Do not copy the pack development context into a book workspace."
echo "  Clean author-context templates are available at: $ROOT/author-context/"
echo
echo "Contributor context for working on this TYF pack:"
echo "  $ROOT/$(ctx_file_for "$HARNESS")"
echo
echo "Then verify: ask the agent to list its TYF skills; it should route through 'using-tyf' first."
