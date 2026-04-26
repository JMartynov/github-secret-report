from scripts.run_daily_scan import RUNNER_CODE_TEMPLATE
import json
import subprocess

with open("test_runner.py", "w") as f:
    f.write(RUNNER_CODE_TEMPLATE.replace("{{TARGET_DIR}}", json.dumps(".")))

try:
    proc = subprocess.run(["python3", "-c", "import py_compile; py_compile.compile('test_runner.py')"], check=True)
    print("Runner template compiles successfully!")
except Exception as e:
    print(f"Compilation failed: {e}")
