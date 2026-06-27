# Workbench adversarial product critique after PR #5

Status: adversarial product review after merging the local Workbench baseline and the live-status/approval-state slice.

This critique assumes the current merged state includes:

- local multi-unit Workbench
- editable draft units with hash-guarded saves
- read-only manuscript preview
- author notes, footnote candidates, Gate packets, and context packets
- MCP bridge for active context and safe actions
- local Codex bridge scaffold
- Codex hook/status files
- live Workbench status polling
- stale draft badge model
- local approval request/decision state
- `tyf-workbench` package entry point

The question is not whether the architecture is elegant. The question is whether this is now close to a real authoring product for someone trying to write two books.

## Adversarial council

### 1. Daily author reviewer

**Attack:** The product is still at risk of feeling like a control panel rather than a writing desk. The live status cards help, but the author still has to understand Codex status, bridge status, approval state, Gate packets, context packets, notes, and drafts.

**Convergence:** The next UX goal should be to hide machinery until needed. The side panel should answer three human questions:

- What am I writing now?
- What does the amanuensis know about this moment?
- Is anything unsafe or stale?

### 2. Momentum reviewer

**Attack:** The author can now write, but the cognitive jump from writing prose to preparing Gate/context/footnote packets is still a procedural break. The Workbench may preserve safety while interrupting flow.

**Convergence:** The primary action should not be “packet.” It should be author-language actions like:

- Ask about this
- Remember this
- Make this a footnote candidate
- Prepare for manuscript review

The underlying packet names can remain local files, but the UI should stop speaking packet-first.

### 3. Trust-boundary reviewer

**Attack:** The product says manuscript is protected, but users will not trust a boundary they cannot see. “Read-only” text is present, but the visible affordance should be stronger: manuscript pane should feel like a locked reference, not a second editor.

**Convergence:** Add a persistent manuscript lock badge and a small explanation: “This pane cannot write. Accepted material moves through review.”

### 4. Codex-skeptic reviewer

**Attack:** The Workbench currently assumes Codex adds value once it knows the active selection. But the author’s pain is not only context transfer; it is continuity, judgment, and reduction of machine-operation burden.

**Convergence:** The amanuensis path should default to reading the active context automatically and proposing next actions, not asking the author to explicitly generate context packets.

### 5. Product-scope reviewer

**Attack:** The PRs have implemented a lot of infrastructure before proving the smallest repeatable author loop. There is a danger of building the cockpit before the writing habit exists.

**Convergence:** Define a single golden loop and optimize only that:

1. open Workbench
2. select unit
3. write
4. highlight awkward passage
5. ask Codex about it through MCP
6. save note or candidate
7. keep writing

Everything else is secondary until that loop is joyful.

### 6. UX language reviewer

**Attack:** “Codex status,” “approval requests,” “Gate packet,” “Amanuensis context,” and “stale draft” are accurate but operational. Authors do not want to manage distributed systems while writing.

**Convergence:** Introduce user-facing language:

- Desk memory
- Assistant sees this passage
- Needs review
- Safe to save
- Changed outside this window
- Ready for manuscript review

Keep technical terms in file paths and docs, not primary UI.

### 7. Concurrency reviewer

**Attack:** Hash-guarded saves are strong, but the stale badge is currently informational. It does not yet guide the author through recovery. A stale warning without a merge/reload decision can cause panic.

**Convergence:** The product needs a conflict recovery flow:

- Reload disk version
- Keep my browser version as a new draft copy
- Show both versions
- Copy my version to clipboard

Do not implement auto-merge yet. Give authors safe choices.

### 8. Approval reviewer

**Attack:** Approval events are now modeled locally, but not actionable in the browser. Showing approval state without an approve/reject route risks turning the UI into a dead indicator.

**Convergence:** The next approval slice must distinguish:

- observed approval request
- author decision recorded locally
- decision sent back to Codex/app-server
- result acknowledged by Codex

Until all four exist, browser-native chat remains visibly incomplete.

### 9. MCP reviewer

**Attack:** MCP tools are safe, but the author will not know whether Codex actually used them. Without visible proof, the old “did it see my context?” anxiety remains.

**Convergence:** Workbench should show last MCP/context use:

- active selection read at time X
- note created by Codex
- Gate packet prepared by Codex
- no manuscript write occurred

This is not just logging; it is author reassurance.

### 10. Installation reviewer

**Attack:** `tyf-workbench` is better than a script path, but it splits the user mental model from `tyf`. Authors will ask: do I use `tyf`, `tyf-workbench`, Codex, or the browser?

**Convergence:** `tyf workbench` should become the canonical command. `tyf-workbench` can remain a packaging shortcut.

### 11. Testing reviewer

**Attack:** Tests cover helpers and invariants, but not the rendered browser behavior. The riskiest product promise is in injected HTML/JS and the daily loop.

**Convergence:** Add a generated-HTML assertion test that verifies:

- Codex status card exists
- Draft state card exists
- Approval card exists
- `/api/live-status` is referenced
- stale badge language is present

No browser automation is needed yet. Static HTML assertions would catch template drift.

### 12. Founder/product reviewer

**Attack:** The project has a strong safety philosophy, but the author’s buying reason is not safety. The buying reason is: “I can finally write inside the apparatus without becoming its operator.”

**Convergence:** Every next slice should be judged by time-to-writing and time-to-return-to-writing, not by architectural completeness.

## Where the critique converges

### Convergence 1: The architecture is now ahead of the product surface

The local/MCP/bridge/hook/status architecture is coherent. The product risk has moved to UX: the author still sees too much machinery.

### Convergence 2: The next slice should be a golden-loop UX slice

Do not build more bridge depth before making the daily writing loop feel calm.

The golden loop:

```text
Open Workbench -> write -> select passage -> ask/remember/review -> keep writing
```

### Convergence 3: Conflict recovery matters more than more conflict detection

The stale badge is good. Now it needs safe choices.

### Convergence 4: Approval state must become an actual interaction

Approval files are useful, but the Workbench needs an author-visible decision path before browser-native chat can be trusted.

### Convergence 5: The main command must be unified

`tyf-workbench` is useful, but `tyf workbench` should become canonical.

## Product decision after this critique

The next product slice should not be “more Codex.”

It should be:

1. Rename primary UI actions away from packet language.
2. Add a calm conflict recovery flow.
3. Show “assistant saw this context” reassurance.
4. Add static HTML tests for the live side panel.
5. Wire `tyf workbench` into the main command surface.

## Proposed next PR

Title:

```text
Make the Workbench daily author loop calmer
```

Scope:

- UI wording pass:
  - “Amanuensis context” -> “Ask with this context” or “Share this moment”
  - “Gate packet” -> “Prepare for manuscript review”
  - “Footnote candidate” -> “Make footnote candidate”
- conflict recovery affordance:
  - “Reload from disk”
  - “Save my version as copy”
- assistant-context reassurance card:
  - last context packet path/time
  - last MCP/Codex status if present
- static HTML tests for side-panel markers
- `tyf workbench` command entry in `scripts/tyf.py` if the parser shape allows a small safe insertion

Out of scope:

- full embedded Codex chat
- automatic merging
- real-time collaboration
- app-server approval round-trip
- semantic graph database

## Verdict

The Workbench is now technically credible. The adversarial product finding is that technical credibility is no longer the bottleneck.

The bottleneck is whether the author can stay in the writing trance. The next improvements should remove operational language, add recovery choices, and make the assistant’s awareness visible without making the author operate the apparatus.
