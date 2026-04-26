import subprocess
import os

target_dir = "."
commit_hash = "HEAD"
try:
    proc = subprocess.run(["git", "-C", target_dir, "diff-tree", "--no-commit-id", "--name-status", "-r", commit_hash], capture_output=True, text=True, check=True)
    print(proc.stdout)
except Exception as e:
    print(e)
