#!/usr/bin/env bash
# Install the TYF skills, and link the `tyf` helper onto your PATH.
# Usage:
#   bash scripts/install.sh                 # interactive: pick a harness
#   bash scripts/install.sh claude          # ~/.claude/skills
#   bash scripts/install.sh codex           # ${CODEX_HOME:-~/.codex}/skills
#   bash scripts/install.sh cursor          # ~/.cursor/skills
#   bash scripts/install.sh codex-plugin    # ${CODEX_HOME:-~/.codex}/plugins/cache/personal/tyf/<version>
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
    codex-plugin) echo "__TYF_CODEX_PLUGIN__" ;;
    cursor)  echo "$HOME/.cursor/skills" ;;
    "")      echo "" ;;
    *)       echo "$1" ;;
  esac
}

ctx_file_for() {
  case "${1:-}" in
    claude) echo "CLAUDE.md" ;;
    codex)  echo "AGENTS.md" ;;
    codex-plugin) echo "AGENTS.md" ;;
    cursor) echo "AGENTS.md" ;;
    *)      echo "CLAUDE.md / AGENTS.md / GEMINI.md" ;;
  esac
}

codex_plugin_version() {
  sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$ROOT/.codex-plugin/plugin.json" | head -n 1
}

install_codex_plugin_cache() {
  local version codex_home cache
  version="$(codex_plugin_version)"
  if [ -z "$version" ]; then
    echo "No Codex plugin version found in $ROOT/.codex-plugin/plugin.json" >&2
    exit 1
  fi
  codex_home="${CODEX_HOME:-$HOME/.codex}"
  cache="$codex_home/plugins/cache/personal/tyf/$version"
  local cache_parent old
  cache_parent="$(dirname "$cache")"
  mkdir -p "$cache_parent"
  for old in "$cache_parent"/*; do
    [ -e "$old" ] || continue
    [ "$(basename "$old")" = "$version" ] && continue
    rm -rf -- "$old"
  done

  rm -rf -- "$cache"
  mkdir -p "$cache"

  local entries=(
    ".codex-plugin"
    ".claude-plugin"
    ".cursor-plugin"
    ".opencode"
    "author-context"
    "bin"
    "cowork"
    "docs"
    "examples"
    "plugin"
    "scripts"
    "skills"
    "CHANGELOG.md"
    "LICENSE"
    "README.md"
    "TYF-manifesto-and-architecture.md"
    "VALIDATION.md"
    "gemini-extension.json"
    "package.json"
    "pyproject.toml"
    "tyf.portable.json"
  )
  local entry
  for entry in "${entries[@]}"; do
    if [ -e "$ROOT/$entry" ]; then
      cp -R "$ROOT/$entry" "$cache/$entry"
    fi
  done

  echo "Installed TYF personal Codex plugin cache:"
  echo "  $cache"
  echo "  version: $version"
  echo "Older TYF personal plugin cache versions were removed."
  echo "Restart Codex so it can reload the TYF plugin from the refreshed cache."
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

if [ "$TARGET" = "__TYF_CODEX_PLUGIN__" ]; then
  install_codex_plugin_cache
else
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
fi

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
ctx_hint="$(ctx_file_for "$HARNESS")"
if [ -f "$ROOT/$ctx_hint" ]; then
  echo "Contributor context for working on this TYF pack:"
  echo "  $ROOT/$ctx_hint"
else
  echo "Contributor context:"
  echo "  This author release archive does not include pack-root contributor context files."
  echo "  Use $ROOT/author-context/ before workspace init, or run tyf init in a book folder."
fi
echo
echo "Then verify: ask the agent to list its TYF skills; it should route through 'using-tyf' first."
