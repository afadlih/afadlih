from __future__ import annotations

from datetime import date
from pathlib import Path
import importlib.util
import json
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


update = load_module("update_engineering_activity", "scripts/update_engineering_activity.py")
render = load_module("render_engineering_activity", "scripts/render_engineering_activity.py")
validate = load_module("validate_engineering_activity", "scripts/validate_engineering_activity.py")


class EngineeringActivityTests(unittest.TestCase):
    def setUp(self):
        self.previous = json.loads(
            (ROOT / "portfolio" / "engineering-activity.json").read_text(encoding="utf-8")
        )
        self.registry = json.loads(
            (ROOT / "portfolio" / "private-project-registry.json").read_text(encoding="utf-8")
        )
        self.mapping = {
            item["project"]: f"private-owner/project-{index}"
            for index, item in enumerate(self.registry["projects"], start=1)
            if item["enabled"]
        }
        previous_by_name = {item["project"]: item for item in self.previous["private_projects"]}
        self.private_counts = {
            repository: (
                previous_by_name[project]["commits"],
                date.fromisoformat(previous_by_name[project]["latest_commit"]),
            )
            for project, repository in self.mapping.items()
        }
        self.period_counts = {
            (item["start"], item["end"]): item["commits"]
            for item in self.previous["periods"]
        }

    def fake_searcher(self, query: str):
        for repository, result in self.private_counts.items():
            if f"repo:{repository} " in query:
                return result
        for (start, end), count in self.period_counts.items():
            if f"author-date:{start}..{end}" in query:
                if start == self.previous["window"]["start"] and end == self.previous["window"]["end"]:
                    return self.previous["summary"]["authored_commits"], date(2026, 8, 5)
                return count, date.fromisoformat(end) if count else None
        if "author-date:2026-02-07..2026-08-05" in query:
            return 383, date(2026, 8, 5)
        raise AssertionError(f"Unexpected query: {query}")

    def test_snapshot_uses_registry_exact_window_and_private_counts(self):
        snapshot = update.build_snapshot(
            self.previous,
            self.registry,
            "afadlih",
            self.mapping,
            today=date(2026, 8, 5),
            searcher=self.fake_searcher,
        )
        self.assertEqual("2.1.0", snapshot["version"])
        self.assertEqual(180, snapshot["window"]["days"])
        self.assertEqual("2026-02-07", snapshot["window"]["start"])
        self.assertEqual("2026-08-05", snapshot["window"]["end"])
        self.assertEqual(383, snapshot["summary"]["authored_commits"])
        self.assertEqual(196, snapshot["summary"]["selected_private_commits"])
        self.assertEqual(7, snapshot["summary"]["selected_private_projects"])
        self.assertEqual(383, sum(item["commits"] for item in snapshot["periods"]))
        self.assertEqual(
            {item["project"] for item in self.registry["projects"] if item["enabled"]},
            {item["project"] for item in snapshot["private_projects"]},
        )

    def test_semver_condition_changes_release_candidate_to_stable(self):
        aqua = next(item for item in self.registry["projects"] if item["project"] == "AquaSense")
        self.assertEqual("Release candidate", update.condition_for(aqua, "2.3.0-rc15"))
        self.assertEqual("Stable release", update.condition_for(aqua, "2.3.0"))
        self.assertEqual("Pre-release", update.condition_for(aqua, "2.4.0-beta1"))

    def test_renderer_is_deterministic_and_private_safe(self):
        svg = render.render_svg(self.previous)
        self.assertIn("ENGINEERING ACTIVITY · 180 DAYS", svg)
        self.assertIn("383", svg)
        self.assertIn("196", svg)
        self.assertIn("AquaSense", svg)
        self.assertIn("118 commits", svg)
        self.assertNotIn("private-owner", svg)
        self.assertNotIn("api.github.com/repos/", svg)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "activity.json"
            self.assertTrue(update.write_json_if_changed(path, self.previous))
            self.assertFalse(update.write_json_if_changed(path, self.previous))

    def test_profile_is_rebuilt_and_sorted_from_registry(self):
        profile = json.loads((ROOT / "portfolio" / "profile.json").read_text(encoding="utf-8"))
        modified = json.loads(json.dumps(self.previous))
        target = next(item for item in modified["private_projects"] if item["project"] == "InternLog AI")
        target["version"] = "9.9.9"
        target["latest_commit"] = "2026-08-06"
        target["commits"] = 50
        synchronized = update.synchronize_profile(profile, modified, self.registry)
        self.assertEqual("3.4.0", synchronized["version"])
        self.assertEqual("InternLog AI", synchronized["current_focus"][0]["project"])
        self.assertEqual("9.9.9", synchronized["current_focus"][0]["version"])
        self.assertNotIn("FormAI", [item["project"] for item in synchronized["current_focus"]])

    def test_snapshot_contains_no_repository_identifiers(self):
        snapshot = update.build_snapshot(
            self.previous,
            self.registry,
            "afadlih",
            self.mapping,
            today=date(2026, 8, 5),
            searcher=self.fake_searcher,
        )
        serialized = json.dumps(snapshot)
        for repository in self.mapping.values():
            self.assertNotIn(repository, serialized)
        self.assertEqual([], validate.collect_forbidden_keys(snapshot))


if __name__ == "__main__":
    unittest.main()
