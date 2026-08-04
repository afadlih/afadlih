from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


proof = load_module("validate_proof_assets", ROOT / "scripts" / "validate_proof_assets.py")


class ProofAndPolicyTests(unittest.TestCase):
    def test_strict_proof_manifest_is_complete(self):
        self.assertEqual([], proof.validate_manifest("strict"))

    def test_featured_public_project_is_pinned_to_source_commit(self):
        payload = json.loads((ROOT / "portfolio" / "proof-assets.json").read_text(encoding="utf-8"))
        project = next(item for item in payload["projects"] if item["slug"] == "ai-content-strategy")
        verified = [item for item in project["items"] if item["status"] == "source-verified"]
        self.assertEqual(1, len(verified))
        self.assertEqual(40, len(verified[0]["source_commit"]))

    def test_removed_export_and_candidate_features_do_not_exist(self):
        removed = [
            "website-export",
            "portfolio/site-config.json",
            "portfolio/candidate-projects.json",
            "scripts/export_website_data.py",
            "scripts/promote_candidate.py",
            ".github/workflows/website-export.yml",
            ".github/workflows/candidate-intake.yml",
            ".github/workflows/profile-update-pr.yml",
            ".github/workflows/final-portfolio-quality-gate.yml",
        ]
        for relative in removed:
            self.assertFalse((ROOT / relative).exists(), relative)

    def test_apply_script_has_dry_run_backup_and_rollback(self):
        text = (ROOT / "APPLY-TO-CURRENT-REPO.ps1").read_text(encoding="utf-8")
        for expected in ["[switch]$DryRun", "Get-RepositoryFileMap", "Show-ApplyPlan", "Compress-Archive", "rollback snapshot", "Clear-RepositoryWorktree", "Restoring the pre-apply snapshot", "final-check"]:
            self.assertIn(expected, text)

    def test_repository_policy_command_passes(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_repository.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
