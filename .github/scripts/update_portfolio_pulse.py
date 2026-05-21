import os
import re
import urllib.request
from datetime import datetime, timezone, timedelta

README_PATH = "README.md"
START = "<!-- PORTFOLIO-PULSE:START -->"
END = "<!-- PORTFOLIO-PULSE:END -->"
GITHUB_USERNAME = os.getenv("GITHUB_REPOSITORY_OWNER", "afadlih")

WIB = timezone(timedelta(hours=7))

FEATURED_REPOS = [
    {
        "name": "AI Content Strategy",
        "url": "https://github.com/afadlih/AI-Content-Strategy---SEO-Assistant--Web-App-",
    },
    {
        "name": "Smart Clothesline IoT",
        "url": "https://github.com/afadlih/smart-clothesline-iot-system",
    },
    {
        "name": "Profile README",
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
        import json
        return json.loads(response.read().decode("utf-8"))


def get_recent_public_repos() -> list[dict[str, str]]:
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?sort=pushed&direction=desc&per_page=30"
    try:
        repos = github_api_json(url)
    except Exception:
        return FEATURED_REPOS

    ignored = {"afadlih"}
    picked = []

    for repo in repos:
        if repo.get("private") or repo.get("fork"):
            continue
        name = repo.get("name", "")
        if name in ignored:
            continue
        picked.append({"name": name, "url": repo.get("html_url", "")})
        if len(picked) == 3:
            break

    return picked or FEATURED_REPOS


def repo_links(repos: list[dict[str, str]]) -> str:
    return " · ".join(f'<a href="{repo["url"]}">{repo["name"]}</a>' for repo in repos)


def build_pulse_block() -> str:
    return f"""{START}
<table>
  <tr>
    <td><b>Last refresh</b></td>
    <td>{format_wib_now()}</td>
  </tr>
  <tr>
    <td><b>Current build focus</b></td>
    <td>FormAI automation flow, validation, execution diagnostics, and operator-facing UX.</td>
  </tr>
  <tr>
    <td><b>Active engineering theme</b></td>
    <td>AI workflow reliability: clear contracts, fallback paths, traceable results, and useful errors.</td>
  </tr>
  <tr>
    <td><b>Recently active public repos</b></td>
    <td>{repo_links(get_recent_public_repos())}</td>
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
