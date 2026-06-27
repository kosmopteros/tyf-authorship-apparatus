---
name: auditing-adversarially
description: Use when the work is near publish, final, or done; when the author says "perfect" or "ship it"; or when a unit needs an adversarial pass for frame-lock, unsupported claims, hidden assumptions, machine cadence, register cross-talk, or unverified citations
---

# Auditing adversarially

## Overview

Nothing is done until it has been attacked. The adversarial audit runs before any unit is marked complete. It optimizes the work against its own best objections, not against a score.

It is read-only. It attacks, records findings to the review log, and changes nothing.

## What it attacks

- **Frame-lock.** The work assumes its own frame and never tests it. Name the unexamined frame.
- **Unsupported claims.** Cross-check load-bearing claims against the claims index. Any claim without a verified source is a finding.
- **Hidden assumptions.** Surface what the argument needs to be true but never states.
- **Machine cadence.** Flag low-entropy, high-cliché passages that read as generated.
- **Register cross-talk.** Catch a passage drifting out of its declared register.
- **Citation integrity.** Treat every citation as untrusted until verified against a real index through MCP (for example Zotero or Scite). A model-generated DOI, page number, or quotation is a defect until confirmed.
- **Redactor integrity (Milchin).** Attack the work's internal integrity at every band: terminology drift between chapters, cross-references that do not resolve, logical contradiction across the argument, promises a part makes and the work never keeps, and typographic finish. Check against the running style sheet. See `keeping-the-redactor-canon`.

## The disciplined move

Attack hard, then stop. The adversarial audit does not fix and does not soften. "The author said perfect" is the trigger to audit, not permission to skip it.

**Audit without a score.** There is no number to clear. The audit passes when every finding has been answered by the author: fixed, or explicitly accepted with a reason, logged in `.review/`. An unanswered finding means the unit is not done.

**Delivery is part of faithfulness.** Faithfulness includes helping the author finish. Distinguish what is unresolved and consequential from what is imperfect but alive, ready enough to meet a reader, or better held for the next edition. Do not confuse further possible improvement with a reason not to deliver.

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "The author said it is perfect, no audit needed." | "Perfect" is exactly when frame-lock hides. | Run the attack anyway; that is what the trigger means. |
| "The citation looks right, I will accept it." | A plausible citation is the most dangerous kind. | Verify against a real index; mark unverified until confirmed. |
| "I found the problem, I will fix it while I am here." | Fixing makes this a controlled Revise, not an audit. | Log the finding; route fixes to `editing-faithfully`. |
| "Most findings are minor, the unit is basically done." | "Basically done" with open findings is not done. | The unit is done only when every finding is answered. |
| "Assigning a score would make this feel objective." | A score hides judgment behind a number. | Replace the score with answered findings. |
| "I can imagine one more improvement, so this cannot ship." | Possible improvement is not the same as a blocking finding. | Name the concrete risk, or record it as next-edition work and finish. |

## Red flags: stop if you catch yourself

- Skipping the audit because the author sounded satisfied.
- Accepting a citation you did not verify.
- Editing the manuscript during the audit.
- Marking a unit done with unanswered findings.

## Output shape

```markdown
## adversarial audit findings: <work> / <unit>
Finding (frame-lock | unsupported | assumption | cadence | register | citation | terminology | cross-ref | logic | composition):
Where:
Why it breaks:
Status: open | fixed | accepted-with-reason

Audit verdict: PASSED only when no finding is open.
```

## Acceptance and edge cases

- **"Perfect, ship it" under deadline:** that phrase is the trigger to audit, not permission to skip. Run it anyway.
- **Citation index unavailable** (offline, no MCP): mark citations unverified and say verification could not run. Never imply a citation passed when it was never checked.
- **Dozens of findings on a large unit:** order by severity, load-bearing first; do not dump an unprioritized wall.
- **A finding the author consciously accepts** (a deliberate provocation): allow accepted-with-reason as a resolved state; do not block "done" forever.
- **A possible improvement that is not a blocking defect:** log it as next-edition work if useful. Do not keep the author permanently provisional.
- **The attack turns on the author:** attack the argument, never the person; an adversarial pass stays civil.

## Next

Findings go to `editing-faithfully` for proposals and to the author for decisions. No fix reaches the manuscript except through `controlling-manuscript-writes`.
