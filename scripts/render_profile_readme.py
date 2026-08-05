#!/usr/bin/env python3
"""Render the final GitHub README with repository-owned visual assets."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "scripts" / "render_profile.py"
ENGINEERING_PATH = ROOT / "portfolio" / "engineering-activity.json"
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


def render_private_activity(activity: dict[str, Any]) -> str:
    """Render a compact private-work index without per-project commit counts."""
    rows = [
        "| Private project | Version | Condition | Latest activity | Deep dive |",
        "| --- | :---: | --- | :---: | --- |",
    ]
    ordered = sorted(
        activity["private_projects"],
        key=lambda entry: (entry["latest_commit"], entry["project"].lower()),
        reverse=True,
    )
    for item in ordered:
        case_study = item.get("case_study")
        deep_dive = core.md_link("Case study", case_study) if case_study else "Overview only"
        rows.append(
            f"| **{core.esc(item['project'])}** | `{core.esc(item['version'])}` | "
            f"{core.esc(item['condition'])} | `{core.esc(item['latest_commit'])}` | {deep_dive} |"
        )

    scopes = "\n".join(
        f"- **{core.esc(item['project'])}** — {core.esc(item['public_summary'])}"
        for item in ordered
    )
    summary = activity["summary"]
    aggregate = (
        f"**Aggregate private activity:** `{int(summary['selected_private_commits'])}` authored commits "
        f"across `{int(summary['selected_private_projects'])}` approved projects during the rolling "
        "180-day window. Per-project commit counts are intentionally not published."
    )
    return aggregate + "\n\n" + "\n".join(rows) + f"""

<details>
<summary><strong>Public-safe scope and deep-dive coverage</strong></summary>

{scopes}

</details>"""


def render_github_activity(_profile: dict[str, Any]) -> str:
    activity = core.load_json(ENGINEERING_PATH)
    window = activity["window"]
    return f'''<p align="center">
  <img src="assets/engineering-activity.svg" width="100%" alt="180-day authored commit history with sanitized private project aggregates" />
</p>

<sub>The chart covers authored commits indexed by GitHub Search from {core.esc(window['start'])} through {core.esc(window['end'])}. It is a bounded snapshot, not a lifetime total, and may differ from contribution-calendar counts because GitHub applies different attribution and indexing rules.</sub>

### Private work activity — sanitized

{render_private_activity(activity)}

<sub>Private aggregation is privacy-reviewed. It publishes only the aggregate private commit total plus approved project labels, source-verified versions, development conditions, dates, and sanitized case-study links—never per-project commit counts, private repository URLs, branch names, commit messages, or SHAs.</sub>'''


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
