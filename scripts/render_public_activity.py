#!/usr/bin/env python3
"""Render the repository-owned public activity SVG from generated JSON."""
from __future__ import annotations

import argparse
import difflib
import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "portfolio" / "public-commit-activity.json"
OUTPUT_PATH = ROOT / "assets" / "public-activity.svg"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def short_repository(repository: str) -> str:
    name = repository.split("/", 1)[-1]
    return name if len(name) <= 27 else name[:24] + "..."


def render_svg(payload: dict[str, Any]) -> str:
    daily = payload["daily"]
    summary = payload["summary"]
    repositories = payload["repositories"]
    window = payload["window"]

    width = 1200
    height = 430
    plot_left = 72
    plot_top = 218
    plot_width = 780
    plot_height = 142
    baseline = plot_top + plot_height
    bar_gap = 5
    bar_width = (plot_width - bar_gap * (len(daily) - 1)) / max(len(daily), 1)
    maximum = max((int(item["commits"]) for item in daily), default=0) or 1

    bars: list[str] = []
    labels: list[str] = []
    for index, item in enumerate(daily):
        count = int(item["commits"])
        visible_height = max(2.0, (count / maximum) * plot_height) if count else 2.0
        x = plot_left + index * (bar_width + bar_gap)
        y = baseline - visible_height
        opacity = "0.34" if count == 0 else "0.92"
        bars.append(
            f'''    <rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{visible_height:.2f}" rx="3" fill="url(#bar)" opacity="{opacity}">
      <title>{esc(item["date"])}: {count} sampled commits</title>
      <animate attributeName="opacity" values="{opacity};1;{opacity}" dur="2.8s" begin="{index * 0.035:.3f}s" repeatCount="indefinite" />
    </rect>'''
        )
        if index in {0, 5, 10, 15, 20, 25, len(daily) - 1}:
            labels.append(
                f'    <text x="{x + bar_width / 2:.2f}" y="{baseline + 24}" text-anchor="middle" class="axis">{esc(item["date"][5:])}</text>'
            )

    repo_lines: list[str] = []
    for index, item in enumerate(repositories[:5]):
        y = 246 + index * 30
        repo_lines.append(
            f'    <text x="905" y="{y}" class="repo">{index + 1}. {esc(short_repository(item["repository"]))}</text>'
        )
        repo_lines.append(
            f'    <text x="1138" y="{y}" text-anchor="end" class="repo-count">{int(item["sampled_commits"])}</text>'
        )

    latest = payload["latest_public_commit_at"][:10]
    cards = [
        ("COMMITS / 30 DAYS", summary["commits_in_window"]),
        ("ACTIVE DAYS", summary["active_days"]),
        ("PUBLIC REPOS SAMPLED", summary["repositories_with_commits"]),
        ("LATEST PUBLIC COMMIT", latest),
    ]
    card_parts: list[str] = []
    for index, (label, value) in enumerate(cards):
        x = 48 + index * 286
        card_parts.append(
            f'''    <g transform="translate({x} 92)">
      <rect width="262" height="88" rx="14" class="card" />
      <text x="18" y="29" class="card-label">{esc(label)}</text>
      <text x="18" y="65" class="card-value">{esc(value)}</text>
    </g>'''
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Public GitHub engineering activity for {esc(payload["username"])}</title>
  <desc id="desc">A repository-owned chart generated from a bounded sample of authored commits in allowlisted public repositories.</desc>
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
      .card-label {{ fill:#94a3b8; font:700 11px Inter,Segoe UI,Arial,sans-serif; letter-spacing:1.1px; }}
      .card-value {{ fill:#f8fafc; font:700 25px Inter,Segoe UI,Arial,sans-serif; }}
      .section {{ fill:#cbd5e1; font:700 13px Inter,Segoe UI,Arial,sans-serif; letter-spacing:0.8px; }}
      .axis {{ fill:#94a3b8; font:400 10px JetBrains Mono,Consolas,monospace; }}
      .repo {{ fill:#cbd5e1; font:500 13px Inter,Segoe UI,Arial,sans-serif; }}
      .repo-count {{ fill:#38bdf8; font:700 13px JetBrains Mono,Consolas,monospace; }}
      .note {{ fill:#64748b; font:400 11px Inter,Segoe UI,Arial,sans-serif; }}
    </style>
  </defs>

  <rect width="{width}" height="{height}" rx="22" fill="url(#background)"/>
  <rect width="{width}" height="{height}" rx="22" fill="url(#grid)"/>

  <text x="48" y="43" class="title">PUBLIC ENGINEERING ACTIVITY</text>
  <text x="48" y="67" class="subtitle">Allowlisted public repositories · last {payload["sample_limit_per_repository"]} authored commits sampled per repository</text>

{chr(10).join(card_parts)}

  <text x="{plot_left}" y="207" class="section">30-DAY COMMIT SAMPLE · {esc(window["start"])} → {esc(window["end"])}</text>
  <line x1="{plot_left}" y1="{baseline}" x2="{plot_left + plot_width}" y2="{baseline}" stroke="#475569" stroke-width="1"/>
{chr(10).join(bars)}
{chr(10).join(labels)}

  <text x="905" y="207" class="section">TOP REPOSITORIES IN SAMPLE</text>
  <line x1="905" y1="217" x2="1140" y2="217" stroke="#334155" stroke-width="1"/>
{chr(10).join(repo_lines)}

  <text x="48" y="407" class="note">Generated inside this repository from GitHub's public commit API. Private repositories are excluded. Values are a bounded sample, not lifetime totals.</text>
</svg>
'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write assets/public-activity.svg")
    mode.add_argument("--check", action="store_true", help="fail when the SVG is stale")
    args = parser.parse_args(argv)

    rendered = render_svg(load_json(INPUT_PATH))
    if args.write:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered, encoding="utf-8", newline="\n")
        print("Wrote assets/public-activity.svg")
        return 0
    if args.check:
        current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if current == rendered:
            print("assets/public-activity.svg is up to date.")
            return 0
        print("assets/public-activity.svg is stale. Diff:")
        print(
            "".join(
                difflib.unified_diff(
                    current.splitlines(True),
                    rendered.splitlines(True),
                    fromfile="assets/public-activity.svg",
                    tofile="generated",
                )
            )
        )
        return 1
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
