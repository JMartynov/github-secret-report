import re

with open("scripts/run_daily_scan.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if i < 100:  # Only modify inside RUNNER_CODE_TEMPLATE
        if "split('\\n')" in line:
            lines[i] = line.replace("split('\\n')", "split('\\\\n')")
        if "split('\\t'" in line:
            lines[i] = line.replace("split('\\t'", "split('\\\\t'")

with open("scripts/run_daily_scan.py", "w") as f:
    f.writelines(lines)
