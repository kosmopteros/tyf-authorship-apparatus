# TYF vs Superpowers: a comparative analysis

A structural and product comparison between TYF and `obra/superpowers`, the established reference for agentic skill packs. The point is not to declare a winner; the two solve different problems. The point is to learn where superpowers is more mature, where TYF has gone further, and where TYF is fooling itself.

Superpowers state used for this comparison: v2.0-era, fetched May 2026. Its core skill set at that time: `using-superpowers`, `writing-skills`, `brainstorming`, `writing-plans`, `executing-plans`, `subagent-driven-development`, `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `requesting-code-review`, `receiving-code-review`, `finishing-a-development-branch`, `using-git-worktrees`, `dispatching-parallel-agents`. Domain: software development. TYF's domain: authorship. So the mapping is by *role in the workflow*, not by subject.

## The honest framing

Superpowers is a methodology with ~210k GitHub stars, multi-harness installs, an eval suite, and years of real-world pressure-testing across thousands of users. TYF is a young, single-author pack validated in one sandbox, never run in anger. Any "TYF does X better" below is a design claim, not a proven outcome. Superpowers has the one thing TYF cannot fake: usage.

## Skill-to-skill mapping, through the "how it breaks" lens

| Superpowers skill | TYF analogue | Shared failure mode both must survive |
|---|---|---|
| `using-superpowers` (dispatcher) | `using-tyf` | Agent rationalizes "no skill applies" and skips the system. Both answer with a hard "if it might apply even 1%, use it." Superpowers is blunter and more imperative; TYF is gentler, which is arguably weaker under pressure. |
| `writing-skills` (TDD-for-skills) | `docs/WRITING_TYF_SKILLS.md` + `keeping-documentation-honest` | A skill written without watching an agent fail first teaches the wrong thing. Superpowers makes RED-GREEN mandatory and is explicit that this is the core. TYF now has direct RED proof for 117/117 hidden command-backed development scenarios, but the prompt-level skill pressure loop has only one weak-baseline subagent run. This remains TYF's biggest proof gap. |
| `brainstorming` | `interviewing-the-author` | Agent supplies the idea instead of eliciting it. Both center elicitation. TYF's thesis-interrogation is arguably deeper; superpowers' is better battle-tested. |
| `writing-plans` | `structuring-knowledge` + outline | Plan/structure is invented rather than derived; too vague to act on. Superpowers' "clear enough for a junior with no judgement" bar is a sharper acceptance test than TYF's. |
| `executing-plans` / `subagent-driven-development` | (no direct analogue) | Execution drifts from the plan. **TYF has no execution-discipline skill.** Authorship's "execution" is composing, which TYF gates hard, but it has nothing about sustaining a long multi-session build the way superpowers' plan-execution does. |
| `test-driven-development` | (closest: `auditing-adversarially`) | Code/claims asserted without verification. Superpowers' TDD is mechanically enforceable (tests pass or fail). TYF's audit is judgment-based and cannot be made binary, which is inherent to the domain but means TYF's "done" is softer. |
| `systematic-debugging` | (no analogue) | Guessing at causes instead of isolating them. **TYF has no debugging analogue.** The authorship equivalent would be "why does this section fail to land," which TYF scatters across diagnosing-text and reading-sympathetically rather than giving a systematic isolation procedure. |
| `verification-before-completion` | `auditing-adversarially` + `tyf check` | "Done" declared without checking. Both strong here. TYF's `tyf check` (deterministic, zero-token) and the attentive `tyf notice` are arguably *ahead* of superpowers in mechanizing the cheap half of verification. |
| `requesting-code-review` / `receiving-code-review` | `receiving-critique` + `editing-faithfully` | Review feedback ignored, obeyed, or defended against. TYF now preserves external critique, treats it as reader experience rather than authority, and routes accepted changes through editing and the Gate. Superpowers remains more mature because its review loop has real usage. |
| `finishing-a-development-branch` | `controlling-manuscript-writes` (partial) | Work left in a half-merged limbo. Superpowers has explicit branch-completion hygiene. TYF's controlled write covers entering the manuscript but not "this unit is fully closed out." |
| `using-git-worktrees` | (no analogue; TYF deliberately avoids git dependency) | Parallel work clobbers itself. Superpowers leans on git worktrees for isolation. TYF chose no-git on purpose (authors may not have repos), and pays for it with weaker isolation and its own content-hash ledger instead. A defensible divergence, not a flaw. |
| `dispatching-parallel-agents` | (no analogue) | Parallel agents collide or duplicate. **TYF is single-threaded by design.** No parallelism story at all. |

## Where superpowers is clearly more mature

1. **Proven, not asserted.** Mass usage, an eval suite, and a feedback loop. TYF has a sandbox and a confident author. This is the gap that matters most.
2. **Execution and parallelism.** Superpowers sustains long multi-session builds (plan execution, subagent-driven development, parallel dispatch). TYF stops at composing a unit; it has no story for driving a whole book to completion across months beyond the cadence loop.
3. **Mechanical verification.** TDD gives superpowers a binary "done." TYF's audit is judgment-based; correct for the domain, but softer.
4. **Imperative dispatch.** Superpowers' "YOU DO NOT HAVE A CHOICE" tone is harder to rationalize around than TYF's gentler routing. Under adversarial pressure, blunt wins.
5. **Distribution architecture.** Superpowers solved skills-auto-update and community contribution via a plugin-shim-plus-skills-repo split. TYF ships as a static bundle with no update path.
6. **Review as a first-class loop.** Two dedicated review skills (request, receive). TYF now has receiving-critique, but it is new and has far less usage evidence.

## Where TYF has genuinely gone further (as implemented design, pending usage)

1. **A real state and memory layer.** Superpowers' state is largely the git repo and the plan files. TYF has an explicit workspace contract, an idempotent initializer, a hash-chained JSONL apparatus event journal, a SQLite notice index, and the content-addressed notice ledger. For a domain without git, this is more than superpowers offers, and the attentive-amanuensis loop (surface-only, never modifies, dismissed-with-resurface) has no superpowers equivalent.
2. **The write boundary as a hard contract.** Superpowers trusts the agent to follow TDD. TYF makes the manuscript reachable only through proposal, audit, author review packet, decision, and `tyf write --decision`, with source and base hashes plus `tyf doctor` detecting out-of-band edits. For irreplaceable authored prose this is a stronger guarantee than "please follow the methodology."
3. **Two cross-cutting substrates.** Voice and the redactor canon are read by every pass at every band. Superpowers has no analogue because code does not have "voice"; but the *pattern* (a substrate every operation consults) is more sophisticated than superpowers' flat skill list.
4. **The no-confabulation commitment as structure.** `[AUTHOR: needed]` gap-marking is enforced at every layer. Superpowers handles this implicitly via tests; TYF makes it an explicit, first-class refusal.
5. **Documentation-honesty as code.** `tyf check` mechanizes drift-detection and runs as a warn-only tail on every mutating command. Superpowers' `writing-skills` teaches the discipline; TYF additionally enforces the mechanical half with zero tokens.

## Where TYF is fooling itself

1. **Partial proof is partial proof.** The command-backed helper contract is no longer paper-only: 117/117 hidden development scenarios have direct RED proof, and the stdlib helper suite has 154 tests including source-grounded attention packets, external-feedback triage, private-context-free author surfaces, exported release-tree check/install smoke coverage, and a fresh exported Codex install opening a separate book workspace from an arrival scaffold. Superpowers earned its confidence through usage; TYF still has only a first prompt-level subagent pressure run. GREEN passed 11/11, but the RED baseline was weak, so skill-pressure proof remains partial rather than settled.
2. **Surface-area-to-usage ratio.** TYF has 17 skills, a broad helper CLI, a SQLite layer, visible reflex hooks, and an opt-in LLM pass, for zero real users. Superpowers grew its surface from usage. TYF risks being over-engineered for problems no author has actually hit.
3. **Gentleness as a liability.** TYF's tone is faithful and warm. Superpowers learned that under pressure, agents need blunt imperatives. TYF's softer dispatch may rationalize more easily, the exact failure its rationalization tables try to prevent.
4. **The redactor/voice substrates are unproven at scale.** They are elegant on paper. Whether an agent actually consults them at every band, every pass, under a long real project, is unknown.

## What TYF should steal from superpowers next

1. **Repeat and strengthen the prompt-level RED/GREEN loop.** This is non-negotiable. The command-backed Be loop now has direct RED proof, but the first subagent pressure run is still thin. TYF needs stronger RED baselines, repeated harness runs, and evidence that failures appear when the skills are absent or constrained.
2. **An execution-and-completion discipline.** Something like `executing-plans` adapted to authorship: how to drive a whole work to done across sessions, not just compose a unit.
3. **Real receiving-critique usage.** The skill and helper path exist now; the next proof is watching it handle actual beta-reader and editor notes without flattening the work.
4. **An update/distribution path.** A way for an installed TYF to pull improvements, the plugin-shim pattern superpowers uses.
5. **Blunter dispatch.** Borrow the imperative register for the one place it matters: the mandatory skill check.

## Bottom line

Superpowers is a proven methodology; TYF is a promising architecture with stronger local evidence than before. TYF's state, memory, feedback-triage, and write-boundary design are genuinely ahead of superpowers for a no-git authored-prose domain, and its documentation-honesty mechanization is a real contribution. But superpowers has the only currency that ultimately counts, real usage, and TYF still lacks two disciplines entirely: execution-to-completion and debugging/isolation. The most honest one-line summary: TYF has out-designed superpowers in its niche and now proves its helper contract, but it is still under-used and under-pressure-tested relative to superpowers in practice. The next move is not more architecture. It is repeated author and harness proof.
