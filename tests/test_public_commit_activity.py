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


update = load_module("update_public_commit_activity", "scripts/update_public_commit_activity.py")
render = load_module("render_public_activity", "scripts/render_public_activity.py")


class PublicCommitActivityTests(unittest.TestCase):
    def setUp(self):
        self.sources = json.loads(
            (ROOT / "portfolio" / "activity-sources.json").read_text(encoding="utf-8")
        )
        self.fixture = json.loads(
            (ROOT / "tests" / "fixtures" / "public-commits-api.json").read_text(
                encoding="utf-8"
            )
        )

    def test_snapshot_uses_fixed_thirty_day_window(self):
        snapshot = update.build_snapshot(
            self.sources,
            "afadlih",
            fixture=self.fixture,
        )
        self.assertEqual(30, len(snapshot["daily"]))
        self.assertEqual("2026-07-06", snapshot["window"]["start"])
        self.assertEqual("2026-08-04", snapshot["window"]["end"])
        self.assertEqual(7, snapshot["summary"]["commits_in_window"])
        self.assertEqual(1, snapshot["summary"]["active_days"])
        self.assertEqual(
            "afadlih/afadlih",
            snapshot["repositories"][0]["repository"],
        )

    def test_incomplete_refresh_keeps_previous_complete_snapshot(self):
        previous = update.build_snapshot(
            self.sources,
            "afadlih",
            fixture=self.fixture,
        )
        incomplete = json.loads(json.dumps(self.fixture))
        del incomplete["commits"]["afadlih/2341720069_ML_2025"]
        result = update.build_snapshot(
            self.sources,
            "afadlih",
            fixture=incomplete,
            previous=previous,
        )
        self.assertEqual(previous, result)

    def test_writer_and_renderer_are_deterministic(self):
        snapshot = update.build_snapshot(
            self.sources,
            "afadlih",
            fixture=self.fixture,
        )
        svg = render.render_svg(snapshot)
        self.assertIn("PUBLIC ENGINEERING ACTIVITY", svg)
        self.assertIn("Private repositories are excluded", svg)
        self.assertNotIn("github-readme-stats.vercel.app", svg)

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "activity.json"
            self.assertTrue(update.write_json_if_changed(path, snapshot))
            self.assertFalse(update.write_json_if_changed(path, snapshot))


if __name__ == "__main__":
    unittest.main()
