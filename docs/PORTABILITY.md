# Portability

> **Tested target vs portability targets.** The canonical, tested target for v1 is Cowork (and the same skills via manual drop-in on Claude Code). The other harness manifests in this repo are portability *targets*: the skills themselves are plain `SKILL.md` and run without change, but each harness's plugin or extension manifest schema must be validated against that harness's current plugin documentation before you publish there. Treat anything beyond Cowork plus manual skills as unverified until you run it.

TYF is one set of skills that runs across multiple agent harnesses. The unit of capability is a single `SKILL.md` per skill. Each harness reads the same seventeen skills plus a context file under the filename that harness expects. The pack-root context files are contributor context for this development repository; author workspaces should use the generated context from `tyf init` or the clean templates in `author-context/`.

## Portable Workspace Format

A TYF workspace is a text-first author-work bundle. For the beta launch, the book folder is the single work. `tyf init` writes `tyf.portable.json` at the workspace root so agents can recognize and re-enter it after a move, zip, chat handoff, or harness switch. The marker identifies:

- `format: "tyf-workspace"` and a format version.
- `single_work: true`.
- canonical text state: `WORKSPACE_STATE.yaml`, `work.yaml`, `manifest.yaml`, `ASSUMPTIONS.md`, `style-sheet.md`, `outline/`, `drafts/`, `manuscript/`, `.review/`, `sources/`, `knowledge-base/`, `voice/`, `redactor-canon/`, and `.tyf/events.jsonl`.
- derived/disposable state: `.tyf/ledger.db` and SQLite journal files.
- `git: "optional"`.

This means Markdown, YAML, and JSONL are the durable truth. SQLite is an index, not prose custody. Git is useful for recovery and recall, but not required for TYF to function.

## What ships for each harness

| Harness | Plugin / extension file | Context file | Skills directory |
|---|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` (+ `marketplace.json`) | `CLAUDE.md` | `~/.claude/skills/` |
| Codex | `.codex-plugin/plugin.json` | `AGENTS.md` | `$CODEX_HOME/skills` or `~/.codex/skills/` |
| Cursor | `.cursor-plugin/plugin.json` | `AGENTS.md` | Cursor skills dir |
| Gemini CLI | `gemini-extension.json` | `GEMINI.md` | extension dir |
| OpenCode | `.opencode/INSTALL.md` | `AGENTS.md` | OpenCode skills dir |

The three pack-root context files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) carry identical contributor content. Each harness reads its own filename. Clean author-facing templates live in `author-context/`. For a book workspace, run `tyf init` in the book folder, or `tyf init <book-folder>` near it, so TYF writes the matching local context files.

## Install

If you use more than one harness, install separately for each.

For non-technical authors, use the paste prompts in `docs/START_HERE.md`. They tell Codex or Claude Cowork to install or load TYF, set up the workspace, run `tyf start` even when the title is unknown, preserve existing material with `tyf start <path>` when it arrives, and open a candidate draft runway before any manuscript write.

**Claude Code** (plugin marketplace):

```
/plugin marketplace add kosmopteros/tyf-authorship-apparatus
/plugin install tyf@tyf-marketplace
```

**Codex CLI** (plugin search):

```
/plugins
tyf
```

Then select Install Plugin.

For manual Codex use, copy the TYF skills into `$CODEX_HOME/skills` or `~/.codex/skills/`:

```
bash scripts/install.sh codex
```

On Windows without bash:

```
powershell -ExecutionPolicy Bypass -File scripts/install.ps1 codex
```

That installs the global dispatcher skill (`using-tyf`). A book repository still needs its local workspace context: run `tyf init` in the book folder, or `tyf init <workspace-name>` near it, then Codex will read the generated `AGENTS.md` and route new-book work through `tyf start` rather than a title-gated setup.

**Cursor** (agent chat):

```
/add-plugin tyf
```

**Gemini CLI** (extension):

```
gemini extensions install https://github.com/kosmopteros/tyf-authorship-apparatus
```

**OpenCode:** tell the agent to fetch and follow `.opencode/INSTALL.md` from the repository.

**Any harness, manual:** copy `skills/*` into the harness skills directory. For a book workspace, run `tyf init` in the book folder, or `tyf init <book-folder>` near it, so the local `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` are generated without contributor-only routing. If your harness needs a manual context template outside an initialized workspace, use the matching file from `author-context/`, not the pack-root development context.

```
bash scripts/install.sh claude     # or: codex | cursor | <explicit path>
```

On Windows without bash:

```
powershell -ExecutionPolicy Bypass -File scripts/install.ps1 claude
```

## A note on manifest schemas

Plugin and extension manifest schemas evolve per harness. The install commands above are the load-bearing portability facts and are current as of v5-era Superpowers tooling. Before publishing to a given harness, validate that harness's plugin manifest schema against its current plugin documentation and adjust the corresponding file. The skills themselves are plain `SKILL.md` and portable without change.

## Verify the install

Ask the agent to list its TYF skills. It should return all seventeen and route any authorship request through `using-tyf` first. If it drafts finished prose from a vague prompt without checking the skills, the context file did not load; re-place it and restart the session.
