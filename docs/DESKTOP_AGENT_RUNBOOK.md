# Desktop agent runbook

Status: author-UX runbook for Codex Desktop, Claude Code Desktop, and similar local agents.

The intended TYF workplace is a PC or Mac where the author talks to an amanuensis agent and the agent can run local helpers. The author should not operate TYF in a terminal. The agent operates TYF, opens local browser surfaces, and reports in plain language.

## Core promise

```text
Author supplies material, judgment, and taste.
Agent operates TYF.
TYF protects the manuscript boundary.
The browser Workbench is the shared writing desk.
```

## First session flow

1. Enter or create the local book folder. If the author has a folder, use it. If not, create a clearly named local folder. Do not make the author choose internal work ids.
2. Initialize the workspace by running `tyf init` in that folder.
3. If an arrival exists, run `tyf start <path>`. If not, run `tyf start`.
4. Read the writing runway and any orientation packet before asking more questions.
5. When the author wants a visual desk, run `tyf workbench --open`.

`tyf workbench --open` starts the local served Workbench. If browser launch fails, copy the localhost URL into the chat.

## Codex Desktop MCP

From the book workspace, run:

```bash
tyf workbench --codex-mcp-config
```

Then restart or reload Codex MCP if the desktop app needs it.

## Return session flow

Run:

```bash
tyf resume
```

Then choose one of: one concrete question, one candidate move, one exact file note, or opening the Workbench.

## Near-finished book flow

Run relevant review commands without turning them into author homework:

```bash
tyf-review continuity
tyf-review polish
tyf-review doctor
```

Report only the highest-value findings and ask for a decision where needed.

## Failure handling

If a local command fails, summarize the human meaning, preserve local state, try the smallest repair, and avoid dumping logs at the author. If the browser did not open, provide the local URL.

Example:

```text
The local Workbench server started, but the browser did not open automatically. Paste this local URL into your browser: http://127.0.0.1:8767/
```

## Boundaries

- The author is not asked to install, initialize, or run TYF commands when the agent has tool access.
- The author is not asked to choose between static and served Workbench mode.
- No silent commits.
- No manuscript writes outside the Gate.
- No automatic conflict merge.
- Generated reports are not accepted manuscript.

## Done condition

A 10/10 sitting starts when the author says something like “let’s work on the book” and the agent can create or enter the workspace, preserve arrivals, open the Workbench, and ask one useful material question without making the author operate the apparatus.
