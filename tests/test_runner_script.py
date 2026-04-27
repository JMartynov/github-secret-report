import pytest
from unittest.mock import patch, MagicMock
import subprocess
import json
from scripts.run_daily_scan import RUNNER_CODE_TEMPLATE

def load_runner_functions():
    """
    Extracts functions from RUNNER_CODE_TEMPLATE for testing.
    Mocks necessary imports to avoid ModuleNotFoundError.
    """
    namespace = {}
    # Mocking the imports and classes that might fail if dependencies are not installed
    namespace['SecretDetector'] = MagicMock()
    namespace['Obfuscator'] = MagicMock()

    code = RUNNER_CODE_TEMPLATE
    # Remove imports that would fail in the test environment
    lines = code.split('\n')
    filtered_lines = [
        line for line in lines
        if not line.strip().startswith("from src.detector")
        and not line.strip().startswith("from src.obfuscator")
    ]
    code = '\n'.join(filtered_lines)

    exec(code, namespace)
    return namespace

# Load functions once for the module
funcs = load_runner_functions()
get_file_content = funcs['get_file_content']
get_commits = funcs['get_commits']


@patch("subprocess.run")
def test_get_file_content_success(mock_run):
    """Test successful file content retrieval."""
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "file content"
    mock_run.return_value = mock_proc

    content = get_file_content("repo_dir", "abc1234", "README.md")

    assert content == "file content"
    mock_run.assert_called_once_with(
        ["git", "-C", "repo_dir", "show", "abc1234:README.md", "--"],
        capture_output=True, text=True, errors="ignore", timeout=30
    )

@patch("subprocess.run")
def test_get_file_content_failure(mock_run):
    """Test failure when git show returns non-zero code."""
    mock_proc = MagicMock()
    mock_proc.returncode = 1
    mock_proc.stdout = ""
    mock_run.return_value = mock_proc

    content = get_file_content("repo_dir", "abc1234", "nonexistent.txt")

    assert content is None

@patch("subprocess.run")
def test_get_file_content_exception(mock_run):
    """Test handling of exceptions during subprocess execution."""
    mock_run.side_effect = subprocess.SubprocessError("Subprocess error")

    content = get_file_content("repo_dir", "abc1234", "README.md")

    assert content is None

@patch("subprocess.Popen")
def test_get_commits_success(mock_popen):
    """Test successful retrieval of commits."""
    mock_proc = MagicMock()
    mock_proc.stdout = ["COMMIT|h1|a1|d1\n", "\n", "COMMIT|h2|a2|d2\n"]
    mock_proc.returncode = 0
    mock_popen.return_value = mock_proc

    commits = get_commits("repo_dir")

    assert len(commits) == 2
    assert commits[0] == {"hash": "h1", "author": "a1", "date": "d1", "files": []}
    assert commits[1] == {"hash": "h2", "author": "a2", "date": "d2", "files": []}

@patch("subprocess.run")
def test_get_commits_exception(mock_run):
    """Test handling of exceptions in get_commits."""
    mock_run.side_effect = Exception("Git error")
    commits = get_commits("repo_dir")
    assert commits == []


