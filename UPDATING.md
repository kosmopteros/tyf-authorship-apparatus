# Updating TYF

TYF is distributed as a plugin or extension per harness, and updated the way
that harness updates plugins, pinned to tagged releases. The pack never updates
itself silently: `tyf update` only notifies; the harness performs the install.
This mirrors the reference pack (`obra/superpowers`), which updates through each
harness's native plugin-update and tagged releases rather than a self-pull.

## Check for a newer version

```
tyf update            # notify-only; once-a-day throttle
tyf update --force    # check now, ignoring the throttle
```

It reads the latest release tag from GitHub, compares it to your installed
version, and tells you when you are behind. It pulls nothing and runs no remote
code. Schedule it daily for a standing reminder (see `cowork/SCHEDULED_TASKS.md`).

## Update, per harness

| Harness | Update command |
|---|---|
| Claude Code | `/plugin update tyf` |
| Gemini CLI | `gemini extensions update tyf` |
| Codex / Cursor / Copilot | update through that harness's plugin marketplace |
| OpenCode | re-copy `skills/` and the helper (see `.opencode/INSTALL.md`) |
| Manual / any | `git pull` a clone, then re-run `bash scripts/install.sh <harness>` |

## Releases

Versions are git tags (for example `v0.2.0`) with matching GitHub releases.
`tyf update` compares against the latest release tag, so cut a release when a new
version should become visible to installs.
