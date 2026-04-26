import json
import os
import subprocess
import tempfile
import argparse
import datetime
import shutil
import sys

def load_state(state_file):
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            return json.load(f)
    return {"last_scanned_index": 0}

def save_state(state_file, state):
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=4)

RUNNER_CODE_TEMPLATE = """
import sys
import os
import json
import time
import subprocess

# In CI/GitHub Action, it relies on python path finding site-packages.
from src.detector import SecretDetector
from src.obfuscator import Obfuscator

def get_commits(target_dir):
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
        return []

def get_commit_files(target_dir, commit_hash):
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
        return []

def get_file_content(target_dir, commit_hash, filepath):
    try:
        proc = subprocess.run(["git", "-C", target_dir, "show", f"{commit_hash}:{filepath}"], capture_output=True, text=True, errors="ignore")
        if proc.returncode == 0:
            return proc.stdout
    except Exception:
        pass
    return None

def main():
    start_time = time.time()
    detector = SecretDetector(
        force_scan_all=True,
        mode="deep",
        include_pii=True,
        pii_regions=["us", "eu"]
    )
    obfuscator = Obfuscator(mode="synthetic")
    all_findings = []
    
    target_dir = {{TARGET_DIR}}
    files_scanned = 0
    
    commits = get_commits(target_dir)

    for commit in commits:
        commit_hash = commit["hash"]
        files = get_commit_files(target_dir, commit_hash)

        for filepath in files:
            files_scanned += 1
            content = get_file_content(target_dir, commit_hash, filepath)
            if content:
                try:
                    findings = detector.scan(content)
                    for fn in findings:
                        fn_dict = {
                            "rule": getattr(fn, 'rule', getattr(fn, 'type', 'Unknown')),
                            "filepath": filepath,
                            "line_num": fn.line_num,
                            "match": obfuscator.obfuscate(fn.match if hasattr(fn, 'match') else fn.secret, [fn]),
                            "entropy": getattr(fn, 'entropy', 0),
                            "score": getattr(fn, 'score', getattr(fn, 'risk_score', 0)),
                            "risk": fn.risk,
                            "confidence": getattr(fn, 'confidence', 'Unknown'),
                            "suggestion": getattr(fn, 'suggestion', 'No suggestion provided.'),
                            "context": obfuscator.obfuscate(getattr(fn, 'context', ''), [fn]),
                            "commit_id": commit_hash,
                            "commit_author": commit["author"],
                            "commit_date": commit["date"]
                        }
                        all_findings.append(fn_dict)
                except Exception:
                    pass

    end_time = time.time()
    duration = end_time - start_time
    
    output = {
        "findings": all_findings,
        "files_scanned": files_scanned,
        "scan_duration_seconds": round(duration, 2)
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
"""

def run_scan(repo, reports_dir):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone target repo
        target_dir = os.path.join(tmpdir, "target_repo")
        print(f"Cloning {repo['name']}...")

        # Clone full depth to count branches correctly
        try:
            # Removed small timeout for clone as requested "without time limitation" for branch validation
            subprocess.run(["git", "clone", repo["url"], target_dir], check=False, capture_output=True, timeout=3600)
        except subprocess.TimeoutExpired:
            print(f"Clone timed out on {repo['name']}")
            return {
                "repo_name": repo['name'],
                "repo_url": repo['url'],
                "findings": [],
                "metrics": {
                    "files_scanned": 0,
                    "branches_count": "Unknown",
                    "repo_size": "Unknown",
                    "scan_duration": 0
                }
            }
        except Exception as e:
            print(f"Error cloning repository: {e}")
            return {
                "repo_name": repo['name'],
                "repo_url": repo['url'],
                "findings": [],
                "metrics": {
                    "files_scanned": 0,
                    "branches_count": "Unknown",
                    "repo_size": "Unknown",
                    "scan_duration": 0
                }
            }

        print(f"Scanning {repo['name']}...")

        # Get repository metrics
        try:
            branches_proc = subprocess.run(["git", "-C", target_dir, "branch", "-r"], capture_output=True, text=True, timeout=60)
            branches_count = len([b for b in branches_proc.stdout.split('\n') if b.strip() and "->" not in b])
        except subprocess.TimeoutExpired:
            branches_count = "Unknown"
        except Exception:
            branches_count = "Unknown"

        try:
            size_proc = subprocess.run(["du", "-sh", target_dir], capture_output=True, text=True, timeout=60)
            repo_size = size_proc.stdout.split('\t')[0] if size_proc.stdout else "Unknown"
        except subprocess.TimeoutExpired:
            repo_size = "Unknown"
        except Exception:
            repo_size = "Unknown"


        # Create a small script that will run the scan programmatically
        runner_script = os.path.join(tmpdir, "runner.py")
        with open(runner_script, "w") as f:
            f.write(RUNNER_CODE_TEMPLATE.replace('{{TARGET_DIR}}', json.dumps(target_dir)))
        
        # Run the runner script - Increased timeout to 1800s (30 mins)
        try:
            process = subprocess.run([sys.executable, runner_script], capture_output=True, text=True, timeout=1800)
        except subprocess.TimeoutExpired:
            print(f"Scanner timed out on {repo['name']}")
            return {
                "repo_name": repo['name'],
                "repo_url": repo['url'],
                "findings": [],
                "metrics": {
                    "files_scanned": 0,
                    "branches_count": branches_count,
                    "repo_size": repo_size,
                    "scan_duration": 1800
                }
            }
        except Exception as e:
            print(f"Error running scanner: {e}")
            return {
                "repo_name": repo['name'],
                "repo_url": repo['url'],
                "findings": [],
                "metrics": {
                    "files_scanned": 0,
                    "branches_count": branches_count,
                    "repo_size": repo_size,
                    "scan_duration": 0
                }
            }
        
        try:
            output = json.loads(process.stdout)
            findings = output.get("findings", [])
            files_scanned = output.get("files_scanned", 0)
            scan_duration = output.get("scan_duration_seconds", 0)
        except json.JSONDecodeError:
            print(f"Failed to parse scanner output. STDOUT: {process.stdout} STDERR: {process.stderr}")
            findings = []
            files_scanned = 0
            scan_duration = 0
            
        # Return deep report data for cumulative aggregation
        return {
            "repo_name": repo['name'],
            "repo_url": repo['url'],
            "findings": findings,
            "metrics": {
                "files_scanned": files_scanned,
                "branches_count": branches_count,
                "repo_size": repo_size,
                "scan_duration": scan_duration
            }
        }

def get_next_repos(repos, current_index, count):
    num_repos = len(repos)
    selected = []
    if num_repos == 0:
        return selected, current_index
        
    for i in range(count):
        idx = (current_index + i) % num_repos
        selected.append(repos[idx])
        
    new_index = (current_index + count) % num_repos
    return selected, new_index

def main():
    parser = argparse.ArgumentParser(description="Daily Secret Scan")
    parser.add_argument("--scan-count", type=int, default=20, help="Number of repos to scan")
    args = parser.parse_args()
    
    state_file = "data/scan_state.json"
    repos_file = "data/target_repos.json"
    reports_dir = "reports"
    
    os.makedirs(reports_dir, exist_ok=True)
    
    state = load_state(state_file)
    index = state.get("last_scanned_index", 0)
    
    with open(repos_file, 'r') as f:
        repos = json.load(f)
        
    num_repos = len(repos)
    if num_repos == 0:
        print("No repos found.")
        return
        
    selected_repos, new_index = get_next_repos(repos, index, args.scan_count)
    
    print("Installing py-secret-scan dependency...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "py-secret-scan==3.0.2"], check=True, capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        print("Timed out installing py-secret-scan dependency.")
        return
    except subprocess.CalledProcessError as e:
        print(f"Failed to install py-secret-scan: {e.stderr}")
        return

    cumulative_results = []

    for i, repo in enumerate(selected_repos):
        print(f"[{i+1}/{args.scan_count}] Scanning {repo['name']}")
        res = run_scan(repo, reports_dir)
        cumulative_results.append(res)
        
    state["last_scanned_index"] = new_index
    save_state(state_file, state)

    # Generate Cumulative Report
    generate_cumulative_report(cumulative_results, reports_dir)
        
def generate_cumulative_report(results, reports_dir):
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    cumulative_path = os.path.join(reports_dir, f"Cumulative-Report-{date_str}.md")
    compact_path = os.path.join(reports_dir, "daily_summary.md")
    
    total_repos = len(results)
    total_findings = sum(len(r['findings']) for r in results)
    total_files_scanned = sum(r['metrics']['files_scanned'] for r in results)
    total_duration = sum(r['metrics']['scan_duration'] for r in results)
    
    # Update Cumulative Report
    with open(cumulative_path, "w") as f:
        f.write(f"# Daily Cumulative Secret Scan Report - {date_str}\n\n")
        
        f.write("## Executive Summary\n\n")
        f.write("| Metric | Value |\n")
        f.write("|---|---|\n")
        f.write(f"| **Total Repositories Scanned** | {total_repos} |\n")
        f.write(f"| **Total Files Scanned** | {total_files_scanned} |\n")
        f.write(f"| **Total Scan Duration** | {round(total_duration, 2)} seconds |\n")
        f.write(f"| **Total Secrets Detected** | {total_findings} |\n\n")
        
        f.write("---\n\n")
        f.write("## Repository Breakdown\n\n")
        
        for r in results:
            repo_name = r['repo_name']
            repo_url = r['repo_url']
            findings = r['findings']
            m = r['metrics']
            
            f.write(f"### {repo_name}\n\n")
            f.write(f"**URL:** {repo_url}\n\n")
            f.write(f"- **Files Scanned:** {m['files_scanned']}\n")
            f.write(f"- **Branches:** {m['branches_count']}\n")
            f.write(f"- **Size:** {m['repo_size']}\n")
            f.write(f"- **Duration:** {m['scan_duration']}s\n")
            f.write(f"- **Findings:** {len(findings)}\n\n")
            
            if findings:
                f.write("<details><summary><b>View Detailed Findings</b></summary>\n\n")
                for fn in findings:
                    f.write(f"#### Finding: {fn['rule']} in `{fn['filepath']}`\n\n")
                    f.write(f"| Attribute | Value |\n")
                    f.write(f"|---|---|\n")
                    f.write(f"| **Risk** | {fn['risk']} |\n")
                    f.write(f"| **Score** | {fn['score']} |\n")
                    f.write(f"| **Confidence** | {fn['confidence']} |\n")
                    f.write(f"| **Line** | {fn['line_num']} |\n")
                    f.write(f"| **Commit** | {fn.get('commit_id', 'HEAD')[:7]} |\n")
                    f.write(f"| **Author** | {fn.get('commit_author', 'Unknown')} |\n")
                    f.write(f"| **Date** | {fn.get('commit_date', 'Unknown')} |\n")
                    f.write(f"| **Obfuscated Match** | `{fn['match']}` |\n\n")
                    
                    if fn.get('context'):
                        f.write("**Context:**\n```\n")
                        f.write(fn['context'])
                        f.write("\n```\n\n")
                    
                    f.write(f"**Suggestion:** {fn['suggestion']}\n\n")
                    f.write("---\n\n")
                f.write("</details>\n\n")
            else:
                f.write("*No secrets detected.*\n\n")
            f.write("---\n\n")
            
    # Update/Create Compact Daily Summary
    summary_line = f"| {date_str} | {total_repos} | {total_files_scanned} | {total_findings} | {round(total_duration, 2)}s |\n"
    
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
    main()