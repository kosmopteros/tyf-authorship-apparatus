# Start Here

TYF is for people writing books, essays, talks, courses, or newsletters with an agent. You should not need to learn the helper commands first. Paste one of these prompts into your agent and let the agent run the setup.

## Paste Into Codex

```text
Use TYF from https://github.com/kosmopteros/tyf-authorship-apparatus.

Install or load the TYF skills for Codex into `$CODEX_HOME/skills` or `~/.codex/skills`, using `powershell -ExecutionPolicy Bypass -File scripts/install.ps1 codex` on Windows if bash is unavailable. Read `using-tyf`, and help me start writing my new book today. Set up the workspace so this repo has its local `AGENTS.md`, but do not block on a title or writing language; ask if either matters now, then keep moving. If I bring existing material, preserve it first. Run `tyf start` or `tyf start <path>` for my scaffold/chat/folder/zip, show me the orientation and writing runway, structure any minted text source fragment before drafting, then ask only the gentle questions needed to begin one candidate passage. Do not write manuscript text yet; candidate prose belongs in `drafts/candidate-draft.md`. If you use git, make recovery points explicit and never commit silently.
```

## Paste Into Claude Cowork

```text
Use TYF from https://github.com/kosmopteros/tyf-authorship-apparatus.

Install or load the TYF skills, using `powershell -ExecutionPolicy Bypass -File scripts/install.ps1 claude` on Windows if bash is unavailable. Paste the TYF project instructions into this Cowork project if they are not already present, and help me start writing my new book today. Set up the workspace, but do not block on a title or writing language; ask if either matters now, then keep moving. If I bring existing material, preserve it first. Run `tyf start` or `tyf start <path>` for my scaffold/chat/folder/zip, show me the orientation and writing runway, structure any minted text source fragment before drafting, then ask only the gentle questions needed to begin one candidate passage. Do not write manuscript text yet; candidate prose belongs in `drafts/candidate-draft.md`. If you use git, make recovery points explicit and never commit silently.
```

## What Your Agent Should Do

1. Load `using-tyf`, then `initializing-a-workspace`.
2. Create or enter a TYF workspace.
3. Run `tyf start` when there is no arrival, or `tyf start <path>` when a scaffold/chat/folder/zip arrives.
4. Show the preserved arrival, orientation packet, `.review/writing-runway.md`, and `drafts/candidate-draft.md` in plain language.
5. Structure any minted text source fragment, then ask only the gentle questions needed to begin one candidate passage.
6. Draft candidates in `drafts/`; keep `manuscript/` empty until explicit controlled write.

The advanced helper commands still exist for agents and maintainers. For a new author, the public path is: paste the prompt, answer the questions, and keep the manuscript empty until you explicitly approve a controlled write.
