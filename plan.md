1. **Refactor `scripts/run_daily_scan.py`**:
   - Extract the runner script generator code into a top-level constant `RUNNER_CODE_TEMPLATE`.
   - Remove f-string escaping for dictionaries and f-strings within the template (e.g. `{{` to `{`).
   - Use `{{TARGET_DIR}}` as a placeholder and inject the variable securely using `.replace('{{TARGET_DIR}}', json.dumps(target_dir))`.

2. **Add `tests/test_runner_script.py`**:
   - Import `RUNNER_CODE_TEMPLATE` from `scripts.run_daily_scan`.
   - Use `exec()` to execute the template code in a local namespace (mocking the environment).
   - Test the `get_commits` function extracted from the local namespace.
   - Mock `subprocess.run` to simulate `git log` output and error cases.

3. **Verify the tests**:
   - Run the new test via `PYTHONPATH=. pytest tests/test_runner_script.py`.
   - Run the full test suite to ensure no regressions.

4. **Complete Pre Commit Steps**:
   - Get instructions from `pre_commit_instructions` to test, verify, and complete checks before submitting.

5. **Submit**:
   - Submit the PR with the title '🧪 [testing improvement] Test get_commits using extracted template and mocked subprocess'.
