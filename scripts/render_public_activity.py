#!/usr/bin/env python3
"""Render a repository-owned engineering activity SVG.

Public bars come from the bounded public commit sample. Private work is shown
only as curated project names and dates from profile.json; no private repository
URL, branch, SHA, or commit message is rendered.
"""
from __future__ import annotations

import argparse
import difflib
import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "portfolio" / "public-commit-activity.json"
PROFILE_PATH = ROOT / "portfolio" / "profile.json"
OUTPUT_PATH = ROOT / "assets" / "public-activity.svg"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def short_label(value: str, limit: int = 28) -> str:
    return value if len(value) <= limit else value[: limit - 3] + "..."


def render_svg(payload: dict[str, Any], private_activity: list[dict[str, Any]]) -> str:
    daily = payload["daily"]
    summary = payload["summary"]
    repositories = payload["repositories"]
    window = payload["window"]
    private_sorted = sorted(private_activity, key=lambda item: item["latest_commit"], reverse=True)

    width = 1200
    height = 540
    plot_left = 72
    plot_top = 232
    plot_width = 735
    plot_height = 178
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
        opacity = "0.32" if count == 0 else "0.92"
        bars.append(
            f'''    <rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{visible_height:.2f}" rx="3" fill="url(#bar)" opacity="{opacity}">
      <title>{esc(item["date"])}: {count} sampled public commits</title>
      <animate attributeName="opacity" values="{opacity};1;{opacity}" dur="2.8s" begin="{index * 0.035:.3f}s" repeatCount="indefinite" />
    </rect>'''
        )
        if index in {0, 5, 10, 15, 20, 25, len(daily) - 1}:
            labels.append(
                f'    <text x="{x + bar_width / 2:.2f}" y="{baseline + 24}" text-anchor="middle" class="axis">{esc(item["date"][5:])}</text>'
            )

    public_lines: list[str] = []
    for index, item in enumerate(repositories[:3]):
        y = 247 + index * 27
        name = short_label(item["repository"].split("/", 1)[-1], 25)
        public_lines.append(f'    <text x="860" y="{y}" class="repo">{index + 1}. {esc(name)}</text>')
        public_lines.append(f'    <text x="1138" y="{y}" text-anchor="end" class="repo-count">{int(item["sampled_commits"])}</text>')

    private_lines: list[str] = []
    for index, item in enumerate(private_sorted[:6]):
        y = 365 + index * 25
        private_lines.append(f'    <text x="860" y="{y}" class="repo">{esc(short_label(item["project"], 25))}</text>')
        private_lines.append(f'    <text x="1138" y="{y}" text-anchor="end" class="private-date">{esc(item["latest_commit"])}</text>')

    latest_private = max((item["latest_commit"] for item in private_sorted), default="—")
    cards = [
        ("PUBLIC COMMITS / 30 DAYS", summary["commits_in_window"]),
        ("ACTIVE PUBLIC DAYS", summary["active_days"]),
        ("PRIVATE PROJECTS TRACKED", len(private_sorted)),
        ("LATEST PRIVATE UPDATE", latest_private),
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
  <title id="title">Public and sanitized private engineering activity for {esc(payload["username"])}</title>
  <desc id="desc">Public authored-commit bars plus a privacy-reviewed snapshot of private project names and latest activity dates.</desc>
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
      .card-label {{ fill:#94a3b8; font:700 11px Inter,Segoe UI,Arial,sans-serif; letter-spacing:1.05px; }}
      .card-value {{ fill:#f8fafc; font:700 24px Inter,Segoe UI,Arial,sans-serif; }}
      .section {{ fill:#cbd5e1; font:700 13px Inter,Segoe UI,Arial,sans-serif; letter-spacing:0.75px; }}
      .axis {{ fill:#94a3b8; font:400 10px JetBrains Mono,Consolas,monospace; }}
      .repo {{ fill:#cbd5e1; font:500 12px Inter,Segoe UI,Arial,sans-serif; }}
      .repo-count {{ fill:#38bdf8; font:700 12px JetBrains Mono,Consolas,monospace; }}
      .private-date {{ fill:#2dd4bf; font:700 11px JetBrains Mono,Consolas,monospace; }}
      .note {{ fill:#64748b; font:400 11px Inter,Segoe UI,Arial,sans-serif; }}
    </style>
  </defs>

  <rect width="{width}" height="{height}" rx="22" fill="url(#background)"/>
  <rect width="{width}" height="{height}" rx="22" fill="url(#grid)"/>

  <text x="48" y="43" class="title">ENGINEERING ACTIVITY</text>
  <text x="48" y="67" class="subtitle">API-derived public commit sample + privacy-reviewed private project snapshot</text>

{chr(10).join(card_parts)}

  <text x="{plot_left}" y="216" class="section">PUBLIC COMMIT SAMPLE · {esc(window["start"])} → {esc(window["end"])}</text>
  <line x1="{plot_left}" y1="{baseline}" x2="{plot_left + plot_width}" y2="{baseline}" stroke="#475569" stroke-width="1"/>
{chr(10).join(bars)}
{chr(10).join(labels)}

  <text x="860" y="216" class="section">TOP PUBLIC REPOSITORIES</text>
  <line x1="860" y1="226" x2="1140" y2="226" stroke="#334155" stroke-width="1"/>
{chr(10).join(public_lines)}

  <text x="860" y="337" class="section">PRIVATE WORK SNAPSHOT</text>
  <line x1="860" y1="347" x2="1140" y2="347" stroke="#334155" stroke-width="1"/>
{chr(10).join(private_lines)}

  <text x="48" y="508" class="note">Public bars are a bounded authored-commit sample. Private entries disclose only approved project names and dates—no URLs, branches, SHAs, or commit messages.</text>
</svg>
'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write assets/public-activity.svg")
    mode.add_argument("--check", action="store_true", help="fail when the SVG is stale")
    args = parser.parse_args(argv)

    public_payload = load_json(INPUT_PATH)
    private_activity = load_json(PROFILE_PATH)["private_activity"]
    rendered = render_svg(public_payload, private_activity)
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
        print("".join(difflib.unified_diff(current.splitlines(True), rendered.splitlines(True), fromfile="assets/public-activity.svg", tofile="generated")))
        return 1
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
