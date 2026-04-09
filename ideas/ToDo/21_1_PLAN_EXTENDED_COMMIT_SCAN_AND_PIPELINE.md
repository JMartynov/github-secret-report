# Task: Extended Commit-Level Scanning and Pipeline Enhancements

## 1. Objective & Context
*   **Goal**: Enhance the daily secret scanning process to perform deep, commit-level scans across all branches of the target repositories, and update the pipeline configuration for larger daily batches and manual triggering.
*   **Rationale**: Scanning only the HEAD of branches might miss secrets that were committed and subsequently removed or hidden in the repository's history. Scanning every commit ensures comprehensive detection of historical leaks.
*   **Key Components**:
    *   Modify `scripts/run_daily_scan.py` to iterate through commits in all branches.
    *   Update reporting logic to include commit ID and attributes.
    *   Ensure secrets are scrubbed/obfuscated from the final reports.
    *   Verify or add manual trigger capabilities to the GitHub Action workflow.
    *   Increase the daily scan volume from 20 to 100 repositories.

## 2. Research & Strategy
*   **Commit-Level Scanning**: 
    *   Instead of just `os.walk` on the working directory, we need to utilize Git commands (e.g., `git log`, `git show`, or a Python Git library like `GitPython`) to retrieve the contents of files at each commit.
    *   We must iterate over all branches (`git branch -r`) and then iterate over all commits in those branches.
    *   **Performance Consideration**: Scanning every file in every commit can be extremely slow. We should optimize by only scanning the *diffs* or files changed in each commit using `git diff-tree` or similar, rather than doing a full repository scan per commit.
*   **Reporting Updates**:
    *   The output JSON and markdown report must be updated to include fields for `commit_id`, `commit_author`, `commit_date`, and the specific `file` that failed.
    *   **Security Standard**: Explicitly ensure that the actual matched secret is excluded from the report or fully obfuscated.
*   **Pipeline Adjustments**:
    *   Ensure `.github/workflows/daily-secret-report.yml` supports `workflow_dispatch` for manual runs (this may already exist but needs verification/testing).
    *   Change the default `SCAN_COUNT` to 100.
    *   Evaluate if increasing `SCAN_COUNT` to 100 requires increasing job timeouts or parallelizing the GitHub Action jobs.

## 3. Implementation Checklist
- [ ] **Script Enhancements (`scripts/run_daily_scan.py`)**:
    - [ ] Update the `runner.py` generation logic to traverse git commits instead of just the filesystem HEAD.
    - [ ] Implement an efficient diff-based scanning mechanism to only scan files altered in a given commit.
    - [ ] Modify the finding data structure to capture `commit_id`, `commit_author`, and `commit_date`.
    - [ ] Ensure the raw `match` string is completely removed or safely obfuscated using `obfuscator.py` before the data is appended to the report.
- [ ] **Reporting Logic**:
    - [ ] Update `generate_cumulative_report()` to format the new commit-level data.
    - [ ] Add columns for Commit Hash and Commit Date in the markdown table.
- [ ] **Pipeline Configuration (`.github/workflows/daily-secret-report.yml`)**:
    - [ ] Verify `workflow_dispatch` is configured and allows manual triggering with a custom `scan_count` parameter.
    - [ ] Change the default `scan_count` input and the daily cron fallback value from `20` to `100`.
    - [ ] Review timeout limits (e.g., `timeout-minutes`) to ensure the job won't be killed prematurely when scanning 100 repos with deep history.

## 4. Testing & Verification
- [ ] **Unit Tests**:
    - [ ] Update `tests/test_run_daily_scan.py` to mock commit-level outputs and ensure the new attributes are parsed correctly.
- [ ] **Acceptance Tests**:
    - [ ] Ensure `test_full_cycle_report_generation` in `tests/test_acceptance.py` reflects the new report structure.
    - [ ] Verify the assertion that raw secrets do not appear in the generated report.
- [ ] **Manual Pipeline Test**:
    - [ ] Trigger the pipeline manually via GitHub UI (`workflow_dispatch`) with a small scan count (e.g., 2) to verify the end-to-end functionality.
