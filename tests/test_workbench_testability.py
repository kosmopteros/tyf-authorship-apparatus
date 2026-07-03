from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class WorkbenchTestabilityTests(unittest.TestCase):
    def test_runbook_states_editable_happy_path_and_static_limit(self):
        text = (ROOT / "docs" / "WORKBENCH_RUNBOOK.md").read_text(encoding="utf-8")
        self.assertIn("tyf workbench --serve --open", text)
        self.assertIn("--open` implies `--serve", text)
        self.assertIn("file://", text)
        self.assertIn("cannot save drafts", text)
        self.assertIn("agent runs", text.lower())

    def test_pyproject_keeps_single_public_workbench_surface(self):
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('tyf = "tyf:main"', text)
        self.assertNotIn('tyf-workbench =', text)


if __name__ == "__main__":
    unittest.main()
