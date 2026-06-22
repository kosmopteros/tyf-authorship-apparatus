# TYF Workspace Instructions

This is an author-owned TYF workspace. This book folder is the single work.

- If the author says "start my book" or wants a first writing session, use `tyf start`; a title can stay unknown.
- If the author brings existing material, use `tyf start <path>` to preserve it and open the writing runway before drafting.
- Keep source, interview notes, and candidate prose in `sources/`, `knowledge-base/`, `voice/`, and `drafts/`.
- `tyf capture --kind source` and text imports mint source fragments in `sources/fragments/`; pass relevant ids to `tyf propose --source-ref <id>`.
- Do not write manuscript prose directly. Manuscript writes must go through proposal, audit, author decision, and `tyf write --decision <id>`.
- Missing knowledge stays visible as `[AUTHOR: needed - what]`.
- If the author edits `manuscript/` directly, use `tyf adopt work <unit> --evidence "<what happened>"` before the next controlled write.
- Use `tyf resume` to recover the active work, pending proposals, open prompts, and next move.
- Use `tyf notice --peek` for read-only inspection and `tyf snapshot --message "..."` only when the author wants an explicit git recovery point.
