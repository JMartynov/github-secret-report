import pytest
from unittest.mock import patch, MagicMock
from scripts.run_daily_scan import RUNNER_CODE_TEMPLATE

# We can execute the definitions in RUNNER_CODE_TEMPLATE and get them in our namespace
import sys
import os
from unittest.mock import MagicMock

# Mock src.detector and src.obfuscator to avoid ModuleNotFoundError
from unittest.mock import patch

namespace = {'__name__': 'test_module'}
with patch.dict('sys.modules', {
    'src': MagicMock(),
    'src.detector': MagicMock(),
    'src.obfuscator': MagicMock()
}):
    exec(RUNNER_CODE_TEMPLATE, namespace)
get_commit_files = namespace['get_commit_files']

@patch('subprocess.run')
def test_get_commit_files_success(mock_run):
    mock_result = MagicMock()
    mock_result.stdout = "A\tadded_file.txt\nM\tmodified_file.py\nD\tdeleted_file.md\n"
    mock_run.return_value = mock_result

    files = get_commit_files("fake_dir", "fake_hash")

    assert files == ["added_file.txt", "modified_file.py"]
    mock_run.assert_called_once_with(
        ["git", "-C", "fake_dir", "diff-tree", "--no-commit-id", "--name-status", "-r", "fake_hash", "--"],
        capture_output=True, text=True, check=True
    )

@patch('subprocess.run')
def test_get_commit_files_error(mock_run):
    mock_run.side_effect = Exception("git failed")

    files = get_commit_files("fake_dir", "fake_hash")

    assert files == []

@patch('subprocess.run')
def test_get_commit_files_empty_output(mock_run):
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_run.return_value = mock_result

    files = get_commit_files("fake_dir", "fake_hash")

    assert files == []

@patch('subprocess.run')
def test_get_commit_files_malformed_output(mock_run):
    mock_result = MagicMock()
    # No tab separation
    mock_result.stdout = "Aadded_file.txt\n"
    mock_run.return_value = mock_result

    files = get_commit_files("fake_dir", "fake_hash")

    assert files == []
