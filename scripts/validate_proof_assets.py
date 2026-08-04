#!/usr/bin/env python3
"""Validate featured-project evidence without overstating private work."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "portfolio" / "proof-assets.json"
PROJECTS_PATH = ROOT / "portfolio" / "projects.json"
VALID_STATUSES = {"documented", "source-verified", "test-verified", "planned", "missing"}
INCOMPLETE_STATUSES = {"planned", "missing"}
PLACEHOLDER_PHRASES = (
    "placeholder",
    "missing-real",
    "pending owner-supplied",
    "replace with real",
    "evidence to add",
)
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def featured_projects() -> dict[str, dict[str, Any]]:
    return {
        project["slug"]: project
        for project in load_json(PROJECTS_PATH)["projects"]
        if project.get("profile_section") == "featured"
    }


def validate_manifest(mode: str) -> list[str]:
    errors: list[str] = []
    payload = load_json(MANIFEST_PATH)
    featured = featured_projects()
    projects = payload.get("projects")
    if not isinstance(projects, list):
        return ["proof-assets.json must contain a top-level projects list"]

    seen_projects: set[str] = set()
    seen_ids: set[str] = set()
    for proof_project in projects:
        slug = proof_project.get("slug")
        if not isinstance(slug, str) or not slug:
            errors.append("proof project missing slug")
            continue
        if slug in seen_projects:
            errors.append(f"duplicate proof project slug: {slug}")
        seen_projects.add(slug)

        source_project = featured.get(slug)
        if source_project is None:
            errors.append(f"proof manifest contains non-featured project: {slug}")
            continue
        if proof_project.get("visibility") != source_project.get("visibility"):
            errors.append(f"proof visibility does not match project data for {slug}")
        if proof_project.get("proof_level") != source_project.get("proof_level"):
            errors.append(f"proof level does not match project data for {slug}")

        items = proof_project.get("items")
        if not isinstance(items, list) or len(items) < 3:
            errors.append(f"proof project {slug} needs at least 3 evidence items")
            continue

        types: set[str] = set()
        source_verified = 0
        for item in items:
            item_id = item.get("id")
            status = item.get("status")
            item_type = item.get("type")
            path_value = item.get("path")
            types.add(str(item_type))

            if not isinstance(item_id, str) or not item_id:
                errors.append(f"proof project {slug} contains an item without id")
                continue
            if item_id in seen_ids:
                errors.append(f"duplicate proof item id: {item_id}")
            seen_ids.add(item_id)
            if status not in VALID_STATUSES:
                errors.append(f"proof item {item_id} has invalid status: {status}")
            if not item.get("reviewed"):
                errors.append(f"proof item {item_id} must be reviewed")
            if not item.get("privacy_reviewed"):
                errors.append(f"proof item {item_id} must pass privacy review")
            if not isinstance(item.get("description"), str) or len(item["description"].strip()) < 20:
                errors.append(f"proof item {item_id} needs a concrete description")
            if not isinstance(path_value, str) or not path_value:
                errors.append(f"proof item {item_id} needs a repository-relative path")
                continue

            absolute = (ROOT / path_value).resolve()
            try:
                absolute.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"proof item {item_id} escapes the repository: {path_value}")
                continue
            if not absolute.is_file():
                errors.append(f"proof item {item_id} file does not exist: {path_value}")
                continue
            if absolute.stat().st_size == 0:
                errors.append(f"proof item {item_id} file is empty: {path_value}")

            if mode == "strict":
                if status in INCOMPLETE_STATUSES:
                    errors.append(f"strict mode rejects incomplete proof item {item_id}: {status}")
                if absolute.suffix.lower() in {".md", ".svg", ".txt"}:
                    text = absolute.read_text(encoding="utf-8", errors="replace").lower()
                    for phrase in PLACEHOLDER_PHRASES:
                        if phrase in text:
                            errors.append(f"strict mode found placeholder phrase in {path_value}: {phrase}")

            if status == "source-verified":
                source_verified += 1
                commit = item.get("source_commit")
                url = item.get("source_url")
                if not isinstance(commit, str) or not SHA40.fullmatch(commit):
                    errors.append(f"source-verified item {item_id} needs a 40-character commit SHA")
                if not isinstance(url, str) or not url.startswith("https://github.com/"):
                    errors.append(f"source-verified item {item_id} needs a GitHub source URL")

        for required_type in {"case-study", "architecture", "evidence"}:
            if required_type not in types:
                errors.append(f"proof project {slug} is missing evidence type: {required_type}")
        if source_project.get("visibility") == "public" and source_verified < 1:
            errors.append(f"public featured project {slug} needs at least one source-verified item")
        if source_project.get("visibility") == "private" and proof_project.get("proof_level") != "documented-private":
            errors.append(f"private featured project {slug} must use documented-private proof level")

    for slug in sorted(set(featured) - seen_projects):
        errors.append(f"featured project {slug} is missing from proof-assets.json")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["starter", "strict"], default="starter")
    args = parser.parse_args()
    errors = validate_manifest(args.mode)
    if errors:
        print("Proof validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Proof validation passed in {args.mode} mode.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
