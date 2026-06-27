# TYF

*The Yours Faithfully.*

*A faithful apparatus for authorship.* *Not a writer.*

---

## 0. What this is, in one line

> TYF does not generate a whole book from a single prompt. It helps you write a complete body of work on your topic, in your voice.

The "book" is shorthand. TYF's scope is any serious authored body of work: a book, an essay series, a course, a talk, a newsletter, a manifesto, an article cluster. One author's reservoir of knowledge typically produces several of these, and TYF holds all of them inside one workspace without flattening them into one voice.

## 1. Manifesto

Most AI writing tools invert the value pyramid. They treat the human as a *prompt*: one sentence in, a manuscript out. The human's role shrinks to ignition; the machine's role is production. The output is plausible and hollow, because the thing that makes a serious body of work worth reading, a specific person who knows something arranging that knowledge into an argument, was the input that got compressed to a single line.

TYF inverts the inversion. The author's knowledge, judgment, and voice are the irreplaceable material. The system's job is everything *around* generation: pulling the knowledge out of the author and holding it in durable form; checking that the argument holds; catching where the prose drifts off-voice or into machine cadence; refusing to invent facts the author has not supplied. Drafting exists, but it is downstream and subordinate, and it never happens without the author in the loop.

This is not a tone preference. It is a set of commitments enforced in the architecture, because politeness in a system prompt gets eaten by context compaction, and a principle that is not load-bearing is not a principle.

**The commitments**

1. **The author is the source, not the prompt.** The highest-value skills elicit and structure knowledge; drafting is downstream. The pyramid stands on its base.
2. **Propose, never dispose.** The system diagnoses and suggests; the author decides and applies. Enforced by the controlled write (read-only by default), not requested in prose.
3. **No confabulation.** When the system lacks knowledge, it marks a gap (`[AUTHOR: needed — what]`) rather than filling it with something plausible. A fabricated citation or invented fact is a defect, not a stylistic blemish.
4. **Voice is substrate, not finish.** The author's voice is an input every pass reads from, not a filter applied at the end. The goal is not "good writing in the abstract" but writing that sounds like *this author, in this register*. The honest ceiling is about 80% voice match; the last 20% is the author's.
5. **One operation, many magnifications.** The same disciplined pass (elicit, read, diagnose, propose, compose, revise, audit) runs at every zoom level from whole-argument to glyph. Nothing is special-cased.
6. **Nothing is done until it has been attacked.** An adversarial audit runs before any unit is marked complete. The system optimizes the work against its own best objections, not against a score.
7. **Portable and inspectable.** The body of work lives in plain Markdown and YAML a human can read. The unit of capability is a single `SKILL.md` that runs across harnesses. No black boxes, no lock-in.
8. **Patterns, not code.** TYF takes ideas and patterns from the projects in the provenance table; it does not import their code. Every borrowed primitive is reimplemented clean. This keeps the license unambiguous and forces every pattern to be re-understood rather than copied.
9. **Faithful to the roles, nothing else.** TYF is an interviewer, an amanuensis, a first reader, a faithful editor, and a redactor; all faithfully to the author. It is not a knowledge-management tool, not a productivity app, not a content engine. Every feature serves one of those five roles. Anything that does not is out.

## 2. One vocabulary

An earlier design ran two parallel registers: a technical one for contributors and a deliberately strange "ceremonial" one for authors. That has been removed. TYF now uses **one plain vocabulary.** A skill is named for what it does, and that name is identical in the file path, the frontmatter, the documentation, and the prose. There is no second surface to learn.

The five roles map to skills directly:

| Role | Skill |
|---|---|
| interviewer | `interviewing-the-author` |
| amanuensis | `composing-as-amanuensis` |
| first reader | `reading-sympathetically` |
| faithful editor | `editing-faithfully` |
| redactor (Milchin tradition; see §12) | `keeping-the-redactor-canon` |

**Voice rules for TYF's own prose.** No em-dashes in prose; use a colon, a semicolon, or a comma. No stacked-negation triads. No "Not X. Y." fragments. Avoid generic AI-writing language: *create content faster, AI-powered writing assistant, unlock your productivity, write 10x faster, get your book written.* The sign-off badge is **Authored with TYF**.

## 3. What we cross-bred, and what we rejected

The design is a synthesis. Lineage matters for an open-source project, both for credit and because every keep and reject below is a decision a contributor should be able to challenge.

| Pattern | Source | Verdict |
|---|---|---|
| Voice document as *input* to drafting | robertguss/claude-code-toolkit | **Keep, promote to substrate.** The single most important borrowed primitive. |
| "80% accuracy is the target; the human adds the final 20%" | robertguss | **Keep as stance.** Honest expectations; reserves the irreplaceable work for the author. |
| Review-then-act; read-only reviewer agents; "agents propose, humans decide" | andrehuang/academic-writing-agents | **Keep, make architectural.** Commitment #2 in code. |
| `.review/` persistence of findings; incremental re-review | andrehuang | **Keep.** Findings outlive the session. |
| Craft principles codified from a *named* authority | andrehuang; hanlulong/econ-writing-skill | **Keep, with a twist:** the authority is the author's own redactor canon, not a generic style guide. |
| State contract (`WORKSPACE_STATE` + `ASSUMPTIONS` + manifest); "one active phase at a time"; audit-before-score ordering; portable router | felipelobomotta-blip/book-genesis-v4 | **Keep the state contract and portability.** **Reject** the Genesis Score, the fiction-craft vocabulary, and the "10+ books in 30 days" volume framing. |
| `.docx` track-changes; multi-pass structural/line/copy/polish | lfurze/book-editor | **Adapt** as the output format of the Revise pass. |
| Running style sheet per pass | ghanemzadeh/claude-skills | **Keep** as the record each pass emits, now the redactor's instrument. |
| Frame-lock / devil's-advocate detection; citation-hallucination taxonomy | Imbad0202/academic-research-skills | **Keep** as the spine of the Audit pass. |
| AI-tell detection; rewriting of machine cadence | andrehuang; ThomasHoussin/Claude-Book | **Keep** as a check at the sentence and paragraph bands. |
| Zotero / Scite via MCP; claims index | 54yyyu/zotero-mcp; Scite MCP | **Keep** for citation discipline. |
| Parallel specialist reviewers, each with clean context | hamy.xyz code-review setup | **Keep as a pattern** for capable harnesses; TYF runs sequential by default. |
| Multi-agent token cost (~15x a single chat) | Anthropic multi-agent engineering post | **Keep as a constraint**, surfaced in budgeting. |
| Hooks, context management, self-extension as a portable deterministic harness; "code over prompts" | personal-infrastructure and agent-harness patterns | **Keep at the pattern level.** Becomes the iterative-phase architecture and the deterministic-first stance of the `tyf` helper. |
| "Fully autonomous, prompt in / book out" | forsonny/Claude-Code-Novel-Writer; KDP "publishing assistants" | **Reject.** The anti-pattern TYF exists to refuse. |

## 4. Four engines, one workspace

TYF is four engines feeding one structured workspace. They form a temporal arc: raw material becomes structured knowledge; structured knowledge becomes faithful draft text; draft text becomes audited, refined work.

- **The extractor.** Turns raw material into structured knowledge when the author offers sources. Input: uploads, transcripts, voice memos, PDFs, links, prior writing, fragments. Output: claims, concepts, examples, contradictions, open questions, candidate registers, recommended next moves. It preserves raw sources and seeds the knowledge base. Skill: `ingesting-sources`.
- **The interlocutor.** Interviews the author for tacit knowledge the system has no other way of reaching. Output: thesis, tensions, personal stake, core concepts, unrecorded examples, voice and register preferences, the shape of an argument that does not yet exist on paper. It seeds the knowledge base and the voice registers. Skill: `interviewing-the-author`.
- **The amanuensis.** Composes faithfully from supplied material: the knowledge base's claims, the work's outline, the selected register. It writes what the author would write from what the author has already supplied. It never invents claims and never selects between competing voices on its own. Its output is always a candidate; the controlled write is what makes it final. Skill: `composing-as-amanuensis`.
- **The editorial apparatus.** Operates on text already in a work. It contains the sympathetic read (`reading-sympathetically`), diagnosis (`diagnosing-text`), the faithful editor (`editing-faithfully`, propose then controlled revise), and the adversarial audit (`auditing-adversarially`). The controlled write (`controlling-manuscript-writes`) is the only path into the manuscript. Section 5 describes how this apparatus works.

**One workspace serves many bodies of work.** Sources are shared. Voice may be shared, inherited, or overridden. Works are separate. A single author's reservoir typically produces a book and a newsletter and a talk and a course; they overlap upstream and diverge downstream. TYF keeps the upstream coherent without forcing the downstream to converge.

Inheritance and override semantics are explicit:

- A **work** declares which registers it uses (one or more), and may declare local overrides for that work only.
- A **work** declares which subsets of the knowledge base and sources are in scope.
- A **work** owns its outline, manuscript, and review log; nothing about a work is implicit in another.

This is what prevents the generic-workspace-soup failure mode. TYF is not a knowledge-management tool. Every feature serves one of three outcomes: extract knowledge, structure an authored work, improve or audit text without stealing authorship.

## 5. The core idea: the Zoom x Pass matrix

Everything inside the editorial apparatus is one operation across two orthogonal axes. This generalizes the typographer's existing five-scale framework: that skill already proves the model works at the lower magnifications; TYF lifts the same operation up the stack to where the author's knowledge lives.

### Axis 1: Zoom (how much text is in scope)

A six-band ladder, widest to tightest. The top three are **knowledge bands**, where the author's expertise is irreplaceable and the system mostly elicits and checks. The bottom three are **craft bands**, where the typographer already operates.

| Band | Scope | Primary question |
|---|---|---|
| 1. Argument | the whole work | Does the thesis hold, and is the claim graph sound? |
| 2. Architecture | parts and chapters | Does the sequence make and keep its promises? |
| 3. Section | moves within a chapter | Does each move land; is each local claim evidenced? |
| 4. Paragraph | the paragraph | Unity, rhythm, register consistency. |
| 5. Sentence | the line | Cadence, line editing, machine-cadence detection. |
| 6. Glyph | punctuation and type | Em-dash discipline, punctuation, typographic finish. |

The new and most valuable work is bands 1 through 3, the knowledge layer, which no surveyed tool handles well.

### Axis 2: Pass (what the operation does)

| Pass | Skill | Action | Write scope |
|---|---|---|---|
| Elicit | `ingesting-sources`, `interviewing-the-author` | Pull knowledge from sources and from the author | Writes to `sources/` and `knowledge-base/` |
| Read | `reading-sympathetically` | Report the sympathetic experience of reading | Read-only |
| Diagnose | `diagnosing-text` | Identify issues; change nothing | Read-only |
| Propose | `editing-faithfully` | Suggest specific edits; apply nothing | Writes findings to `.review/` |
| Compose | `composing-as-amanuensis` | Draft from supplied material in the selected register; output is a candidate | Writes to root `drafts/` |
| Revise | `editing-faithfully` + `controlling-manuscript-writes` | Apply accepted edits to the manuscript | Writes to root `manuscript/` only via the controlled write |
| Audit | `auditing-adversarially` | Attack the unit before it is called done | Read-only; findings to `.review/` |

### The matrix

A skill is, roughly, a `(Band x Pass)` cell, though several disciplines are cross-cutting (see §7 and §12). Not every cell is filled. Elicit concentrates in the knowledge bands; Compose in the middle bands; Revise in the craft bands.

```
            ELICIT   READ    DIAGNOSE  PROPOSE  COMPOSE  REVISE   AUDIT
Argument      ●●●     ●●       ●●        ●●       ·        ·       ●●●
Architecture  ●●      ●●●      ●●●       ●●       ·        ·       ●●
Section       ●       ●●●      ●●●       ●●●      ●●       ○       ●●
Paragraph     ·       ●●       ●●        ●●●      ●●●      ●●      ●
Sentence      ·       ●        ●●        ●●●      ●●       ●●●     ●●   ← typographer
Glyph         ·       ·        ●         ●●       ·        ●●●     ●    ← typographer
                                                  ▲        ▲
                              controlled write required to enter these columns
●● = primary cell   ● = secondary   ○ = behind the controlled write   · = intentionally empty
```

## 6. The knowledge-first layer

This is the part no surveyed repo does, and the reason TYF is an assistant and not a writer. It lives in the knowledge bands.

The layer runs in two modes: **intake**, a front-loaded onboarding invoked for a new workspace, a new register, or a new work; and **ongoing**, the knowledge work that persists through the rest of every project. The same skills serve both.

**Intake** has two surfaces:

- **Ingesting sources.** The author brings raw material: uploads, pastes, voice recordings, fragments, existing drafts, reading notes, transcripts. The extractor preserves it under `sources/` (raw, kept) and seeds `knowledge-base/` (concepts, claims, examples, contradictions, open questions). The original material remains the source of truth and is never summarized-then-discarded.
- **Interviewing the author.** The interlocutor elicits what is not yet written down: tacit knowledge, the shape of an argument, unresolved tensions, the registers the author wants. It asks where the idea is in its life (a sentence, an outline, a half-manuscript), elicits voice as annotated examples or stated preferences or both, and elicits the structure the author has in mind, if any.

Where the author is uncertain, both modes widen the choice space by proposing scaffolds the author can accept, reject, or rearrange. The system never invents what the author should believe or want. Intake terminates by writing out the workspace substrate (sources, knowledge base, voice registers) and, if a work is the active target, the per-work scaffold. Intake can be paused and resumed across days (see resolved questions in §13).

**Ongoing disciplines** stay available after intake. These currently live inside `interviewing-the-author`, `structuring-knowledge`, and `auditing-adversarially` rather than as separate skills; promoting them to their own cells is later roadmap work.

- **Thesis interrogation** (Argument / Elicit). Refuses to proceed until the author has stated, in one paragraph, the thesis and the tension it resolves. It does not propose a thesis; it pressures the author's until it is sharp.
- **Argument spine** (Argument / Elicit + Diagnose). Captures the claim graph: each load-bearing claim, what supports it, what it depends on. Surfaces orphan claims and circular support.
- **Claims index** (Architecture / Audit). A living `knowledge-base/claims.md` mapping every load-bearing claim to at least one source. Claims without a source are flagged, not quietly accepted. Sources are verified through MCP (Zotero or Scite), never invented.
- **Gap-marking instead of confabulation** (all knowledge bands). When the system needs a fact, statistic, anecdote, or citation the author has not supplied, it inserts `[AUTHOR: needed — what]` and stops. Commitment #3 as behavior: the system is structurally incapable of pretending to know what only the author knows.

## 7. Managing voice

Voice is an input, not a finishing filter. The voice registers are read by every Diagnose, Propose, and Revise pass at every band. It is **a library of registers, not a single voice document.** Skill: `managing-voice`.

A single author writes in multiple registers (for example: public-intellectual, product-strategist, intimate-philosophical, internal-notes, investor-facing), and a workspace may hold registers belonging to more than one author (a co-author, a licensed interview subject). Each work declares which registers are in scope. A passage written in one register is not corrected toward another; this is the **register fence.**

Each register contains: voice anchors (a handful of calibrated sentences); sentence and punctuation patterns; an anti-pattern list of cadences and phrases never used; annotated exemplar passages of the author's own prose. The lower-band component is the typographer canon (em-dash discipline, punctuation, the five-scale framework), shared across all registers. The honest ceiling is about 80% voice match; the final 20% is the author's, by hand, by design.

## 8. Integrity gates

The commitments made mechanical.

- **Read-only by default.** Elicit, Read, Diagnose, and Audit passes get no write access to any work's `manuscript/`. In Claude Code this is real tool scoping on the subagent; in Cowork and Desktop it is enforced by the skill contract and by routing every write through the single controlled-write skill plus the `tyf` helper, which is the only writer into `manuscript/`.
- **The controlled write.** Entering the Revise column requires proposal, audit, author review packet, explicit author decision, and `tyf write --decision <id>`. No pass crosses from Propose to Revise on its own. It is the only path into any manuscript. If the author edits the manuscript directly, `tyf adopt <work> <unit> --evidence "<what happened>"` records that author edit as the new base before the next controlled write.
- **Adversarial audit before done.** A unit cannot be marked complete until the audit has tried to break it (frame-lock, unsupported claims, hidden assumptions, machine cadence, register cross-talk, unverified citations, redactor-integrity findings) and the author has answered each finding. There is no score: the audit passes when every finding is fixed or explicitly accepted with a reason, logged in `.review/`.
- **AI-tell check.** At the sentence and paragraph bands, a detector flags low-entropy, high-cliché, machine-cadence text. Failing prose is sent back to Propose, never auto-rewritten, and is checked against the author's own register so an authentic style is not mistaken for a machine tell.
- **Citation verification.** Every citation is checked against a real index through MCP. Unverified citations are marked unverified; a model-generated DOI or page number is untrusted until confirmed. When the index is unavailable, the audit says so rather than implying a pass.

## 9. State and file contract

The body of work lives in plain, readable Markdown and YAML, owned by and legible to the author. For the v0.5 beta and Cowork v1 surface, the book folder is the single work. Shared substrate and work-local state live together at the workspace root so a first-time author does not have to reason about a catalog of works before writing.

```
workspace/
├── CLAUDE.md / AGENTS.md / GEMINI.md   # router + the commitments + conventions (identical)
├── manifest.yaml                       # hooks, voice inheritance rules
├── WORKSPACE_STATE.yaml                # durable state: active work, active band, write_control
├── ASSUMPTIONS.md                      # explicit, updated as the author learns
├── work.yaml                           # type, registers, status, scope, overrides
├── outline/                            # thesis, argument spine, chapter outlines
├── drafts/                             # candidate text from the amanuensis
├── manuscript/                         # behind the controlled write
├── style-sheet.md                      # running, the redactor's instrument
├── design/book-style.yaml              # typeface, paragraph styles, production intent
├── assets/images/                      # image files + image-use index
├── .review/                            # findings + write-log, never auto-applied
│
├── sources/                            # raw, preserved, shared      [read-mostly]
│   ├── uploads/  transcripts/  interviews/  imports/  notes/  links.md
│   ├── fragments/  fragments.jsonl
│
├── knowledge-base/                     # structured, shared
│   ├── concepts/  claims/  examples/  contradictions/  open-questions/
│   └── claims.md                       # every load-bearing claim → source(s)
│
├── voice/                              # registers, shared
│   ├── registers/                      # one file per register
│   ├── exemplar-passages/
│   ├── register-fences.md
│   └── anti-patterns.md
│
├── redactor-canon/                     # integrity substrate (terminology, logic, apparatus, finish)
│
├── .tyf/                               # apparatus memory: SQLite ledger + event log (NOT the work)
│   └── ledger.db
├── .proposals/                         # surfaced notices and self-extensions awaiting the author
└── .hooks/                             # contextual hook definitions
```

A `work.yaml` minimum:

```yaml
id: attunement-book
type: book           # book | essay-series | course | talk | newsletter | manifesto | article-cluster
registers:
  - author-poetic-philosophical
status: structuring  # intake | structuring | drafting | auditing | done
scope:
  knowledge: full    # or a named subset
  sources: full      # or a named subset
overrides:
  voice: []          # work-local overrides of any register
```

**Apparatus memory is separate from the work.** Everything above is the author's, in plain text. Machine bookkeeping lives under `.tyf/`: `.tyf/events.jsonl` is the human-readable hash-chained journal of apparatus actions, while `.tyf/ledger.db` (stdlib SQLite, no third-party dependency) is the derived content-addressed notice index for statuses, dismissals, and real timestamps. The notice index is rebuildable by re-scanning content and mirrorable to Markdown with `tyf reconcile --export`. See `docs/ATTENTIVENESS.md` and `docs/WORKSPACE_CONTRACT.md`.

**The `tyf` helper** performs the concrete file operations so the agent does not freelance, and it is the single writer into `manuscript/`. Commands include `init` (idempotent: creates only missing structure, never clobbers), `start`, `begin`, `import`, `capture`, `attend`, `session`, `diagnose`, `treat`, `surface`, `resume`, `status`, `new-work`, `open`, `mark-ready`, `propose`, `audit`, `accept`, `adopt`, `write --decision`, `doctor [--repair]`, `check`, `notice`, `dismiss`, and `reconcile`.

**The Draft Review Workbench** is the first local book surface. `tyf surface` generates an inspectable HTML/JSON table under `.review/surface/`: candidate draft on one side, approved manuscript units on the other, and book-style plus image-asset context alongside them. `tyf surface --serve` may save `drafts/candidate-draft.md`, but only by matching the loaded base hash against the current file; concurrent edits become conflicts. The manuscript pane is read-only. Moving candidate text into the manuscript still requires the Gate.

## 10. Portability: one skill, many runtimes

The atom is a single `SKILL.md` per discipline, with progressive disclosure. All runtimes consume the same atoms plus an identical context file under the name each expects (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md`).

- **Cowork (primary v1 target).** Local files, drop-in skills, a plugin that bundles them, and a native scheduler for the ongoing-work cadence. The controlled write is a contract enforced by the helper and the project instructions, since Cowork has no hard per-subagent read-only scoping. See `cowork/SETUP.md`.
- **Claude Code.** Read-only passes get read-only tool scopes, making commitment #2 physically true rather than promised. Capable harnesses can run parallel specialist reviewers into a work's `.review/`.
- **Other harnesses (portability targets).** Codex, Cursor, Gemini CLI, OpenCode. The skills are plain `SKILL.md` and portable without change; each harness's plugin manifest schema should be validated against its current docs before publishing there. See `docs/PORTABILITY.md`.

A runtime is a place TYF runs, never part of its doctrine. The core is the skills, the helper, and the workspace contract, which outlive any one runtime.

## 11. The iteration harness: hooks, context, attentiveness

After intake scaffolds a workspace and a work, what follows is iterative, not a pipeline. Drafting, revising, restructuring, walking away, returning, changing one's mind about chapter three. TYF handles this phase with a portable harness, taken at the pattern level from deterministic agent infrastructure and its "code over prompts" discipline.

- **Contextual hooks.** Events trigger small, named, inspectable actions. Saving a chapter fires an AI-tell scan and a register-fence check. Opening a chapter loads only the relevant registers, the claims touching this chapter, the running style sheet, and the latest `.review/`. Marking a unit ready fires the adversarial audit. Hooks are declared in `manifest.yaml`, readable and disableable.
- **Efficient context.** A workspace does not fit in one context window. The harness loads only what the active band, pass, and work need. Progressive disclosure is the default; the author can override.
- **The attentive amanuensis loop.** `tyf notice` surfaces, and never modifies: gaps left to fill, lines that trail off, claims with no source, a style sheet lagging its manuscript, unused registers. It is deterministic and spends no tokens, and it is ledger-backed so it shows only genuinely new or resurfaced items rather than re-nagging. A dismissed item resurfaces only if its surrounding context changes. When two authored passages conflict, it never ranks which wins; it surfaces the contradiction for the author. A second, opt-in semantic layer (the Learn pass, `docs/LEARN_PASS.md`) reads only the diff and asks a model the few questions code cannot answer; it too only surfaces. See `docs/ATTENTIVENESS.md`.
- **Gated self-extension.** The harness observes which proposals the author accepts, which findings recur, which questions they keep answering by hand, and proposes (never applies) extensions: a new anti-pattern, a register fence, a terminology rule, a new skill. It writes to `.proposals/`, never to `voice/`, `redactor-canon/`, or the skills directory.
- **Documentation honesty.** `tyf check` mechanizes the deterministic half of keeping the routing docs true (skill count, names, dead references, identical context files, valid JSON, glyph discipline), and runs warn-only as a tail of every mutating command. See `skills/keeping-documentation-honest`.

A workspace that runs for six months should know the author better at month six than month one, and yield a register library and a set of skills the author carries into every new work.

## 12. The redactor (Milchin tradition)

The typographer skill operates in the Russian / Soviet **редактор** tradition (Milchin and his lineage): structural, terminological, and logical rigor; consistency of argument and reference; editorial responsibility for a text's internal integrity. *Not* the Anglophone narrow sense of typesetting, though typographic hygiene is part of the lower bands. In TYF this role is the **redactor**, and it is a cross-cutting substrate parallel to voice, not a single band. Skill: `keeping-the-redactor-canon`.

Where voice governs how the work sounds, the redactor canon governs whether it holds together. It is read and updated by every Diagnose, Propose, Revise, Treatment, and Audit pass, across body magnifications:

- **micro** (glyph, mark, sentence): punctuation, dash discipline, cadence, quote style, numerals, binding, and typographic finish for the writing language.
- **meso** (sentence, paragraph, section): facts/source status, logic, composition, rubrication, language, and style.
- **macro** (chapter, module, body section): terminology consistency, kept promises, compositional balance, logical coherence, resolved cross-references, and honest headings.
- **mega** (the single work body): front/body/back matter, chapter sequence, apparatus, proportional treatment, and full-work reader service.

The redactor has three jobs: it occupies the lower zoom bands directly; it is the pattern template for the upper bands (the Diagnose-then-Propose-then-controlled-Revise rhythm it runs at the line is the rhythm the Argument, Architecture, and Section work run at their scales); and its canon is the lower component of the voice registers, so a line-level pass never proposes something the glyph-level rules forbid. Where voice and canon seem to conflict, the register fence wins on voice and the canon wins on integrity; the tension is surfaced, not silently resolved.

## 13. Scope, resolved questions, and what remains

**The current pack ships 19 skills** in three groups: lifecycle (`initializing-a-workspace`, `working-the-workspace`, `continuing-the-work`, `scheduling-ongoing-work`, `keeping-documentation-honest`); editorial apparatus (`using-tyf`, `ingesting-sources`, `interviewing-the-author`, `structuring-knowledge`, `composing-as-amanuensis`, `reading-sympathetically`, `diagnosing-text`, `typographer-redactor`, `editing-faithfully`, `receiving-critique`, `auditing-adversarially`, `controlling-manuscript-writes`); and two cross-cutting substrates (`managing-voice`, `keeping-the-redactor-canon`). Plus the `tyf` helper, the JSONL event journal, the SQLite notice index, and the Cowork packaging.

**Resolved decisions** (were open questions in the original design):

- **Matrix granularity.** A skill is one `(Band x Pass)` cell; band-level orchestrators may compose cells, but the atom is the cell.
- **Audit without a score.** The audit passes when every finding is answered (fixed or explicitly accepted with a reason), logged in `.review/`. No number.
- **Where the controlled write lives.** A single gated skill plus the proposal, audit, author review packet, author decision, and `tyf write --decision` helper chain, which is the only apparatus writer into `manuscript/`; direct author edits can be reconciled with `tyf adopt`.
- **Register-fence representation.** Declared in `voice/register-fences.md` and on each work; passes read it before editing.
- **Hook taxonomy.** Minimal set: save, open, mark-ready, daily, weekly, return-after-idle.
- **Surfacing self-extensions and notices.** A content-addressed ledger plus on-demand `tyf notice` / `tyf reconcile` and a daily digest to `.proposals/`, rather than interrupting flow.
- **Intake durability.** Intake can pause and resume; `WORKSPACE_STATE.yaml` and `ASSUMPTIONS.md` stay honest about what is done and open across sessions.

**Genuine open questions and known gaps** (see `docs/COMPARISON_SUPERPOWERS.md` for the benchmark against the reference pack):

1. **Testing.** The helper suite and hidden development behaviours now cover the runtime contract, and the pressure scenarios have had an initial run. The remaining testing gap is realistic harness evaluation across Codex, Claude Cowork, Gemini, macOS, Linux, Windows, and longer author sessions.
2. **Register inheritance semantics.** When a work overrides a workspace-level register, how does the override compose with the base: replace, merge, layer, or per-rule? `manifest.yaml` currently defaults to layer.
3. **Promoting the knowledge-band disciplines.** Thesis interrogation, the argument spine, and the claims index are embedded in three skills; promoting them to their own cells remains later roadmap work.
4. **Usage maturity vs the reference.** Diagnostic isolation, continuing-work, and receiving-critique now exist as command-backed packets, but need real long-form author, editor, and beta-reader use before they can be called mature.
5. **Distribution.** No update path for an installed pack; superpowers' plugin-shim-plus-skills-repo split is the model to study.
6. **Token budget.** A full multi-band parallel review is roughly 15x a single chat. TYF runs sequential by default; parallelism is opt-in.

---

### License note

MIT, so the harvested MIT-licensed patterns compose cleanly. One caution from the survey: the `ghost-writer` skill that inspired the voice-as-substrate pattern carries a `Proprietary` frontmatter inside its otherwise-MIT parent repo. TYF's voice layer is a clean-room reimplementation of the *pattern* (voice as input, register-aware, read by all passes), not a copy of that file, so the license stays unambiguous.

---

*Authored with TYF.*
