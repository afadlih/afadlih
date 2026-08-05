from __future__ import annotations

from datetime import date
from pathlib import Path
import importlib.util
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "discover_projects.py"
spec = importlib.util.spec_from_file_location("discover_projects", MODULE_PATH)
discover = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(discover)


class ProjectDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.previous = json.loads(
            (ROOT / "portfolio" / "discovered-projects.json").read_text(encoding="utf-8")
        )
        self.repositories = [
            {
                "name": "approved",
                "full_name": "afadlih/approved",
                "html_url": "https://github.com/afadlih/approved",
                "private": False,
                "fork": False,
                "archived": False,
                "pushed_at": "2026-08-04T10:00:00Z",
                "description": "Already approved",
                "language": "Python",
                "size": 10,
            },
            {
                "name": "new-project",
                "full_name": "afadlih/new-project",
                "html_url": "https://github.com/afadlih/new-project",
                "private": False,
                "fork": False,
                "archived": False,
                "pushed_at": "2026-08-05T10:00:00Z",
                "description": "A new public project",
                "language": "TypeScript",
                "size": 20,
            },
            {
                "name": "old-project",
                "full_name": "afadlih/old-project",
                "html_url": "https://github.com/afadlih/old-project",
                "private": False,
                "fork": False,
                "archived": False,
                "pushed_at": "2025-01-01T10:00:00Z",
                "description": None,
                "language": None,
                "size": 20,
            },
            {
                "name": "forked",
                "full_name": "afadlih/forked",
                "html_url": "https://github.com/afadlih/forked",
                "private": False,
                "fork": True,
                "archived": False,
                "pushed_at": "2026-08-05T10:00:00Z",
                "size": 20,
            },
        ]

    def test_detects_recent_public_and_private_labels_without_auto_publish(self):
        payload = discover.build_discovery(
            self.previous,
            "afadlih",
            self.repositories,
            {"afadlih/approved"},
            {"AquaSense"},
            {
                "AquaSense": "private-owner/aquasense",
                "New Approved Label": "private-owner/new-project",
            },
            today=date(2026, 8, 5),
        )
        self.assertFalse(payload["policy"]["auto_publish"])
        self.assertEqual(["afadlih/new-project"], [item["repository"] for item in payload["public_candidates"]])
        self.assertEqual(["New Approved Label"], [item["label"] for item in payload["private_candidates"]])
        serialized_private = json.dumps(payload["private_candidates"])
        self.assertNotIn("private-owner", serialized_private)
        self.assertNotIn("repository", serialized_private)

    def test_ignored_status_and_changed_at_are_stable(self):
        first = discover.build_discovery(
            self.previous,
            "afadlih",
            self.repositories,
            set(),
            set(),
            {},
            today=date(2026, 8, 5),
        )
        candidate = next(item for item in first["public_candidates"] if item["repository"] == "afadlih/new-project")
        candidate["status"] = "ignored"
        first["changed_at"] = "2026-08-05"
        second = discover.build_discovery(
            first,
            "afadlih",
            self.repositories,
            set(),
            set(),
            {},
            today=date(2026, 8, 6),
        )
        ignored = next(item for item in second["public_candidates"] if item["repository"] == "afadlih/new-project")
        self.assertEqual("ignored", ignored["status"])
        self.assertEqual("2026-08-05", second["changed_at"])

    def test_candidate_ids_do_not_use_raw_private_repository(self):
        identifier = discover.candidate_id("private", "Public Safe Label")
        self.assertRegex(identifier, r"^private-[0-9a-f]{12}$")
        self.assertNotIn("Public Safe Label", identifier)


if __name__ == "__main__":
    unittest.main()
