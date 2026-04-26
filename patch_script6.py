import re

with open("scripts/run_daily_scan.py", "r") as f:
    content = f.read()

template_start = content.find('RUNNER_CODE_TEMPLATE = """')
template_end = content.find('"""\n', template_start + 10)

template_content = content[template_start:template_end]
# The literal in Python needs to be \\n so when compiled it's a \n in the string,
# but since the whole thing is a multiline string without `r"""`, a simple `\n` is interpreted as a real newline by python.
# So we need to put `\\n` to represent literal `\n` in the file.
template_content = template_content.replace(".split('\n')", ".split('\\\\n')")
template_content = template_content.replace(".split('\t', 1)", ".split('\\\\t', 1)")

content = content[:template_start] + template_content + content[template_end:]

with open("scripts/run_daily_scan.py", "w") as f:
    f.write(content)
