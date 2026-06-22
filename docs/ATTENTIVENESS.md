# Attentiveness: memory without git, and whose word wins

The attentive loop (`tyf notice`) surfaces what the author may have forgotten or left unfinished. Two hard questions decide whether it is useful or just noisy: how does it remember what it already saw, without git, and what does it do when the author said contradictory things at different times. This document answers both.

## The ledger: content-addressed, not time-addressed

The loop keeps a small SQLite database, `.tyf/ledger.db` (using Python's stdlib `sqlite3`, so no third-party dependency). For every item it has ever surfaced it stores a fingerprint of the *content the item is about* (the gap line, the unfinished sentence, the claim row), a fingerprint of the *surrounding context*, and a status: open, dismissed, or resolved.

For style-sheet lag, timestamps remain only the first hint. If a manuscript file is newer than the style sheet but its content hash matches the latest controlled `tyf write` record, and the style sheet still carries the core language and decision sections, TYF treats that as a clean controlled write rather than a style problem. It still surfaces lag for direct or unlogged manuscript changes, changed hashes, or a style sheet missing its core metadata.

The fingerprint is a hash of normalized text, whitespace-insensitive, so a reflow or reindent does not read as a new item. Crucially it is keyed on *what was said*, never on *when*. This matters because TYF cannot assume git, and filesystem timestamps lie: a sync tool, a copy, a Cowork file operation, or an editor "save all" changes mtime without changing content, and a restore can do the reverse. So the loop uses mtime only as a cheap hint about what is worth re-reading, never as the thing that decides what changed or what is true.

On each run the loop re-derives items from current content, hashes each, and diffs against the ledger:

- content never seen before becomes a *new* notice;
- content already open is *still open*, not re-raised as if fresh;
- content dismissed in the same context stays silent;
- content dismissed but now in a *different context* *resurfaces*, because the situation changed and the old dismissal no longer covers it;
- content that has vanished entirely is marked *resolved*, since the author's own edit settled it.

This is the temp memory reservoir, content-addressed so it survives with no git and no trustworthy timestamps. SQLite gives notice state atomic updates (a scheduled run and a write will not clobber each other) and real timestamp columns. Apparatus actions live in a separate canonical journal, `.tyf/events.jsonl`: one JSON object per action, chained by `previous_hash` and `hash`, recording actions such as init, start, begin, import, capture, adopt, write, mark-ready, dismiss, repair, and explicit snapshots. SQLite keeps a derived event mirror for count/reconcile display, but the human-readable JSONL journal is the operational history `tyf doctor` verifies. The notice index is disposable derived state, rebuildable by re-scanning content, and `tyf reconcile --export` mirrors it to Markdown for reading. The body of work itself never goes here; it stays in Markdown and YAML, owned by and legible to the author.

## Dismissal and resurfacing

`tyf dismiss <hash>` quiets an item. A dismissal is not "I am right, drop it forever." It means "I have seen this in isolation and chose to leave it." The dismissal is bound to the content *and the context it was dismissed in*. The moment that content becomes part of a new situation, for example a passage that previously stood alone now contradicts a new line, the dismissal no longer applies and the item returns, framed as the new situation rather than as a repeat of the old nag. Nothing is ever lost; settled things simply stay quiet until they stop being settled.

## Whose word wins: the system refuses to decide

The deepest version of your question has no mechanical answer. Chapter two asserts X. Chapter nine now asserts not-X. The author wrote both. There is no timestamp on a belief, and even perfect per-line history would not tell you whether the author changed their mind, wrote a deliberate tension, or simply forgot chapter two. The resolving information is tacit, in the author's head.

So the loop does not rank authored statements and never assumes the newer one wins. When it detects a conflict between two authored passages it records both, with their locations, as a single open contradiction addressed to the author: these two say opposite things; which holds, or is the tension intended. The author's answer is the only authority. If the author resolves it, the resolution is recorded in the redactor canon, and from then on it is a logged decision future runs check against. The system's twin obligations are to never lose a discrepancy and to never silently resolve one. (The semantic detection of cross-passage contradiction needs a reading pass; see `docs/LEARN_PASS.md`. The deterministic loop handles the bookkeeping, dedup, and resurfacing for whatever is surfaced, by code or by model.)

## When the ledger updates: three tiers, degrading gracefully

TYF cannot guarantee a per-message hook, because the harness owns the message loop. So capture works at three levels, and the lower two ship and work everywhere:

1. **Per-run (always).** Any time `tyf notice` runs, manually or on a schedule, it reconciles against the ledger. This is the baseline and needs nothing from the harness.
2. **Per-write (wired now).** Every `tyf write` updates the ledger and reports only genuinely new or resurfaced items, so a manuscript write never nags about things already seen.
3. **Per-message (opt-in, harness-specific).** The ideal is to capture intent continuously as the author and the assistant exchange messages, so a thought stated and then dropped is not lost. TYF cannot provide this portably, but a harness that exposes a per-message or post-turn hook can call `tyf notice --peek` (or append a one-line intent capture to `.proposals/`) on each turn. Wire it the way you wire the Learn pass: deliberately, with a known cost. Until then, per-run and per-write cover the durable cases.

The principle throughout: the loop remembers so the author does not have to, surfaces without ranking, and modifies nothing.
