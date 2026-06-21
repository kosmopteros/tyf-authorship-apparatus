Feature: tyf (recovered)

@source:signature @stub @incomplete @path:tyf.py::append @covers:signature_tyf_append
Scenario: signature append accepts <unknown>, <unknown> returns <unknown>
  Given parameter `path` of type `<unknown>`
  And parameter `text` of type `<unknown>`
  When `append(path, text)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::cmd_audit @covers:signature_tyf_cmd_audit
Scenario: signature cmd_audit accepts <unknown> returns <unknown>
  Given parameter `args` of type `<unknown>`
  When `cmd_audit(args)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::cmd_check @covers:signature_tyf_cmd_check
Scenario: signature cmd_check accepts <unknown> returns <unknown>
  Given parameter `args` of type `<unknown>`
  When `cmd_check(args)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::cmd_dismiss @covers:signature_tyf_cmd_dismiss
Scenario: signature cmd_dismiss accepts <unknown> returns <unknown>
  Given parameter `args` of type `<unknown>`
  When `cmd_dismiss(args)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::cmd_doctor @covers:signature_tyf_cmd_doctor
Scenario: signature cmd_doctor accepts <unknown> returns <unknown>
  Given parameter `args` of type `<unknown>`
  When `cmd_doctor(args)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::cmd_init @covers:signature_tyf_cmd_init
Scenario: signature cmd_init accepts <unknown> returns <unknown>
  Given parameter `args` of type `<unknown>`
  When `cmd_init(args)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::cmd_mark_ready @covers:signature_tyf_cmd_mark_ready
Scenario: signature cmd_mark_ready accepts <unknown> returns <unknown>
  Given parameter `args` of type `<unknown>`
  When `cmd_mark_ready(args)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::cmd_new_work @covers:signature_tyf_cmd_new_work
Scenario: signature cmd_new_work accepts <unknown> returns <unknown>
  Given parameter `args` of type `<unknown>`
  When `cmd_new_work(args)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::cmd_notice @covers:signature_tyf_cmd_notice
Scenario: signature cmd_notice accepts <unknown> returns <unknown>
  Given parameter `args` of type `<unknown>`
  When `cmd_notice(args)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::cmd_open @covers:signature_tyf_cmd_open
Scenario: signature cmd_open accepts <unknown> returns <unknown>
  Given parameter `args` of type `<unknown>`
  When `cmd_open(args)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::cmd_reconcile @covers:signature_tyf_cmd_reconcile
Scenario: signature cmd_reconcile accepts <unknown> returns <unknown>
  Given parameter `args` of type `<unknown>`
  When `cmd_reconcile(args)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::cmd_status @covers:signature_tyf_cmd_status
Scenario: signature cmd_status accepts <unknown> returns <unknown>
  Given parameter `args` of type `<unknown>`
  When `cmd_status(args)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::cmd_update @covers:signature_tyf_cmd_update
Scenario: signature cmd_update accepts <unknown> returns <unknown>
  Given parameter `args` of type `<unknown>`
  When `cmd_update(args)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::cmd_write @covers:signature_tyf_cmd_write
Scenario: signature cmd_write accepts <unknown> returns <unknown>
  Given parameter `args` of type `<unknown>`
  When `cmd_write(args)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::dismiss_notice @covers:signature_tyf_dismiss_notice
Scenario: signature dismiss_notice accepts <unknown>, <unknown> returns <unknown>
  Given parameter `root` of type `<unknown>`
  And parameter `content_hash` of type `<unknown>`
  When `dismiss_notice(root, content_hash)` is called
  Then result type is `<unknown>`

# Mirror the SQLite ledger to a human-readable Markdown file. The db stays
# the source of truth; this is for reading and inspection.
@source:signature @stub @incomplete @path:tyf.py::export_ledger_markdown @covers:signature_tyf_export_ledger_markdown
Scenario: signature export_ledger_markdown accepts <unknown> returns <unknown>
  Given parameter `root` of type `<unknown>`
  When `export_ledger_markdown(root)` is called
  Then result type is `<unknown>`

# Return notice dicts the author may want to revisit.
#
# Each notice: {kind, where, message, content_hash, context_hash}.
# Surface-only. Nothing here writes, edits, or heals. Pure inspection.
@source:signature @stub @incomplete @path:tyf.py::gather_notices @covers:signature_tyf_gather_notices
Scenario: signature gather_notices accepts <unknown> returns <unknown>
  Given parameter `root` of type `<unknown>`
  When `gather_notices(root)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::get @covers:signature_tyf_get
Scenario: signature get accepts <unknown> returns <unknown>
  Given parameter `d` of type `<unknown>`
  When `get(d)` is called
  Then result type is `<unknown>`

# Return (items_dict, events_count) for reconcile display.
@source:signature @stub @incomplete @path:tyf.py::ledger_summary @covers:signature_tyf_ledger_summary
Scenario: signature ledger_summary accepts <unknown> returns <unknown>
  Given parameter `root` of type `<unknown>`
  When `ledger_summary(root)` is called
  Then result type is `<unknown>`

# Append-only record of an apparatus action. The git-like spine.
@source:signature @stub @incomplete @path:tyf.py::log_event @covers:signature_tyf_log_event
Scenario: signature log_event accepts <unknown>, <unknown>, <unknown>, <unknown> returns <unknown>
  Given parameter `root` of type `<unknown>`
  And parameter `kind` of type `<unknown>`
  And parameter `ref` of type `<unknown>`
  And parameter `detail` of type `<unknown>`
  When `log_event(root, kind, ref, detail)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::main @covers:signature_tyf_main
Scenario: signature main accepts no args returns <unknown>
  Given no parameters
  When `main()` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::mkdirs @covers:signature_tyf_mkdirs
Scenario: signature mkdirs accepts no args returns <unknown>
  Given no parameters
  When `mkdirs()` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::now @covers:signature_tyf_now
Scenario: signature now accepts no args returns <unknown>
  Given no parameters
  When `now()` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::read_state @covers:signature_tyf_read_state
Scenario: signature read_state accepts <unknown> returns <unknown>
  Given parameter `path` of type `<unknown>`
  When `read_state(path)` is called
  Then result type is `<unknown>`

# Diff current notices against the SQLite ledger. Returns (new, still_open,
# resurfaced). Updates the ledger when update=True. Never touches the work.
#
# Status model, keyed on content_hash:
#   - unseen content       -> new
#   - seen, status 'open'  -> still_open (not re-raised as if new)
#   - seen, status 'dismissed', same context_hash -> stays silent
#   - seen, status 'dismissed', DIFFERENT context_hash -> resurfaced
@source:signature @stub @incomplete @path:tyf.py::reconcile_notices @covers:signature_tyf_reconcile_notices
Scenario: signature reconcile_notices accepts <unknown>, <unknown>, <unknown> returns <unknown>
  Given parameter `root` of type `<unknown>`
  And parameter `notices` of type `<unknown>`
  And parameter `update` of type `<unknown>`
  When `reconcile_notices(root, notices, update)` is called
  Then result type is `<unknown>`

# Return (problems, notes). Pure file/string inspection; no LLM, no deps.
@source:signature @stub @incomplete @path:tyf.py::run_doc_check @covers:signature_tyf_run_doc_check
Scenario: signature run_doc_check accepts <unknown> returns <unknown>
  Given parameter `root` of type `<unknown>`
  When `run_doc_check(root)` is called
  Then result type is `<unknown>`

@source:signature @stub @incomplete @path:tyf.py::write @covers:signature_tyf_write
Scenario: signature write accepts <unknown>, <unknown> returns <unknown>
  Given parameter `path` of type `<unknown>`
  And parameter `text` of type `<unknown>`
  When `write(path, text)` is called
  Then result type is `<unknown>`

@recovered:true @source:pytest @path:test_tyf.py::CLIBehaviour::test_audit_requires_existing_work @incomplete @covers:CLIBehaviour_test_audit_requires_existing_work
Scenario: audit requires existing work
  When `self.ws()` is called
  When `run_tyf(['audit', 'missing', 'unit'], ws)` is called
  When `self.assertNotEqual(rc, 0, 'audit on a nonexistent work must refuse')` is called
  Then test completes without error

@recovered:true @source:pytest @path:test_tyf.py::CLIBehaviour::test_doctor_detects_out_of_band_edit @incomplete @covers:CLIBehaviour_test_doctor_detects_out_of_band_edit
Scenario: doctor detects out of band edit
  When `self.ws()` is called
  When `run_tyf(['new-work', 'demo'], ws)` is called
  When `self.make_draft(ws)` is called
  When `run_tyf(['write', 'demo', '--from', src, '--confirm'], ws)` is called
  When `self.assertEqual(rc, 0)` is called
  When `man_file.write_text(man_file.read_text(encoding='utf-8') + 'SNUCK IN\n', encoding='utf-8')` is called
  When `run_tyf(['doctor'], ws)` is called
  When `self.assertIn('ch1.md', out)` is called
  When `self.assertRegex(out.lower(), 'out-of-band|out of band|modified|hash')` is called
  Then test completes without error

@recovered:true @source:pytest @path:test_tyf.py::CLIBehaviour::test_doctor_flags_unlogged_manuscript_file @incomplete @covers:CLIBehaviour_test_doctor_flags_unlogged_manuscript_file
Scenario: doctor flags unlogged manuscript file
  When `self.ws()` is called
  When `run_tyf(['new-work', 'demo'], ws)` is called
  When `man.mkdir(parents=True, exist_ok=True)` is called
  When `(man / 'rogue.md').write_text('snuck in\n', encoding='utf-8')` is called
  When `run_tyf(['doctor'], ws)` is called
  When `self.assertIn('rogue.md', out)` is called
  When `self.assertRegex(out.lower(), 'uncontrolled|not recorded')` is called
  Then test completes without error

@recovered:true @source:pytest @path:test_tyf.py::CLIBehaviour::test_init_creates_and_is_idempotent @incomplete @covers:CLIBehaviour_test_init_creates_and_is_idempotent
Scenario: init creates and is idempotent
  When `self.ws()` is called
  When `self.assertTrue((ws / 'WORKSPACE_STATE.yaml').is_file())` is called
  When `(ws / 'ASSUMPTIONS.md').write_text('CUSTOM CONTENT\n', encoding='utf-8')` is called
  When `run_tyf(['init', 'ws'], self.tmp)` is called
  When `self.assertEqual(rc, 0, out)` is called
  When `self.assertEqual((ws / 'ASSUMPTIONS.md').read_text(encoding='utf-8'), 'CUSTOM CONTENT\n')` is called
  Then test completes without error

@recovered:true @source:pytest @path:test_tyf.py::CLIBehaviour::test_init_refuses_nonempty_foreign_dir @incomplete @covers:CLIBehaviour_test_init_refuses_nonempty_foreign_dir
Scenario: init refuses nonempty foreign dir
  When `foreign.mkdir()` is called
  When `(foreign / 'existing.txt').write_text('hi\n', encoding='utf-8')` is called
  When `run_tyf(['init', '.'], foreign)` is called
  When `self.assertNotEqual(rc, 0, 'init into a non-empty non-TYF dir must refuse without --force')` is called
  When `self.assertFalse((foreign / 'WORKSPACE_STATE.yaml').exists())` is called
  When `run_tyf(['init', '.', '--force'], foreign)` is called
  When `self.assertEqual(rc2, 0, out2)` is called
  When `self.assertTrue((foreign / 'WORKSPACE_STATE.yaml').is_file())` is called
  Then test completes without error

@recovered:true @source:pytest @path:test_tyf.py::CLIBehaviour::test_mark_ready_rejects_traversal @incomplete @covers:CLIBehaviour_test_mark_ready_rejects_traversal
Scenario: mark ready rejects traversal
  When `self.ws()` is called
  When `run_tyf(['mark-ready', '../escape', 'u'], ws)` is called
  When `self.assertNotEqual(rc, 0, 'traversal in mark-ready work id must be rejected')` is called
  When `self.assertFalse((ws / 'escape').exists())` is called
  When `self.assertFalse((self.tmp / 'escape').exists())` is called
  Then test completes without error

@recovered:true @source:pytest @path:test_tyf.py::CLIBehaviour::test_mark_ready_requires_existing_work @incomplete @covers:CLIBehaviour_test_mark_ready_requires_existing_work
Scenario: mark ready requires existing work
  When `self.ws()` is called
  When `run_tyf(['mark-ready', 'missing', 'unit'], ws)` is called
  When `self.assertNotEqual(rc, 0, 'mark-ready on a nonexistent work must refuse')` is called
  When `self.assertFalse((ws / 'works/missing').exists())` is called
  Then test completes without error

@recovered:true @source:pytest @path:test_tyf.py::CLIBehaviour::test_mark_ready_requires_workspace @incomplete @covers:CLIBehaviour_test_mark_ready_requires_workspace
Scenario: mark ready requires workspace
  When `run_tyf(['mark-ready', 'ghost', 'u'], self.tmp)` is called
  When `self.assertNotEqual(rc, 0, 'mark-ready outside a workspace must refuse')` is called
  When `self.assertFalse((self.tmp / 'works').exists())` is called
  Then test completes without error

@recovered:true @source:pytest @path:test_tyf.py::CLIBehaviour::test_new_work_rejects_absolute_id @incomplete @covers:CLIBehaviour_test_new_work_rejects_absolute_id
Scenario: new work rejects absolute id
  When `self.ws()` is called
  When `run_tyf(['new-work', str(pwn)], ws)` is called
  When `self.assertNotEqual(rc, 0, 'absolute work id must be rejected')` is called
  When `self.assertFalse((pwn / 'work.yaml').exists(), 'absolute work id escaped the workspace')` is called
  Then test completes without error

@recovered:true @source:pytest @path:test_tyf.py::CLIBehaviour::test_new_work_rejects_parent_traversal @incomplete @covers:CLIBehaviour_test_new_work_rejects_parent_traversal
Scenario: new work rejects parent traversal
  When `self.ws()` is called
  When `run_tyf(['new-work', '../escape'], ws)` is called
  When `self.assertNotEqual(rc, 0, "'..' in work id must be rejected")` is called
  When `self.assertFalse((self.tmp / 'escape').exists())` is called
  When `self.assertFalse((ws / 'escape').exists())` is called
  Then test completes without error

@recovered:true @source:pytest @path:test_tyf.py::CLIBehaviour::test_new_work_rejects_separator_in_id @incomplete @covers:CLIBehaviour_test_new_work_rejects_separator_in_id
Scenario: new work rejects separator in id
  When `self.ws()` is called
  When `run_tyf(['new-work', 'a/b'], ws)` is called
  When `self.assertNotEqual(rc, 0, 'path separators in a work id must be rejected')` is called
  When `self.assertFalse((ws / 'works/a/b').exists())` is called
  Then test completes without error

@recovered:true @source:pytest @path:test_tyf.py::CLIBehaviour::test_new_work_rejects_spaces_in_id @incomplete @covers:CLIBehaviour_test_new_work_rejects_spaces_in_id
Scenario: new work rejects spaces in id
  When `self.ws()` is called
  When `run_tyf(['new-work', 'a b'], ws)` is called
  When `self.assertNotEqual(rc, 0, 'a work id with a space must be rejected')` is called
  Then test completes without error

@recovered:true @source:pytest @path:test_tyf.py::CLIBehaviour::test_new_work_requires_workspace @incomplete @covers:CLIBehaviour_test_new_work_requires_workspace
Scenario: new work requires workspace
  When `run_tyf(['new-work', 'demo'], self.tmp)` is called
  When `self.assertNotEqual(rc, 0, 'new-work outside a workspace must refuse')` is called
  When `self.assertFalse((self.tmp / 'works').exists(), 'new-work must not create works/ outside a workspace')` is called
  Then test completes without error
