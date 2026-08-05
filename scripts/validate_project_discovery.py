#!/usr/bin/env python3
"""Validate discovery queue separation, approval boundaries, and privacy."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "portfolio" / "discovered-projects.json"
SOURCES_PATH = ROOT / "portfolio" / "activity-sources.json"
REGISTRY_PATH = ROOT / "portfolio" / "private-project-registry.json"
FORBIDDEN_PRIVATE_KEYS = {"repository", "url", "branch", "sha", "message", "commit_message"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_private_forbidden(value: Any, path: str = "private_candidates") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_PRIVATE_KEYS:
                errors.append(f"private discovery candidate exposes forbidden key: {path}.{key}")
            errors.extend(collect_private_forbidden(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(collect_private_forbidden(child, f"{path}[{index}]"))
    return errors


def main() -> int:
    queue = load_json(QUEUE_PATH)
    sources = load_json(SOURCES_PATH)
    registry = load_json(REGISTRY_PATH)
    errors = collect_private_forbidden(queue["private_candidates"])

    if queue["policy"]["auto_publish"] is not False:
        errors.append("project discovery must never auto-publish candidates")

    approved_public = {
        item["repository"] for item in sources["repositories"]
        if item.get("enabled") is True
    }
    approved_private = {
        item["project"] for item in registry["projects"]
        if item.get("enabled") is True
    }

    seen_ids: set[str] = set()
    for item in queue["public_candidates"]:
        if item["candidate_id"] in seen_ids:
            errors.append(f"duplicate discovery candidate id: {item['candidate_id']}")
        seen_ids.add(item["candidate_id"])
        if item["repository"] in approved_public:
            errors.append(f"approved public repository remains in discovery queue: {item['repository']}")
    for item in queue["private_candidates"]:
        if item["candidate_id"] in seen_ids:
            errors.append(f"duplicate discovery candidate id: {item['candidate_id']}")
        seen_ids.add(item["candidate_id"])
        if item["label"] in approved_private:
            errors.append(f"approved private label remains in discovery queue: {item['label']}")

    serialized_registry = json.dumps(registry, ensure_ascii=False).lower()
    for marker in ("github.com/", "api.github.com/repos/", "refs/heads/"):
        if marker in serialized_registry:
            errors.append(f"private project registry contains a private repository identifier: {marker}")

    if errors:
        print("Project discovery validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Project discovery validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
