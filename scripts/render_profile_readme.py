#!/usr/bin/env python3
"""Render the final GitHub README with repository-owned visual assets."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "scripts" / "render_profile.py"
spec = importlib.util.spec_from_file_location("render_profile_core", CORE_PATH)
core = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(core)


def render_visual_header(profile: dict[str, Any]) -> str:
    return f'''<p align="center">
  <img src="assets/profile-banner.svg" width="100%" alt="Animated engineering profile banner for {core.esc(profile['name'])}" />
</p>

<p align="center"><strong>{core.esc(profile['role'])}</strong></p>
<p align="center">
  <code>AI WORKFLOWS</code> ·
  <code>FULL-STACK SYSTEMS</code> ·
  <code>ON-PREMISE IOT</code> ·
  <code>SYSTEM INTEGRATION</code>
</p>
<p align="center">
  <a href="{core.esc(profile['portfolio_url'])}">Portfolio</a> ·
  <a href="{core.esc(profile['linkedin_url'])}">LinkedIn</a> ·
  <a href="{core.esc(profile['github_url'])}">GitHub</a>
</p>
<p align="center">
  <a href="#current-engineering-focus">Current focus</a> ·
  <a href="#selected-work">Selected work</a> ·
  <a href="#github-activity">GitHub activity</a> ·
  <a href="#contact">Contact</a>
</p>'''


def render_private_activity(profile: dict[str, Any]) -> str:
    rows = [
        "| Private project | Latest private commit | Stage | Public-safe scope |",
        "| --- | --- | --- | --- |",
    ]
    for item in sorted(profile["private_activity"], key=lambda entry: entry["latest_commit"], reverse=True):
        project = core.md_link(core.esc(item["project"]), item.get("case_study")) or f"**{core.esc(item['project'])}**"
        rows.append(
            f"| {project} | {core.esc(item['latest_commit'])} | `{core.esc(item['stage'])}` | {core.esc(item['public_summary'])} |"
        )
    return "\n".join(rows)


def render_github_activity(profile: dict[str, Any]) -> str:
    return f'''<p align="center">
  <img src="assets/public-activity.svg" width="100%" alt="Generated public commit activity with a sanitized private work snapshot" />
</p>

<sub>The bars are generated from a bounded sample of authored commits in allowlisted public repositories. Private work is shown only as a curated project/date snapshot—never as repository URLs, branches, commit messages, or SHAs.</sub>

### Private work activity — sanitized

{render_private_activity(profile)}

<sub>Private dates were reviewed through authenticated repository access on 2026-08-05. They are intentionally static until the next privacy-reviewed profile update; the public workflow does not receive a cross-repository private token.</sub>'''


core.render_visual_header = render_visual_header
core.render_github_activity = render_github_activity

load_json = core.load_json
validate_profile = core.validate_profile
validate_projects = core.validate_projects
validate_activity = core.validate_activity
render_readme = core.render_readme
require_valid = core.require_valid


def main(argv: list[str] | None = None) -> int:
    return core.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
