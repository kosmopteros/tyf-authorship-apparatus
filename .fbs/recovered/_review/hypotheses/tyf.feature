Feature: tyf (recovered)

@source:llm-hypothesis @review @path:tyf.py::hypothesis @covers:hypothesis_tyf_peek-notice-leaves-ledger-unchanged
Scenario: Peek notice leaves ledger unchanged
  Given a TYF workspace with noticeable unfinished material
  When the author runs `tyf notice --peek`
  Then the command surfaces notices without inserting or updating notice rows in `.tyf/ledger.db`

@source:llm-hypothesis @review @path:tyf.py::hypothesis @covers:hypothesis_tyf_dismiss-accepts-unique-hash-prefix
Scenario: Dismiss accepts unique hash prefix
  Given the notice ledger contains exactly one notice whose content hash begins with a provided prefix
  When the author runs `tyf dismiss <prefix>`
  Then TYF marks that notice dismissed and logs a dismiss event for the full content hash

@source:llm-hypothesis @review @path:tyf.py::hypothesis @covers:hypothesis_tyf_dismiss-rejects-ambiguous-hash-prefix
Scenario: Dismiss rejects ambiguous hash prefix
  Given the notice ledger contains multiple notices whose content hashes begin with the same provided prefix
  When the author runs `tyf dismiss <prefix>`
  Then TYF refuses to dismiss any notice and reports that the hash prefix is ambiguous

@source:llm-hypothesis @review @path:tyf.py::hypothesis @covers:hypothesis_tyf_reconcile-export-mirrors-ledger
Scenario: Reconcile export mirrors ledger
  Given the notice ledger contains tracked notices and events
  When the author runs `tyf reconcile --export`
  Then TYF writes `.proposals/notice-ledger.md` grouped by notice status without changing the SQLite ledger state

@source:llm-hypothesis @review @path:tyf.py::hypothesis @covers:hypothesis_tyf_mutating-command-doc-check-is-warn-only
Scenario: Mutating command doc check is warn only
  Given a valid TYF workspace and a pack with documentation-honesty drift
  When the author runs a mutating command such as `tyf mark-ready`
  Then the command reports the documentation drift as a warn-only hook and preserves the mutating command result
