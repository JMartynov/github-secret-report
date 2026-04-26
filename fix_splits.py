with open("scripts/run_daily_scan.py", "r") as f:
    content = f.read()

# Fix split('\n')
content = content.replace("split('\\\n')", "split('\\n')")

# Fix split('\t') - handle any potential tab characters embedded there
content = content.replace("split('\\\t', 1)", "split('\\t', 1)")
content = content.replace("split('\t', 1)", "split('\\t', 1)")

with open("scripts/run_daily_scan.py", "w") as f:
    f.write(content)
