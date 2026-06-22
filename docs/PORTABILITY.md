# Portability

> **Tested target vs portability targets.** The canonical, tested target for v1 is Cowork (and the same skills via manual drop-in on Claude Code). The other harness manifests in this repo are portability *targets*: the skills themselves are plain `SKILL.md` and run without change, but each harness's plugin or extension manifest schema must be validated against that harness's current plugin documentation before you publish there. Treat anything beyond Cowork plus manual skills as unverified until you run it.

TYF is one set of skills that runs across multiple agent harnesses. The unit of capability is a single `SKILL.md` per skill. Each harness reads the same sixteen skills plus a context file under the filename that harness expects.

## Portable Workspace Format

A TYF workspace is a text-first author-work bundle. `tyf init` writes `tyf.portable.json` at the workspace root so agents can recognize and re-enter it after a move, zip, chat handoff, or harness switch. The marker identifies:

- `format: "tyf-workspace"` and a format version.
- canonical text state: `WORKSPACE_STATE.yaml`, `manifest.yaml`, `ASSUMPTIONS.md`, `sources/`, `knowledge-base/`, `voice/`, `redactor-canon/`, `works/`, and `.tyf/events.jsonl`.
- derived/disposable state: `.tyf/ledger.db` and SQLite journal files.
- `git: "optional"`.

This means Markdown, YAML, and JSONL are the durable truth. SQLite is an index, not prose custody. Git is useful for recovery and recall, but not required for TYF to function.

## What ships for each harness

| Harness | Plugin / extension file | Context file | Skills directory |
|---|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` (+ `marketplace.json`) | `CLAUDE.md` | `~/.claude/skills/` |
| Codex | `.codex-plugin/plugin.json` | `AGENTS.md` | `~/.agents/skills/` |
| Cursor | `.cursor-plugin/plugin.json` | `AGENTS.md` | Cursor skills dir |
| Gemini CLI | `gemini-extension.json` | `GEMINI.md` | extension dir |
| OpenCode | `.opencode/INSTALL.md` | `AGENTS.md` | OpenCode skills dir |

The three context files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) carry identical content. Each harness reads its own filename.

## Install

If you use more than one harness, install separately for each.

For non-technical authors, use the paste prompts in `docs/START_HERE.md`. They tell Codex or Claude Cowork to install or load TYF, set up the workspace, start even when the title is unknown, preserve existing material with `tyf import <path>` when it arrives, and ask source questions before drafting.

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

**Cursor** (agent chat):

```
/add-plugin tyf
```

**Gemini CLI** (extension):

```
gemini extensions install https://github.com/kosmopteros/tyf-authorship-apparatus
```

**OpenCode:** tell the agent to fetch and follow `.opencode/INSTALL.md` from the repository.

**Any harness, manual:** copy `skills/*` into the harness skills directory and place the matching context file where the harness reads session context.

```
bash scripts/install.sh claude     # or: codex | cursor | <explicit path>
```

## A note on manifest schemas

Plugin and extension manifest schemas evolve per harness. The install commands above are the load-bearing portability facts and are current as of v5-era Superpowers tooling. Before publishing to a given harness, validate that harness's plugin manifest schema against its current plugin documentation and adjust the corresponding file. The skills themselves are plain `SKILL.md` and portable without change.

## Verify the install

Ask the agent to list its TYF skills. It should return all sixteen and route any authorship request through `using-tyf` first. If it drafts finished prose from a vague prompt without checking the skills, the context file did not load; re-place it and restart the session.
