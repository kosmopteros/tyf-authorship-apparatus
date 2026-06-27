# Candidate requirements

Review-only advisory artifact. No requirements were promoted into the state of record.

## TYF should prefer deterministic checks and use model judgment only for issues th

- id: `cand:9c3a917fd65e`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.720`
- statement: TYF should prefer deterministic checks and use model judgment only for issues that cannot be settled mechanically.
- subject hints: tyf notice, deterministic-first, model boundary

Source pointers:
- docs/LEARN_PASS.md:13
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: docs/LEARN_PASS.md:13
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Supported by LEARN_PASS and helper wiring for notice/check; still needs executable behaviour coverage for the broader model-boundary claim.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## `tyf check` should hard-fail with exit code 1 when documentation or pack consist

- id: `cand:5bff1f60cf12`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.780`
- statement: `tyf check` should hard-fail with exit code 1 when documentation or pack consistency drift is detected.
- subject hints: tyf check, 1, doc honesty, exit code

Source pointers:
- skills/keeping-documentation-honest/SKILL.md:23
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: skills/keeping-documentation-honest/SKILL.md:23
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Multiple docs state this as command contract and the helper exposes check/doc-hook paths; statement was truncated and should be normalized before promotion.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## Each `tyf notice` run should reconcile surfaced items against the content-addres

- id: `cand:76e6a6357c36`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.740`
- statement: Each `tyf notice` run should reconcile surfaced items against the content-addressed ledger.
- subject hints: tyf notice, ledger, per-run

Source pointers:
- docs/ATTENTIVENESS.md:35
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: docs/ATTENTIVENESS.md:35
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: ATTENTIVENESS states the per-run ledger behaviour and the helper contains ledger/database paths; behaviour coverage should prove dedupe/resurface semantics.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## After `tyf write`, the notice ledger should be updated so already-seen manuscrip

- id: `cand:8e0d2aa87326`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.700`
- statement: After `tyf write`, the notice ledger should be updated so already-seen manuscript issues are not re-reported unless their context changes.
- subject hints: tyf write, ledger, notice dedupe

Source pointers:
- docs/ATTENTIVENESS.md:36
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: docs/ATTENTIVENESS.md:36
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: ATTENTIVENESS calls this wired now, but recovery did not map a behaviour cluster; keep as intent until a write/notice test covers it.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## TYF's pressure scenarios should be run against real agent/subagent harnesses bef

- id: `cand:a01b9381a159`
- kind: `advisory-recommendation`
- disposition: `review`
- confidence: `0.750`
- statement: TYF's pressure scenarios should be run against real agent/subagent harnesses before the pack is described as production-bulletproof.
- subject hints: tests/, pressure scenarios, agent validation

Source pointers:
- TYF-manifesto-and-architecture.md:288
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1003
- scripts/tyf.py:110
- scripts/tyf.py:853
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:487
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: TYF-manifesto-and-architecture.md:288
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: The architecture doc explicitly names the testing gap; it is validation work rather than a runtime capability.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- up: module:tests.test_tyf -> doc:VALIDATION.md

## `tyf notice` should surface, without modifying files, gaps, trailing fragments,

- id: `cand:0c260dc69ad0`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.820`
- statement: `tyf notice` should surface, without modifying files, gaps, trailing fragments, unsourced claims, stale style sheets, and unused registers.
- subject hints: tyf notice, read-only, attentiveness

Source pointers:
- TYF-manifesto-and-architecture.md:254
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: TYF-manifesto-and-architecture.md:254
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: This is a central README/manifesto claim and maps to helper notice scanning; each notice class should have behaviour coverage.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## The manuscript revise/write boundary should require explicit author action throu

- id: `cand:b11c16782e4f`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.840`
- statement: The manuscript revise/write boundary should require explicit author action through `tyf write --confirm`.
- subject hints: tyf write --confirm, controlled write, author consent

Source pointers:
- TYF-manifesto-and-architecture.md:173
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: TYF-manifesto-and-architecture.md:173
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Controlled write is a core TYF commitment across docs and helper command surface; keep as a top-level requirement with executable refusal/confirm checks.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## A correctly installed harness should expose all sixteen TYF skills and route aut

- id: `cand:3e4fdf4948b7`
- kind: `affordance`
- disposition: `review`
- confidence: `0.680`
- statement: A correctly installed harness should expose all sixteen TYF skills and route authorship requests through `using-tyf` first.
- subject hints: using-tyf, install verification, skills

Source pointers:
- .opencode/INSTALL.md:13
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: .opencode/INSTALL.md:13
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: This is an install-verification affordance from OpenCode docs; merge with duplicate harness-verification candidates before promotion.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## The `tyf` helper command surface should include init, status, new-work, open, ma

- id: `cand:de8bae2ee406`
- kind: `inferred-capability`
- disposition: `review`
- confidence: `0.800`
- statement: The `tyf` helper command surface should include init, status, new-work, open, mark-ready, audit, write --confirm, doctor, check, notice, dismiss, and reconcile.
- subject hints: init, status, CLI, command surface

Source pointers:
- TYF-manifesto-and-architecture.md:236
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:102
- scripts/tyf.py:105
Supporting evidence:
- doc hypothesis: TYF-manifesto-and-architecture.md:236
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Documented command list matches public CLI shape but should be reconciled with current README because `update` is also documented elsewhere.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: doc:INSTALL.md -> module:scripts.tyf -> function:cmd_init
- up: function:cmd_init -> module:scripts.tyf -> doc:INSTALL.md

## When `scripts/tyf.py` is copied outside the repo, `TYF_PACK_ROOT` should point b

- id: `cand:e56d150893d7`
- kind: `affordance`
- disposition: `review`
- confidence: `0.760`
- statement: When `scripts/tyf.py` is copied outside the repo, `TYF_PACK_ROOT` should point back to the pack root so `tyf check` can inspect the correct files.
- subject hints: TYF_PACK_ROOT, install

Source pointers:
- cowork/SETUP.md:13
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: cowork/SETUP.md:13
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Cowork setup documents this operational fallback and helper code has pack-root logic; likely suitable as install documentation, not core product intent.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## Installed harness verification should confirm all sixteen TYF skills are visible

- id: `cand:049d5a36fd33`
- kind: `affordance`
- disposition: `review`
- confidence: `0.670`
- statement: Installed harness verification should confirm all sixteen TYF skills are visible and authorship requests route through `using-tyf`.
- subject hints: using-tyf, install verification

Source pointers:
- docs/PORTABILITY.md:65
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: docs/PORTABILITY.md:65
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Duplicate of other harness-verification candidates from portability docs; consolidate rather than promote separately.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## Cowork install verification should confirm all sixteen skills are visible, `usin

- id: `cand:2186380d665b`
- kind: `affordance`
- disposition: `review`
- confidence: `0.720`
- statement: Cowork install verification should confirm all sixteen skills are visible, `using-tyf` is the first authorship router, and manuscript writes are refused outside `tyf write`.
- subject hints: using-tyf, manuscript/, Cowork, install verification, manuscript

Source pointers:
- cowork/SETUP.md:37
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: cowork/SETUP.md:37
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Cowork setup adds the manuscript refusal clause; promote only if harness-specific verification requirements are tracked.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## TYF should preserve project lineage and rationale so contributors can challenge

- id: `cand:66d60ccf92dd`
- kind: `advisory-recommendation`
- disposition: `review`
- confidence: `0.620`
- statement: TYF should preserve project lineage and rationale so contributors can challenge accepted and rejected design decisions.
- subject hints: open-source, lineage, contributors, rationale

Source pointers:
- TYF-manifesto-and-architecture.md:53
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:1125
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:105
Supporting evidence:
- doc hypothesis: TYF-manifesto-and-architecture.md:53
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Supported by manifesto language, but it is a contribution/governance value rather than an executable product behaviour.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: doc:INSTALL.md -> module:scripts.tyf -> function:cmd_open
- up: function:cmd_open -> module:scripts.tyf -> doc:INSTALL.md

## TYF should keep machine-only bookkeeping in `.tyf/ledger.db`, including notice s

- id: `cand:0a02c628cd70`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.760`
- statement: TYF should keep machine-only bookkeeping in `.tyf/ledger.db`, including notice statuses, dismissals, timestamps, and an append-only event log for init/write/mark-ready/dismiss/repair.
- subject hints: .tyf/ledger.db, init, ledger, event log

Source pointers:
- TYF-manifesto-and-architecture.md:234
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: TYF-manifesto-and-architecture.md:234
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Strong documentation support and helper database/event-log hints; needs behaviour checks for event coverage and no hand-edit contract.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## `tyf init` and `tyf doctor --repair` should be idempotent, creating only missing

- id: `cand:dcfef99eac7d`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.800`
- statement: `tyf init` and `tyf doctor --repair` should be idempotent, creating only missing workspace structure without clobbering existing authored files.
- subject hints: tyf init, doctor --repair, idempotency

Source pointers:
- tests/acceptance-and-edge-cases.md:116
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: tests/acceptance-and-edge-cases.md:116
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Acceptance docs state this and helper scaffold/repair code exists; should become an executable behaviour if not already covered.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## `tyf check` should exempt historical/validation files that intentionally preserv

- id: `cand:9310ac365be5`
- kind: `inferred-capability`
- disposition: `review`
- confidence: `0.660`
- statement: `tyf check` should exempt historical/validation files that intentionally preserve older command lists or examples.
- subject hints: tyf check, history exemptions

Source pointers:
- tests/acceptance-and-edge-cases.md:143
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: tests/acceptance-and-edge-cases.md:143
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Acceptance docs mention exemptions, but promotion should name exact exempt paths and why they are history rather than drift.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## TYF workspace operations should preserve per-work isolation

- id: `cand:b8dd391c27a8`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.700`
- statement: TYF workspace operations should preserve per-work isolation.
- subject hints: per-work, per-work isolation, workspace

Source pointers:
- tests/acceptance-and-edge-cases.md:126
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:487
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:105
Supporting evidence:
- doc hypothesis: tests/acceptance-and-edge-cases.md:126
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Acceptance docs and path-confinement functions support this, though the original statement is fragmentary and needs concrete path/write behaviours.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: doc:INSTALL.md -> module:scripts.tyf -> function:_confine_work
- up: function:_safe_work_id -> module:scripts.tyf -> doc:INSTALL.md

## When manuscript files and write logs disagree, `tyf doctor` should surface the i

- id: `cand:59859656aff4`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.730`
- statement: When manuscript files and write logs disagree, `tyf doctor` should surface the inconsistency.
- subject hints: tyf doctor, write log, manuscript

Source pointers:
- tests/acceptance-and-edge-cases.md:106
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: tests/acceptance-and-edge-cases.md:106
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Acceptance docs state the desired doctor behaviour; behaviour coverage should construct mismatched manuscript/log state.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## When TYF is uncertain about a write boundary, not writing should be the safe def

- id: `cand:9c108c5e01a8`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.690`
- statement: When TYF is uncertain about a write boundary, not writing should be the safe default.
- subject hints: safe, safe default, write boundary

Source pointers:
- tests/acceptance-and-edge-cases.md:127
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:487
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:105
Supporting evidence:
- doc hypothesis: tests/acceptance-and-edge-cases.md:127
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: This is a core safety posture in acceptance docs but needs formulation into concrete refusal behaviours.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: doc:INSTALL.md -> module:scripts.tyf -> function:_safe_work_id
- up: function:_safe_work_id -> module:scripts.tyf -> doc:INSTALL.md

## TYF should resolve real paths and refuse writes outside the workspace root

- id: `cand:399567a979ec`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.780`
- statement: TYF should resolve real paths and refuse writes outside the workspace root.
- subject hints: root, path confinement, workspace root, security

Source pointers:
- tests/acceptance-and-edge-cases.md:125
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:1125
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
Supporting evidence:
- doc hypothesis: tests/acceptance-and-edge-cases.md:125
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Acceptance docs and helper path logic support this; it is important security/path-confinement behaviour.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail -> function:run_doc_check -> function:_pack_root
- up: function:_pack_root -> module:scripts.tyf -> doc:INSTALL.md

## Workspace-affecting commands should scaffold or repair required structure before

- id: `cand:e04ec0f6138c`
- kind: `inferred-capability`
- disposition: `review`
- confidence: `0.640`
- statement: Workspace-affecting commands should scaffold or repair required structure before relying on it.
- subject hints: scaffold, workspace structure

Source pointers:
- tests/acceptance-and-edge-cases.md:119
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:110
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
Supporting evidence:
- doc hypothesis: tests/acceptance-and-edge-cases.md:119
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: The original is too fragmentary; keep as a helper design affordance unless tied to specific commands.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: doc:INSTALL.md -> module:scripts.tyf -> function:_scaffold
- up: function:_scaffold -> module:scripts.tyf -> doc:INSTALL.md

## Source material areas should be treated as read-mostly, with writes reserved for

- id: `cand:82a71c018fb0`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.660`
- statement: Source material areas should be treated as read-mostly, with writes reserved for explicit ingest or author-approved operations.
- subject hints: read-mostly, sources, write zones

Source pointers:
- tests/acceptance-and-edge-cases.md:128
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:853
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
Supporting evidence:
- doc hypothesis: tests/acceptance-and-edge-cases.md:128
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Acceptance docs support read-mostly source posture, but exact allowed write paths need clarification before promotion.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:gather_notices -> function:_read
- up: function:read_state -> module:scripts.tyf -> doc:INSTALL.md

## Harnesses with post-turn hooks may call `tyf notice --peek` or append intent cap

- id: `cand:1dc73a6bdaeb`
- kind: `advisory-recommendation`
- disposition: `review`
- confidence: `0.680`
- statement: Harnesses with post-turn hooks may call `tyf notice --peek` or append intent capture to `.proposals/`, while TYF itself should not claim this portability universally.
- subject hints: tyf notice --peek, .proposals/, hooks, .proposals

Source pointers:
- docs/ATTENTIVENESS.md:37
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: docs/ATTENTIVENESS.md:37
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: ATTENTIVENESS frames this as harness-dependent future/optional integration, not a portable core requirement.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## `tyf write` should require `--confirm` as the concrete signal of explicit author

- id: `cand:308a79228582`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.860`
- statement: `tyf write` should require `--confirm` as the concrete signal of explicit author acceptance.
- subject hints: tyf write, --confirm, author acceptance

Source pointers:
- cowork/SETUP.md:27
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: cowork/SETUP.md:27
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: Strong duplicate of controlled-write intent; consolidate with the main controlled-write requirement.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## The documentation-honesty check should run warn-only after mutating `tyf` comman

- id: `cand:e5efeee579fe`
- kind: `recovered-intent`
- disposition: `review`
- confidence: `0.740`
- statement: The documentation-honesty check should run warn-only after mutating `tyf` commands and hard-fail when invoked as standalone `tyf check`.
- subject hints: tyf, 1, doc honesty, mutating commands, tyf check

Source pointers:
- VALIDATION.md:6
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: VALIDATION.md:6
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: VALIDATION describes this as observed behaviour; treat as command contract rather than mere recommendation if tests still prove it.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## The existing validation evidence records an end-to-end POSIX exercise of core `t

- id: `cand:ef117f5e8edc`
- kind: `advisory-recommendation`
- disposition: `review`
- confidence: `0.700`
- statement: The existing validation evidence records an end-to-end POSIX exercise of core `tyf` helper commands, including write refusal without `--confirm` and success with it.
- subject hints: tyf, --confirm, validation, POSIX, helper commands

Source pointers:
- VALIDATION.md:13
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: VALIDATION.md:13
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: This is validation history/evidence, not a future requirement; keep as supporting evidence for promoted behaviours.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md

## Validation evidence should demonstrate that introduced documentation drift is wa

- id: `cand:3fe008191654`
- kind: `advisory-recommendation`
- disposition: `review`
- confidence: `0.720`
- statement: Validation evidence should demonstrate that introduced documentation drift is warned after mutating commands and fails standalone `tyf check`.
- subject hints: tyf check, 1, doc drift, validation

Source pointers:
- VALIDATION.md:6
- scripts/tyf.py:145
- scripts/tyf.py:471
- scripts/tyf.py:468
- scripts/tyf.py:1101
- scripts/tyf.py:348
- scripts/tyf.py:1062
- scripts/tyf.py:1012
- scripts/tyf.py:186
- scripts/tyf.py:1020
- scripts/tyf.py:839
- scripts/tyf.py:336
- scripts/tyf.py:177
- scripts/tyf.py:305
- scripts/tyf.py:342
- scripts/tyf.py:1045
- scripts/tyf.py:154
- scripts/tyf.py:120
- scripts/tyf.py:640
- scripts/tyf.py:127
- scripts/tyf.py:623
- scripts/tyf.py:671
- scripts/tyf.py:740
- scripts/tyf.py:1036
- scripts/tyf.py:465
- scripts/tyf.py:1041
- scripts/tyf.py:1003
- scripts/tyf.py:138
- scripts/tyf.py:1052
- scripts/tyf.py:110
- scripts/tyf.py:791
- scripts/tyf.py:915
- scripts/tyf.py:963
- scripts/tyf.py:853
- scripts/tyf.py:699
- scripts/tyf.py:781
- scripts/tyf.py:719
- scripts/tyf.py:921
- scripts/tyf.py:753
- scripts/tyf.py:971
- scripts/tyf.py:769
- scripts/tyf.py:1068
- scripts/tyf.py:804
- scripts/tyf.py:565
- scripts/tyf.py:600
- scripts/tyf.py:354
- scripts/tyf.py:92
- scripts/tyf.py:586
- scripts/tyf.py:487
- scripts/tyf.py:1125
- scripts/tyf.py:115
- scripts/tyf.py:102
- scripts/tyf.py:53
- scripts/tyf.py:500
- scripts/tyf.py:193
- scripts/tyf.py:105
- tests/test_tyf.py:43
- tests/test_tyf.py:34
Supporting evidence:
- doc hypothesis: VALIDATION.md:6
- non-test graph wiring reaches related structure
- public/docs/route/command surface reaches related structure
- LLM intent synthesis: This is a quality gate recommendation derived from VALIDATION; can support behaviour promotion for doc-honesty checks.
Counter evidence:
- doc-side intent has no recovered behaviour cluster
Graph paths:
- down: function:main -> function:_doc_hook_tail
- up: module:scripts.tyf -> doc:INSTALL.md
