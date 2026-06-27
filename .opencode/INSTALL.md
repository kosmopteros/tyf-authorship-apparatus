# Installing TYF on OpenCode

OpenCode uses its own plugin install. Install TYF separately even if you already use it in another harness.

## Steps for the agent

1. From this repository, run `bash scripts/install.sh <opencode-skills-dir>`; on Windows without bash, run `powershell -ExecutionPolicy Bypass -File scripts/install.ps1 <opencode-skills-dir>`. This installs the skills and the `tyf` helper launcher.
2. Confirm `tyf --help` works in the shell OpenCode will use. If it does not, add the reported launcher directory to PATH or call the generated launcher directly.
3. For an author book folder, run `tyf init` in that folder so TYF writes clean local context files. If OpenCode needs context before init, copy the matching file from `author-context/`, not the repository-root contributor context.
4. Confirm the nineteen skills are discoverable by name, beginning with `using-tyf`.

## Verify

Ask the agent: "List the TYF skills you can see." It should return all nineteen, and it should route any authorship request through `using-tyf` first.

If the agent drafts finished prose from a vague prompt without checking the skills, the install did not take. Re-run `scripts/install.*`, confirm `tyf --help`, place clean `author-context/` context if needed, then restart the session.
