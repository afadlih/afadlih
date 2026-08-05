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

    def test_activity_workflow_uses_validated_fast_forward_main_update(self):
        text = (
            ROOT / ".github" / "workflows" / "update-profile-activity.yml"
        ).read_text(encoding="utf-8")
        for expected in [
            "git checkout -B main origin/main",
            'BASE_SHA=$(git rev-parse origin/main)',
            "scripts/update_repository_activity.py --write",
            "scripts/update_public_commit_activity.py --write",
            "scripts/portfolio_ci.py update",
            "scripts/portfolio_ci.py final-check",
            "assets/public-activity.svg",
            'CURRENT_REMOTE_SHA="$(git rev-parse origin/main)"',
            "git push origin HEAD:main",
        ]:
            self.assertIn(expected, text)

        for forbidden in [
            "--force",
            "gh pr create",
            "gh pr edit",
            "pull-requests: write",
            "automation/profile-activity",
        ]:
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
