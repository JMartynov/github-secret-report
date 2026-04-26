import pytest
import subprocess
from unittest.mock import patch, MagicMock
import sys

from scripts.run_daily_scan import RUNNER_CODE_TEMPLATE

# We extract get_commits dynamically from the runner template
namespace = {}

# Mock the 'src' module imports since we only want to test get_commits
sys.modules['src'] = MagicMock()
sys.modules['src.detector'] = MagicMock()
sys.modules['src.obfuscator'] = MagicMock()

exec(RUNNER_CODE_TEMPLATE, namespace)

get_commits = namespace['get_commits']

@patch("subprocess.run")
def test_get_commits_success(mock_run):
    mock_result = MagicMock()
    # Format matches: "%H|%an|%cI"
    mock_result.stdout = "abc1234|Alice|2023-10-25T10:00:00Z\ndef5678|Bob|2023-10-26T11:00:00Z\n"
    mock_run.return_value = mock_result

    commits = get_commits("/tmp/target_repo")

    # Assert subprocess.run was called correctly
    mock_run.assert_called_once_with(
        ["git", "-C", "/tmp/target_repo", "log", "--all", "--format=%H|%an|%cI"],
        capture_output=True, text=True, check=True
    )

    # Assert commits were parsed correctly
    assert len(commits) == 2
    assert commits[0]["hash"] == "abc1234"
    assert commits[0]["author"] == "Alice"
    assert commits[0]["date"] == "2023-10-25T10:00:00Z"

    assert commits[1]["hash"] == "def5678"
    assert commits[1]["author"] == "Bob"
    assert commits[1]["date"] == "2023-10-26T11:00:00Z"

@patch("subprocess.run")
def test_get_commits_invalid_format(mock_run):
    mock_result = MagicMock()
    # Missing fields
    mock_result.stdout = "abc1234|Alice\ndef5678\n"
    mock_run.return_value = mock_result

    commits = get_commits("/tmp/target_repo")

    # Invalid format lines should be skipped
    assert len(commits) == 0

@patch("subprocess.run")
def test_get_commits_empty_output(mock_run):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result

    commits = get_commits("/tmp/target_repo")

    # Empty output should result in empty list
    assert len(commits) == 0

@patch("subprocess.run")
def test_get_commits_exception(mock_run):
    # Simulate a subprocess error (e.g., git repo doesn't exist)
    mock_run.side_effect = subprocess.SubprocessError("Git command failed")

    commits = get_commits("/tmp/target_repo")

    # Exception should be caught and return empty list
    assert len(commits) == 0
