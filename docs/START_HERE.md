# Start Here

TYF is for people writing books, essays, talks, courses, or newsletters with an agent. You should not need to learn the helper commands first. Paste one of these prompts into your agent and let the agent run the setup.

## Paste Into Codex

```text
Use TYF from https://github.com/kosmopteros/tyf-authorship-apparatus.

If the TYF repository or installer scripts are not already present, fetch them first with `git clone https://github.com/kosmopteros/tyf-authorship-apparatus`, then `cd tyf-authorship-apparatus` and run the installer from that clone or load the skills directly.

Install or load the TYF skills for Codex into `$CODEX_HOME/skills` or `~/.codex/skills`, using `powershell -ExecutionPolicy Bypass -File scripts/install.ps1 codex` on Windows if bash is unavailable. Read `using-tyf`, and help me start writing my new book today. Set up the workspace so this repo has its local `AGENTS.md`, but do not block on a title or writing language; ask if either matters now, then keep moving. If I bring existing material, preserve it first. Run `tyf start` or `tyf start <path>` for my scaffold/chat/PDF/Pages file/formatted manuscript/audio/scan/large text/folder/zip, show me the orientation and writing runway, structure any minted text source fragment before drafting, and if the next question is unclear run `tyf attend work --source-ref <id> --query "<focus>"` for a source-grounded gentle attention packet with transparent local retrieval. If extraction is needed use OCR or transcription, document conversion, or chunk explicitly. For existing work, read or fill `.review/existing-work-recovery.md` when TYF creates it: recover the spine, source status, draft status, voice clues, illustration inventory, open author decisions, and one next writing move before forward drafting. Do not invent contents from preserved artifacts. Then use the gentle attention deck or `.review/gentle-attention.md`, ask one question at a time, and stop asking once one candidate passage can begin. Do not write manuscript text yet; candidate prose belongs in `drafts/candidate-draft.md`. If you use git, make recovery points explicit and never commit silently.
```

## Paste Into Claude Cowork

```text
Use TYF from https://github.com/kosmopteros/tyf-authorship-apparatus.

If the TYF repository or installer scripts are not already present, fetch them first with `git clone https://github.com/kosmopteros/tyf-authorship-apparatus`, then `cd tyf-authorship-apparatus` and run the installer from that clone or load the skills directly.

Install or load the TYF skills, using `powershell -ExecutionPolicy Bypass -File scripts/install.ps1 claude` on Windows if bash is unavailable. Paste the TYF project instructions into this Cowork project if they are not already present, and help me start writing my new book today. Set up the workspace, but do not block on a title or writing language; ask if either matters now, then keep moving. If I bring existing material, preserve it first. Run `tyf start` or `tyf start <path>` for my scaffold/chat/PDF/Pages file/formatted manuscript/audio/scan/large text/folder/zip, show me the orientation and writing runway, structure any minted text source fragment before drafting, and if the next question is unclear run `tyf attend work --source-ref <id> --query "<focus>"` for a source-grounded gentle attention packet with transparent local retrieval. If extraction is needed use OCR or transcription, document conversion, or chunk explicitly. For existing work, read or fill `.review/existing-work-recovery.md` when TYF creates it: recover the spine, source status, draft status, voice clues, illustration inventory, open author decisions, and one next writing move before forward drafting. Do not invent contents from preserved artifacts. Then use the gentle attention deck or `.review/gentle-attention.md`, ask one question at a time, and stop asking once one candidate passage can begin. Do not write manuscript text yet; candidate prose belongs in `drafts/candidate-draft.md`. If you use git, make recovery points explicit and never commit silently.
```

## What Your Agent Should Do

1. Load `using-tyf`, then `initializing-a-workspace`.
2. Create or enter a TYF workspace.
3. Run `tyf start` when there is no arrival, or `tyf start <path>` when a scaffold/chat/PDF/Pages file/formatted manuscript/audio/scan/large text/folder/zip arrives.
4. Show the preserved arrival, orientation packet, any `.review/existing-work-recovery.md` packet, `.review/writing-runway.md`, and `drafts/candidate-draft.md` in plain language.
5. Structure any minted text source fragment. If no fragment was minted because extraction is needed, use OCR or transcription or chunk explicitly before deriving claims. Do not invent contents from preserved artifacts.
6. Use the generated gentle attention deck without making the author answer every prompt; when focus matters, use the packet's transparent local retrieval section; ask one question at a time.
7. Draft candidates in `drafts/`; keep `manuscript/` empty until explicit controlled write.

The advanced helper commands still exist for agents and maintainers. For a new author, the public path is: paste the prompt, answer the questions, and keep the manuscript empty until you explicitly approve a controlled write.
