#!/usr/bin/env python3
"""Render the final GitHub README with repository-owned visual assets.

The core renderer keeps profile content and validation in one place. This
adapter replaces fragile third-party image endpoints with local SVG assets.
"""
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


def render_github_activity(_profile: dict[str, Any]) -> str:
    return '''<p align="center">
  <img src="assets/public-activity.svg" width="100%" alt="Generated public commit activity from allowlisted repositories" />
</p>

<sub>The chart is generated inside this repository from a bounded GitHub public commit API sample. Private repositories are excluded, and the values are not presented as lifetime totals.</sub>'''


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
