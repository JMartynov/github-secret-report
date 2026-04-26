import re

with open("tests/test_runner_script.py", "r") as f:
    content = f.read()

content = content.replace("exec(RUNNER_CODE_TEMPLATE, namespace)", """
import sys
# Mock the 'src' module imports since we only want to test get_commits
import sys
from unittest.mock import MagicMock
sys.modules['src'] = MagicMock()
sys.modules['src.detector'] = MagicMock()
sys.modules['src.obfuscator'] = MagicMock()

exec(RUNNER_CODE_TEMPLATE, namespace)
""")

with open("tests/test_runner_script.py", "w") as f:
    f.write(content)
