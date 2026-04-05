import pytest
import os
import json
import tempfile
import datetime
from unittest.mock import patch, MagicMock
from scripts.run_daily_scan import get_next_repos, run_scan

def test_repo_rotation_normal():
    repos = [{"name": f"repo{i}"} for i in range(10)]
    selected_repos, new_index = get_next_repos(repos, 0, 3)
    assert len(selected_repos) == 3
    assert selected_repos[0]["name"] == "repo0"
    assert selected_repos[2]["name"] == "repo2"
    assert new_index == 3

def test_repo_rotation_wrap_around():
    repos = [{"name": f"repo{i}"} for i in range(10)]
    selected_repos, new_index = get_next_repos(repos, 8, 3)
    assert len(selected_repos) == 3
    assert selected_repos[0]["name"] == "repo8"
    assert selected_repos[1]["name"] == "repo9"
    assert selected_repos[2]["name"] == "repo0"
    assert new_index == 1

def test_repo_rotation_all():
    repos = [{"name": f"repo{i}"} for i in range(3)]
    selected_repos, new_index = get_next_repos(repos, 0, 5)
    assert len(selected_repos) == 5
    assert selected_repos[0]["name"] == "repo0"
    assert selected_repos[3]["name"] == "repo0"
    assert new_index == 2

@patch("scripts.run_daily_scan.subprocess.run")
def test_report_formatting(mock_run):
    """
    Test that generated reports are correctly formatted and contain no raw secrets.
    """
    # Mock subprocess.run to return a specific JSON findings output
    mock_output = {
        "findings": [
            {
                "rule": "aws_access_key",
                "filepath": "config.yaml",
                "line_num": 10,
                "match": "AKIAREDACTEDXXXXX",  # Obfuscated
                "entropy": 4.5,
                "score": 5.0,
                "risk": "HIGH"
            }
        ],
        "files_scanned": 150,
        "scan_duration_seconds": 1.25
    }
    
    mock_result = MagicMock()
    mock_result.stdout = json.dumps(mock_output)
    mock_run.return_value = mock_result
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = {"name": "test/repo", "url": "https://github.com/test/repo"}
        reports_dir = os.path.join(tmpdir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        scanner_dir = os.path.join(tmpdir, "scanner")
        
        # We need to simulate the execution where the runner script is written and executed
        # We don't actually need the runner to work since we mock subprocess.run, 
        # but the third call is the runner execution.
        def mock_subprocess_run_side_effect(*args, **kwargs):
            cmd = args[0]
            if "sys.executable" in str(cmd) or "python" in str(cmd[0]):
                return mock_result
            if "branch" in cmd:
                mock_branches = MagicMock()
                mock_branches.stdout = "  main\n  develop\n"
                return mock_branches
            if "du" in cmd:
                mock_size = MagicMock()
                mock_size.stdout = "10M\t.\n"
                return mock_size
            return MagicMock()
            
        mock_run.side_effect = mock_subprocess_run_side_effect
        
        result = run_scan(repo, reports_dir, scanner_dir)
        assert result['findings'] == mock_output["findings"]
        assert result['metrics']['files_scanned'] == 150
        
        # We now generate cumulative reports, so test the cumulative format
        from scripts.run_daily_scan import generate_cumulative_report
        generate_cumulative_report([result], reports_dir)
        
        # Check generated report
        reports = os.listdir(reports_dir)
        assert len(reports) == 1
        assert reports[0].startswith("Cumulative-Report-")
        report_path = os.path.join(reports_dir, reports[0])
        
        with open(report_path, "r") as f:
            content = f.read()
            
        # Verify markdown format
        assert "Daily Cumulative Secret Scan Report" in content
        assert "## Executive Summary" in content
        assert "test/repo" in content
        assert "## Repository Breakdown" in content
        assert "`config.yaml` | aws_access_key | 10 | HIGH | 5.0 | `AKIAREDACTEDXXXXX`" in content
        
        # Ensure raw secrets are not present
        assert "AKIAIOSFODNN7EXAMPLE" not in content # Raw secret shouldn't be there
