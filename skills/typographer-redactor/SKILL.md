---
name: typographer-redactor
description: Use when a substantial draft, manuscript chapter, or full-work body needs typographic craft, language treatment, AI-cadence cleanup, rubrication, apparatus, or Milchin-style redactor review
---

# Typographer Redactor

## Overview

The typographer-redactor prepares an existing body of work for the reader. This is real craft, not punctuation decoration: the Milchin tradition of facts, logic, composition, rubrication, language and style, plus language-specific typographic finish.

Use this when the work already has a body and the useful move is treatment rather than discovery. Do not ask philosophical entry questions when the draft is already 80 percent there. Treat the page, the paragraph, the chapter, and the body as reader instruments.

## The disciplined move

Run:

```bash
tyf treat
```

or, for a bounded sample:

```bash
tyf treat work --unit manuscript/<file> --focus "<treatment focus>"
```

Read `.review/typographic-treatment.md` before proposing edits. The packet is review-only. It may guide a candidate treatment in `drafts/` or editorial proposals in `.review/`, but it never authorizes a manuscript write.

## Milchin passes

Run the passes separately. Do not collapse them into "make it better".

- **Facts/source status:** mark claims, figures, names, quotations, citations, and source gaps before improving sentences.
- **Logic:** test whether the reasoning follows and whether connectives earn their force.
- **Composition:** test whether the order of sections and paragraphs is the path the reader needs.
- **Rubrication:** test whether headings, breaks, and chapter architecture form a load-bearing skeleton.
- **Language and style:** treat precision, rhythm, register, voice, and AI cadence after the earlier passes are named.
- **Typographic finish:** apply the work's writing-language rules for punctuation, quotes, spacing, numerals, notes, and apparatus.

## Full-work body posture

When `manuscript/` already contains chapters, prefer a body treatment over a fresh interview. Inventory the body, pick a representative sample, and propose a treatment pass of roughly 500 to 800 words before scaling to the whole work. Use the strongest author-authored passages as the style key. If Act I is clearly the best register anchor, use it as the treatment standard for later acts.

The meta/corpus layer is out of scope for this beta posture unless the author explicitly asks for it. Stay inside the single work: body, chapters, sections, notes, illustrations, front matter, back matter, and apparatus.

## What To Fix

- Machine cadence: stock phrases, over-balanced clauses, uniform sentence lengths, "not just X" patterns, inflated abstractions.
- Typographic finish: straight quotes in prose, ASCII fallbacks, ellipses, dash intent, spacing, numerals, unit binding, heading punctuation.
- Redactor continuity: terms of art, forbidden variants, unresolved cross-references, orphan claims, inconsistent illustration references.
- Rubrication: decorative headings, false parallelism, over-nesting, missing section breaks, weak chapter openings or landings.

## What Not To Do

- Do not rewrite the argument because you can phrase it more cleanly.
- Do not replace the author's productive strangeness with generic polish.
- Do not apply treatment directly to `manuscript/`.
- Do not treat a whole book with one global find-and-replace.
- Do not apply English punctuation rules to a non-English work.

## Output Shape

```markdown
## Typographic treatment proposal: <unit>
Scope:
Register honored:
Milchin pass:
Treatment targets:
Sample before:
Sample after:
Reason:
Open author decisions:
(Nothing applied. Acceptance required via the controlled write.)
```

## Next

Accepted treatments go through `editing-faithfully` and `controlling-manuscript-writes`. The typographer-redactor proposes craft; the author accepts; the Gate writes.
