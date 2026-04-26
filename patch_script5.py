import re

with open("scripts/run_daily_scan.py", "r") as f:
    content = f.read()

template_start = content.find('RUNNER_CODE_TEMPLATE = """')
template_end = content.find('"""\n', template_start + 10)

template_content = content[template_start:template_end]
template_content = template_content.replace(".split('\\n')", r".split('\\n')")
template_content = template_content.replace(".split('\\t', 1)", r".split('\\t', 1)")

content = content[:template_start] + template_content + content[template_end:]

with open("scripts/run_daily_scan.py", "w") as f:
    f.write(content)
