from pathlib import Path
import re
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SHA40 = re.compile(r"^[0-9a-f]{40}$")


class WorkflowTests(unittest.TestCase):
    def test_all_workflows_parse_and_pin_actions(self):
        workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
        self.assertEqual(2, len(workflows))
        for path in workflows:
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
            self.assertIsInstance(payload, dict, path.name)
            text = path.read_text(encoding="utf-8")
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("uses:"):
                    reference = stripped.split("@", 1)[1].split("#", 1)[0].strip()
                    self.assertRegex(reference, SHA40, f"{path.name}: {line}")
            self.assertIn("permissions:", text)
            self.assertIn("concurrency:", text)
            self.assertIn("timeout-minutes:", text)

    def test_activity_workflow_runs_daily_discovers_and_fast_forwards(self):
        text = (ROOT / ".github" / "workflows" / "update-profile-activity.yml").read_text(encoding="utf-8")
        for expected in [
            'cron: "17 23 * * *"',
            "git checkout -B main origin/main",
            'BASE_SHA=$(git rev-parse origin/main)',
            "scripts/update_repository_activity.py --write",
            "scripts/discover_projects.py --write",
            "scripts/update_engineering_activity.py --write",
            "PROFILE_ACTIVITY_TOKEN",
            "PROFILE_PRIVATE_REPOSITORIES_JSON",
            "preserving the checked-in privacy-reviewed snapshot",
            "scripts/portfolio_ci.py update",
            "scripts/portfolio_ci.py final-check",
            "portfolio/engineering-activity.json",
            "portfolio/discovered-projects.json",
            "assets/engineering-activity.svg",
            'CURRENT_REMOTE_SHA="$(git rev-parse origin/main)"',
            "git push origin HEAD:main",
        ]:
            self.assertIn(expected, text)
        self.assertNotIn('cron: "17 23 * * 0"', text)
        for forbidden in ["--force", "gh pr create", "pull-requests: write", "automation/profile-activity"]:
            self.assertNotIn(forbidden, text)

    def test_generated_push_does_not_retrigger_activity_workflow(self):
        text = (ROOT / ".github" / "workflows" / "update-profile-activity.yml").read_text(encoding="utf-8")
        push_block = text.split("  push:\n", 1)[1].split("\n\npermissions:", 1)[0]
        for generated in [
            "README.md",
            "portfolio/engineering-activity.json",
            "portfolio/discovered-projects.json",
            "assets/engineering-activity.svg",
        ]:
            self.assertNotIn(f'- "{generated}"', push_block)
        self.assertIn('- "portfolio/private-project-registry.json"', push_block)

    def test_repository_enforces_two_persistent_branches(self):
        text = (ROOT / ".github" / "workflows" / "update-profile-activity.yml").read_text(encoding="utf-8")
        for expected in [
            "create:", "enforce-branch-policy:", "main|develop", "Keep only main and develop",
            "Remove stale branches", "git/refs/heads/$CREATED_BRANCH", "git/refs/heads/$branch",
            "git merge-base --is-ancestor origin/develop HEAD", "git push origin HEAD:develop",
        ]:
            self.assertIn(expected, text)
        self.assertFalse((ROOT / ".github" / "dependabot.yml").exists())


if __name__ == "__main__":
    unittest.main()
