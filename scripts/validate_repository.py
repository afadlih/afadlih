#!/usr/bin/env python3
"""Validate repository-level policies for the special GitHub profile."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REMOVED_PATHS = [
    "website-export",
    "portfolio/site-config.json",
    "scripts/export_website_data.py",
    "scripts/validate_website_export.py",
    ".github/workflows/website-export.yml",
    "portfolio/candidate-projects.json",
    "scripts/promote_candidate.py",
    ".github/workflows/candidate-intake.yml",
    "assets/profile/hero-monochrome-banner.png",
    ".github/dependabot.yml",
    "portfolio/public-commit-activity.json",
    "schemas/public-commit-activity.schema.json",
    "scripts/update_public_commit_activity.py",
    "scripts/render_public_activity.py",
    "assets/public-activity.svg",
    "tests/test_public_commit_activity.py",
    "tests/fixtures/public-commits-api.json",
]
FORBIDDEN_README_TERMS = [
    "PORTFOLIO-PULSE",
    "Live Portfolio Pulse",
    "2341720069@student.belajar.id",
    "hero-monochrome-banner",
    "placeholder asset",
    "missing-real",
    "SIMAK",
    "readme-typing-svg.demolab.com",
    "github-readme-stats.vercel.app",
    "github-readme-activity-graph.vercel.app",
    "PUBLIC COMMITS / 30 DAYS",
    "Version / stage",
]
ACTION_REF = re.compile(r"^\s*uses:\s*([^\s]+)@([^\s#]+)", re.MULTILINE)
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def main() -> int:
    errors: list[str] = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    projects = json.loads((ROOT / "portfolio/projects.json").read_text(encoding="utf-8"))["projects"]

    for relative in REMOVED_PATHS:
        if (ROOT / relative).exists():
            errors.append(f"removed or superseded path still exists: {relative}")
    for term in FORBIDDEN_README_TERMS:
        if term.lower() in readme.lower():
            errors.append(f"forbidden or stale README term found: {term}")

    for marker in ("<!-- PROFILE-ACTIVITY:START -->", "<!-- PROFILE-ACTIVITY:END -->"):
        if readme.count(marker) != 1:
            errors.append(f"README must contain exactly one marker: {marker}")

    for section in (
        "## What I build",
        "## Current engineering focus",
        "## Selected work",
        "## Experience & recognition",
        "## More projects",
        "## GitHub activity",
        "### Private work activity — sanitized",
        "## How I work",
        "## Contact",
    ):
        if section not in readme:
            errors.append(f"README missing required section: {section}")

    for local_asset in ("assets/profile-banner.svg", "assets/engineering-activity.svg"):
        if local_asset not in readme:
            errors.append(f"README must reference repository-owned asset: {local_asset}")
        if not (ROOT / local_asset).is_file():
            errors.append(f"missing repository-owned asset: {local_asset}")

    featured = [project for project in projects if project.get("profile_section") == "featured"]
    if len(featured) != 3:
        errors.append("exactly three featured projects are required")
    if not any(project.get("visibility") == "public" for project in featured):
        errors.append("at least one featured project must be publicly inspectable")
    if any(project.get("slug") == "simak" for project in projects):
        errors.append("SIMAK must not be present in project data")

    required_workflows = {"validate-profile.yml", "update-profile-activity.yml"}
    workflow_dir = ROOT / ".github/workflows"
    actual_workflows = {path.name for path in workflow_dir.glob("*.yml")}
    if actual_workflows != required_workflows:
        errors.append(
            f"workflow set must be focused: expected {sorted(required_workflows)}, found {sorted(actual_workflows)}"
        )

    activity_workflow = (workflow_dir / "update-profile-activity.yml").read_text(encoding="utf-8")
    for required_text in (
        'cron: "17 23 * * *"',
        "scripts/discover_projects.py --write",
        "portfolio/discovered-projects.json",
        "portfolio/private-project-registry.json",
        "git push origin HEAD:main",
    ):
        if required_text not in activity_workflow:
            errors.append(f"daily activity workflow missing required behavior: {required_text}")
    if 'cron: "17 23 * * 0"' in activity_workflow:
        errors.append("weekly-only schedule is still configured")

    for workflow in sorted(workflow_dir.glob("*.yml")):
        text = workflow.read_text(encoding="utf-8")
        if "permissions:" not in text or "concurrency:" not in text or "timeout-minutes:" not in text:
            errors.append(f"workflow lacks security/operational guardrails: {workflow.relative_to(ROOT)}")
        for action, ref in ACTION_REF.findall(text):
            if not SHA40.fullmatch(ref):
                errors.append(
                    f"workflow action is not pinned to a full SHA: {workflow.relative_to(ROOT)} uses {action}@{ref}"
                )

    required_paths = (
        "docs/REPOSITORY_SETTINGS.md",
        "docs/ACTIVITY_DATA_PROVENANCE.md",
        "docs/PROJECT_DISCOVERY.md",
        "schemas/profile.schema.json",
        "schemas/projects.schema.json",
        "schemas/proof-assets.schema.json",
        "schemas/activity-sources.schema.json",
        "schemas/repository-activity.schema.json",
        "schemas/engineering-activity.schema.json",
        "schemas/private-project-registry.schema.json",
        "schemas/discovered-projects.schema.json",
        "portfolio/engineering-activity.json",
        "portfolio/private-project-registry.json",
        "portfolio/discovered-projects.json",
        "scripts/update_engineering_activity.py",
        "scripts/discover_projects.py",
        "scripts/review_discovered_project.py",
        "scripts/render_engineering_activity.py",
        "scripts/validate_engineering_activity.py",
        "scripts/validate_project_discovery.py",
        "scripts/render_profile_readme.py",
        "tests/test_engineering_activity.py",
        "tests/test_project_discovery.py",
    )
    for required_path in required_paths:
        if not (ROOT / required_path).is_file():
            errors.append(f"missing required repository hardening file: {required_path}")

    tracked_private_files = [
        ROOT / "portfolio/private-project-registry.json",
        ROOT / "portfolio/engineering-activity.json",
        ROOT / "portfolio/discovered-projects.json",
    ]
    for path in tracked_private_files:
        text = path.read_text(encoding="utf-8").lower()
        for marker in ("api.github.com/repos/", "refs/heads/"):
            if marker in text:
                errors.append(f"tracked privacy-reviewed file exposes forbidden repository metadata: {path.relative_to(ROOT)}")

    if errors:
        print("Repository policy validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Repository policy validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
