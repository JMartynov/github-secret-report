# Task: GitHub Secret Reporting Automation (ACTUALIZED)

## 1. Objective & Context
*   **Goal**: Automatically scan popular open-source repositories for secrets and publish anonymized findings to a dedicated public repository (`github-secret-report`).
*   **Rationale**: Demonstrates the tool's effectiveness on real-world data and provides valuable security insights to the community while driving visibility.
*   **Key Components**:
    *   Dedicated report repository: `github-secret-report`.
    *   Daily automated scanning workflows **hosted within** `github-secret-report`.
    *   Curated list of 500 popular repositories.
    *   Automated report publishing and commit workflow.

## 2. Research & Strategy
*   **Repository Curation**: Use GitHub API or curated lists to identify top 500 repositories by stars/activity across major ecosystems (JS, Python, Go, Java).
*   **Scan Orchestration**: GitHub Action scheduled daily **within the `github-secret-report` repository**.
*   **Scanning Parameters**: Use `secret-scan` (installed as a dependency or via container) with standard rules; ensure high performance to handle multiple repositories within action time limits.
*   **Reporting Workflow**: 
    1.  Read the current scan state from `data/scan_state.json`.
    2.  Select the **next** $N$ repositories (default: 3) from the curated list of 500.
    3.  Scan the selected repositories.
    4.  Anonymize/obfuscate findings.
    5.  Generate a markdown/JSON report.
    6.  Update `data/scan_state.json` with the new progress.
    7.  Commit and push both the **new report** and the **updated state file** directly back to the `github-secret-report` repository.
    8.  **Notification**: Send an e-mail notification to the repository owner summarizing the task implementation state (Success/Failure, repositories scanned, finding count).

## 3. Implementation Checklist
- [ ] **Infrastructure Setup**:
    - [ ] Create the `github-secret-report` repository on GitHub.
    - [ ] Configure repository secrets (e.g., `REPORT_PUSH_TOKEN`, `SMTP_PASSWORD`, `NOTIFY_EMAIL`) for automated commits and notifications.
- [ ] **Repository List Generation**:
    - [ ] Create a script (e.g., `tools/curate_repos.py`) to generate `data/target_repos.json` containing 500 popular repositories.
- [ ] **Daily Workflow (GitHub Action in `github-secret-report`)**:
    - [ ] Implement `.github/workflows/daily-secret-report.yml` in the new repo.
    - [ ] Add a configurable setting `SCAN_COUNT` (default: 3) in the workflow.
    - [ ] **Rotation Logic**: Implement a Python script to manage selection and update `data/scan_state.json` to ensure sequential coverage of the 500 repositories.
    - [ ] **E-mail Notification Step**: Use the `dawidd6/action-send-mail` action or similar best-practice approach. For advanced integrations, explore the GitHub REST API for creating issues/comments that trigger notifications, or use a dedicated e-mail service (SendGrid/Mailgun).
- [ ] **Report Publishing**:
    - [ ] Implement logic to format scan results into readable reports.
    - [ ] Automate the commit and push of report files to the target repository.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_repo_rotation`: Verify the logic for selecting the next $N$ repositories from the list of 500.
- [ ] `test_report_formatting`: Ensure the generated report is correctly formatted and contains no raw secrets.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Full Cycle (Run the scanning script locally on 3 mock repos and verify a report is generated and ready for push).
- [ ] **Scenario**: Configurable Limit (Change $N=5$ and verify the system scans exactly 5 repositories).

### 4.3 Test Data
- [ ] Use a small subset of the target list for testing the workflow integrity.

## 5. Engineering Standards
*   **Safety**: NEVER publish raw secrets. All findings MUST be obfuscated using the standard `obfuscator.py` logic.
*   **Ethics**: Focus on high-level trends and notifications; avoid shaming specific projects.
*   **Automation**: The entire pipeline from selection to publishing must be zero-touch.
