import subprocess
from unittest.mock import patch, MagicMock
import tempfile
from scripts.run_daily_scan import run_scan

@patch("scripts.run_daily_scan.subprocess.run")
def test_run_scan_timeout(mock_run):
    repo = {"name": "test/timeout", "url": "https://github.com/test/timeout"}

    def mock_subprocess_run_side_effect(*args, **kwargs):
        cmd = args[0]
        if "python" in str(cmd[0]) or "runner.py" in str(cmd):
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=1800)
        return MagicMock(stdout="", returncode=0)

    mock_run.side_effect = mock_subprocess_run_side_effect

    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_scan(repo, tmpdir)
        print(result)
        assert result["metrics"]["scan_duration"] == 1800

test_run_scan_timeout()
