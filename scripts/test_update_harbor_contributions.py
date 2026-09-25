import tempfile
import unittest
from pathlib import Path

from update_harbor_contributions import END, START, render_pull_requests, update_readme


class HarborContributionTests(unittest.TestCase):
    def test_new_prs_and_state_changes_update_the_list(self):
        items = [
            {
                "number": 1969,
                "title": "Reconcile replicas",
                "created_at": "2026-09-14T06:08:48Z",
                "state": "closed",
                "pull_request": {"merged_at": "2026-09-25T00:00:00Z"},
            },
            {
                "number": 1985,
                "title": "Recover coupon groups",
                "created_at": "2026-09-16T16:17:40Z",
                "state": "open",
                "pull_request": {"merged_at": None},
            },
            {
                "number": 1999,
                "title": "A new <task> [draft]",
                "created_at": "2026-09-25T00:00:00Z",
                "state": "closed",
                "pull_request": {"merged_at": None},
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            readme = Path(directory) / "README.md"
            readme.write_text(f"Before\n{START}\nOld list\n{END}\nAfter\n", encoding="utf-8")
            self.assertTrue(update_readme(readme, items))
            self.assertFalse(update_readme(readme, items))
            result = readme.read_text(encoding="utf-8")
        self.assertIn("**3 pull requests**", result)
        self.assertLess(result.index("#1999"), result.index("#1985"))
        self.assertLess(result.index("#1985"), result.index("#1969"))
        self.assertIn("[#1969 · Reconcile replicas]", result)
        self.assertIn("`MERGED`", result)
        self.assertIn("`OPEN`", result)
        self.assertIn("`CLOSED`", result)
        self.assertIn("&lt;task&gt;", result)
        self.assertNotIn("<task>", result)
        self.assertTrue(result.startswith("Before\n"))
        self.assertTrue(result.endswith("After\n"))

    def test_missing_markers_fail_without_changing_readme(self):
        with tempfile.TemporaryDirectory() as directory:
            readme = Path(directory) / "README.md"
            readme.write_text("No markers\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                update_readme(readme, [])
            self.assertEqual(readme.read_text(encoding="utf-8"), "No markers\n")


if __name__ == "__main__":
    unittest.main()
