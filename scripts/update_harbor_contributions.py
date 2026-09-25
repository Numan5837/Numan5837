"""Refresh the Terminal-Bench PR list in the profile README."""

from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen


OWNER = "harbor-framework"
REPOSITORY = "terminal-bench"
AUTHOR = "Numan5837"
START = "<!-- harbor-prs:start -->"
END = "<!-- harbor-prs:end -->"
SEARCH_URL = (
    "https://github.com/harbor-framework/terminal-bench/pulls"
    "?q=is%3Apr+author%3ANuman5837"
)


def fetch_pull_requests() -> list[dict]:
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Numan5837-profile-readme",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    results: list[dict] = []
    for page in range(1, 11):
        query = urlencode(
            {
                "q": f"repo:{OWNER}/{REPOSITORY} is:pr author:{AUTHOR}",
                "per_page": 100,
                "page": page,
                "sort": "created",
                "order": "desc",
            }
        )
        request = Request(f"https://api.github.com/search/issues?{query}", headers=headers)
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
        if payload.get("incomplete_results"):
            raise RuntimeError("GitHub returned incomplete PR search results")
        items = payload.get("items")
        if not isinstance(items, list):
            raise RuntimeError("GitHub returned a PR search response without items")
        results.extend(items)
        if len(results) >= payload["total_count"]:
            return results
    raise RuntimeError("GitHub PR search exceeded its 1,000-result limit")


def escape_markdown(value: str) -> str:
    escaped = html.escape(value, quote=False).replace("\n", " ").replace("\r", " ")
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", escaped)


def render_pull_requests(items: list[dict]) -> str:
    prs = sorted(items, key=lambda item: item["created_at"], reverse=True)
    count = len(prs)
    label = "pull request" if count == 1 else "pull requests"
    lines = [f"**{count} {label}** · [View all on Harbor]({SEARCH_URL})"]
    if not prs:
        lines.extend(["", "No Terminal-Bench pull requests yet."])
    else:
        lines.append("")
        for item in prs:
            number = int(item["number"])
            title = escape_markdown(item["title"])
            state = item["state"]
            if item.get("pull_request", {}).get("merged_at"):
                status = "MERGED"
            elif state == "open":
                status = "OPEN"
            elif state == "closed":
                status = "CLOSED"
            else:
                raise RuntimeError(f"Unexpected PR state for #{number}: {state!r}")
            url = f"https://github.com/{OWNER}/{REPOSITORY}/pull/{number}"
            lines.append(f"- [#{number} · {title}]({url}) · `{status}`")
    return "\n".join(lines)


def update_readme(readme: Path, items: list[dict]) -> bool:
    original = readme.read_text(encoding="utf-8")
    if original.count(START) != 1 or original.count(END) != 1:
        raise RuntimeError("README must contain exactly one Harbor PR marker pair")
    before, rest = original.split(START, 1)
    _, after = rest.split(END, 1)
    updated = before + START + "\n" + render_pull_requests(items) + "\n" + END + after
    if updated == original:
        return False
    readme.write_text(updated, encoding="utf-8", newline="")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, default=Path("README.md"))
    parser.add_argument("--input-json", type=Path, help="Use saved API results for local verification")
    args = parser.parse_args()
    if args.input_json:
        payload = json.loads(args.input_json.read_text(encoding="utf-8"))
        items = payload["items"]
    else:
        items = fetch_pull_requests()
    changed = update_readme(args.readme, items)
    print(f"Harbor PR list: {len(items)} pull requests, README {'updated' if changed else 'unchanged'}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as error:
        print(f"Could not refresh Harbor contributions: {error}", file=sys.stderr)
        sys.exit(1)
