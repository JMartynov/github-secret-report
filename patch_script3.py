import re

with open("scripts/run_daily_scan.py", "r") as f:
    content = f.read()

# Replace everything from `with open(runner_script, "w") as f:` up to `if __name__ == "__main__":\n    main()\n""")`
pattern = r'        with open\(runner_script, "w"\) as f:\n            f\.write\(f"""(.*?)"""\)'
replacement = r'        with open(runner_script, "w") as f:\n            f.write(RUNNER_CODE_TEMPLATE.replace("{{TARGET_DIR}}", json.dumps(target_dir)))'

content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
print(f"Replaced {count} times")

with open("scripts/run_daily_scan.py", "w") as f:
    f.write(content)
