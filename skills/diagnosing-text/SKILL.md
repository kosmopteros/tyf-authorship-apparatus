---
name: diagnosing-text
description: Use when the author asks what is wrong, why something does not work, where structure fails, where logic breaks, why a passage feels off, or wants a diagnosis at any zoom level without an edit being made
---

# Diagnosing text

## Overview

Diagnosis inspects work that already exists. It diagnoses and changes nothing. It can inspect any band, from the whole argument down to the glyph.

It is read-only. It identifies issues and separates the problem from any proposed fix.

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

## Red flags: stop if you catch yourself

- Editing the text while "explaining" the problem.
- Diagnosing across every band when one was asked for.
- Reporting taste as defect.

## Output shape

```markdown
## Diagnosis
Band:
Severity:
Issue:
Why it matters:
Possible direction (not an edit):
```

## Next

For the felt experience, use `reading-sympathetically`. To turn a diagnosis into proposals, use `editing-faithfully`. For an adversarial pass before done, use `auditing-adversarially`.
