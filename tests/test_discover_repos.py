import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from scripts.discover_repos import fetch_random_repos, main

@patch("scripts.discover_repos.urllib.request.urlopen")
def test_fetch_random_repos_success(mock_urlopen):
    # Mock the response from GitHub API
    mock_response = MagicMock()
    mock_data = {
        "items": [
            {"full_name": "user/repo1", "clone_url": "https://github.com/user/repo1.git"},
            {"full_name": "user/repo2", "clone_url": "https://github.com/user/repo2.git"},
            {"full_name": "user/repo3", "clone_url": "https://github.com/user/repo3.git"}
        ]
    }
    mock_response.read.return_value = json.dumps(mock_data).encode("utf-8")
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    repos = fetch_random_repos(count=2)
    
    # Since fetch_random_repos uses random.sample if count < items, 
    # and we requested 2 out of 3, we should get 2.
    assert len(repos) == 2
    for repo in repos:
        assert "name" in repo
        assert "url" in repo
        assert repo["status"] == "Hasn't yet validated"

@patch("scripts.discover_repos.urllib.request.urlopen")
def test_fetch_random_repos_failure(mock_urlopen):
    import urllib.error
    mock_urlopen.side_effect = urllib.error.URLError("API Error")
    repos = fetch_random_repos(count=20)
    assert repos == []

def test_main_logic_with_duplicates(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_repos_file = os.path.join(tmpdir, "data", "target_repos.json")
        os.makedirs(os.path.dirname(temp_repos_file), exist_ok=True)
        
        # Initial data
        initial_repos = [
            {"name": "existing/repo", "url": "https://github.com/existing/repo.git", "status": "validated"}
        ]
        with open(temp_repos_file, "w") as f:
            json.dump(initial_repos, f)

        # Mock fetch_random_repos to return one new repo (as duplicates are now handled in fetch_random_repos)
        mock_new_repos = [
            {"name": "new/repo", "url": "https://github.com/new/repo.git", "status": "Hasn't yet validated"}
        ]
        
        # Patch the fetch function
        monkeypatch.setattr("scripts.discover_repos.fetch_random_repos", lambda count=20, existing_urls=None, max_attempts=10: mock_new_repos)
        
        # Import main
        from scripts.discover_repos import main as discover_main
        
        # Run main with the temporary file path
        discover_main(repos_file=temp_repos_file)

        # Verify results
        with open(temp_repos_file, "r") as f:
            updated_repos = json.load(f)
            
        assert len(updated_repos) == 2
        urls = [r["url"] for r in updated_repos]
        assert "https://github.com/existing/repo.git" in urls
        assert "https://github.com/new/repo.git" in urls
        
        # Verify status of existing repo didn't change (if we wanted to check that)
        for r in updated_repos:
            if r["url"] == "https://github.com/existing/repo.git":
                assert r["status"] == "validated"
            if r["url"] == "https://github.com/new/repo.git":
                assert r["status"] == "Hasn't yet validated"
