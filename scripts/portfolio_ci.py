#!/usr/bin/env python3
"""Run deterministic maintenance and quality gates for the special profile repo."""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def check(strict: bool = False) -> None:
    run([sys.executable, "scripts/validate_schemas.py"])
    run([sys.executable, "scripts/render_profile.py", "--check"])
    run([sys.executable, "scripts/validate_proof_assets.py", "--mode", "strict" if strict else "starter"])
    run([sys.executable, "scripts/validate_local_links.py"])
    run([sys.executable, "scripts/validate_markdown_anchors.py"])
    run([sys.executable, "scripts/validate_repository.py"])
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests"])


def update() -> None:
    run([sys.executable, "scripts/render_profile.py", "--write"])
    run([sys.executable, "scripts/generate_proof_report.py"])
    run([sys.executable, "scripts/write_update_summary.py"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "update", "final-check"])
    args = parser.parse_args()
    try:
        if args.command == "update":
            update()
        elif args.command == "final-check":
            check(strict=True)
        else:
            check(strict=False)
    except subprocess.CalledProcessError as exc:
        return exc.returncode or 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
