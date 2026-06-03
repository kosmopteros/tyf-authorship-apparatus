# Installing TYF on OpenCode

OpenCode uses its own plugin install. Install TYF separately even if you already use it in another harness.

## Steps for the agent

1. Copy every directory under `skills/` of this repository into the OpenCode skills directory for this project or profile.
2. Copy `AGENTS.md` from the repository root into the location OpenCode reads for session context, so the commitments and the mandatory skill check load at startup.
3. Confirm the sixteen skills are discoverable by name, beginning with `using-tyf`.

## Verify

Ask the agent: "List the TYF skills you can see." It should return all sixteen, and it should route any authorship request through `using-tyf` first.

If the agent drafts finished prose from a vague prompt without checking the skills, the install did not take. Re-copy `AGENTS.md` and the `skills/` tree, then restart the session.
