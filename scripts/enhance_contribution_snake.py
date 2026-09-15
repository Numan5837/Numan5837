#!/usr/bin/env python3
"""Add live GitHub activity counters to a generated contribution-snake SVG."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any


GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
GRAPHQL_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
          }
        }
      }
    }
    repositories(first: 1, ownerAffiliations: OWNER, privacy: PUBLIC) {
      totalCount
    }
  }
}
""".strip()

NUMBER_ROW_HEIGHT = 34


@dataclass(frozen=True)
class ActivityStats:
    pull_requests: int
    active_days: int
    contributions: int
    public_repositories: int


@dataclass(frozen=True)
class AnimationTiming:
    loop_ms: int
    reveal_at: float
    count_from: float
    count_until: float
    hide_at: float


@dataclass(frozen=True)
class Theme:
    card: str
    border: str
    text: str
    muted: str
    accent: str


DARK_THEME = Theme(
    card="#0d1117",
    border="#30363d",
    text="#f0f6fc",
    muted="#8b949e",
    accent="#55e6cc",
)

LIGHT_THEME = Theme(
    card="#ffffff",
    border="#d0d7de",
    text="#1f2328",
    muted="#59636e",
    accent="#3b82f6",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch public GitHub activity totals and place animated counters inside "
            "Platane/snk contribution graphs."
        )
    )
    parser.add_argument("--username", required=True, help="GitHub username to query")
    parser.add_argument("--light", required=True, type=Path, help="Light SVG to update")
    parser.add_argument("--dark", required=True, type=Path, help="Dark SVG to update")
    parser.add_argument(
        "--stats-json",
        help=(
            "Optional JSON object for deterministic local runs. When omitted, "
            "GITHUB_TOKEN is used to query GitHub GraphQL."
        ),
    )
    return parser.parse_args()


def require_nonnegative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a nonnegative integer")
    return value


def stats_from_mapping(payload: dict[str, Any]) -> ActivityStats:
    return ActivityStats(
        pull_requests=require_nonnegative_int(payload.get("pull_requests"), "pull_requests"),
        active_days=require_nonnegative_int(payload.get("active_days"), "active_days"),
        contributions=require_nonnegative_int(payload.get("contributions"), "contributions"),
        public_repositories=require_nonnegative_int(
            payload.get("public_repositories"), "public_repositories"
        ),
    )


def fetch_public_pull_requests(username: str) -> int:
    query = urllib.parse.urlencode(
        {"q": f"is:pr author:{username}", "per_page": "1"}
    )
    # A repository-scoped Actions token filters this search to its installation.
    # An unauthenticated request returns the full public profile count instead.
    request = urllib.request.Request(
        f"https://api.github.com/search/issues?{query}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Numan5837-profile-workflow",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub search returned HTTP {error.code}: {details}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not reach GitHub search: {error.reason}") from error

    return require_nonnegative_int(payload.get("total_count"), "pull_requests")


def fetch_stats(username: str, token: str) -> ActivityStats:
    request_body = json.dumps(
        {"query": GRAPHQL_QUERY, "variables": {"login": username}}
    ).encode("utf-8")
    request = urllib.request.Request(
        GRAPHQL_ENDPOINT,
        data=request_body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Numan5837-profile-workflow",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub GraphQL returned HTTP {error.code}: {details}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not reach GitHub GraphQL: {error.reason}") from error

    if payload.get("errors"):
        raise RuntimeError(f"GitHub GraphQL returned errors: {payload['errors']}")

    user = payload.get("data", {}).get("user")
    if user is None:
        raise RuntimeError(f"GitHub user {username!r} was not found")

    calendar = user.get("contributionsCollection", {}).get(
        "contributionCalendar", {}
    )
    contribution_days = [
        day
        for week in calendar.get("weeks", [])
        for day in week.get("contributionDays", [])
    ]
    active_days = sum(
        1
        for day in contribution_days
        if require_nonnegative_int(
            day.get("contributionCount"), "contributionCount"
        )
        > 0
    )

    return stats_from_mapping(
        {
            "pull_requests": fetch_public_pull_requests(username),
            "active_days": active_days,
            "contributions": calendar.get("totalContributions"),
            "public_repositories": user.get("repositories", {}).get("totalCount"),
        }
    )


def counter_values(total: int) -> list[int]:
    step_count = min(12, max(1, total))
    return [round(total * step / step_count) for step in range(step_count + 1)]


def counter_keyframes(
    index: int, value_count: int, timing: AnimationTiming
) -> str:
    step_count = value_count - 1
    lines = [
        f"@keyframes stat-count-{index}{{",
        f"0%,{format_number(timing.count_from)}%{{transform:translateY(0)}}",
    ]
    for step in range(1, step_count):
        percentage = timing.count_from + (
            timing.count_until - timing.count_from
        ) * step / step_count
        offset = NUMBER_ROW_HEIGHT * step
        lines.append(f"{percentage:.3f}%{{transform:translateY(-{offset}px)}}")

    final_offset = NUMBER_ROW_HEIGHT * step_count
    lines.extend(
        [
            f"{format_number(timing.count_until)}%,"
            f"{format_number(timing.hide_at - 0.01)}%"
            f"{{transform:translateY(-{final_offset}px)}}",
            f"{format_number(timing.hide_at)}%,100%{{transform:translateY(0)}}",
            "}",
        ]
    )
    return "".join(lines)


def find_contribution_grid(svg_root: ET.Element) -> tuple[float, float, float, float]:
    cells: list[tuple[float, float, float, float]] = []
    for element in svg_root.iter():
        if not element.tag.endswith("rect"):
            continue
        classes = element.attrib.get("class", "").split()
        if "c" not in classes:
            continue
        cells.append(
            (
                float(element.attrib["x"]),
                float(element.attrib["y"]),
                float(element.attrib.get("width", "12")),
                float(element.attrib.get("height", "12")),
            )
        )

    if not cells:
        raise ValueError("SVG does not contain Platane/snk contribution cells")

    left = min(cell[0] for cell in cells)
    top = min(cell[1] for cell in cells)
    right = max(cell[0] + cell[2] for cell in cells)
    bottom = max(cell[1] + cell[3] for cell in cells)
    return left, top, right, bottom


def find_animation_timing(source: str) -> AnimationTiming:
    duration_match = re.search(
        r"\banimation:none\s+(\d+)ms\s+linear\s+infinite", source
    )
    if duration_match is None:
        raise ValueError("SVG does not contain the Platane/snk loop duration")

    consumed_at = [
        float(match)
        for match in re.findall(r"([0-9]+(?:\.[0-9]+)?)%,100%\{", source)
    ]
    if not consumed_at:
        raise ValueError("SVG does not contain contribution-consumption keyframes")

    reset_match = re.search(
        r"@keyframes\s+s0\{0%,([0-9]+(?:\.[0-9]+)?)%\{", source
    )
    if reset_match is None:
        raise ValueError("SVG does not contain the Platane/snk reset keyframe")

    reset_at = float(reset_match.group(1))
    hide_at = reset_at - 0.05
    reveal_at = max(consumed_at) + 2.5
    count_from = reveal_at + 2.8
    count_until = min(reveal_at + 10.2, hide_at - 1.0)
    if not 0 < reveal_at < count_from < count_until < hide_at < 100:
        raise ValueError("SVG animation leaves no safe interval for activity counters")

    return AnimationTiming(
        loop_ms=int(duration_match.group(1)),
        reveal_at=reveal_at,
        count_from=count_from,
        count_until=count_until,
        hide_at=hide_at,
    )


def format_number(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def build_overlay(
    stats: ActivityStats,
    theme: Theme,
    grid: tuple[float, float, float, float],
    timing: AnimationTiming,
) -> tuple[str, str, str]:
    left, top, right, bottom = grid
    left_margin = 16.0
    right_margin = 32.0
    gap = 20.0
    card_top = top + 13.0
    card_height = bottom - top - 30.0
    available_width = right - left - left_margin - right_margin - 3 * gap
    card_width = available_width / 4

    items = [
        ("PULL REQUESTS", stats.pull_requests),
        ("ACTIVE DAYS", stats.active_days),
        ("CONTRIBUTIONS", stats.contributions),
        ("PUBLIC REPOS", stats.public_repositories),
    ]

    counter_data = [(label, total, counter_values(total)) for label, total in items]
    keyframes = "".join(
        counter_keyframes(index, len(values), timing)
        for index, (_, _, values) in enumerate(counter_data)
    )

    style = f"""
/* live GitHub activity counters; values refreshed by GitHub Actions */
.live-stats{{visibility:hidden;animation:stats-show {timing.loop_ms}ms steps(1,end) infinite;pointer-events:none}}
@keyframes stats-show{{0%,{format_number(timing.reveal_at - 0.01)}%{{visibility:hidden}}{format_number(timing.reveal_at)}%,{format_number(timing.hide_at - 0.01)}%{{visibility:visible}}{format_number(timing.hide_at)}%,100%{{visibility:hidden}}}}
.live-stat-card{{fill:{theme.card};stroke:{theme.border};stroke-width:1.25px}}
.live-stat-rule{{stroke:{theme.accent};stroke-width:2px;stroke-linecap:round}}
.live-stat-label{{fill:{theme.muted};font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:10px;font-weight:650;letter-spacing:.8px;text-anchor:middle}}
.live-stat-number{{fill:{theme.text};font-family:ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace;font-size:27px;font-weight:700;font-variant-numeric:tabular-nums;text-anchor:middle}}
.live-stat-stack{{animation-duration:{timing.loop_ms}ms;animation-timing-function:steps(1,end);animation-iteration-count:infinite}}
{keyframes}
""".strip()

    clip_paths: list[str] = []
    cards: list[str] = []
    for index, (label, _, values) in enumerate(counter_data):
        card_left = left + left_margin + index * (card_width + gap)
        text_x = card_left + card_width / 2
        label_y = card_top + 22
        number_y = card_top + 59
        clip_y = number_y - 27
        clip_height = 34
        rule_y = card_top + card_height - 1

        clip_paths.append(
            f'<clipPath id="live-stat-clip-{index}" clipPathUnits="userSpaceOnUse">'
            f'<rect x="{format_number(card_left)}" y="{format_number(clip_y)}" '
            f'width="{format_number(card_width)}" height="{format_number(clip_height)}"/>'
            "</clipPath>"
        )

        number_rows = "".join(
            f'<text class="live-stat-number" x="{format_number(text_x)}" '
            f'y="{format_number(number_y + row * NUMBER_ROW_HEIGHT)}">{value}</text>'
            for row, value in enumerate(values)
        )

        cards.append(
            f'<g class="live-stat-item live-stat-item-{index}">'
            f'<rect class="live-stat-card" x="{format_number(card_left)}" '
            f'y="{format_number(card_top)}" width="{format_number(card_width)}" '
            f'height="{format_number(card_height)}" rx="6" ry="6"/>'
            f'<text class="live-stat-label" x="{format_number(text_x)}" '
            f'y="{format_number(label_y)}">{label}</text>'
            f'<line class="live-stat-rule" x1="{format_number(card_left + 14)}" '
            f'y1="{format_number(rule_y)}" x2="{format_number(card_left + card_width - 14)}" '
            f'y2="{format_number(rule_y)}"/>'
            f'<g clip-path="url(#live-stat-clip-{index})">'
            f'<g class="live-stat-stack" style="animation-name:stat-count-{index}">'
            f"{number_rows}</g></g></g>"
        )

    definitions = f'<defs id="live-github-stats-defs">{"".join(clip_paths)}</defs>'
    scene = f'<g id="live-github-stats" class="live-stats">{"".join(cards)}</g>'
    return style, definitions, scene


def enhance_svg(path: Path, stats: ActivityStats, theme: Theme) -> None:
    source = path.read_text(encoding="utf-8")
    if 'id="live-github-stats"' in source:
        raise ValueError(f"{path} already contains live activity counters")
    if not re.search(r"</svg>\s*$", source):
        raise ValueError(f"{path} does not end with a closing SVG element")

    try:
        root = ET.fromstring(source)
    except ET.ParseError as error:
        raise ValueError(f"{path} is not valid SVG XML: {error}") from error

    style_closings = list(re.finditer(r"</style>", source))
    if len(style_closings) != 1:
        raise ValueError(f"{path} must contain exactly one closing style element")

    grid = find_contribution_grid(root)
    timing = find_animation_timing(source)
    style, definitions, scene = build_overlay(stats, theme, grid, timing)
    style_closing = style_closings[0]
    enhanced = (
        f"{source[:style_closing.start()]}{style}{source[style_closing.start():style_closing.end()]}"
        f"{definitions}{source[style_closing.end():]}"
    )

    if re.search(r'<rect\b[^>]*\bclass="s s0"[^>]*>', enhanced) is None:
        raise ValueError(f"{path} does not contain the first Platane/snk snake segment")
    enhanced = re.sub(r"</svg>\s*$", f"{scene}</svg>", enhanced, count=1)

    try:
        ET.fromstring(enhanced)
    except ET.ParseError as error:
        raise ValueError(f"Generated SVG for {path} is invalid: {error}") from error

    path.write_text(enhanced, encoding="utf-8", newline="\n")


def main() -> int:
    args = parse_args()
    try:
        if args.stats_json:
            raw_stats = json.loads(args.stats_json)
            if not isinstance(raw_stats, dict):
                raise ValueError("--stats-json must contain a JSON object")
            stats = stats_from_mapping(raw_stats)
        else:
            token = os.environ.get("GITHUB_TOKEN")
            if not token:
                raise ValueError("GITHUB_TOKEN is required when --stats-json is omitted")
            stats = fetch_stats(args.username, token)

        enhance_svg(args.light, stats, LIGHT_THEME)
        enhance_svg(args.dark, stats, DARK_THEME)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(
        "Added live activity counters: "
        f"public PRs={stats.pull_requests}, active days={stats.active_days}, "
        f"contributions={stats.contributions}, public repos={stats.public_repositories}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
