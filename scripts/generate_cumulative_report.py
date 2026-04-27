import os
import re
import datetime
import argparse

def generate_cumulative_report(reports_dir):
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    daily_path = os.path.join(reports_dir, f"Daily-Report-{yesterday_str}.md")
    cumulative_path = os.path.join(reports_dir, f"Cumulative-Report-{yesterday_str}.md")
    compact_path = os.path.join(reports_dir, "daily_summary.md")

    if not os.path.exists(daily_path):
        print(f"No daily report found for {yesterday_str}.")
        return

    with open(daily_path, "r") as f:
        content = f.read()

    # Parse metrics from daily report
    total_repos = len(re.findall(r"### (.*?)\n", content))

    files_scanned = re.findall(r"- \*\*Files Scanned:\*\* (\d+)", content)
    total_files_scanned = sum(int(f) for f in files_scanned)

    durations = re.findall(r"- \*\*Duration:\*\* ([\d\.]+)s", content)
    total_duration = sum(float(d) for d in durations)

    findings = re.findall(r"- \*\*Findings:\*\* (\d+)", content)
    total_findings = sum(int(f) for f in findings)

    # Create Cumulative Report
    with open(cumulative_path, "w") as f:
        f.write(f"# Daily Cumulative Secret Scan Report - {yesterday_str}\n\n")

        f.write("## Executive Summary\n\n")
        f.write("| Metric | Value |\n")
        f.write("|---|---|\n")
        f.write(f"| **Total Repositories Scanned** | {total_repos} |\n")
        f.write(f"| **Total Files Scanned** | {total_files_scanned} |\n")
        f.write(f"| **Total Scan Duration** | {round(total_duration, 2)} seconds |\n")
        f.write(f"| **Total Secrets Detected** | {total_findings} |\n\n")

        f.write("---\n\n")
        f.write("## Repository Breakdown\n\n")

        # Strip the header part of the daily report
        breakdown_start = content.find("---")
        if breakdown_start != -1:
            f.write(content[breakdown_start + 3:].lstrip())

    # Update Compact Daily Summary
    summary_line = f"| {yesterday_str} | {total_repos} | {total_files_scanned} | {total_findings} | {round(total_duration, 2)}s |\n"

    if not os.path.exists(compact_path):
        with open(compact_path, "w") as f:
            f.write("# Compact Daily Secret Scan Summary\n\n")
            f.write("| Date | Repos | Files | Findings | Duration |\n")
            f.write("|---|---|---|---|---|\n")

    with open(compact_path, "a") as f:
        f.write(summary_line)

    print(f"Cumulative report saved to {cumulative_path}")
    print(f"Compact summary updated at {compact_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", type=str, default="reports")
    args = parser.parse_args()
    generate_cumulative_report(args.reports_dir)
