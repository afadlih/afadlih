#!/usr/bin/env python3
"""Review project-discovery candidates without publishing private identifiers."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "portfolio" / "discovered-projects.json"
PUBLIC_SOURCES_PATH = ROOT / "portfolio" / "activity-sources.json"
PRIVATE_REGISTRY_PATH = ROOT / "portfolio" / "private-project-registry.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def find_candidate(queue: dict[str, Any], candidate_id: str) -> tuple[str, dict[str, Any]]:
    for group in ("public_candidates", "private_candidates"):
        for item in queue[group]:
            if item["candidate_id"] == candidate_id:
                return group, item
    raise SystemExit(f"Candidate not found: {candidate_id}")


def remove_candidate(queue: dict[str, Any], candidate_id: str) -> None:
    for group in ("public_candidates", "private_candidates"):
        queue[group] = [item for item in queue[group] if item["candidate_id"] != candidate_id]


def command_list(queue: dict[str, Any]) -> None:
    rows = []
    for item in queue["public_candidates"]:
        rows.append((item["candidate_id"], "public", item["status"], item["repository"]))
    for item in queue["private_candidates"]:
        rows.append((item["candidate_id"], "private", item["status"], item["label"]))
    if not rows:
        print("No project candidates are awaiting review.")
        return
    for candidate_id, visibility, status, label in rows:
        print(f"{candidate_id}\t{visibility}\t{status}\t{label}")


def command_ignore(queue: dict[str, Any], candidate_id: str) -> None:
    _, item = find_candidate(queue, candidate_id)
    item["status"] = "ignored"
    write_json(QUEUE_PATH, queue)
    print(f"Ignored {candidate_id}; future scans preserve this decision while the candidate remains eligible.")


def command_approve_public(queue: dict[str, Any], candidate_id: str, display_name: str | None) -> None:
    group, candidate = find_candidate(queue, candidate_id)
    if group != "public_candidates":
        raise SystemExit("approve-public requires a public candidate")
    sources = load_json(PUBLIC_SOURCES_PATH)
    repository = candidate["repository"]
    if any(item.get("repository") == repository for item in sources["repositories"]):
        raise SystemExit("Repository is already in the approved public activity allowlist")
    sources["repositories"].append(
        {
            "name": display_name or candidate["name"],
            "repository": repository,
            "url": candidate["url"],
            "enabled": True,
        }
    )
    remove_candidate(queue, candidate_id)
    write_json(PUBLIC_SOURCES_PATH, sources)
    write_json(QUEUE_PATH, queue)
    print("Public repository approved for the recently-updated activity table.")
    print("Add a curated portfolio/projects.json record separately before featuring it as selected work.")


def command_approve_private(queue: dict[str, Any], args: argparse.Namespace) -> None:
    group, candidate = find_candidate(queue, args.candidate_id)
    if group != "private_candidates":
        raise SystemExit("approve-private requires a private candidate")
    registry = load_json(PRIVATE_REGISTRY_PATH)
    label = candidate["label"]
    if any(item.get("project") == label for item in registry["projects"]):
        raise SystemExit("Private label is already approved in the registry")
    source: dict[str, Any] = {"path": args.version_path, "strategy": args.version_strategy}
    if args.version_strategy == "json":
        source["field"] = args.version_field
    else:
        if not args.version_pattern:
            raise SystemExit("--version-pattern is required for regex version sources")
        source["pattern"] = args.version_pattern
    registry["projects"].append(
        {
            "project": label,
            "enabled": True,
            "condition": args.condition,
            "condition_strategy": args.condition_strategy,
            "public_summary": args.public_summary,
            "focus": args.focus,
            "case_study": args.case_study,
            "profile_link": args.profile_link,
            "show_in_current_focus": not args.hide_from_current_focus,
            "version_source": source,
        }
    )
    remove_candidate(queue, args.candidate_id)
    write_json(PRIVATE_REGISTRY_PATH, registry)
    write_json(QUEUE_PATH, queue)
    print("Private project public metadata approved.")
    print("The encrypted label-to-repository mapping remains the only source of its private identifier.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list")

    ignore = subparsers.add_parser("ignore")
    ignore.add_argument("candidate_id")

    public = subparsers.add_parser("approve-public")
    public.add_argument("candidate_id")
    public.add_argument("--display-name")

    private = subparsers.add_parser("approve-private")
    private.add_argument("candidate_id")
    private.add_argument("--condition", required=True)
    private.add_argument("--condition-strategy", choices=["fixed", "semver"], default="fixed")
    private.add_argument("--public-summary", required=True)
    private.add_argument("--focus", required=True)
    private.add_argument("--case-study")
    private.add_argument("--profile-link")
    private.add_argument("--hide-from-current-focus", action="store_true")
    private.add_argument("--version-path", required=True)
    private.add_argument("--version-strategy", choices=["json", "regex"], required=True)
    private.add_argument("--version-field", default="version")
    private.add_argument("--version-pattern")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    queue = load_json(QUEUE_PATH)
    if args.command == "list":
        command_list(queue)
    elif args.command == "ignore":
        command_ignore(queue, args.candidate_id)
    elif args.command == "approve-public":
        command_approve_public(queue, args.candidate_id, args.display_name)
    elif args.command == "approve-private":
        command_approve_private(queue, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
