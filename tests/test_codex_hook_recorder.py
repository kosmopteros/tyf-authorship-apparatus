import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"

spec_v06 = importlib.util.spec_from_file_location("tyf_workbench_v06", SCRIPTS / "tyf_workbench_v06.py")
workbench = importlib.util.module_from_spec(spec_v06)
spec_v06.loader.exec_module(workbench)
sys.modules["tyf_workbench_v06"] = workbench

spec_hook = importlib.util.spec_from_file_location("tyf_codex_hook", SCRIPTS / "tyf_codex_hook.py")
hook = importlib.util.module_from_spec(spec_hook)
spec_hook.loader.exec_module(hook)


class CodexHookRecorderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / ".tyf").mkdir()
        (self.root / "drafts").mkdir()
        (self.root / "manuscript").mkdir()
        (self.root / "design").mkdir()
        (self.root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
        (self.root / "work.yaml").write_text("title: Hook Book\nlanguage: en\nstatus: draft\n", encoding="utf-8")
        (self.root / "style-sheet.md").write_text("Voice: clear.\n", encoding="utf-8")
        (self.root / "design" / "book-style.yaml").write_text("font: Charter\n", encoding="utf-8")
        (self.root / "drafts" / "chapter-one.md").write_text("Draft line.\n", encoding="utf-8")
        (self.root / "manuscript" / "chapter-one.md").write_text("Approved line.\n", encoding="utf-8")
        self.old_cwd = os.getcwd()
        os.chdir(self.root)
        work_id, work_root, workspace = workbench.resolve_work(None)
        workbench.ensure_workbench_shape(work_root, workspace)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.temp.cleanup()

    def test_records_hook_status_files(self):
        work_id, work_root, workspace = workbench.resolve_work(None)
        before = (work_root / "manuscript" / "chapter-one.md").read_text(encoding="utf-8")
        record = hook.record_hook(
            work_id,
            work_root,
            workspace,
            "PostToolUse",
            {"summary": "draft changed", "changed_paths": ["drafts/chapter-one.md"]},
        )
        self.assertEqual(record["hook"], "PostToolUse")
        self.assertEqual(record["changed_paths"], ["drafts/chapter-one.md"])
        self.assertTrue((work_root / ".review" / "surface" / "codex-hooks.jsonl").is_file())
        self.assertTrue((work_root / ".review" / "surface" / "codex-turn-status.json").is_file())
        self.assertEqual((work_root / "manuscript" / "chapter-one.md").read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
