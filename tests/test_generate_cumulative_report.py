import os
import datetime
import tempfile
import unittest
from scripts.generate_cumulative_report import generate_cumulative_report

class TestGenerateCumulativeReport(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.reports_dir = self.temp_dir.name
        self.yesterday = datetime.date.today() - datetime.timedelta(days=1)
        self.yesterday_str = self.yesterday.strftime('%Y-%m-%d')
        self.daily_path = os.path.join(self.reports_dir, f"Daily-Report-{self.yesterday_str}.md")
        self.cumulative_path = os.path.join(self.reports_dir, f"Cumulative-Report-{self.yesterday_str}.md")
        self.compact_path = os.path.join(self.reports_dir, "daily_summary.md")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_daily_report(self):
        # Should not crash, should just return
        generate_cumulative_report(self.reports_dir)
        self.assertFalse(os.path.exists(self.cumulative_path))
        self.assertFalse(os.path.exists(self.compact_path))

    def test_happy_path_report_generation(self):
        # Create a mock daily report
        daily_content = """# Daily Scan Report

Some intro text...
---
### user/repo1
- **Files Scanned:** 15
- **Duration:** 2.5s
- **Findings:** 3

### user/repo2
- **Files Scanned:** 10
- **Duration:** 1.0s
- **Findings:** 0
"""
        with open(self.daily_path, "w") as f:
            f.write(daily_content)

        generate_cumulative_report(self.reports_dir)

        # Check cumulative report
        self.assertTrue(os.path.exists(self.cumulative_path))
        with open(self.cumulative_path, "r") as f:
            cumul_content = f.read()

        self.assertIn(f"# Daily Cumulative Secret Scan Report - {self.yesterday_str}", cumul_content)
        self.assertIn("| **Total Repositories Scanned** | 2 |", cumul_content)
        self.assertIn("| **Total Files Scanned** | 25 |", cumul_content)
        self.assertIn("| **Total Scan Duration** | 3.5 seconds |", cumul_content)
        self.assertIn("| **Total Secrets Detected** | 3 |", cumul_content)
        self.assertIn("### user/repo1", cumul_content)
        self.assertIn("### user/repo2", cumul_content)

        # Check compact summary
        self.assertTrue(os.path.exists(self.compact_path))
        with open(self.compact_path, "r") as f:
            compact_content = f.read()

        self.assertIn("# Compact Daily Secret Scan Summary", compact_content)
        self.assertIn("| Date | Repos | Files | Findings | Duration |", compact_content)
        self.assertIn(f"| {self.yesterday_str} | 2 | 25 | 3 | 3.5s |", compact_content)

    def test_append_to_existing_summary(self):
        # Existing compact summary
        existing_summary = """# Compact Daily Secret Scan Summary

| Date | Repos | Files | Findings | Duration |
|---|---|---|---|---|
| 2023-01-01 | 1 | 10 | 0 | 1.0s |
"""
        with open(self.compact_path, "w") as f:
            f.write(existing_summary)

        # Create a mock daily report
        daily_content = """---
### user/repo1
- **Files Scanned:** 5
- **Duration:** 0.5s
- **Findings:** 1
"""
        with open(self.daily_path, "w") as f:
            f.write(daily_content)

        generate_cumulative_report(self.reports_dir)

        # Check compact summary
        with open(self.compact_path, "r") as f:
            compact_content = f.read()

        # Ensure headers aren't duplicated
        self.assertEqual(compact_content.count("# Compact Daily Secret Scan Summary"), 1)
        self.assertIn("| 2023-01-01 | 1 | 10 | 0 | 1.0s |", compact_content)
        self.assertIn(f"| {self.yesterday_str} | 1 | 5 | 1 | 0.5s |", compact_content)

    def test_empty_or_zero_findings(self):
        daily_content = """---
### empty/repo
- **Files Scanned:** 0
- **Duration:** 0.0s
- **Findings:** 0
"""
        with open(self.daily_path, "w") as f:
            f.write(daily_content)

        generate_cumulative_report(self.reports_dir)

        with open(self.cumulative_path, "r") as f:
            cumul_content = f.read()

        self.assertIn("| **Total Repositories Scanned** | 1 |", cumul_content)
        self.assertIn("| **Total Files Scanned** | 0 |", cumul_content)
        self.assertIn("| **Total Scan Duration** | 0.0 seconds |", cumul_content)
        self.assertIn("| **Total Secrets Detected** | 0 |", cumul_content)

if __name__ == '__main__':
    unittest.main()
