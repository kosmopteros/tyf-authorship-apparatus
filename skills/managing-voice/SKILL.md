---
name: managing-voice
description: Use when voice, style, register, tone, or "make it sound like me" is in play; when text drifts into generic AI cadence; when a passage in one register risks being corrected toward another; or when an author's registers and anti-patterns need recording
---

# Managing voice

## Overview

Voice is an input every pass reads from, not a filter applied at the end. The voice registers is a library of registers, not one voice document. A single author writes in several: public, intimate, strategist, internal, investor-facing. A workspace may also hold a co-author's or interview subject's licensed voice.

Every Diagnose, Propose, and Revise pass at every band reads the relevant register before touching prose.

Fictional or dramatic characters are kept narrower than author registers. Character voice notes live under `voice/characters/`, and character knowledge notes live under `knowledge-base/characters/`. A character consultation may borrow cadence from that character dossier, but it may not borrow another character's knowledge, another register's authority, or the author's voice as evidence.

## What a register holds

- **Voice anchors:** a handful of calibrated sentences that sound unmistakably like this author in this register.
- **Sentence and punctuation patterns:** how they build a line.
- **Anti-patterns:** cadences and phrases the author never uses. This list grows when the author rejects a phrasing more than once.
- **Exemplar passages:** annotated samples of the author's own prose in the register.
- **Character voice notes:** isolated notes for one named character when the work needs dramatic consultation.

The lower-band component (punctuation discipline, dash rules, the typographer canon) is shared across all registers for a work and must honor that work's writing language, so a line-level pass never proposes something the glyph-level rules forbid.

## The disciplined move

**Register fence.** A passage written in register X is not corrected toward register Y. Identify the register before editing. Honor the fence. "More professional" does not mean "standard SaaS polish" unless the author's register says so.

**AI-tell.** At the sentence and paragraph bands, flag low-entropy, high-cliché, machine cadence. Failing prose is sent back to Propose; it is never silently auto-rewritten.

**The honest ceiling.** The system reaches roughly 80% voice match. The final 20% is the author's, by hand, by design. Do not claim the last 20%.

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "More professional means cleaner and more standard." | Standardizing erases the productive strangeness that is the voice. | Read the register; preserve what the author's anchors show. |
| "This odd phrasing is a mistake, I will smooth it." | Distinctive cadence often reads as error to a generic ear. | Check it against the register's anchors before changing anything. |
| "I can infer the register well enough to start editing." | A guessed register is how voice gets flattened. | Identify or ask the register first; otherwise diagnose, do not revise. |
| "I will rewrite the AI-sounding line to save a step." | Auto-rewrite skips the controlled write and the author's judgment. | Flag it and route to `editing-faithfully` as a proposal. |

## Red flags: stop if you catch yourself

- Editing toward generic polish without naming the register.
- Removing a quirk that appears in the author's exemplars.
- Auto-rewriting flagged machine cadence instead of proposing.
- Claiming the output is fully in the author's voice.
- Treating a character consultation as permission to invent the character's private knowledge.

## Output shape

```markdown
## Register: <name>
Voice anchors:
Sentence / punctuation patterns:
Anti-patterns (grows on repeated rejection):
Exemplar passages (annotated):
Register fence note (where this register applies):
```

## Next

Registers feed every Diagnose, Propose, and Revise pass. AI-tell findings route to `editing-faithfully`. Voice never reaches the manuscript except through `controlling-manuscript-writes`.
