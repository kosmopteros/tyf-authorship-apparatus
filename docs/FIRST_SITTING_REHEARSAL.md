# First Sitting Rehearsal

This is a reproducible author-session rehearsal for a fresh TYF workspace. It uses the public example scaffold in `examples/first-sitting-arrival/scaffold.txt` and proves that an agent can preserve an arrival, structure source, ask one grounded question, start candidate prose, and leave `manuscript/` empty.

Run from a temporary folder with the TYF helper on PATH:

```sh
mkdir my-book
cd my-book
tyf init
tyf start /path/to/tyf/examples/first-sitting-arrival/scaffold.txt --kind chat --title "The Storm Index" --language English
tyf structure work --source-ref <fragment-id-from-start>
tyf attend work --source-ref <fragment-id-from-start> --query "storm ritual"
```

Then the agent should read `.review/gentle-attention.md`, ask the one first question, and draft candidate prose in `drafts/candidate-draft.md`. The first sitting is successful when these are true:

- `sources/imports/` preserves the original scaffold.
- `sources/fragments.jsonl` records the source fragment.
- `knowledge-base/retrieval-index.jsonl` shows the plain-file retrieval anchors.
- `.review/writing-runway.md` and `.review/gentle-attention.md` show the next move.
- `.review/current-session.md` can be written with `tyf session work --focus "first candidate passage" --minutes 25`.
- `manuscript/` remains empty.

The smoke test `CLIBehaviour.test_first_sitting_rehearsal_from_example_scaffold_reaches_candidate_session` runs this flow with subprocess commands and verifies the artifacts.
