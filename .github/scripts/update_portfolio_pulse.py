import html
import json
import os
import re
import urllib.request
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

README_PATH = "README.md"
START = "<!-- PORTFOLIO-PULSE:START -->"
END = "<!-- PORTFOLIO-PULSE:END -->"
GITHUB_USERNAME = os.getenv("GITHUB_REPOSITORY_OWNER", "afadlih")

WIB = timezone(timedelta(hours=7))

CURRENT_BUILD_FOCUS = (
    "FormAI automation flow, validation, execution diagnostics, and operator-facing UX."
)
ACTIVE_ENGINEERING_THEME = (
    "AI workflow reliability: clear contracts, fallback paths, traceable results, and useful errors."
)

# Keep this curated so the profile README stays portfolio-ready.
# The script may reorder these by recent activity, but it will not surface random public repos.
PORTFOLIO_REPOS = [
    {
        "name": "AI Content Strategy",
        "owner": "afadlih",
        "repo": "AI-Content-Strategy---SEO-Assistant--Web-App-",
        "url": "https://github.com/afadlih/AI-Content-Strategy---SEO-Assistant--Web-App-",
    },
    {
        "name": "Smart Clothesline IoT",
        "owner": "afadlih",
        "repo": "smart-clothesline-iot-system",
        "url": "https://github.com/afadlih/smart-clothesline-iot-system",
    },
    {
        "name": "Profile README",
        "owner": "afadlih",
        "repo": "afadlih",
        "url": "https://github.com/afadlih/afadlih",
    },
]


def format_wib_now() -> str:
    now = datetime.now(WIB)
    return now.strftime("%A, %d %B %Y, %H:%M WIB")


def github_api_json(url: str):
    token = os.getenv("GITHUB_TOKEN")
    request = urllib.request.Request(url)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("User-Agent", "portfolio-pulse-updater")
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_github_date(value: str) -> datetime:
    return parsedate_to_datetime(value or "Thu, 01 Jan 1970 00:00:00 GMT")


def get_highlighted_portfolio_repos() -> list[dict[str, str]]:
    highlighted = []

    for item in PORTFOLIO_REPOS:
        api_url = f"https://api.github.com/repos/{item['owner']}/{item['repo']}"
        try:
            repo = github_api_json(api_url)
            pushed_at = parse_github_date(repo.get("pushed_at", ""))
        except Exception:
            pushed_at = parse_github_date("")

        highlighted.append(
            {
                "name": item["name"],
                "url": item["url"],
                "pushed_at": pushed_at,
            }
        )

    highlighted.sort(key=lambda repo: repo["pushed_at"], reverse=True)
    return highlighted


def repo_links(repos: list[dict[str, str]]) -> str:
    return " · ".join(
        f'<a href="{html.escape(repo["url"], quote=True)}">{html.escape(repo["name"])}</a>'
        for repo in repos
    )


def build_pulse_block() -> str:
    return f"""{START}
<table>
  <tr>
    <td><b>Last refresh</b></td>
    <td>{format_wib_now()}</td>
  </tr>
  <tr>
    <td><b>Current build focus</b></td>
    <td>{html.escape(CURRENT_BUILD_FOCUS)}</td>
  </tr>
  <tr>
    <td><b>Active engineering theme</b></td>
    <td>{html.escape(ACTIVE_ENGINEERING_THEME)}</td>
  </tr>
  <tr>
    <td><b>Highlighted portfolio repos</b></td>
    <td>{repo_links(get_highlighted_portfolio_repos())}</td>
  </tr>
</table>
{END}"""


def update_readme() -> bool:
    with open(README_PATH, "r", encoding="utf-8") as file:
        readme = file.read()

    pattern = re.compile(rf"{re.escape(START)}.*?{re.escape(END)}", re.DOTALL)
    replacement = build_pulse_block()

    updated, count = pattern.subn(replacement, readme)
    if count != 1:
        raise RuntimeError("Portfolio pulse markers were not found exactly once in README.md")

    if updated == readme:
        return False

    with open(README_PATH, "w", encoding="utf-8", newline="\n") as file:
        file.write(updated)

    return True


if __name__ == "__main__":
    changed = update_readme()
    print("portfolio_pulse_changed=true" if changed else "portfolio_pulse_changed=false")
