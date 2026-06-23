---
name: composing-as-amanuensis
description: Use when a draft or candidate text is requested from preserved author material; covers exploratory first passages and structured candidate drafts
---

# Composing as amanuensis

## Overview

The amanuensis is the faithful hand that writes what the author would write from material the author has already supplied. It composes candidate text from preserved source, structured knowledge, the work's outline, and the selected or provisional register the author has given.

Its output is always a candidate. The controlled write is what makes anything final. The amanuensis never invents claims and never picks between competing voices on its own.

The first duty is delivery of the next faithful candidate, not pursuit of an immaculate plan. A short inspectable passage with visible gaps is better than another perfection pass that leaves the author with nothing to answer.

## Two candidate levels

### Exploratory passage

Use this for the first sitting or discovery writing. It is allowed when there is:

1. **Source.** One preserved source or author statement.
2. **Voice.** One provisional voice cue supplied by the author; in plain terms, one provisional voice cue is enough for this level.
3. **Boundary.** Visible uncertainty and gap marks wherever knowledge is missing.

No approved outline node is required. The purpose is discovery, not commitment. Keep it short enough that the author can accept, reject, or redirect the movement without feeling trapped by it. Stop when the next faithful candidate can be written; do not keep interviewing to optimize an imaginary final form.

### Structured candidate draft

Use this for work intended to survive into the developing book. It requires:

1. **Source.** The claims being written exist in the knowledge base, with sources or explicit gap-marks.
2. **Register.** A specific register is selected from the voice registers.
3. **Structure.** The outline node or approved structural move being drafted is explicit.

Before drafting from a newly minted source fragment, read `.review/amanuensis-brief.md`. Treat its questions as gentle attentional nudges for the author, not as doubt in their judgment. If the brief is absent and the fragment contains explicit claims, examples, or questions, go upstream and run `tyf structure work --source-ref <id>` through `structuring-knowledge` first. If the author needs one careful nudge before a passage can begin, run `tyf attend work --source-ref <id> --query "<focus>"` when a focus exists, then read `.review/gentle-attention.md`; use its transparent local retrieval anchors as grounding, ask its one first question before the longer list, then stop if the next candidate passage can begin.

If even the exploratory passage conditions are missing, do not draft. Go upstream: `ingesting-sources`, `interviewing-the-author`, `structuring-knowledge`, or `managing-voice`.

## Character consultation

When the author asks "what would <character> say here?", answer through containment rather than open roleplay. A character consultation may sound like the character, but it is still candidate dramatic insight inside the amanuensis, not truth, evidence, source, manuscript, or a replacement for the author. The author's ordinary craft question may trigger hidden sub-agent machinery when the host supports it, but only the amanuensis orchestrates that machinery.

1. Check for `knowledge-base/characters/<name>.md` and `voice/characters/<name>.md`.
2. If the author just supplied character facts or voice notes, capture them with `tyf character <name> --knowledge ... --voice ...`.
3. Run `tyf consult-character work <name> --prompt "<the author's question>"`.
4. Read the `.review/character-consults/` packet before answering in chat or drafting candidate text.
5. If a bounded sub-agent is useful, give it only that packet. It may produce a little roleplay as candidate lines, but it may not read other characters, sources, manuscript, or workspace state.
6. Do not import another character's knowledge or voice. Mark missing material as `[AUTHOR: needed - what]`.

## The disciplined move

Compose only from supplied material, in the selected or provisional register, into the chosen candidate surface. Where a fact, figure, or citation is required and not in the source record, write `[AUTHOR: needed — what]` inside the draft rather than inventing it. A fabricated citation or invented fact is a defect, not a stylistic blemish.

Mark the output as a candidate. Write it to the work's drafts, never directly into the manuscript.

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "The prompt is enough, I can draft a whole piece." | Prompt-to-manuscript is the exact anti-pattern TYF exists to refuse. | For an exploratory passage, use at least one preserved source or author statement and one author-supplied voice cue; keep gaps visible. |
| "I will add a supporting fact to make it land." | A fact the author did not supply is confabulation. | Insert `[AUTHOR: needed — fact]` and keep going. |
| "Two registers could work, I will pick the better one." | Selecting voice is the author's call, not the amanuensis's. | Use the selected register; if none is selected, stop and ask. |
| "One more round will make the first passage perfect." | Perfection loops hide as diligence and delay the author's real response to a candidate. | Write the smallest faithful candidate with gaps visible. |
| "This draft is good enough to drop into the manuscript." | Composing is candidate work; the manuscript is behind the controlled write. | Write to drafts; route through `controlling-manuscript-writes`. |
| "A citation here would be persuasive, I recall one." | A recalled citation is untrusted until verified. | Mark it needed; verification is the adversarial audit's job. |

## Red flags: stop if you catch yourself

- Drafting from a one-line prompt with no preserved source or author statement behind it.
- Treating an exploratory passage as if it were a structured candidate draft.
- Drafting a structured candidate from a preserved source fragment before it has been structured or marked unclassified.
- Letting character roleplay cross-contaminate another character's voice or knowledge.
- Asking the author to manage sub-agents for a normal dramatic question.
- Keeping the author in questions after one faithful candidate passage can begin.
- Inventing a statistic, quote, source, or anecdote.
- Choosing a voice the author did not select.
- Writing straight into `manuscript/` instead of `drafts/`.

## Output shape

```markdown
## Candidate draft: <work> / <candidate level>
Candidate level: exploratory passage | structured candidate draft
Register used or provisional voice cue:
Claims drawn on (ids):
Gaps in this draft: [AUTHOR: needed — ...]

<draft text, clearly marked CANDIDATE>
```

## Next

A candidate goes to `reading-sympathetically` or `diagnosing-text` for response, then to `editing-faithfully` for proposals. It enters the manuscript only through `controlling-manuscript-writes`.
