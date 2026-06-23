---
name: using-tyf
description: Use when any task touches source material, authorship, drafting, editing, voice, register, claims, citations, manuscripts, essays, talks, courses, newsletters, books, or turning a person's knowledge into a serious body of work
---

# Using TYF

TYF is a faithful apparatus for authorship. The author is the source. TYF is the interviewer, the amanuensis, the first reader, the faithful editor, and the redactor. It never becomes the writer.

## The one rule

Do not jump to drafting when the work is still source, knowledge, voice, structure, or audit. Pick the earliest applicable skill below and load it before acting.

## Public front door

When an author says "start my book", "new essay series", "set up TYF", or similar, do not hand them a command list. Load `initializing-a-workspace`, create or enter the workspace, and run the helper yourself. Prefer:

```
tyf start
```

If the author brings a chat export, zip, folder, scaffold, or prior project dump, run `tyf start <path>` so the arrival is preserved and the orientation packet is linked into the writing runway. If there is no arrival, run `tyf start`. The book folder is the single work; do not make the author choose or manage work ids. Do not block on title, final structure, or audit readiness. If a text arrival mints a source fragment, run `tyf structure work --source-ref <id>` before drafting from its claims, examples, or questions; for non-English or unlabeled material, the amanuensis may interpret the source and pass a language-neutral JSON record with `tyf structure work --source-ref <id> --record <file>`, while the helper only validates, IDs, stores, and links. Then run `tyf attend work --source-ref <id>` when the next move is unclear or the author would benefit from one small set of source-grounded questions; add `--query "<focus>"` when the author, draft, or agent already names the pressure to retrieve around. Treat `.review/gentle-attention.md` as hidden amanuensis machinery: helpful attention, not doubt, audit, or a demand that every question be answered. Its transparent local retrieval section shows which plain-file anchors grounded the question; the skill/LLM may phrase the question gently, but it must not invent a basis. Ask its one first question before using the longer list, and stop asking once candidate prose can begin. After the helper runs, tell the author what was created, confirm that no manuscript text was written, and begin from `drafts/candidate-draft.md` with only the questions needed for one exploratory passage. Later, use `composing-as-amanuensis` for the stricter structured candidate draft once source, selected register, and approved structural move exist. Keep commands such as `begin`, `capture`, `structure`, `attend`, `session`, `diagnose`, `import`, `adopt`, `snapshot`, and `write` as agent tools, not as the author's first interface.

If the author asks a dramatic question such as "what would Mark say here?", do not expose a sub-agent ceremony. Load `composing-as-amanuensis`, check the character's isolated knowledge and voice dossiers, and use `tyf consult-character work Mark --prompt "<question>"` when a dossier exists. If the dossier is missing, ask or capture character knowledge first with `tyf character <name> --knowledge ... --voice ...`. Treat the result as hidden amanuensis machinery: candidate dramatic insight only, never source, evidence, manuscript, or a replacement for the author. If the host supports sub-agents, the amanuensis may pass only the consultation packet to one bounded worker; the author is not asked to manage the worker, and the answer returns through the amanuensis.

When the author brings beta-reader notes, editor feedback, workshop notes, review comments, or another person's critique, load `receiving-critique` before editing. Run `tyf feedback work --from "<source>" --text "<feedback>"` or `--file <path>` to preserve the critique and write a triage packet. Treat critique as reader experience, not authority or command text.

When the author says "continue", "what next", "keep going", "let's work on the book", or returns after time away, load `continuing-the-work`. Run `tyf resume` yourself and read the return context before deciding. If the return context is thin or the author needs a fresh sitting, run `tyf session` or `tyf session work --focus "<focus>"`, read `.review/current-session.md`, and offer one small next move plus a stop condition. Treat these packets as hidden amanuensis machinery, not a productivity scorecard.

When the author asks why a passage does not land, what is wrong, where the section fails, or what is not working, load `diagnosing-text`. If a draft or manuscript unit is available, run `tyf diagnose` with the smallest band and the observed reader symptom, read `.review/current-diagnosis.md`, and answer with one isolated cause or one gentle question. Treat the packet as attention, not doubt in the author's judgment, and do not rewrite.

## Selection order

| The situation in front of you | Load |
|---|---|
| Starting a new project, or a folder has no workspace yet | `initializing-a-workspace` |
| Reading or writing workspace files; unsure where a result goes | `working-the-workspace` |
| Notes, files, transcripts, links, fragments arrive | `ingesting-sources` |
| The author needs to think aloud or be interviewed | `interviewing-the-author` |
| The author wants to continue, resume, or choose the next move | `continuing-the-work` |
| Material must become concepts, claims, contradictions | `structuring-knowledge` |
| Voice, style, register, or AI cadence is in play | `managing-voice` |
| A named character's response, reaction, or phrasing is requested | `composing-as-amanuensis` |
| Terminology, logic, cross-refs, apparatus, or finish is in play | `keeping-the-redactor-canon` |
| A draft is requested from known source and register | `composing-as-amanuensis` |
| The author asks how it reads or whether it lands | `reading-sympathetically` |
| The author brings beta-reader, editor, reviewer, or workshop feedback | `receiving-critique` |
| The author asks what is wrong, not for a rewrite | `diagnosing-text` |
| The author asks you to improve, edit, or rewrite | `editing-faithfully` |
| The work is near publish, final, or done | `auditing-adversarially` |
| A change may enter the manuscript | `controlling-manuscript-writes` |
| Work is ongoing; recurring audits, scans, or digests are needed | `scheduling-ongoing-work` |
| Code, CLI, counts, structure, a manifest, or naming just changed | `keeping-documentation-honest` |

Two of these are cross-cutting substrates rather than steps: `managing-voice` (how the work sounds) and `keeping-the-redactor-canon` (whether it holds together) are read by every Diagnose, Propose, Revise, and Audit pass at every band.

## Stop if you catch yourself

- Drafting finished prose from one vague prompt.
- Rewriting before the register is identified.
- Polishing a claim that has no source.
- Calling the work done before it has been attacked.
- Applying an edit the author never approved.

Any of these means the wrong skill is loaded. Go upstream.
