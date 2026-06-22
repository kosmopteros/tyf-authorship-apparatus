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

If the author brings a chat export, zip, folder, scaffold, or prior project dump, run `tyf start <path>` so the arrival is preserved and the orientation packet is linked into the writing runway. If there is no arrival, run `tyf start`. The book folder is the single work; do not make the author choose or manage work ids. Do not block on title, final structure, or audit readiness. After the helper runs, tell the author what was created, confirm that no manuscript text was written, and begin from `drafts/candidate-draft.md` with only the questions needed for one candidate passage. Keep commands such as `begin`, `capture`, `import`, `adopt`, `snapshot`, and `write` as agent tools, not as the author's first interface.

## Selection order

| The situation in front of you | Load |
|---|---|
| Starting a new project, or a folder has no workspace yet | `initializing-a-workspace` |
| Reading or writing workspace files; unsure where a result goes | `working-the-workspace` |
| Notes, files, transcripts, links, fragments arrive | `ingesting-sources` |
| The author needs to think aloud or be interviewed | `interviewing-the-author` |
| Material must become concepts, claims, contradictions | `structuring-knowledge` |
| Voice, style, register, or AI cadence is in play | `managing-voice` |
| Terminology, logic, cross-refs, apparatus, or finish is in play | `keeping-the-redactor-canon` |
| A draft is requested from known source and register | `composing-as-amanuensis` |
| The author asks how it reads or whether it lands | `reading-sympathetically` |
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
