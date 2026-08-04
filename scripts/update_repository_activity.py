#!/usr/bin/env python3
"""Refresh the curated public repository activity snapshot.

The output is deterministic for a given GitHub API response. It deliberately
omits a fetch timestamp so scheduled runs do not create empty timestamp-only
commits.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCES_PATH = ROOT / "portfolio" / "activity-sources.json"
OUTPUT_PATH = ROOT / "portfolio" / "repository-activity.json"
API_ROOT = "https://api.github.com/repos"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_if_changed(path: Path, payload: Any) -> bool:
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if current == rendered:
        return False
    path.write_text(rendered, encoding="utf-8", newline="\n")
    return True


def request_json(url: str, token: str | None) -> dict[str, Any]:
    request = urllib.request.Request(url)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    request.add_header("User-Agent", "afadlih-profile-activity")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_repository(repository: str, token: str | None) -> dict[str, Any]:
    url = f"{API_ROOT}/{repository}"
    attempts = [(token, "authenticated")]
    if token:
        attempts.append((None, "public fallback"))

    last_error: Exception | None = None
    for auth, _label in attempts:
        for attempt in range(2):
            try:
                return request_json(url, auth)
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code in {403, 404}:
                    break
                if exc.code >= 500 and attempt == 0:
                    time.sleep(1)
                    continue
                raise
            except urllib.error.URLError as exc:
                last_error = exc
                if attempt == 0:
                    time.sleep(1)
                    continue
                raise
    raise RuntimeError(f"Unable to read public repository metadata for {repository}: {last_error}")


def fixture_lookup(payload: Any, repository: str) -> dict[str, Any]:
    if isinstance(payload, dict) and "repositories" in payload:
        payload = payload["repositories"]
    if isinstance(payload, dict):
        value = payload.get(repository)
        if isinstance(value, dict):
            return value
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict) and item.get("full_name") == repository:
                return item
    raise KeyError(f"Fixture does not contain {repository}")


def normalized_item(source: dict[str, Any], repo: dict[str, Any]) -> dict[str, Any] | None:
    if repo.get("private") is True or repo.get("archived") is True or repo.get("disabled") is True:
        return None
    pushed_at = repo.get("pushed_at")
    return {
        "name": source["name"],
        "repository": source["repository"],
        "url": source.get("url") or repo.get("html_url") or f"https://github.com/{source['repository']}",
        "description": (repo.get("description") or "").strip() or None,
        "language": repo.get("language"),
        "pushed_at": pushed_at if isinstance(pushed_at, str) else None,
    }


def build_snapshot(sources: dict[str, Any], fixture: Any | None = None, token: str | None = None, previous: dict[str, Any] | None = None) -> dict[str, Any]:
    maximum = int(sources.get("maximum_items", 5))
    items: list[dict[str, Any]] = []
    failures: list[str] = []
    cached = {item.get("repository"): item for item in (previous or {}).get("items", []) if isinstance(item, dict)}

    for source in sources.get("repositories", []):
        if not source.get("enabled", True):
            continue
        repository = source.get("repository")
        if not isinstance(repository, str) or "/" not in repository:
            failures.append(f"invalid repository entry: {repository!r}")
            continue
        try:
            repo = fixture_lookup(fixture, repository) if fixture is not None else fetch_repository(repository, token)
            item = normalized_item(source, repo)
            if item:
                items.append(item)
        except Exception as exc:  # keep scheduled updates resilient to one broken source
            failures.append(f"{repository}: {exc}")
            if repository in cached:
                items.append(cached[repository])

    items.sort(key=lambda item: (item.get("pushed_at") or "", item["repository"]), reverse=True)
    items = items[:maximum]
    as_of = max((item.get("pushed_at") or "" for item in items), default="") or None

    if not items:
        raise RuntimeError("No public repository activity could be generated. " + "; ".join(failures))

    if failures:
        for warning in failures:
            print(f"warning: {warning}")
    return {
        "$schema": "../schemas/repository-activity.schema.json",
        "version": "2.0.0",
        "as_of": as_of,
        "source": "GitHub repository metadata",
        "items": items,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, help="use an offline GitHub API fixture")
    parser.add_argument("--write", action="store_true", help="write portfolio/repository-activity.json")
    parser.add_argument("--verify", action="store_true", help="validate the source/fixture without writing a snapshot")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args(argv)

    sources = load_json(SOURCES_PATH)
    fixture = load_json(args.fixture) if args.fixture else None
    token = os.getenv("GITHUB_TOKEN")
    previous = None
    if args.output.exists() and args.output.stat().st_size > 0:
        try:
            previous = load_json(args.output)
        except json.JSONDecodeError:
            print(f"warning: ignoring invalid previous snapshot: {args.output}")
    snapshot = build_snapshot(sources, fixture=fixture, token=token, previous=previous)

    if args.write and args.verify:
        parser.error("--write and --verify cannot be used together")
    if args.write:
        changed = write_json_if_changed(args.output, snapshot)
        print("repository_activity_changed=true" if changed else "repository_activity_changed=false")
    elif args.verify:
        print(f"repository_activity_valid=true items={len(snapshot['items'])} as_of={snapshot['as_of']}")
    else:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
