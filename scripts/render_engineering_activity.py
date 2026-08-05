#!/usr/bin/env python3
"""Render a repository-owned six-month engineering activity SVG."""
from __future__ import annotations

import argparse
import difflib
import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "portfolio" / "engineering-activity.json"
OUTPUT_PATH = ROOT / "assets" / "engineering-activity.svg"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def short_label(value: str, limit: int = 29) -> str:
    return value if len(value) <= limit else value[: limit - 3] + "..."


def render_svg(payload: dict[str, Any]) -> str:
    periods = payload["periods"]
    summary = payload["summary"]
    private_projects = sorted(
        payload["private_projects"],
        key=lambda item: (item["latest_commit"], item["project"].lower()),
        reverse=True,
    )
    window = payload["window"]

    width = 1200
    height = 590
    plot_left = 68
    plot_top = 250
    plot_width = 730
    plot_height = 220
    baseline = plot_top + plot_height
    bar_gap = 24
    bar_width = (plot_width - bar_gap * (len(periods) - 1)) / max(len(periods), 1)
    maximum = max((int(item["commits"]) for item in periods), default=0) or 1

    bars: list[str] = []
    labels: list[str] = []
    for index, item in enumerate(periods):
        count = int(item["commits"])
        visible_height = max(3.0, (count / maximum) * plot_height) if count else 3.0
        x = plot_left + index * (bar_width + bar_gap)
        y = baseline - visible_height
        opacity = "0.28" if count == 0 else "0.94"
        bars.append(
            f'''    <rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{visible_height:.2f}" rx="6" fill="url(#bar)" opacity="{opacity}">
      <title>{esc(item["start"])} to {esc(item["end"])}: {count} authored commits indexed by GitHub Search</title>
      <animate attributeName="opacity" values="{opacity};1;{opacity}" dur="3s" begin="{index * 0.12:.2f}s" repeatCount="indefinite" />
    </rect>'''
        )
        labels.append(
            f'    <text x="{x + bar_width / 2:.2f}" y="{baseline + 25}" text-anchor="middle" class="axis">{esc(item["label"])}</text>'
        )
        if count:
            labels.append(
                f'    <text x="{x + bar_width / 2:.2f}" y="{max(y - 10, plot_top - 8):.2f}" text-anchor="middle" class="bar-value">{count}</text>'
            )

    private_lines: list[str] = []
    visible_private = private_projects[:7]
    for index, item in enumerate(visible_private):
        y = 270 + index * 37
        private_lines.append(
            f'    <text x="830" y="{y}" class="repo">{index + 1}. {esc(short_label(item["project"]))}</text>'
        )
        private_lines.append(
            f'    <text x="1138" y="{y}" text-anchor="end" class="repo-date">{esc(item["latest_commit"])}</text>'
        )
        private_lines.append(
            f'    <text x="848" y="{y + 16}" class="repo-meta">{esc(item["version"])} · {esc(item["condition"])}</text>'
        )

    if len(private_projects) > len(visible_private):
        private_lines.append(
            f'    <text x="850" y="536" class="repo-meta">+{len(private_projects) - len(visible_private)} more approved project(s) in README</text>'
        )

    cards = [
        ("AUTHORED COMMITS / 180 DAYS", summary["authored_commits"]),
        ("PRIVATE COMMITS · AGGREGATE", summary["selected_private_commits"]),
        ("PRIVATE PROJECTS TRACKED", summary["selected_private_projects"]),
        ("LATEST PRIVATE UPDATE", summary["latest_private_update"]),
    ]
    card_parts: list[str] = []
    for index, (label, value) in enumerate(cards):
        x = 48 + index * 286
        card_parts.append(
            f'''    <g transform="translate({x} 96)">
      <rect width="262" height="90" rx="14" class="card" />
      <text x="18" y="30" class="card-label">{esc(label)}</text>
      <text x="18" y="68" class="card-value">{esc(value)}</text>
    </g>'''
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Six-month engineering activity for {esc(payload["username"])}</title>
  <desc id="desc">Authored commit history grouped by period with one privacy-reviewed aggregate total for selected private projects.</desc>
  <defs>
    <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#07111f"/>
      <stop offset="0.55" stop-color="#0b1f3a"/>
      <stop offset="1" stop-color="#102a43"/>
    </linearGradient>
    <linearGradient id="bar" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="#38bdf8"/>
      <stop offset="1" stop-color="#2dd4bf"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="#94a3b8" stroke-opacity="0.08" stroke-width="1"/>
    </pattern>
    <style>
      .title {{ fill:#f8fafc; font:700 25px Inter,Segoe UI,Arial,sans-serif; }}
      .subtitle {{ fill:#94a3b8; font:400 14px Inter,Segoe UI,Arial,sans-serif; }}
      .card {{ fill:#0f172a; stroke:#334155; stroke-width:1; }}
      .card-label {{ fill:#94a3b8; font:700 10.5px Inter,Segoe UI,Arial,sans-serif; letter-spacing:0.85px; }}
      .card-value {{ fill:#f8fafc; font:700 24px Inter,Segoe UI,Arial,sans-serif; }}
      .section {{ fill:#cbd5e1; font:700 13px Inter,Segoe UI,Arial,sans-serif; letter-spacing:0.72px; }}
      .axis {{ fill:#94a3b8; font:500 9.5px JetBrains Mono,Consolas,monospace; }}
      .bar-value {{ fill:#e2e8f0; font:700 12px JetBrains Mono,Consolas,monospace; }}
      .repo {{ fill:#cbd5e1; font:600 12px Inter,Segoe UI,Arial,sans-serif; }}
      .repo-date {{ fill:#38bdf8; font:700 11px JetBrains Mono,Consolas,monospace; }}
      .repo-meta {{ fill:#64748b; font:500 10px JetBrains Mono,Consolas,monospace; }}
      .note {{ fill:#64748b; font:400 10.5px Inter,Segoe UI,Arial,sans-serif; }}
    </style>
  </defs>

  <rect width="{width}" height="{height}" rx="22" fill="url(#background)"/>
  <rect width="{width}" height="{height}" rx="22" fill="url(#grid)"/>

  <text x="48" y="44" class="title">ENGINEERING ACTIVITY · 180 DAYS</text>
  <text x="48" y="69" class="subtitle">Authenticated authored-commit snapshot · public history + approved private aggregates</text>

{chr(10).join(card_parts)}

  <text x="{plot_left}" y="222" class="section">AUTHORED COMMIT HISTORY · {esc(window["start"])} → {esc(window["end"])}</text>
  <line x1="{plot_left}" y1="{baseline}" x2="{plot_left + plot_width}" y2="{baseline}" stroke="#475569" stroke-width="1"/>
{chr(10).join(bars)}
{chr(10).join(labels)}

  <text x="830" y="222" class="section">PRIVATE PROJECTS · LATEST ACTIVITY</text>
  <line x1="830" y1="232" x2="1140" y2="232" stroke="#334155" stroke-width="1"/>
{chr(10).join(private_lines)}

  <text x="48" y="550" class="note">GitHub Search snapshot, not a lifetime total. Private commit activity is shown only as one aggregate total.</text>
  <text x="48" y="567" class="note">Project rows expose approved labels, versions, conditions, and dates—never per-project counts, URLs, branches, SHAs, or commit messages.</text>
</svg>
'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write assets/engineering-activity.svg")
    mode.add_argument("--check", action="store_true", help="fail when the SVG is stale")
    args = parser.parse_args(argv)

    rendered = render_svg(load_json(INPUT_PATH))
    if args.write:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered, encoding="utf-8", newline="\n")
        print("Wrote assets/engineering-activity.svg")
        return 0
    if args.check:
        current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if current == rendered:
            print("assets/engineering-activity.svg is up to date.")
            return 0
        print("assets/engineering-activity.svg is stale. Diff:")
        print("".join(difflib.unified_diff(current.splitlines(True), rendered.splitlines(True), fromfile="assets/engineering-activity.svg", tofile="generated")))
        return 1
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
