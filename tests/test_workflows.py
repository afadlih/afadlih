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


if __name__ == "__main__":
    unittest.main()
