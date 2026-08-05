#!/usr/bin/env python3
"""Validate engineering activity arithmetic, registry alignment, and privacy."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ACTIVITY_PATH = ROOT / "portfolio" / "engineering-activity.json"
PROFILE_PATH = ROOT / "portfolio" / "profile.json"
REGISTRY_PATH = ROOT / "portfolio" / "private-project-registry.json"
FORBIDDEN_KEYS = {"repository", "url", "branch", "sha", "message", "commit_message"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_forbidden_keys(value: Any, path: str = "<root>") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key.lower() in FORBIDDEN_KEYS:
                errors.append(f"private activity must not persist sensitive key: {child_path}")
            errors.extend(collect_forbidden_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(collect_forbidden_keys(child, f"{path}[{index}]"))
    return errors


def main() -> int:
    activity = load_json(ACTIVITY_PATH)
    profile = load_json(PROFILE_PATH)
    registry = load_json(REGISTRY_PATH)
    errors = collect_forbidden_keys(activity)

    window = activity["window"]
    start = date.fromisoformat(window["start"])
    end = date.fromisoformat(window["end"])
    if (end - start).days + 1 != window["days"]:
        errors.append("engineering activity window.days does not match inclusive start/end")

    expected_start = start
    for index, period in enumerate(activity["periods"]):
        period_start = date.fromisoformat(period["start"])
        period_end = date.fromisoformat(period["end"])
        if period_start != expected_start:
            errors.append(f"period {index + 1} is not contiguous; expected {expected_start}")
        if period_end < period_start:
            errors.append(f"period {index + 1} ends before it starts")
        expected_start = period_end + timedelta(days=1)
    if expected_start != end + timedelta(days=1):
        errors.append("activity periods do not cover the complete 180-day window")

    period_total = sum(int(period["commits"]) for period in activity["periods"])
    if period_total != int(activity["summary"]["authored_commits"]):
        errors.append("summary.authored_commits does not equal the sum of period commits")

    private_projects = activity["private_projects"]
    if int(activity["summary"]["selected_private_commits"]) > int(activity["summary"]["authored_commits"]):
        errors.append("summary.selected_private_commits cannot exceed authored_commits")
    if len(private_projects) != int(activity["summary"]["selected_private_projects"]):
        errors.append("summary.selected_private_projects does not match the project list")
    if max(item["latest_commit"] for item in private_projects) != activity["summary"]["latest_private_update"]:
        errors.append("summary.latest_private_update does not match private project data")

    seen: set[str] = set()
    private_by_project: dict[str, dict[str, Any]] = {}
    for item in private_projects:
        project = item["project"]
        if project in seen:
            errors.append(f"duplicate private activity project: {project}")
        seen.add(project)
        if "commits" in item:
            errors.append(f"{project} must not publish a per-project commit count")
        private_by_project[project] = item

    enabled_registry = {
        item["project"]: item for item in registry["projects"] if item["enabled"] is True
    }
    if set(private_by_project) != set(enabled_registry):
        errors.append("engineering activity labels must exactly match enabled private registry labels")
    for project, item in private_by_project.items():
        approved = enabled_registry.get(project)
        if not approved:
            continue
        if item["public_summary"] != approved["public_summary"]:
            errors.append(f"{project} public summary differs from private registry")
        if item["case_study"] != approved["case_study"]:
            errors.append(f"{project} case study differs from private registry")

    expected_focus = [
        item for item in private_projects
        if enabled_registry[item["project"]].get("show_in_current_focus") is True
    ]
    expected_focus.sort(
        key=lambda item: (item["latest_commit"], item["project"].lower()),
        reverse=True,
    )
    profile_focus_names = [item["project"] for item in profile["current_focus"]]
    expected_focus_names = [item["project"] for item in expected_focus[:3]]
    if profile_focus_names != expected_focus_names:
        errors.append("profile current_focus is not ordered by latest approved private activity")

    for focus in profile["current_focus"]:
        item = private_by_project.get(focus["project"])
        approved = enabled_registry.get(focus["project"])
        if not item or not approved:
            errors.append(f"current focus is not backed by an approved private project: {focus['project']}")
            continue
        for field in ("version", "condition"):
            if focus[field] != item[field]:
                errors.append(f"{focus['project']} {field} differs between profile and activity")
        if focus["updated"] != item["latest_commit"]:
            errors.append(f"{focus['project']} latest commit differs between profile and activity")
        if focus["focus"] != approved["focus"] or focus["link"] != approved["profile_link"]:
            errors.append(f"{focus['project']} focus metadata differs from private registry")

    serialized = json.dumps(activity, ensure_ascii=False).lower()
    for forbidden in ("github.com/", "api.github.com/repos/", "refs/heads/"):
        if forbidden in serialized:
            errors.append(f"private engineering snapshot leaks repository metadata: {forbidden}")

    if errors:
        print("Engineering activity validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Engineering activity validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
