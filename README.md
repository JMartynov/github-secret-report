# GitHub Secret Reporting Automation

This repository hosts an automated system to scan popular open-source repositories for sensitive secrets and publish anonymized, cumulative deep findings.

## Purpose

The goal is to automatically discover new open-source repositories, scan them daily using the [`secret-scan`](https://github.com/JMartynov/secret-scan) engine, obfuscate the results, and generate comprehensive Markdown reports. This demonstrates the effectiveness of the tool on real-world data and helps raise awareness about secret leaks in codebases, prompts, and logs. It operates completely hands-free via GitHub Actions.

## Architecture & Components

The pipeline consists of three main components working together to curate targets, scan them, and publish findings.

### 1. Repository Discovery & Curation
*   **`tools/curate_repos.py`**: A one-time setup script that fetches the top 500 popular repositories across major programming languages (Python, JavaScript, Go, Java, Ruby) to establish a baseline list in `data/target_repos.json`.
*   **`scripts/discover_repos.py`**: A daily script run by GitHub Actions. It queries the GitHub API for recently updated repositories, deduplicates them against our existing list, and appends up to 20 new repositories with the status `"Hasn't yet validated"`. This ensures our pipeline always has fresh data to process.

### 2. Deep Scanning Pipeline
*   **`scripts/run_daily_scan.py`**: The core execution script.
    *   **Rotation:** It reads `data/scan_state.json` to remember which repository was scanned last, then picks the next $N$ (default: 20) repositories in a round-robin fashion.
    *   **Dynamic Cloning:** To adhere to engineering standards, it does not store the `secret-scan` code here. Instead, it dynamically clones `JMartynov/secret-scan` into a temporary directory and executes it on the fly.
    *   **Deep Metrics:** It clones the target repositories and gathers deep analytics, including:
        *   Files scanned count
        *   Remote branches count
        *   Repository size on disk
        *   Execution time (Scan Duration)
    *   **Obfuscation:** All findings are heavily obfuscated (e.g., using synthetic or redacted rules). **Raw secrets are never captured or stored.**

### 3. Reporting & Automation
*   **Cumulative Reports:** Instead of cluttering the repository with individual files per repository, the system aggregates all metrics and findings into a single, comprehensive daily report formatted as `reports/Cumulative-Report-YYYY-MM-DD.md`.
*   **GitHub Action (`.github/workflows/daily-secret-report.yml`)**: This workflow triggers daily via `cron` (or manually via `workflow_dispatch`). It runs the discovery script, runs the scanner, commits the new list/state/reports back to the repository, and optionally emails an administrator with the run status.

---

## How to Run Locally

To simulate the exact behavior of the GitHub Action on your local machine:

1.  **Curate Initial Repositories (If starting from scratch):**
    ```bash
    python tools/curate_repos.py
    ```

2.  **Discover New Repositories:**
    ```bash
    python scripts/discover_repos.py
    ```

3.  **Run the Scan:**
    ```bash
    # Scan default amount of repositories
    python scripts/run_daily_scan.py --scan-count 3
    ```
    This will output a `Cumulative-Report-YYYY-MM-DD.md` in the `reports/` directory.

---

## Testing

The project includes unit and acceptance tests to verify rotation logic, proper secret obfuscation, configurable limits, and cumulative report formatting without making actual network requests.

Run the tests using `pytest`:

```bash
pip install -r requirements.txt # Or install pytest directly
PYTHONPATH=. pytest tests/
```

---

## Ethical Considerations

*   **No Raw Secrets:** All findings are heavily obfuscated (redacted/synthetic) before being saved. Real credentials are never published in the markdown reports.
*   **Zero-touch Pipeline:** The process is fully automated to avoid direct human interaction with potentially sensitive data.
*   **API Usage:** Scripts respect GitHub search API limits by polling infrequently and caching results in tracked JSON files.