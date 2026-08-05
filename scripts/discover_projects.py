#!/usr/bin/env python3
"""Detect recent public repositories and unregistered private project labels.

Detection never publishes a project into the README. Public repositories enter a
review queue with public metadata. Private candidates are derived only from the
public-safe labels in PROFILE_PRIVATE_REPOSITORIES_JSON; private repository
identifiers are never written to tracked files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "portfolio" / "discovered-projects.json"
ACTIVITY_SOURCES_PATH = ROOT / "portfolio" / "activity-sources.json"
PRIVATE_REGISTRY_PATH = ROOT / "portfolio" / "private-project-registry.json"
DEFAULT_RECENCY_DAYS = 180

RepositoryFetcher = Callable[[str], list[dict[str, Any]]]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_if_changed(path: Path, payload: Any) -> bool:
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if current == rendered:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8", newline="\n")
    return True


def request_json(url: str, token: str | None) -> Any:
    request = urllib.request.Request(url)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    request.add_header("User-Agent", "afadlih-profile-project-discovery")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code >= 500 and attempt < 2:
                time.sleep(1 + attempt)
                continue
            raise RuntimeError(f"GitHub repository discovery HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            if attempt < 2:
                time.sleep(1 + attempt)
                continue
            raise RuntimeError(f"GitHub repository discovery network error: {exc}") from exc
    raise RuntimeError("GitHub repository discovery failed")


def fetch_public_repositories(username: str, token: str | None) -> list[dict[str, Any]]:
    repositories: list[dict[str, Any]] = []
    page = 1
    while page <= 10:
        query = urllib.parse.urlencode(
            {"per_page": 100, "page": page, "sort": "pushed", "direction": "desc"}
        )
        payload = request_json(f"https://api.github.com/users/{username}/repos?{query}", token)
        if not isinstance(payload, list):
            raise RuntimeError("Unexpected GitHub repositories response")
        repositories.extend(item for item in payload if isinstance(item, dict))
        if len(payload) < 100:
            break
        page += 1
    return repositories


def parse_private_mapping(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("PROFILE_PRIVATE_REPOSITORIES_JSON is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("PROFILE_PRIVATE_REPOSITORIES_JSON must be an object")
    result: dict[str, str] = {}
    for key, value in payload.items():
        if not isinstance(key, str) or not key.strip() or not isinstance(value, str) or "/" not in value:
            raise RuntimeError("Private project mapping must contain label-to-owner/repository strings")
        result[key.strip()] = value.strip()
    return result


def candidate_id(prefix: str, identity: str) -> str:
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def iso_date(raw: Any) -> str | None:
    if not isinstance(raw, str) or not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc).date().isoformat()
    except ValueError:
        return None


def build_discovery(
    previous: dict[str, Any],
    username: str,
    repositories: list[dict[str, Any]],
    approved_public_repositories: set[str],
    approved_private_labels: set[str],
    private_mapping: dict[str, str],
    *,
    today: date | None = None,
) -> dict[str, Any]:
    today = today or datetime.now(timezone.utc).date()
    policy = previous.get("policy") if isinstance(previous.get("policy"), dict) else {}
    recency_days = int(policy.get("public_recency_days", DEFAULT_RECENCY_DAYS))
    cutoff = today - timedelta(days=recency_days - 1)

    prior_public = {
        item.get("repository"): item
        for item in previous.get("public_candidates", [])
        if isinstance(item, dict) and isinstance(item.get("repository"), str)
    }
    public_candidates: list[dict[str, Any]] = []
    for repository in repositories:
        full_name = repository.get("full_name")
        if not isinstance(full_name, str) or not full_name.startswith(f"{username}/"):
            continue
        if full_name in approved_public_repositories:
            continue
        if repository.get("private") is True:
            continue
        if policy.get("exclude_forks", True) and repository.get("fork") is True:
            continue
        if policy.get("exclude_archived", True) and repository.get("archived") is True:
            continue
        if policy.get("exclude_empty", True) and int(repository.get("size") or 0) <= 0:
            continue
        pushed_at = iso_date(repository.get("pushed_at"))
        if pushed_at is None or date.fromisoformat(pushed_at) < cutoff:
            continue
        prior = prior_public.get(full_name, {})
        status = prior.get("status") if prior.get("status") in {"pending_review", "ignored"} else "pending_review"
        public_candidates.append(
            {
                "candidate_id": candidate_id("public", full_name),
                "name": str(repository.get("name") or full_name.split("/", 1)[1]),
                "repository": full_name,
                "url": str(repository.get("html_url") or f"https://github.com/{full_name}"),
                "description": repository.get("description") if isinstance(repository.get("description"), str) else None,
                "pushed_at": pushed_at,
                "language": repository.get("language") if isinstance(repository.get("language"), str) else None,
                "status": status,
                "reason": "Recent public repository is not yet in the approved activity allowlist.",
            }
        )
    public_candidates.sort(key=lambda item: (item["pushed_at"], item["repository"].lower()), reverse=True)
    public_candidates = public_candidates[:30]

    prior_private = {
        item.get("label"): item
        for item in previous.get("private_candidates", [])
        if isinstance(item, dict) and isinstance(item.get("label"), str)
    }
    private_candidates: list[dict[str, Any]] = []
    if private_mapping:
        for label in sorted(set(private_mapping) - approved_private_labels, key=str.lower):
            prior = prior_private.get(label, {})
            status = prior.get("status") if prior.get("status") in {"pending_review", "ignored"} else "pending_review"
            private_candidates.append(
                {
                    "candidate_id": candidate_id("private", label),
                    "label": label,
                    "status": status,
                    "reason": "Encrypted private mapping contains a public-safe label that is not yet approved in the registry.",
                }
            )
    else:
        private_candidates = [dict(item) for item in previous.get("private_candidates", []) if isinstance(item, dict)]

    payload = {
        "$schema": "../schemas/discovered-projects.schema.json",
        "version": "1.0.0",
        "username": username,
        "changed_at": today.isoformat(),
        "policy": {
            "auto_publish": False,
            "public_recency_days": recency_days,
            "exclude_forks": bool(policy.get("exclude_forks", True)),
            "exclude_archived": bool(policy.get("exclude_archived", True)),
            "exclude_empty": bool(policy.get("exclude_empty", True)),
        },
        "public_candidates": public_candidates,
        "private_candidates": private_candidates,
    }

    previous_comparable = dict(previous)
    previous_comparable.pop("changed_at", None)
    current_comparable = dict(payload)
    current_comparable.pop("changed_at", None)
    if previous_comparable == current_comparable and isinstance(previous.get("changed_at"), str):
        payload["changed_at"] = previous["changed_at"]
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the review queue")
    parser.add_argument("--check", action="store_true", help="fail when the queue is stale")
    parser.add_argument("--today", type=date.fromisoformat, help="override UTC date")
    parser.add_argument("--fixture", type=Path, help="read repository API data from a JSON fixture")
    args = parser.parse_args(argv)
    if args.write and args.check:
        parser.error("--write and --check cannot be combined")

    previous = load_json(OUTPUT_PATH)
    sources = load_json(ACTIVITY_SOURCES_PATH)
    registry = load_json(PRIVATE_REGISTRY_PATH)
    username = previous["username"]
    approved_public = {
        item["repository"]
        for item in sources.get("repositories", [])
        if isinstance(item, dict) and item.get("enabled") is True and isinstance(item.get("repository"), str)
    }
    approved_private = {
        item["project"]
        for item in registry.get("projects", [])
        if isinstance(item, dict) and item.get("enabled") is True and isinstance(item.get("project"), str)
    }
    private_mapping = parse_private_mapping(os.getenv("PROFILE_PRIVATE_REPOSITORIES_JSON"))
    if args.fixture:
        repositories = json.loads(args.fixture.read_text(encoding="utf-8"))
        if not isinstance(repositories, list):
            raise SystemExit("Repository fixture must be a JSON array")
    else:
        repositories = fetch_public_repositories(username, os.getenv("GITHUB_TOKEN"))

    payload = build_discovery(
        previous,
        username,
        repositories,
        approved_public,
        approved_private,
        private_mapping,
        today=args.today,
    )
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
    if args.write:
        changed = write_json_if_changed(OUTPUT_PATH, payload)
        print(f"project_discovery_changed={str(changed).lower()}")
        return 0
    if args.check:
        if current == rendered:
            print("portfolio/discovered-projects.json is up to date.")
            return 0
        print("portfolio/discovered-projects.json is stale; run scripts/discover_projects.py --write")
        return 1
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
