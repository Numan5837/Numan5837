"""Offline contract checks for the profile's calendar rendering pipeline."""

import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as ET

import render_arcade


FIXTURE = Path(__file__).with_name("fixtures") / "contribution-calendar.json"
SVG = "{http://www.w3.org/2000/svg}"


class OfflineArcadeTests(unittest.TestCase):
    def render_fixture(self, directory):
        output = Path(directory) / "nested" / "contribution-pacman.svg"
        argv = [
            "render_arcade.py", "--username", "offline-example",
            "--calendar-json", str(FIXTURE), "--output", str(output),
        ]
        # A missing token and fail-fast network guards prove this path remains
        # usable offline, instead of silently relying on developer credentials.
        with patch.dict("os.environ", {}, clear=True), \
             patch.object(render_arcade, "urlopen", side_effect=AssertionError("Unexpected network access")), \
             patch.object(sys, "argv", argv):
            render_arcade.main()
        return output

    def test_cli_outputs_preserve_the_same_calendar_and_public_totals(self):
        expected = json.loads(FIXTURE.read_text(encoding="utf-8"))
        expected_days = sorted(
            [day for week in expected["weeks"] for day in week["contributionDays"]],
            key=lambda day: day["date"],
        )
        with tempfile.TemporaryDirectory() as directory:
            output = self.render_fixture(directory)
            self.assertEqual(
                {path.name for path in output.parent.iterdir()},
                {"contribution-pacman.svg", "contribution-pacman-static.svg", "contribution-data.json"},
            )
            animated = ET.parse(output).getroot()
            snapshot = json.loads(output.with_name("contribution-data.json").read_text(encoding="utf-8"))

        self.assertEqual(snapshot["username"], "offline-example")
        self.assertEqual(snapshot["days"], expected_days)
        self.assertEqual(snapshot["totalContributions"], sum(day["contributionCount"] for day in expected_days))
        self.assertEqual(snapshot["activeDays"], sum(day["contributionCount"] > 0 for day in expected_days))
        self.assertEqual(snapshot["pullRequests"], expected["publicPullRequests"])
        self.assertEqual(snapshot["publicRepositories"], expected["publicRepositories"])
        self.assertEqual(datetime.fromisoformat(snapshot["updatedAt"].replace("Z", "+00:00")).utcoffset().total_seconds(), 0)
        cells = animated.findall(f".//{SVG}rect[@class='contribution-cell']")
        self.assertEqual(len(cells), len(expected_days))
        self.assertEqual(sum(int(cell.attrib["data-count"]) for cell in cells), snapshot["totalContributions"])

    def test_static_fallback_keeps_calendar_and_visible_counters_without_animation(self):
        with tempfile.TemporaryDirectory() as directory:
            output = self.render_fixture(directory)
            static = ET.parse(output.with_name("contribution-pacman-static.svg")).getroot()

        self.assertFalse(any(element.tag.rsplit("}", 1)[-1].startswith("animate") for element in static.iter()))
        self.assertIsNone(static.find(f"{SVG}g[@class='players']"))
        cells = static.findall(f".//{SVG}rect[@class='contribution-cell']")
        self.assertEqual(len(cells), 14)
        self.assertTrue(all(cell.attrib.get("opacity", "1") == "1" for cell in cells))
        counters = static.find(f"{SVG}g[@class='activity-counters']")
        self.assertIsNotNone(counters)
        self.assertEqual(counters.attrib["opacity"], "1")
        labels = {element.text for element in counters.findall(f".//{SVG}text[@class='counter-label']")}
        self.assertEqual(labels, {"CONTRIBUTIONS", "ACTIVE DAYS", "PUBLIC PULL REQUESTS", "PUBLIC REPOSITORIES"})


if __name__ == "__main__":
    unittest.main()
