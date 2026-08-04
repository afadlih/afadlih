from pathlib import Path
import copy
import importlib.util
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "render_profile.py"
spec = importlib.util.spec_from_file_location("render_profile", MODULE_PATH)
render_profile = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(render_profile)


class ProfileRenderTests(unittest.TestCase):
    def load_all(self):
        return (
            render_profile.load_json(ROOT / "portfolio" / "profile.json"),
            render_profile.load_json(ROOT / "portfolio" / "projects.json"),
            render_profile.load_json(ROOT / "portfolio" / "repository-activity.json"),
        )

    def test_profile_projects_and_activity_are_valid(self):
        profile, projects, activity = self.load_all()
        errors = (
            render_profile.validate_profile(profile, ROOT)
            + render_profile.validate_projects(projects, ROOT)
            + render_profile.validate_activity(activity)
        )
        self.assertEqual([], errors)

    def test_render_contains_focused_sections_and_truthful_labels(self):
        profile, projects, activity = self.load_all()
        readme = render_profile.render_readme(profile, projects, activity)
        for expected in [
            "## What I build",
            "## Selected work",
            "## Experience & recognition",
            "## More projects",
            "## How I work",
            "AquaSense",
            "InternLog AI",
            "AI Content Strategy",
            "PT Pindad (Persero)",
            "PKM-KC 2026 Funding Recipient",
            "Public source · Source-verifiable",
            "Private source · Sanitized case study",
            "<!-- PROFILE-ACTIVITY:START -->",
        ]:
            self.assertIn(expected, readme)
        self.assertNotIn("2341720069@student.belajar.id", readme)
        self.assertNotIn("hero-monochrome-banner", readme)
        self.assertNotIn("SIMAK", readme)

    def test_requires_three_featured_projects_and_one_public_feature(self):
        _, projects, _ = self.load_all()
        payload = copy.deepcopy(projects)
        featured = [p for p in payload["projects"] if p["profile_section"] == "featured"]
        featured[0]["profile_section"] = "supporting"
        errors = render_profile.validate_projects(payload, ROOT)
        self.assertTrue(any("exactly 3 featured" in error for error in errors))

        payload = copy.deepcopy(projects)
        for project in payload["projects"]:
            if project["profile_section"] == "featured":
                project["visibility"] = "private"
        errors = render_profile.validate_projects(payload, ROOT)
        self.assertTrue(any("at least one featured project" in error for error in errors))

    def test_rejects_case_study_that_escapes_repository(self):
        _, projects, _ = self.load_all()
        payload = copy.deepcopy(projects)
        featured = next(p for p in payload["projects"] if p["profile_section"] == "featured")
        featured["links"]["case_study"] = "../../outside.md"
        errors = render_profile.validate_projects(payload, ROOT)
        self.assertTrue(any("escapes repository" in error for error in errors))

    def test_render_is_idempotent_against_checked_in_readme(self):
        profile, projects, activity = self.load_all()
        rendered = render_profile.render_readme(profile, projects, activity)
        current = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertEqual(current, rendered)


if __name__ == "__main__":
    unittest.main()
