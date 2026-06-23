---
name: structuring-knowledge
description: Use when raw or elicited material must become structured knowledge (concepts, claims, examples, contradictions, open questions), or when the load-bearing claims of an argument need mapping, or when a claim graph has orphans or circular support
---

# Structuring knowledge

## Overview

The knowledge base is the author's structured knowledge: concepts, claims, examples, contradictions, open questions, and the claim graph that holds an argument together. It is shared across every work in the workspace.

This skill turns the loose candidates from `ingesting-sources` and `interviewing-the-author` into a structure that later passes read from. It also carries two knowledge-band disciplines the manifesto promotes to first class: the argument spine and the claims index.

## The disciplined move

Structure is not summary. The job is to expose the architecture of what the author knows, including where it is weak, not to produce a tidy précis that hides the seams.

**Concept and claim capture.** Every load-bearing claim gets an entry. Each claim records what supports it and what it depends on.

**Argument spine.** Build the claim graph for the active work. Surface orphan claims (nothing supports them) and circular support (A leans on B leans on A). Report these; do not quietly patch them.

**Existing work recovery.** For a half-written manuscript, the first structure is `.review/existing-work-recovery.md` rather than a new outline: what sections exist, what spine seems to be present, which passages are source-backed, which are raw notes, which seem AI-drafted or uncertain, which illustrations carry argument or atmosphere, which decisions belong to the author, and which next writing move can begin.

**Claims index.** Maintain `claims.md`: every load-bearing claim mapped to at least one source in the sources. A claim with no source is flagged, never silently accepted.

**Deterministic source structuring.** For stable source fragments, prefer the helper before hand-authoring derived records:

```bash
tyf structure work --source-ref <id>
```

This pass appends source-linked knowledge records, writes `.review/amanuensis-brief.md`, updates the derived `knowledge-base/retrieval-index.jsonl` with plain-file anchors and sample questions, and leaves unclassified source material visible for the author. The helper can extract explicit English `Claim:`, `Example:`, and `Question:` labels as a convenience, but interpretation belongs to the skill-guided amanuensis. For non-English, unlabeled, or nuanced material, read the source and provide a language-neutral JSON record to `tyf structure work --source-ref <id> --record <file>` with `claims`, `examples`, `questions`, and `unclassified` arrays. The helper then validates, IDs, stores, and links; it does not become the judge of meaning. Its questions are gentle nudges of attention, not doubts in the author's judgment. It is not a summarizer, not an interrogation, and not a drafting pass.

When the next sitting needs a small source-grounded question set, run:

```bash
tyf attend work --source-ref <id> --query "<focus>"
```

That writes `.review/gentle-attention.md`. Treat it as review-only amanuensis attention: useful nudges, not audit findings, defects, or a demand that every question be answered before drafting. The retrieval section is transparent local grounding over `sources/` and `knowledge-base/`; it helps choose the next question but does not replace the author's judgment or become manuscript text.

**Gap-marking, not confabulation.** When the structure needs a fact, figure, anecdote, or citation the author has not supplied, insert `[AUTHOR: needed — what]` and stop. The system is structurally unable to pretend to know what only the author knows.

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "A clean summary is good structure." | Summary smooths over the gaps that the author needs to see. | Map claims and dependencies; expose orphans and circular support. |
| "This claim is common knowledge, no source needed." | "Common knowledge" is where unsupported assertions hide. | Add it to the claims index flagged as unsourced until the author supplies one. |
| "I can supply the obvious citation." | A model-supplied citation is untrusted until verified against a real index. | Mark `[AUTHOR: needed — citation]`; verification belongs to `auditing-adversarially`. |
| "These two claims roughly agree, I will merge them." | Merging can hide a real contradiction the author should keep. | Keep both; log the tension in contradictions. |

## Red flags: stop if you catch yourself

- Writing a summary in place of a claim graph.
- Accepting a load-bearing claim with no source.
- Inventing a citation, DOI, page number, or statistic.
- Erasing a contradiction to make the structure look finished.

## Output shape

```markdown
## Knowledge update
### Concepts
### Claims (id → statement → support → depends-on → source?)
### Argument spine (claim graph; orphans and cycles flagged)
### Examples
### Contradictions
### Open questions
### Gaps marked: [AUTHOR: needed — ...]
```

## Acceptance and edge cases

- **Legitimate co-definition vs vicious circularity:** two claims that mutually define each other are not always a defect. Distinguish a valid definitional loop from circular *support*, and present rather than condemn.
- **A claim the author calls "obvious":** keep it flagged as unsourced regardless of their confidence; obviousness is not a source.
- **A "claim" that is actually a value or preference** (not falsifiable): classify it as stance, not claim, and do not demand evidence for a taste.
- **A whole book's worth of claims:** scope the claim graph to the active unit each run; a corpus-wide graph is unreadable and unusable.
- **Unlabelled source material:** do not infer the hidden claim. Preserve it in `.review/amanuensis-brief.md` as unclassified and ask the author what it is doing.
- **A formatted prior manuscript:** do not smooth it into a summary. Fill the existing-work recovery packet with source status, draft status, voice clues, illustration inventory, open author decisions, and one next writing move before composing new candidate prose.

## Next

Voice material goes to `managing-voice`. A structured knowledge base plus a selected register unlocks `composing-as-amanuensis`; `.review/gentle-attention.md` can help choose the next author question when the path is still tacit. Source verification of the claims index happens in `auditing-adversarially`.
