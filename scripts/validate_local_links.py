#!/usr/bin/env python3
"""Validate repository-relative Markdown and HTML links.

Only rendered document content is inspected. Markdown fenced code blocks are
excluded because links inside examples and generated diffs are plain code, not
clickable document links.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MD_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HTML_LINK = re.compile(r"(?:href|src)=[\"']([^\"']+)[\"']")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
SKIP_PREFIX = ("http://", "https://", "mailto:", "tel:", "#", "data:")


def without_fenced_code(text: str) -> str:
    """Remove Markdown fenced code blocks while preserving normal content."""
    visible: list[str] = []
    fence_char: str | None = None
    fence_length = 0

    for line in text.splitlines(keepends=True):
        match = FENCE.match(line)
        if match:
            marker = match.group(1)
            if fence_char is None:
                fence_char = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_length:
                fence_char = None
                fence_length = 0
            continue
        if fence_char is None:
            visible.append(line)

    return "".join(visible)


def target_path(source: Path, raw: str) -> Path | None:
    value = raw.strip().split()[0].strip("<>")
    if not value or value.startswith(SKIP_PREFIX):
        return None
    value = unquote(value.split("#", 1)[0].split("?", 1)[0])
    if not value or value.startswith("/"):
        return None
    return (source.parent / value).resolve()


def markdown_files() -> list[Path]:
    files = [ROOT / "README.md"]
    for directory in ("case-studies", "docs"):
        path = ROOT / directory
        if path.exists():
            files.extend(sorted(path.rglob("*.md")))
    return files


def main() -> int:
    errors: list[str] = []
    files = markdown_files()
    for source in files:
        if not source.exists():
            continue
        text = without_fenced_code(source.read_text(encoding="utf-8"))
        for raw in MD_LINK.findall(text) + HTML_LINK.findall(text):
            target = target_path(source, raw)
            if target is None:
                continue
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{source.relative_to(ROOT)}: link escapes repository: {raw}")
                continue
            if not target.exists():
                errors.append(f"{source.relative_to(ROOT)}: missing target: {raw}")
    if errors:
        print("Local link validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Local link validation passed for {len(files)} Markdown files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
