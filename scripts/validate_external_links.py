#!/usr/bin/env python3
"""Best-effort manual checker for external links; intentionally excluded from deterministic CI."""
from __future__ import annotations
import argparse
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = re.compile(r"https://[^\s)>\"]+")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=12.0)
    args = parser.parse_args()
    urls: set[str] = set()
    for path in [ROOT / "README.md", *sorted((ROOT / "case-studies").rglob("*.md"))]:
        urls.update(value.rstrip(".,") for value in URL.findall(path.read_text(encoding="utf-8")))
    failures: list[str] = []
    for url in sorted(urls):
        request = urllib.request.Request(url, headers={"User-Agent": "afadlih-profile-link-check"})
        try:
            with urllib.request.urlopen(request, timeout=args.timeout) as response:
                if response.status >= 400:
                    failures.append(f"{response.status} {url}")
        except (urllib.error.URLError, TimeoutError) as exc:
            failures.append(f"{url}: {exc}")
    if failures:
        print("External link check found unavailable links:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"External link check passed for {len(urls)} links.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
