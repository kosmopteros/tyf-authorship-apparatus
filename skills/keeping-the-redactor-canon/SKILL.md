---
name: keeping-the-redactor-canon
description: Use when terminology must stay consistent, when cross-references or citations form an apparatus, when an argument must not contradict itself, when typographic finish matters, or when any pass needs the integrity rules and running style sheet for a work
---

# Keeping the redactor canon

## Overview

The redactor is the integrity substrate, parallel to voice. Voice registers govern how the work sounds; the redactor canon governs whether the work holds together. It is the Milchin (редактор) tradition: factual accuracy, logic, composition, language and style, and the apparatus, not the narrow Anglophone sense of typesetting.

The Canon is read and updated by every Diagnose, Propose, Revise, and Audit pass, at every band. The redactor is not a band. It is a layer the bands all consult, the way every pass consults the voice registers.

## The three magnifications

The same integrity discipline runs at every zoom level.

- **micro** (glyph, sentence): punctuation, em-dash discipline, cadence, the typographic finish. The lower-band typographer canon lives here and is shared across registers.
- **macro** (section, architecture, argument): terminology consistency, kept promises, compositional balance, logical coherence, no orphaned or circular claims, sound transitions.
- **meta** (the whole work, across sessions): the canon itself plus the running style sheet, the persistent record every pass reads before touching prose and writes to after.

## What the Canon holds

- **Terminology register:** canonical terms and their forbidden variants. "Synthesized respondents", never "synthetic personas", is a terminology rule, not a style preference.
- **Logic rules:** the claim graph must not contradict itself; every load-bearing claim resolves; assumptions are stated.
- **Composition rules:** each part makes a promise the work keeps; sequence is deliberate.
- **Apparatus rules:** citation style, cross-reference format, note conventions, index discipline. Cross-references must resolve to real targets. Documentation that routes behavior is apparatus too: when structure or naming changes, the routing docs must stay true. See `keeping-documentation-honest`.
- **Typographic finish:** the five-scale typographer canon, including em-dash discipline. Shared across all registers.

## The running style sheet

Each work carries `works/<id>/style-sheet.md`. It is the redactor's working instrument: a living record of every decision made about terminology, apparatus, and finish for that work. Every pass appends decisions to it and reads it before proposing. The style sheet is how a decision made in chapter two survives to chapter nine.

## The disciplined move

At each band, run the integrity checks for that magnification and reconcile against the style sheet. Diagnose reports integrity defects. Propose conforms edits to the canon and records new decisions. Audit treats a terminology drift, a broken cross-reference, or a logical contradiction as a finding, not a quibble. The redactor proposes and records; it never disposes, and it never overrides the author's voice. Where voice and canon seem to conflict, the register fence wins on voice and the canon wins on integrity; surface the tension rather than silently resolving it.

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "Terminology variation reads more naturally." | Drift between terms is a defect the reader pays for. | Hold the canonical term; log variants as forbidden in the style sheet. |
| "Typographer means punctuation only." | Milchin is structural and logical integrity across all bands. | Run macro checks too: terminology, cross-refs, logic, composition. |
| "This cross-reference is probably fine." | A reference that does not resolve is a broken apparatus. | Verify the target exists; flag it if it does not. |
| "I will keep the style decisions in my head." | A decision not written down does not survive the session. | Append every decision to the running style sheet. |
| "Integrity overrides the author's odd phrasing." | Voice is fenced; the canon governs integrity, not taste. | Keep the voice; raise the integrity issue separately. |

## Red flags: stop if you catch yourself

- Treating the redactor as a glyph-only pass.
- Letting two terms for one concept coexist unflagged.
- Proposing an edit without consulting the style sheet.
- Resolving a voice-versus-integrity tension silently.

## Output shape

```markdown
## Redactor canon entry: <work>
Magnification: micro | macro | meta
Kind: terminology | logic | composition | apparatus | finish
Rule / decision:
Applies to:
Recorded in style-sheet: yes
```

## Next

The diagnosis pass runs these checks in Diagnose, the editor enforces them in Propose and controlled Revise, and the adversarial audit audits them at the end. All three read this Canon.
