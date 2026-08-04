#!/usr/bin/env python3
"""Validate same-document Markdown anchor links in README and case studies."""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]+\]\(#([^)]+)\)")
HTML_ID = re.compile(r"<(?:a|[A-Za-z0-9]+)[^>]+(?:id|name)=[\"']([^\"']+)[\"']")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)


def slugify(value: str) -> str:
    value = re.sub(r"[`*_~]", "", value.strip().lower())
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    return re.sub(r"[\s-]+", "-", value).strip("-")


def main() -> int:
    errors: list[str] = []
    files = [ROOT / "README.md", *sorted((ROOT / "case-studies").rglob("*.md"))]
    for path in files:
        text = path.read_text(encoding="utf-8")
        anchors = {slugify(value) for value in HEADING.findall(text)} | set(HTML_ID.findall(text))
        for target in LINK.findall(text):
            if target not in anchors:
                errors.append(f"{path.relative_to(ROOT)}: missing anchor #{target}")
    if errors:
        print("Markdown anchor validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Markdown anchor validation passed for {len(files)} files.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
