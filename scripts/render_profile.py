#!/usr/bin/env python3
"""Render the special GitHub profile README from curated JSON data."""
from __future__ import annotations

import argparse
import difflib
import html
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "README.md"
PROFILE_PATH = ROOT / "portfolio" / "profile.json"
PROJECTS_PATH = ROOT / "portfolio" / "projects.json"
ACTIVITY_PATH = ROOT / "portfolio" / "repository-activity.json"

VALID_STATUSES = {"draft", "active", "featured", "stable", "archived"}
VALID_SECTIONS = {"featured", "major", "supporting", "archive"}
VALID_VISIBILITY = {"public", "private"}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing required file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def md_link(label: str, url: str | None) -> str:
    return f"[{label}]({url})" if isinstance(url, str) and url.strip() else ""


def validate_profile(profile: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    required = {
        "name", "short_name", "username", "role", "headline", "location",
        "portfolio_url", "github_url", "linkedin_url", "availability",
        "focus_areas", "experience", "recognition", "engineering_principles",
        "profile_notes",
    }
    missing = sorted(required - profile.keys())
    if missing:
        errors.append(f"profile.json missing fields: {', '.join(missing)}")

    for field in ("focus_areas", "experience", "recognition", "engineering_principles", "profile_notes"):
        if field in profile and not isinstance(profile[field], list):
            errors.append(f"profile.{field} must be a list")

    if isinstance(profile.get("focus_areas"), list) and len(profile["focus_areas"]) != 3:
        errors.append("profile.focus_areas must contain exactly 3 focused areas")
    if isinstance(profile.get("engineering_principles"), list) and len(profile["engineering_principles"]) < 4:
        errors.append("profile.engineering_principles must contain at least 4 items")
    return errors


def validate_projects(payload: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    projects = payload.get("projects")
    if not isinstance(projects, list):
        return ["projects.json must contain a top-level projects list"]

    required = {
        "slug", "name", "title", "status", "profile_section", "visibility",
        "category", "priority", "role", "summary", "problem", "outcome",
        "technologies", "proof_points", "feature_deep_dives", "links",
        "limitations", "proof_level",
    }
    seen_slugs: set[str] = set()
    seen_priorities: set[int] = set()
    featured: list[dict[str, Any]] = []
    major_count = 0

    for index, project in enumerate(projects, start=1):
        if not isinstance(project, dict):
            errors.append(f"projects[{index}] must be an object")
            continue
        slug = project.get("slug", f"#{index}")
        missing = sorted(required - project.keys())
        if missing:
            errors.append(f"project {slug} missing fields: {', '.join(missing)}")
        if not isinstance(slug, str) or not SLUG.fullmatch(slug):
            errors.append(f"project {slug} has invalid slug")
        if slug in seen_slugs:
            errors.append(f"duplicate project slug: {slug}")
        seen_slugs.add(slug)

        if project.get("status") not in VALID_STATUSES:
            errors.append(f"project {slug} has invalid status: {project.get('status')}")
        section = project.get("profile_section")
        if section not in VALID_SECTIONS:
            errors.append(f"project {slug} has invalid profile_section: {section}")
        if project.get("visibility") not in VALID_VISIBILITY:
            errors.append(f"project {slug} has invalid visibility: {project.get('visibility')}")

        priority = project.get("priority")
        if not isinstance(priority, int) or priority < 1:
            errors.append(f"project {slug} priority must be a positive integer")
        elif priority in seen_priorities:
            errors.append(f"duplicate project priority: {priority}")
        else:
            seen_priorities.add(priority)

        for field in ("technologies", "proof_points", "feature_deep_dives", "limitations"):
            if not isinstance(project.get(field), list):
                errors.append(f"project {slug}.{field} must be a list")

        links = project.get("links")
        if not isinstance(links, dict):
            errors.append(f"project {slug}.links must be an object")
            links = {}
        case_study = links.get("case_study")
        if case_study:
            path = (root / case_study).resolve()
            try:
                path.relative_to(root.resolve())
            except ValueError:
                errors.append(f"project {slug} case study escapes repository: {case_study}")
            else:
                if not path.is_file():
                    errors.append(f"project {slug} case study does not exist: {case_study}")

        if section == "featured":
            featured.append(project)
            if project.get("status") != "featured":
                errors.append(f"featured project {slug} must use status featured")
            if len(project.get("proof_points", [])) < 3:
                errors.append(f"featured project {slug} needs at least 3 proof points")
            if len(project.get("limitations", [])) < 1:
                errors.append(f"featured project {slug} needs at least 1 limitation")
            if not case_study:
                errors.append(f"featured project {slug} needs a case study")
        elif section == "major":
            major_count += 1
            if not case_study:
                errors.append(f"major project {slug} needs a case study")

    if len(featured) != 3:
        errors.append(f"profile must contain exactly 3 featured projects; found {len(featured)}")
    if not any(project.get("visibility") == "public" for project in featured):
        errors.append("at least one featured project must have a public repository")
    if major_count > 1:
        errors.append("profile may contain at most 1 major case study")
    return errors


def validate_activity(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    items = payload.get("items")
    if not isinstance(items, list):
        return ["repository-activity.json must contain an items list"]
    seen: set[str] = set()
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"activity item {index} must be an object")
            continue
        for field in ("name", "repository", "url"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"activity item {index}.{field} must be a non-empty string")
        repository = item.get("repository")
        if repository in seen:
            errors.append(f"duplicate activity repository: {repository}")
        seen.add(repository)
    return errors


def require_valid(profile: dict[str, Any], projects: dict[str, Any], activity: dict[str, Any]) -> None:
    errors = validate_profile(profile) + validate_projects(projects) + validate_activity(activity)
    if errors:
        raise SystemExit("Profile data validation failed:\n" + "\n".join(f"- {error}" for error in errors))


def project_badge(project: dict[str, Any]) -> str:
    if project["visibility"] == "public":
        return "Public source · Source-verifiable"
    return "Private source · Sanitized case study"


def project_links(project: dict[str, Any]) -> str:
    links = project.get("links", {})
    rendered = [
        md_link("Repository", links.get("repository")),
        md_link("Case study", links.get("case_study")),
        md_link("Demo", links.get("demo")),
        md_link("Video", links.get("video")),
    ]
    return " · ".join(item for item in rendered if item)


def render_focus(profile: dict[str, Any]) -> str:
    chunks = []
    for item in profile["focus_areas"]:
        chunks.append(f"**{esc(item['title'])}**  \n{esc(item['description'])}")
    return "\n\n".join(chunks)


def render_featured(project: dict[str, Any], number: int) -> str:
    proof = "\n".join(f"- {esc(item)}" for item in project["proof_points"])
    limits = "\n".join(f"- {esc(item)}" for item in project["limitations"])
    tech = " ".join(f"`{esc(item)}`" for item in project["technologies"])
    deep = "\n".join(f"- {esc(item)}" for item in project["feature_deep_dives"])
    links = project_links(project)
    return f'''### {number}. {esc(project['name'])}

**{esc(project['category'])} · {project_badge(project)}**

{esc(project['summary'])}

{tech}

**Inspectable evidence**

{proof}

<details>
<summary><strong>Architecture, decisions, and current boundaries</strong></summary>

**Problem**  
{esc(project['problem'])}

**What I built**  
{esc(project['outcome'])}

**Deep-dive topics**

{deep}

**Current boundaries**

{limits}

</details>

{links}'''


def render_supporting(projects: list[dict[str, Any]]) -> str:
    rows = ["| Project | What it demonstrates | Access |", "| --- | --- | --- |"]
    for project in projects:
        links = project_links(project) or "Private source"
        rows.append(f"| **{esc(project['name'])}** | {esc(project['summary'])} | {links} |")
    return "\n".join(rows)


def render_activity(payload: dict[str, Any]) -> str:
    items = payload.get("items", [])
    if not items:
        return "The curated public activity snapshot has not been populated yet."
    rows = ["| Repository | Last public update | Language |", "| --- | --- | --- |"]
    for item in items:
        pushed = item.get("pushed_at")
        date = pushed[:10] if isinstance(pushed, str) and len(pushed) >= 10 else "—"
        language = item.get("language") or "—"
        rows.append(f"| [{esc(item['name'])}]({esc(item['url'])}) | {esc(date)} | {esc(language)} |")
    return "\n".join(rows)


def render_experience(profile: dict[str, Any]) -> str:
    items: list[str] = []
    for entry in profile["experience"]:
        items.append(
            f"- **{esc(entry['organization'])} — {esc(entry['title'])}** ({esc(entry['period'])})  \n"
            f"  {esc(entry['summary'])}"
        )
    for entry in profile["recognition"]:
        items.append(
            f"- **{esc(entry['title'])} — {esc(entry['project'])}**  \n"
            f"  {esc(entry['summary'])}"
        )
    return "\n".join(items)


def render_readme(profile: dict[str, Any], projects_payload: dict[str, Any], activity: dict[str, Any]) -> str:
    projects = sorted(projects_payload["projects"], key=lambda item: item["priority"])
    featured = [project for project in projects if project["profile_section"] == "featured"]
    major = [project for project in projects if project["profile_section"] == "major"]
    supporting = [project for project in projects if project["profile_section"] == "supporting"]
    featured_text = "\n\n---\n\n".join(render_featured(project, index) for index, project in enumerate(featured, start=1))
    major_text = "\n\n".join(render_featured(project, index + len(featured)) for index, project in enumerate(major, start=1))
    principles = "\n".join(f"- {esc(item)}" for item in profile["engineering_principles"])
    notes = "<br>".join(esc(item) for item in profile["profile_notes"])

    return f'''<!-- PROFILE-README:GENERATED -->
<!-- Edit portfolio/*.json, then run: python scripts/portfolio_ci.py update -->

<h1 align="center">{esc(profile['name'])}</h1>
<p align="center"><strong>{esc(profile['role'])}</strong></p>
<p align="center">
  <a href="{esc(profile['portfolio_url'])}">Portfolio</a> ·
  <a href="{esc(profile['linkedin_url'])}">LinkedIn</a> ·
  <a href="{esc(profile['github_url'])}">GitHub</a>
</p>

> {esc(profile['headline'])}

## What I build

{render_focus(profile)}

## Selected work

{featured_text}

## Additional case study

{major_text}

## Experience & recognition

{render_experience(profile)}

## More projects

{render_supporting(supporting)}

## Public work, recently updated

<!-- PROFILE-ACTIVITY:START -->
{render_activity(activity)}
<!-- PROFILE-ACTIVITY:END -->

This snapshot is generated from an allowlisted set of public repositories. Private repository metadata is never published by the updater.

## How I work

{principles}

## Contact

{esc(profile['availability'])}

[Portfolio]({esc(profile['portfolio_url'])}) · [LinkedIn]({esc(profile['linkedin_url'])})

<sub>{notes}</sub>
'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write README.md")
    mode.add_argument("--check", action="store_true", help="fail when README.md is stale")
    args = parser.parse_args(argv)

    profile = load_json(PROFILE_PATH)
    projects = load_json(PROJECTS_PATH)
    activity = load_json(ACTIVITY_PATH)
    require_valid(profile, projects, activity)
    rendered = render_readme(profile, projects, activity)

    if args.write:
        README_PATH.write_text(rendered, encoding="utf-8", newline="\n")
        print("Wrote README.md")
        return 0
    if args.check:
        current = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
        if current == rendered:
            print("README.md is up to date.")
            return 0
        print("README.md is stale. Diff:")
        print("".join(difflib.unified_diff(current.splitlines(True), rendered.splitlines(True), fromfile="README.md", tofile="generated")))
        return 1
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
