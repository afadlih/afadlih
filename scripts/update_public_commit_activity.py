#!/usr/bin/env python3
"""Refresh a deterministic public commit activity sample for the profile.

Only allowlisted public repositories are queried. The snapshot stores no
wall-clock fetch timestamp, so scheduled runs do not create timestamp-only
commits. The chart is a bounded sample, not a lifetime GitHub total.
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCES_PATH = ROOT / "portfolio" / "activity-sources.json"
PROFILE_PATH = ROOT / "portfolio" / "profile.json"
OUTPUT_PATH = ROOT / "portfolio" / "public-commit-activity.json"
API_ROOT = "https://api.github.com/repos"
WINDOW_DAYS = 30
PER_REPOSITORY_LIMIT = 100


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
    request.add_header("User-Agent", "afadlih-profile-public-commit-activity")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_commits(repository: str, username: str, token: str | None) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode(
        {"author": username, "per_page": PER_REPOSITORY_LIMIT}
    )
    url = f"{API_ROOT}/{repository}/commits?{query}"
    attempts = [token]
    if token:
        attempts.append(None)

    last_error: Exception | None = None
    for auth in attempts:
        for attempt in range(2):
            try:
                payload = request_json(url, auth)
                if not isinstance(payload, list):
                    raise RuntimeError(f"Unexpected commits response for {repository}")
                return [item for item in payload if isinstance(item, dict)]
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code in {403, 404, 409}:
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
    raise RuntimeError(f"Unable to read commits for {repository}: {last_error}")


def fixture_commits(payload: Any, repository: str) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        raise KeyError("Commit fixture must be an object")
    commits = payload.get("commits", payload)
    if not isinstance(commits, dict):
        raise KeyError("Commit fixture must contain a commits object")
    value = commits.get(repository)
    if not isinstance(value, list):
        raise KeyError(f"Commit fixture does not contain {repository}")
    return [item for item in value if isinstance(item, dict)]


def parse_commit_date(commit: dict[str, Any]) -> datetime | None:
    nested = commit.get("commit")
    if not isinstance(nested, dict):
        return None
    for person_key in ("author", "committer"):
        person = nested.get(person_key)
        if not isinstance(person, dict):
            continue
        raw = person.get("date")
        if not isinstance(raw, str):
            continue
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            continue
        return parsed.astimezone(timezone.utc)
    return None


def build_snapshot(
    sources: dict[str, Any],
    username: str,
    *,
    fixture: Any | None = None,
    token: str | None = None,
    previous: dict[str, Any] | None = None,
) -> dict[str, Any]:
    dates: list[datetime] = []
    repository_counts: Counter[str] = Counter()
    failures: list[str] = []

    for source in sources.get("repositories", []):
        if not isinstance(source, dict) or not source.get("enabled", True):
            continue
        repository = source.get("repository")
        if not isinstance(repository, str) or "/" not in repository:
            failures.append(f"invalid repository entry: {repository!r}")
            continue
        try:
            commits = (
                fixture_commits(fixture, repository)
                if fixture is not None
                else fetch_commits(repository, username, token)
            )
        except Exception as exc:
            failures.append(f"{repository}: {exc}")
            continue

        seen_shas: set[str] = set()
        for commit in commits:
            sha = commit.get("sha")
            if isinstance(sha, str) and sha:
                if sha in seen_shas:
                    continue
                seen_shas.add(sha)
            committed_at = parse_commit_date(commit)
            if committed_at is None:
                continue
            dates.append(committed_at)
            repository_counts[repository] += 1

    if failures and previous and previous.get("daily"):
        for warning in failures:
            print(f"warning: {warning}")
        print("warning: retaining previous complete public commit activity snapshot")
        return previous

    if not dates:
        detail = "; ".join(failures) if failures else "no authored public commits found"
        raise RuntimeError(f"Public commit activity could not be generated: {detail}")

    latest = max(dates)
    window_end = latest.date()
    window_start = window_end - timedelta(days=WINDOW_DAYS - 1)
    daily_counts: Counter[date] = Counter(
        committed_at.date()
        for committed_at in dates
        if window_start <= committed_at.date() <= window_end
    )
    daily = [
        {
            "date": (window_start + timedelta(days=offset)).isoformat(),
            "commits": daily_counts[window_start + timedelta(days=offset)],
        }
        for offset in range(WINDOW_DAYS)
    ]

    in_window = sum(item["commits"] for item in daily)
    active_days = sum(1 for item in daily if item["commits"] > 0)
    top_repositories = [
        {"repository": repository, "sampled_commits": count}
        for repository, count in repository_counts.most_common(5)
    ]

    if failures:
        for warning in failures:
            print(f"warning: {warning}")

    return {
        "$schema": "../schemas/public-commit-activity.schema.json",
        "version": "1.0.0",
        "username": username,
        "source": "GitHub public commit API sample",
        "sample_limit_per_repository": PER_REPOSITORY_LIMIT,
        "latest_public_commit_at": latest.isoformat().replace("+00:00", "Z"),
        "window": {
            "start": window_start.isoformat(),
            "end": window_end.isoformat(),
            "days": WINDOW_DAYS,
        },
        "summary": {
            "sampled_commits": len(dates),
            "commits_in_window": in_window,
            "active_days": active_days,
            "repositories_with_commits": len(repository_counts),
        },
        "daily": daily,
        "repositories": top_repositories,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, help="use an offline commits fixture")
    parser.add_argument("--write", action="store_true", help="write the generated snapshot")
    parser.add_argument("--verify", action="store_true", help="build without writing")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args(argv)

    if args.write and args.verify:
        parser.error("--write and --verify cannot be used together")

    sources = load_json(SOURCES_PATH)
    profile = load_json(PROFILE_PATH)
    username = profile["username"]
    fixture = load_json(args.fixture) if args.fixture else None
    previous = None
    if args.output.exists() and args.output.stat().st_size > 0:
        try:
            previous = load_json(args.output)
        except json.JSONDecodeError:
            print(f"warning: ignoring invalid previous snapshot: {args.output}")

    snapshot = build_snapshot(
        sources,
        username,
        fixture=fixture,
        token=os.getenv("GITHUB_TOKEN"),
        previous=previous,
    )

    if args.write:
        changed = write_json_if_changed(args.output, snapshot)
        print("public_commit_activity_changed=true" if changed else "public_commit_activity_changed=false")
    elif args.verify:
        print(
            "public_commit_activity_valid=true "
            f"window_commits={snapshot['summary']['commits_in_window']} "
            f"latest={snapshot['latest_public_commit_at']}"
        )
    else:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
