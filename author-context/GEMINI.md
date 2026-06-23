# TYF Workspace Instructions

This is an author-owned TYF workspace. This book folder is the single work.

- If the author says "start my book" or wants a first writing session, use `tyf start`; a title can stay unknown.
- If the author brings existing material, use `tyf start <path>` to preserve it and open the writing runway before drafting.
- Keep source, interview notes, and candidate prose in `sources/`, `knowledge-base/`, `voice/`, and `drafts/`.
- `tyf capture --kind source` and text imports mint source fragments in `sources/fragments/`; run `tyf structure work --source-ref <id>` before drafting when a fragment contains explicit claims, examples, or questions. When the next author question is unclear, run `tyf attend work --source-ref <id>` and use `.review/gentle-attention.md` as hidden amanuensis guidance, then pass relevant ids to `tyf propose --source-ref <id>`.
- If the author asks why a passage does not land, run `tyf diagnose` with the smallest band and use `.review/current-diagnosis.md` as hidden amanuensis guidance. Diagnosis is attention, not doubt, and it never rewrites manuscript text.
- If the author asks what a named character would say, do, or notice, keep it as hidden amanuensis machinery: capture supplied character facts or cadence with `tyf character <name> --knowledge ... --voice ...`, then run `tyf consult-character work <name> --prompt "<question>"`. The contained packet may guide candidate dramatic insight; it is not manuscript text or a replacement for the author.
- Do not write manuscript prose directly. Manuscript writes must go through proposal, audit, author review packet, author decision, and `tyf write --decision <id>`.
- Missing knowledge stays visible as `[AUTHOR: needed - what]`.
- If the author edits `manuscript/` directly, use `tyf adopt work <unit> --evidence "<what happened>"` before the next controlled write.
- Use `tyf resume` to recover the active work, pending proposals, open prompts, and next move.
- Use `tyf notice --peek` for read-only inspection and `tyf snapshot --message "..."` only when the author wants an explicit git recovery point.
