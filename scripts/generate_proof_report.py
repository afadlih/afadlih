#!/usr/bin/env python3
"""Generate a readable summary of the evidence manifest."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "portfolio" / "proof-assets.json"
OUTPUT = ROOT / "docs" / "PROOF_ASSET_REPORT.md"


def main() -> int:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    lines = [
        "# Featured Project Evidence Report",
        "",
        "This report is generated from `portfolio/proof-assets.json`. Evidence levels are explicit so private projects are not presented as public source audits.",
        "",
    ]
    counts: Counter[str] = Counter()
    for project in payload["projects"]:
        lines.extend([
            f"## {project['slug']}",
            "",
            f"- Visibility: `{project['visibility']}`",
            f"- Proof level: `{project['proof_level']}`",
            "",
            "| Evidence | Type | Status | Path |",
            "| --- | --- | --- | --- |",
        ])
        for item in project["items"]:
            counts[item["status"]] += 1
            lines.append(f"| `{item['id']}` | `{item['type']}` | `{item['status']}` | `{item['path']}` |")
        lines.append("")
    lines.extend(["## Status totals", "", "| Status | Count |", "| --- | ---: |"])
    for status, count in sorted(counts.items()):
        lines.append(f"| `{status}` | {count} |")
    lines.append("")
    OUTPUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
