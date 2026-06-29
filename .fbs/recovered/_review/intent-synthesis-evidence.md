# Intent synthesis evidence

Compact per-slice LLM/sub-agent evidence. Prompts and transcripts are not stored here.

- stage=intent-synthesis; surface=subagent; status=timeout; prompt_chars=58551; prompt_hash=80cfedf04815; response_kind=candidate-requirements; detail=fbs: no sub-agent serviced the review query within 5s at .fbs\store\agent_io\queries\q-80cfedf048157a94-a519fa0a9c784e02bbd242027c8492ac.response.json. A review-mode Be needs an LLM sub-agent to judge it; this path is NOT deterministic. To proceed: (1) run inside Claude Code or Codex, which services this transport; (2) set FBS_LLM_BACKEND=sdk with ANTHROPIC_API_KEY for a direct SDK reviewer; or (3) cover the behaviour with a hard @tool-check Be (cli/file/http/ansi) instead of review mode. Set FBS_NO_SUBAGENT=1 to fail fast instead of waiting.
