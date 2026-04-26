import re

with open("scripts/run_daily_scan.py", "r") as f:
    content = f.read()

# Let's fix this manually with exact replacement block
old_get_commits = """def get_commits(target_dir):
    try:
        # log --all ensures we see all branches
        proc = subprocess.run(["git", "-C", target_dir, "log", "--all", "--format=%H|%an|%cI"], capture_output=True, text=True, check=True)
        lines = proc.stdout.strip().split('\n')
        commits = []
        for line in lines:
            if line:
                parts = line.split('|', 2)
                if len(parts) == 3:
                    commits.append({"hash": parts[0], "author": parts[1], "date": parts[2]})
        return commits
    except Exception:
        return []"""

new_get_commits = """def get_commits(target_dir):
    try:
        # log --all ensures we see all branches
        proc = subprocess.run(["git", "-C", target_dir, "log", "--all", "--format=%H|%an|%cI"], capture_output=True, text=True, check=True)
        lines = proc.stdout.strip().split('\\n')
        commits = []
        for line in lines:
            if line:
                parts = line.split('|', 2)
                if len(parts) == 3:
                    commits.append({"hash": parts[0], "author": parts[1], "date": parts[2]})
        return commits
    except Exception:
        return []"""

old_get_commit_files = """def get_commit_files(target_dir, commit_hash):
    try:
        proc = subprocess.run(["git", "-C", target_dir, "diff-tree", "--no-commit-id", "--name-status", "-r", commit_hash], capture_output=True, text=True, check=True)
        lines = proc.stdout.strip().split('\n')
        files = []
        for line in lines:
            if line:
                parts = line.split('\t', 1)
                if len(parts) == 2:
                    status, filepath = parts
                    if status.startswith('A') or status.startswith('M'):
                        files.append(filepath)
        return files
    except Exception:
        return []"""

new_get_commit_files = """def get_commit_files(target_dir, commit_hash):
    try:
        proc = subprocess.run(["git", "-C", target_dir, "diff-tree", "--no-commit-id", "--name-status", "-r", commit_hash], capture_output=True, text=True, check=True)
        lines = proc.stdout.strip().split('\\n')
        files = []
        for line in lines:
            if line:
                parts = line.split('\\t', 1)
                if len(parts) == 2:
                    status, filepath = parts
                    if status.startswith('A') or status.startswith('M'):
                        files.append(filepath)
        return files
    except Exception:
        return []"""

content = content.replace(old_get_commits, new_get_commits)
content = content.replace(old_get_commit_files, new_get_commit_files)

with open("scripts/run_daily_scan.py", "w") as f:
    f.write(content)
