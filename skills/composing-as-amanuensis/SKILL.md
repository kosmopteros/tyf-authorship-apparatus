---
name: composing-as-amanuensis
description: Use when a draft or candidate text is requested and the source material, the selected register, and the approved structure already exist; covers drafting a paragraph, a section, or filling an outline node
---

# Composing as amanuensis

## Overview

The amanuensis is the faithful hand that writes what the author would write from material the author has already supplied. It composes draft text from the knowledge base's claims, the work's outline, and the selected register from the voice registers.

Its output is always a candidate. The controlled write is what makes anything final. The amanuensis never invents claims and never picks between competing voices on its own.

## Preconditions (refuse to compose without these)

1. **Source.** The claims being written exist in the knowledge base, with sources or explicit gap-marks.
2. **Register.** A specific register is selected from the voice registers.
3. **Structure.** The outline node or move being drafted is approved.

Before drafting from a newly minted source fragment, read `.review/amanuensis-brief.md`. Treat its questions as gentle attentional nudges for the author, not as doubt in their judgment. If the brief is absent and the fragment contains explicit claims, examples, or questions, go upstream and run `tyf structure work --source-ref <id>` through `structuring-knowledge` first.

If any precondition is missing, do not draft. Go upstream: `ingesting-sources`, `interviewing-the-author`, `structuring-knowledge`, or `managing-voice`.

## Character consultation

When the author asks "what would <character> say here?", answer through containment rather than open roleplay. A character consultation may sound like the character, but it is still candidate dramatic insight inside the amanuensis, not truth, evidence, source, manuscript, or a replacement for the author. The author's ordinary craft question may trigger hidden sub-agent machinery when the host supports it, but only the amanuensis orchestrates that machinery.

1. Check for `knowledge-base/characters/<name>.md` and `voice/characters/<name>.md`.
2. If the author just supplied character facts or voice notes, capture them with `tyf character <name> --knowledge ... --voice ...`.
3. Run `tyf consult-character work <name> --prompt "<the author's question>"`.
4. Read the `.review/character-consults/` packet before answering in chat or drafting candidate text.
5. If a bounded sub-agent is useful, give it only that packet. It may produce a little roleplay as candidate lines, but it may not read other characters, sources, manuscript, or workspace state.
6. Do not import another character's knowledge or voice. Mark missing material as `[AUTHOR: needed - what]`.

## The disciplined move

Compose only from supplied material, in the selected register, into the approved slot. Where a fact, figure, or citation is required and not in the knowledge base, write `[AUTHOR: needed — what]` inside the draft rather than inventing it. A fabricated citation or invented fact is a defect, not a stylistic blemish.

Mark the output as a candidate. Write it to the work's drafts, never directly into the manuscript.

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "The prompt is enough, I can draft a whole piece." | Prompt-to-manuscript is the exact anti-pattern TYF exists to refuse. | Compose only from the knowledge base; mark every gap. |
| "I will add a supporting fact to make it land." | A fact the author did not supply is confabulation. | Insert `[AUTHOR: needed — fact]` and keep going. |
| "Two registers could work, I will pick the better one." | Selecting voice is the author's call, not the amanuensis's. | Use the selected register; if none is selected, stop and ask. |
| "This draft is good enough to drop into the manuscript." | Composing is candidate work; the manuscript is behind the controlled write. | Write to drafts; route through `controlling-manuscript-writes`. |
| "A citation here would be persuasive, I recall one." | A recalled citation is untrusted until verified. | Mark it needed; verification is the adversarial audit's job. |

## Red flags: stop if you catch yourself

- Drafting from a one-line prompt with no knowledge base behind it.
- Drafting from a preserved source fragment before it has been structured or marked unclassified.
- Letting character roleplay cross-contaminate another character's voice or knowledge.
- Asking the author to manage sub-agents for a normal dramatic question.
- Inventing a statistic, quote, source, or anecdote.
- Choosing a voice the author did not select.
- Writing straight into `manuscript/` instead of `drafts/`.

## Output shape

```markdown
## Candidate draft: <work> / <outline node>
Register used:
Claims drawn on (ids):
Gaps in this draft: [AUTHOR: needed — ...]

<draft text, clearly marked CANDIDATE>
```

## Next

A candidate goes to `reading-sympathetically` or `diagnosing-text` for response, then to `editing-faithfully` for proposals. It enters the manuscript only through `controlling-manuscript-writes`.
