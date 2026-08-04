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
]
FORBIDDEN_README_TERMS = [
    "PORTFOLIO-PULSE",
    "Live Portfolio Pulse",
    "2341720069@student.belajar.id",
    "hero-monochrome-banner",
    "placeholder asset",
    "missing-real",
    "SIMAK",
]
ACTION_REF = re.compile(r"^\s*uses:\s*([^\s]+)@([^\s#]+)", re.MULTILINE)
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def main() -> int:
    errors: list[str] = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    projects = json.loads((ROOT / "portfolio/projects.json").read_text(encoding="utf-8"))["projects"]

    for relative in REMOVED_PATHS:
        if (ROOT / relative).exists():
            errors.append(f"removed feature path still exists: {relative}")
    for term in FORBIDDEN_README_TERMS:
        if term.lower() in readme.lower():
            errors.append(f"forbidden or stale README term found: {term}")

    for marker in ("<!-- PROFILE-ACTIVITY:START -->", "<!-- PROFILE-ACTIVITY:END -->"):
        if readme.count(marker) != 1:
            errors.append(f"README must contain exactly one marker: {marker}")

    for section in ("## What I build", "## Selected work", "## Experience & recognition", "## More projects", "## How I work", "## Contact"):
        if section not in readme:
            errors.append(f"README missing required section: {section}")

    featured = [project for project in projects if project.get("profile_section") == "featured"]
    if len(featured) != 3:
        errors.append("exactly three featured projects are required")
    if not any(project.get("visibility") == "public" for project in featured):
        errors.append("at least one featured project must be publicly inspectable")
    if any(project.get("slug") == "simak" for project in projects):
        errors.append("SIMAK must not be present in project data")

    sources = json.loads((ROOT / "portfolio/activity-sources.json").read_text(encoding="utf-8")).get("repositories", [])
    private_names = {"afadlih/Internlog-ai", "afadlih/AquaSense", "afadlih/Polinema_Adaptive_TOEIC", "afadlih/OrthoBreath"}
    if any(item.get("repository") in private_names for item in sources):
        errors.append("private repositories must not be listed in public activity sources")

    required_workflows = {
        "validate-profile.yml",
        "update-profile-activity.yml",
    }
    workflow_dir = ROOT / ".github/workflows"
    actual_workflows = {path.name for path in workflow_dir.glob("*.yml")}
    if actual_workflows != required_workflows:
        errors.append(f"workflow set must be focused: expected {sorted(required_workflows)}, found {sorted(actual_workflows)}")

    for workflow in sorted(workflow_dir.glob("*.yml")):
        text = workflow.read_text(encoding="utf-8")
        if "permissions:" not in text or "concurrency:" not in text or "timeout-minutes:" not in text:
            errors.append(f"workflow lacks security/operational guardrails: {workflow.relative_to(ROOT)}")
        for action, ref in ACTION_REF.findall(text):
            if not SHA40.fullmatch(ref):
                errors.append(f"workflow action is not pinned to a full SHA: {workflow.relative_to(ROOT)} uses {action}@{ref}")

    for required_path in (".github/dependabot.yml", "docs/REPOSITORY_SETTINGS.md", "schemas/profile.schema.json", "schemas/projects.schema.json", "schemas/proof-assets.schema.json", "schemas/activity-sources.schema.json", "schemas/repository-activity.schema.json"):
        if not (ROOT / required_path).is_file():
            errors.append(f"missing required repository hardening file: {required_path}")

    if errors:
        print("Repository policy validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Repository policy validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
