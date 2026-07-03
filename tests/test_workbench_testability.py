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

    def test_using_tyf_mentions_desktop_agent_flow(self):
        text = (ROOT / "skills" / "using-tyf" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Codex Desktop", text)
        self.assertIn("Claude Code Desktop", text)
        self.assertIn("tyf workbench --open", text)
        self.assertIn("The agent runs TYF commands", text)

    def test_initialization_skill_mentions_agent_operated_setup(self):
        text = (ROOT / "skills" / "initializing-a-workspace" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Desktop-agent promise", text)
        self.assertIn("agent-operated", text)
        self.assertIn("tyf workbench --open", text)

    def test_start_here_and_desktop_runbook_are_aligned(self):
        start = (ROOT / "docs" / "START_HERE.md").read_text(encoding="utf-8")
        runbook = (ROOT / "docs" / "DESKTOP_AGENT_RUNBOOK.md").read_text(encoding="utf-8")
        self.assertIn("Codex Desktop", start)
        self.assertIn("Claude Code Desktop", start)
        self.assertIn("run `tyf workbench --open` yourself", start)
        self.assertIn("Agent operates TYF", runbook)
        self.assertIn("tyf workbench --open", runbook)

    def test_author_ux_iterations_document_20_passes(self):
        text = (ROOT / "docs" / "AUTHOR_UX_20X_ITERATIONS.md").read_text(encoding="utf-8")
        for idx in range(1, 21):
            self.assertIn(f"Pass {idx:02d}", text)
        self.assertIn("the agent creates or enters the workspace", text)


if __name__ == "__main__":
    unittest.main()
