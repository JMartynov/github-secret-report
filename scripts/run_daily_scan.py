import json
import os
import subprocess
import tempfile
import argparse
import datetime
import shutil

def load_state(state_file):
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            return json.load(f)
    return {"last_scanned_index": 0}

def save_state(state_file, state):
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=4)

def run_scan(repo, reports_dir, scanner_dir):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone target repo
        target_dir = os.path.join(tmpdir, "target_repo")
        print(f"Cloning {repo['name']}...")
        
        # Clone full depth to count branches correctly
        subprocess.run(["git", "clone", repo["url"], target_dir], check=False, capture_output=True)
        
        print(f"Scanning {repo['name']}...")
        
        # Get repository metrics
        try:
            branches_proc = subprocess.run(["git", "-C", target_dir, "branch", "-r"], capture_output=True, text=True)
            branches_count = len([b for b in branches_proc.stdout.split('\n') if b.strip() and "->" not in b])
        except Exception:
            branches_count = "Unknown"
            
        try:
            size_proc = subprocess.run(["du", "-sh", target_dir], capture_output=True, text=True)
            repo_size = size_proc.stdout.split('\t')[0] if size_proc.stdout else "Unknown"
        except Exception:
            repo_size = "Unknown"
            

        # Create a small script that will run the scan programmatically
        runner_script = os.path.join(tmpdir, "runner.py")
        with open(runner_script, "w") as f:
            f.write(f"""
import sys
import os
import json
import time

sys.path.append(r'{scanner_dir}')

from detector import SecretDetector
from obfuscator import Obfuscator

def main():
    start_time = time.time()
    detector = SecretDetector(force_scan_all=True)
    obfuscator = Obfuscator(mode="synthetic")
    all_findings = []
    
    target_dir = r'{target_dir}'
    files_scanned = 0
    
    for root, dirs, files in os.walk(target_dir):
        if '.git' in dirs:
            dirs.remove('.git')
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, target_dir)
            files_scanned += 1
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    findings = detector.scan(content)
                    for fn in findings:
                        # Convert to dict and obfuscate match
                        fn_dict = {{
                            "rule": fn.rule,
                            "filepath": rel_path,
                            "line_num": fn.line_num,
                            "match": obfuscator.obfuscate(fn.match, [fn]),
                            "entropy": fn.entropy,
                            "score": fn.score,
                            "risk": fn.risk
                        }}
                        all_findings.append(fn_dict)
            except Exception as e:
                pass
                
    end_time = time.time()
    duration = end_time - start_time
    
    output = {{
        "findings": all_findings,
        "files_scanned": files_scanned,
        "scan_duration_seconds": round(duration, 2)
    }}
    print(json.dumps(output))

if __name__ == "__main__":
    main()
""")
        
        # Run the runner script
        process = subprocess.run(["python3", runner_script], capture_output=True, text=True)
        
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
    
    # Clone secret-scan once
    with tempfile.TemporaryDirectory() as tmpdir:
        scanner_dir = os.path.join(tmpdir, "secret-scan")
        print(f"Cloning secret-scan dependency...")
        subprocess.run(["git", "clone", "https://github.com/JMartynov/secret-scan.git", scanner_dir], check=True, capture_output=True)
        
        print("Installing secret-scan dependencies...")
        subprocess.run(["pip", "install", "-r", os.path.join(scanner_dir, "requirements.txt")], check=True, capture_output=True)
        
        cumulative_results = []
        
        for i, repo in enumerate(selected_repos):
            print(f"[{i+1}/{args.scan_count}] Scanning {repo['name']}")
            res = run_scan(repo, reports_dir, scanner_dir)
            cumulative_results.append(res)
            
        state["last_scanned_index"] = new_index
        save_state(state_file, state)
        
        # Generate Cumulative Report
        generate_cumulative_report(cumulative_results, reports_dir)
        
def generate_cumulative_report(results, reports_dir):
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    cumulative_path = os.path.join(reports_dir, f"Cumulative-Report-{date_str}.md")
    
    total_repos = len(results)
    total_findings = sum(len(r['findings']) for r in results)
    total_files_scanned = sum(r['metrics']['files_scanned'] for r in results)
    total_duration = sum(r['metrics']['scan_duration'] for r in results)
    
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
                f.write("<details><summary><b>View Findings</b></summary>\n\n")
                f.write("| File | Rule | Line | Risk | Score | Obfuscated Match |\n")
                f.write("|---|---|---|---|---|---|\n")
                for fn in findings:
                    f.write(f"| `{fn['filepath']}` | {fn['rule']} | {fn['line_num']} | {fn['risk']} | {fn['score']} | `{fn['match']}` |\n")
                f.write("\n</details>\n\n")
            else:
                f.write("*No secrets detected.*\n\n")
            f.write("---\n\n")
            
    print(f"Cumulative report saved to {cumulative_path}")
        
if __name__ == "__main__":
    main()