#!/usr/bin/env python3
"""Refresh the privacy-reviewed rolling 180-day engineering snapshot.

Approved public labels and safe descriptions live in the tracked private project
registry. Private repository identifiers remain in an encrypted secret. The
updater never persists private URLs, repository names, branches, SHAs, or commit
messages.
"""
from __future__ import annotations

import argparse
import base64
import calendar
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "portfolio" / "engineering-activity.json"
PROFILE_PATH = ROOT / "portfolio" / "profile.json"
REGISTRY_PATH = ROOT / "portfolio" / "private-project-registry.json"
API_URL = "https://api.github.com/search/commits"
WINDOW_DAYS = 180

SearchResult = tuple[int, date | None]
Searcher = Callable[[str], SearchResult]
VersionResolver = Callable[[dict[str, Any], str, str], str]


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


def request_json(url: str, token: str) -> dict[str, Any]:
    request = urllib.request.Request(url)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    request.add_header("User-Agent", "afadlih-profile-engineering-activity")
    request.add_header("Authorization", f"Bearer {token}")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, dict):
                raise RuntimeError("Unexpected GitHub API response")
            if payload.get("incomplete_results") is True:
                raise RuntimeError("GitHub Search returned incomplete results")
            return payload
        except urllib.error.HTTPError as exc:
            if exc.code >= 500 and attempt < 2:
                time.sleep(1 + attempt)
                continue
            raise RuntimeError(f"GitHub API HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            if attempt < 2:
                time.sleep(1 + attempt)
                continue
            raise RuntimeError(f"GitHub API network error: {exc}") from exc
    raise RuntimeError("GitHub API request failed")


def fetch_repository_text(repository: str, path: str, token: str) -> str:
    encoded_path = urllib.parse.quote(path, safe="/")
    payload = request_json(f"https://api.github.com/repos/{repository}/contents/{encoded_path}", token)
    content = payload.get("content")
    if not isinstance(content, str) or payload.get("encoding") != "base64":
        raise RuntimeError("Approved version source could not be read")
    return base64.b64decode(content).decode("utf-8")


def nested_json_field(payload: Any, field: str) -> Any:
    current = payload
    for part in field.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def resolve_version_from_source(
    registry_item: dict[str, Any], repository: str, current_version: str, token: str
) -> str:
    source = registry_item["version_source"]
    text = fetch_repository_text(repository, source["path"], token)
    if source["strategy"] == "json":
        version = nested_json_field(json.loads(text), source["field"])
    else:
        match = re.search(source["pattern"], text, re.IGNORECASE | re.MULTILINE)
        version = match.group(1) if match else None
    if not isinstance(version, str) or not version.strip():
        raise RuntimeError(f"Version source did not yield a version for {registry_item['project']}")
    return version.strip()


def condition_for(registry_item: dict[str, Any], version: str) -> str:
    if registry_item.get("condition_strategy") != "semver":
        return str(registry_item["condition"])
    lowered = version.lower()
    if re.search(r"(?:^|[-.])rc\d*(?:$|[-.])", lowered):
        return "Release candidate"
    if re.search(r"(?:^|[-.])(?:alpha|beta|preview|dev)\d*(?:$|[-.])", lowered):
        return "Pre-release"
    return "Stable release"


def search_commits(query: str, token: str) -> SearchResult:
    encoded = urllib.parse.urlencode(
        {"q": query, "sort": "author-date", "order": "desc", "per_page": 1}
    )
    payload = request_json(f"{API_URL}?{encoded}", token)
    total = payload.get("total_count")
    if not isinstance(total, int):
        raise RuntimeError("GitHub Search response lacks total_count")
    latest: date | None = None
    items = payload.get("items")
    if isinstance(items, list) and items:
        commit = items[0].get("commit") if isinstance(items[0], dict) else None
        author = commit.get("author") if isinstance(commit, dict) else None
        raw = author.get("date") if isinstance(author, dict) else None
        if isinstance(raw, str):
            latest = datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc).date()
    return total, latest


def month_periods(start: date, end: date) -> list[tuple[str, date, date]]:
    periods: list[tuple[str, date, date]] = []
    cursor = date(start.year, start.month, 1)
    while cursor <= end:
        month_end = date(cursor.year, cursor.month, calendar.monthrange(cursor.year, cursor.month)[1])
        period_start = max(start, cursor)
        period_end = min(end, month_end)
        label = period_start.strftime("%b").upper()
        if period_start.day != 1 or period_end != month_end:
            label = f"{label} {period_start.day:02d}–{period_end.day:02d}"
        periods.append((label, period_start, period_end))
        cursor = month_end + timedelta(days=1)
    return periods


def enabled_registry_projects(registry: dict[str, Any]) -> list[dict[str, Any]]:
    projects = [
        item for item in registry.get("projects", [])
        if isinstance(item, dict) and item.get("enabled") is True
    ]
    if not projects:
        raise RuntimeError("Private project registry has no enabled projects")
    names = [item.get("project") for item in projects]
    if len(names) != len(set(names)):
        raise RuntimeError("Private project registry contains duplicate labels")
    return projects


def build_snapshot(
    previous: dict[str, Any],
    registry: dict[str, Any],
    username: str,
    repository_mapping: dict[str, str],
    *,
    today: date | None = None,
    searcher: Searcher,
    version_resolver: VersionResolver | None = None,
) -> dict[str, Any]:
    today = today or datetime.now(timezone.utc).date()
    provisional_start = today - timedelta(days=WINDOW_DAYS - 1)
    _, latest = searcher(
        f"author:{username} author-date:{provisional_start.isoformat()}..{today.isoformat()}"
    )
    if latest is None:
        raise RuntimeError("No authored commits found in the rolling 180-day window")

    end = latest
    start = end - timedelta(days=WINDOW_DAYS - 1)
    authored_commits, confirmed_latest = searcher(
        f"author:{username} author-date:{start.isoformat()}..{end.isoformat()}"
    )
    if confirmed_latest and confirmed_latest != end:
        raise RuntimeError("Latest commit changed during snapshot generation; rerun the updater")

    periods = []
    for label, period_start, period_end in month_periods(start, end):
        count, _ = searcher(
            f"author:{username} author-date:{period_start.isoformat()}..{period_end.isoformat()}"
        )
        periods.append(
            {
                "label": label,
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
                "commits": count,
            }
        )

    previous_by_project = {
        item.get("project"): item
        for item in previous.get("private_projects", [])
        if isinstance(item, dict) and isinstance(item.get("project"), str)
    }
    private_projects: list[dict[str, Any]] = []
    selected_private_commits = 0
    for approved in enabled_registry_projects(registry):
        project = approved["project"]
        repository = repository_mapping.get(project)
        if not isinstance(repository, str) or "/" not in repository:
            raise RuntimeError(f"Missing encrypted private repository mapping for approved label: {project}")
        count, latest_private = searcher(
            f"repo:{repository} author:{username} author-date:{start.isoformat()}..{end.isoformat()}"
        )
        prior = previous_by_project.get(project, {})
        prior_latest = prior.get("latest_commit") if isinstance(prior.get("latest_commit"), str) else start.isoformat()
        latest_text = latest_private.isoformat() if latest_private else prior_latest
        current_version = str(prior.get("version") or "Unversioned")
        version = (
            version_resolver(approved, repository, current_version)
            if version_resolver is not None
            else current_version
        )
        selected_private_commits += count
        private_projects.append(
            {
                "project": project,
                "version": version,
                "condition": condition_for(approved, version),
                "latest_commit": latest_text,
                "public_summary": approved["public_summary"],
                "case_study": approved["case_study"],
            }
        )

    private_projects.sort(key=lambda item: (item["latest_commit"], item["project"].lower()), reverse=True)
    latest_private_update = max(item["latest_commit"] for item in private_projects)
    return {
        "$schema": "../schemas/engineering-activity.schema.json",
        "version": "2.2.0",
        "username": username,
        "source": "Authenticated GitHub commit search snapshot",
        "snapshot_as_of": end.isoformat(),
        "window": {"start": start.isoformat(), "end": end.isoformat(), "days": WINDOW_DAYS},
        "summary": {
            "authored_commits": authored_commits,
            "selected_private_commits": selected_private_commits,
            "selected_private_projects": len(private_projects),
            "latest_private_update": latest_private_update,
        },
        "periods": periods,
        "private_projects": private_projects,
    }


def synchronize_profile(
    profile: dict[str, Any], snapshot: dict[str, Any], registry: dict[str, Any]
) -> dict[str, Any]:
    approved = {item["project"]: item for item in enabled_registry_projects(registry)}
    focus_items: list[dict[str, Any]] = []
    for private in snapshot["private_projects"]:
        registry_item = approved[private["project"]]
        if registry_item.get("show_in_current_focus") is not True:
            continue
        focus_items.append(
            {
                "project": private["project"],
                "version": private["version"],
                "condition": private["condition"],
                "updated": private["latest_commit"],
                "focus": registry_item["focus"],
                "link": registry_item["profile_link"],
            }
        )
    focus_items.sort(
        key=lambda item: (item["updated"], item["project"].lower()),
        reverse=True,
    )
    updated = json.loads(json.dumps(profile))
    updated["version"] = "3.5.0"
    updated["current_focus"] = focus_items[:8]
    updated["profile_notes"] = [
        "Private projects are represented through one privacy-reviewed aggregate activity total and sanitized case studies, never repository links.",
        "The engineering activity snapshot uses a rolling 180-day GitHub Search window; it is not a lifetime contribution total.",
        "Private activity exposes one aggregate commit total plus approved project labels, versions, conditions, dates, and sanitized case studies; per-project counts, branch names, messages, SHAs, and URLs remain undisclosed.",
        "New repositories are detected daily but remain in a review queue until their public presentation is explicitly approved.",
        "A professional public email is intentionally omitted until a durable address is configured.",
    ]
    return updated


def parse_repository_mapping(raw: str | None) -> dict[str, str]:
    if not raw:
        raise RuntimeError(
            "PROFILE_PRIVATE_REPOSITORIES_JSON is required; keep repository identifiers in an encrypted secret"
        )
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("PROFILE_PRIVATE_REPOSITORIES_JSON is not valid JSON") from exc
    if not isinstance(payload, dict) or not payload:
        raise RuntimeError("PROFILE_PRIVATE_REPOSITORIES_JSON must be a non-empty object")
    result: dict[str, str] = {}
    for key, value in payload.items():
        if not isinstance(key, str) or not key.strip() or not isinstance(value, str) or "/" not in value:
            raise RuntimeError("Private mapping must contain public-label to owner/repository strings")
        result[key.strip()] = value.strip()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write engineering activity and profile")
    parser.add_argument("--verify", action="store_true", help="build without writing")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--today", type=date.fromisoformat, help="override UTC date")
    args = parser.parse_args(argv)
    if args.write and args.verify:
        parser.error("--write and --verify cannot be combined")

    token = os.getenv("PROFILE_ACTIVITY_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        raise SystemExit("PROFILE_ACTIVITY_TOKEN or GITHUB_TOKEN is required")
    mapping = parse_repository_mapping(os.getenv("PROFILE_PRIVATE_REPOSITORIES_JSON"))
    previous = load_json(args.output)
    profile = load_json(PROFILE_PATH)
    registry = load_json(REGISTRY_PATH)
    snapshot = build_snapshot(
        previous,
        registry,
        previous["username"],
        mapping,
        today=args.today,
        searcher=lambda query: search_commits(query, token),
        version_resolver=lambda approved, repository, current: resolve_version_from_source(
            approved, repository, current, token
        ),
    )
    synchronized_profile = synchronize_profile(profile, snapshot, registry)

    if args.write:
        activity_changed = write_json_if_changed(args.output, snapshot)
        profile_changed = write_json_if_changed(PROFILE_PATH, synchronized_profile)
        print(
            f"engineering_activity_changed={str(activity_changed).lower()} "
            f"profile_changed={str(profile_changed).lower()}"
        )
    elif args.verify:
        print(
            "engineering_activity_valid=true "
            f"authored_commits={snapshot['summary']['authored_commits']} "
            f"private_commits={snapshot['summary']['selected_private_commits']} "
            f"as_of={snapshot['snapshot_as_of']}"
        )
    else:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
