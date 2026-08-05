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


def render_private_activity(activity: dict[str, Any]) -> str:
    """Render private work as one aggregate plus a collapsed metadata index."""
    ordered = sorted(
        activity["private_projects"],
        key=lambda entry: (entry["latest_commit"], entry["project"].lower()),
        reverse=True,
    )
    rows = [
        "| Project | Version | Condition | Latest activity |",
        "| --- | :---: | --- | :---: |",
    ]
    for item in ordered:
        rows.append(
            f"| **{core.esc(item['project'])}** | `{core.esc(item['version'])}` | "
            f"{core.esc(item['condition'])} | `{core.esc(item['latest_commit'])}` |"
        )

    summary = activity["summary"]
    aggregate = (
        f"**Private work aggregate:** `{int(summary['selected_private_commits'])}` authored commits "
        f"across `{int(summary['selected_private_projects'])}` approved projects in the rolling "
        "180-day snapshot. This is context, not a project-quality score."
    )
    return f'''{aggregate}

<details>
<summary><strong>Private project version and activity index</strong></summary>

{"\n".join(rows)}

</details>'''


def render_github_activity(_profile: dict[str, Any]) -> str:
    activity = core.load_json(ENGINEERING_PATH)
    window = activity["window"]
    return f'''<p align="center">
  <img src="assets/engineering-activity.svg" width="100%" alt="180-day engineering activity overview with privacy-reviewed private aggregate" />
</p>

{render_private_activity(activity)}

<sub>The visualization covers authored commits indexed from {core.esc(window['start'])} through {core.esc(window['end'])}. It is a bounded snapshot rather than a lifetime total, and private repository URLs, branches, SHAs, and commit messages are never published.</sub>'''


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
