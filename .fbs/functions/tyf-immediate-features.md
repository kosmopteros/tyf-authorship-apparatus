# TYF immediate writing features

**Purpose:** make the TYF authorship apparatus usable for starting a new book today while keeping the apparatus visible, recoverable, and provenance-safe.

**Stakeholders:** Alexander, Pegasus/Codex, Claude Cowork, and future helpers entering the same writing workspace.

**Parent:** root

## Claims

- `tyf-helper-current-contract`: the TYF helper smoke suite exercises workspace safety, a plain-language first-session start path, explicit writing-language metadata, provenance-safe capture, visible reflexes, explicit git snapshots, Gate-controlled writes, partial source-line acceptance, documentation honesty, and update checks without writing manuscript text outside proposal, audit, author decision with acceptance evidence, optional accepted line ranges, and `tyf write --decision` records {formulated_by=req:d6e294d5;req:b2b3df90;req:012517f3;req:e4214bd5, axes=bad-outcome;edge;boundary;integration;security, na=non-functional:no throughput or latency budget for first-day writing setup}
- `tyf-public-onboarding-contract`: the public TYF onboarding surface gives non-technical authors paste-ready Codex and Claude Cowork prompts, routes agents through `using-tyf` and `tyf start`, and keeps advanced helper commands behind agent-facing skill guidance rather than presenting them as the author's first task {formulated_by=req:d2077fb4, axes=bad-outcome;edge;boundary;integration, na=security:local documentation and skill routing with no secret or auth boundary;non-functional:no throughput or latency budget for onboarding text}
- `tyf-codex-plugin-valid`: the Codex plugin manifest validates against the current local Codex plugin validator, including skills path, author object, interface metadata, and skill frontmatter YAML {formulated_by=req:d2077fb4, axes=bad-outcome;edge;boundary;integration, na=security:local plugin metadata has no runtime permission grant or secret-handling surface;non-functional:no performance budget for manifest validation}
