---
name: diagnosing-text
description: Use when the author asks what is wrong, why something does not work, where structure fails, where logic breaks, why a passage feels off, or wants a diagnosis at any zoom level without an edit being made
---

# Diagnosing text

## Overview

Diagnosis inspects work that already exists. It diagnoses and changes nothing. It can inspect any band, from the whole argument down to the glyph.

It is read-only. It identifies issues and separates the problem from any proposed fix. The question is never "is the author wrong?" The question is "what is the smallest cause of the reader's difficulty, and what single experiment would reveal it?"

When a passage or unit feels off, run:

```bash
tyf diagnose [work] --unit drafts/candidate-draft.md --band section --symptom "<what the reader experiences>"
```

The helper writes `.review/current-diagnosis.md` and an archived `.review/diagnostics/<id>.md` review-only diagnostic isolation packet. Read it before answering. The packet is hidden amanuensis machinery: it surfaces band, reader symptom, cause hypotheses, source/register reminders, and one next experiment. No manuscript text is written.

## The bands

| Band | Scope | Primary question |
|---|---|---|
| Argument | the whole work | Does the thesis hold, and is the claim graph sound? |
| Architecture | parts and chapters | Does the sequence make and keep its promises? |
| Section | moves within a chapter | Does each move land; is each local claim evidenced? |
| Paragraph | the paragraph | Unity, rhythm, register consistency. |
| Sentence | the line | Cadence; machine-cadence detection. |
| Glyph | punctuation and type | Em-dash discipline, punctuation, typographic finish. |

## The disciplined move

Name the band before diagnosing, because a fix at the wrong band is noise. State the problem and why it matters; keep any direction for a fix separate and clearly labeled as not-yet-an-edit. Distinguish a defect from a matter of taste; the author owns taste.

The diagnosis pass never rewrites. If the author wants the change made, that is a different pass behind the controlled write.

Use systematic isolation when the cause is unclear:

1. Name the reader symptom in experiential terms.
2. Choose one band only: argument, architecture, section, paragraph, sentence, or glyph.
3. Read the source/register reminders before deciding whether the issue is evidence, structure, voice, cadence, or taste.
4. Offer one next experiment or one gentle question, not a fix-list.

## Redactor layer (Milchin)

At every band the diagnosis pass also runs the integrity checks from `keeping-the-redactor-canon`, reconciled against the work's running style sheet.

- micro (glyph, sentence): punctuation, em-dash discipline, cadence.
- macro (section, architecture, argument): terminology drift, broken cross-references, logical contradiction, kept promises, composition.
- meta (whole work): consistency against the style sheet across the whole work.

These are diagnosed and reported here, never fixed here.

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "I see the fix, I will just apply it." | Applying anything makes this a Revise pass, which is controlled. | Report the issue and a possible direction; stop there. |
| "Terminology is a style quibble, not a defect." | Drift between terms for one concept is a Milchin integrity defect. | Diagnose it against the canon; report it as macro. |
| "This phrasing is wrong." | It may be the author's register, not an error. | Check the register; flag as taste if it is not a defect. |
| "Diagnosing the whole thing at once is efficient." | Cross-band noise buries the load-bearing problems. | Pick the band the author asked about; diagnose at that magnification. |
| "I know why it fails to land." | A confident cause can be a guess. | Use `tyf diagnose` to isolate the symptom, band, and one next experiment. |
| "The author needs to justify this choice." | Diagnosis is attention, not doubt in the author's judgment. | Ask only the gentle question that reveals the missing support, promise, or register cue. |

## Red flags: stop if you catch yourself

- Editing the text while "explaining" the problem.
- Diagnosing across every band when one was asked for.
- Reporting taste as defect.
- Producing a list of fixes before the smallest cause is isolated.
- Answering without reading `.review/current-diagnosis.md` when the author asked why it does not land.

## Output shape

```markdown
## Diagnosis
Band:
Severity:
Issue:
Why it matters:
Possible direction (not an edit):
One next experiment:
```

## Next

For the felt experience, use `reading-sympathetically`. To turn a diagnosis into proposals, use `editing-faithfully`. For an adversarial pass before done, use `auditing-adversarially`.
