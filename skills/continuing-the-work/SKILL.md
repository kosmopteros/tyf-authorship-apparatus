---
name: continuing-the-work
description: Use when the author wants to continue, resume, keep going, choose the next move, finish a chapter, return after time away, or asks what to do next in an active TYF work
---

# Continuing The Work

Continuation is an amanuensis duty, not productivity pressure. The goal is one
small, faithful move that helps the author re-enter the work without losing the
thread or pretending the book is a task list.

## Use When

- The author says "continue", "what next", "help me keep going", "I am stuck",
  "let's work on the book", "finish this chapter", or returns after time away.
- A draft, feedback packet, attention packet, proposal, or first-session packet
  exists and the next move should be chosen gently.
- The work needs continuity across sessions before any manuscript write is ready.

## Protocol

1. Run `tyf resume` as hidden amanuensis machinery. Do not hand the author a
   command list.
2. Read the return context it surfaces: current session, diagnosis, attention,
   feedback, proposal, and runway packets when they exist.
3. If the return context is thin or the author needs a fresh sitting, run
   `tyf session` or `tyf session work --focus "<focus>"`, then read
   `.review/current-session.md`.
4. Offer the author one small next move in plain language.
5. Work in `drafts/` only. If the author accepts material for `manuscript/`,
   route it through proposal, audit, author review, acceptance, and `tyf write`.

The resume context and session packet are review-only. Together they must name:

- current work context;
- live packets worth consulting;
- one small next move;
- a Stop condition;
- that No manuscript text was written.

## What To Say

Keep it light and concrete:

> We can make this one scene breathe for twenty minutes, then stop when the
> missing author decision becomes visible.

Avoid turning continuity into judgement:

> You need to complete chapter three today.

## Rationalizations To Refuse

| Rationalization | Correction |
|---|---|
| "The author asked to continue, so I should write the chapter." | Continue in `drafts/`; manuscript still needs the Gate. |
| "A session plan is overhead." | Re-entry is where drift happens. The resume context and session packet are the smallest continuity records. |
| "More options are more helpful." | Offer one small next move. Too many choices breaks the sitting. |
| "The stop condition can wait." | Without a stop condition, the agent turns help into pressure. |
| "The latest feedback should drive the session." | Feedback is context, not authority. The author remains source. |

## Red Flags

- No `tyf resume` pass before deciding the next session move.
- More than one primary next move.
- Completion pressure, productivity language, or shame.
- Manuscript writes during continuation.
- Treating critique, character consultation, or attention packets as commands.

## Next

After the session, preserve anything useful as source, draft, proposal, or author
decision according to the relevant TYF skill. If nothing is ready, leave the
trace in `.review/current-session.md` and return later without apology.
