import pytest
import os
import tempfile
import json
import subprocess

def test_full_cycle_report_generation(monkeypatch):
    """
    Acceptance test for the daily scan run logic (Scenario: Full Cycle & Formatting).
    We create a dummy 'secret-scan' and a dummy 'target repo' to avoid making network requests.
    """
    # Create a dummy secret-scan structure
    with tempfile.TemporaryDirectory() as tmpdir:
        # Mocking repos
        dummy_repos_file = os.path.join(tmpdir, "target_repos.json")
        dummy_state_file = os.path.join(tmpdir, "scan_state.json")
        reports_dir = os.path.join(tmpdir, "reports")
        os.makedirs(reports_dir)

        with open(dummy_repos_file, "w") as f:
            json.dump([
                {"name": "test/dummy1", "url": "local/dummy1"},
                {"name": "test/dummy2", "url": "local/dummy2"}
            ], f)

        with open(dummy_state_file, "w") as f:
            json.dump({"last_scanned_index": 0}, f)

        # Mock subprocess.run in run_daily_scan so we don't actually git clone
        original_run = subprocess.run

        def mock_subprocess_run(cmd, *args, **kwargs):
            if "git" in cmd and "clone" in cmd:
                # Fake clone by creating a directory
                dest = cmd[-1]
                os.makedirs(dest, exist_ok=True)

                if "secret-scan" in cmd:
                    # Create fake requirements.txt and detector/obfuscator mock
                    with open(os.path.join(dest, "requirements.txt"), "w") as f:
                        f.write("")
                    with open(os.path.join(dest, "detector.py"), "w") as f:
                        f.write("""
class SecretDetector:
    def __init__(self, force_scan_all=False):
        pass
    def scan(self, text):
        class Finding:
            def __init__(self):
                self.rule = 'mock-rule'
                self.line_num = 1
                self.match = 'supersecret'
                self.entropy = 4.0
                self.score = 5.0
                self.risk = 'HIGH'
        return [Finding()]
""")
                    with open(os.path.join(dest, "obfuscator.py"), "w") as f:
                        f.write("""
class Obfuscator:
    def __init__(self, mode):
        self.mode = mode
    def obfuscate(self, match, findings):
        return 'REDACTED'
""")
                else:
                    # Dummy target repo file
                    with open(os.path.join(dest, "test.txt"), "w") as f:
                        f.write("supersecret")

                # Mock a successful run
                class MockResult:
                    returncode = 0
                    stdout = ""
                    stderr = ""
                return MockResult()
            elif "pip" in cmd and "install" in cmd:
                class MockResult:
                    returncode = 0
                    stdout = ""
                    stderr = ""
                return MockResult()
            else:
                return original_run(cmd, *args, **kwargs)

        monkeypatch.setattr(subprocess, "run", mock_subprocess_run)

        # Now run the logic
        from scripts.run_daily_scan import load_state, save_state, get_next_repos, run_scan

        state = load_state(dummy_state_file)
        with open(dummy_repos_file, 'r') as f:
            repos = json.load(f)

        selected_repos, new_index = get_next_repos(repos, state.get("last_scanned_index", 0), 1)

        # We need a fake secret-scan dir
        scanner_dir = os.path.join(tmpdir, "fake-secret-scan")
        mock_subprocess_run(["git", "clone", "secret-scan", scanner_dir])

        # Need to put an empty __init__.py so runner can import it if necessary
        with open(os.path.join(scanner_dir, "__init__.py"), "w") as f:
            f.write("")

        # Generate cumulative report manually since we mock run_scan loop
        from scripts.run_daily_scan import generate_cumulative_report

        cumulative_results = []
        for repo in selected_repos:
            res = run_scan(repo, reports_dir, scanner_dir)
            cumulative_results.append(res)

        generate_cumulative_report(cumulative_results, reports_dir)

        # Verify
        reports = os.listdir(reports_dir)
        assert len(reports) == 1
        assert reports[0].startswith("Cumulative-Report-")
        with open(os.path.join(reports_dir, reports[0]), "r") as f:
            content = f.read()
            assert "test/dummy1" in content
            assert "REDACTED" in content
            assert "supersecret" not in content # Raw secret must not be there


def test_configurable_limit(monkeypatch):
    """
    Acceptance test for the daily scan run logic (Scenario: Configurable Limit).
    Verify the system scans exactly N repositories when limit is configured.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Mocking repos (10 repos)
        dummy_repos_file = os.path.join(tmpdir, "target_repos.json")
        dummy_state_file = os.path.join(tmpdir, "scan_state.json")
        reports_dir = os.path.join(tmpdir, "reports")
        os.makedirs(reports_dir)

        repos = [{"name": f"test/dummy{i}", "url": f"local/dummy{i}"} for i in range(10)]
        with open(dummy_repos_file, "w") as f:
            json.dump(repos, f)

        with open(dummy_state_file, "w") as f:
            json.dump({"last_scanned_index": 2}, f)

        # We just need to assert that `run_scan` is called N times.
        from scripts.run_daily_scan import load_state, save_state, get_next_repos

        state = load_state(dummy_state_file)
        with open(dummy_repos_file, 'r') as f:
            loaded_repos = json.load(f)

        selected_repos, new_index = get_next_repos(loaded_repos, state.get("last_scanned_index", 0), 5)

        assert len(selected_repos) == 5
        assert selected_repos[0]["name"] == "test/dummy2"
        assert selected_repos[-1]["name"] == "test/dummy6"
        assert new_index == 7
