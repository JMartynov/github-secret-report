import pytest
import json
import urllib.error
from unittest.mock import patch, MagicMock, mock_open

from tools.curate_repos import fetch_top_repos, main

@patch("urllib.request.urlopen")
def test_fetch_top_repos_success(mock_urlopen):
    # Mock the response from GitHub API
    mock_response = MagicMock()
    mock_data = {
        "items": [
            {"full_name": "user/repo1", "clone_url": "https://github.com/user/repo1.git"},
            {"full_name": "user/repo2", "clone_url": "https://github.com/user/repo2.git"}
        ]
    }
    mock_response.read.return_value = json.dumps(mock_data).encode("utf-8")
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    repos = fetch_top_repos("python", count=2)

    assert len(repos) == 2
    assert repos[0]["name"] == "user/repo1"
    assert repos[0]["url"] == "https://github.com/user/repo1.git"
    assert repos[1]["name"] == "user/repo2"
    assert repos[1]["url"] == "https://github.com/user/repo2.git"

@patch("urllib.request.urlopen")
def test_fetch_top_repos_url_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.URLError("API Error")

    repos = fetch_top_repos("python", count=2)

    assert repos == []

@patch("urllib.request.urlopen")
def test_fetch_top_repos_json_error(mock_urlopen):
    mock_response = MagicMock()
    # Invalid JSON
    mock_response.read.return_value = b"{invalid_json:"
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    repos = fetch_top_repos("python", count=2)

    assert repos == []

@patch("tools.curate_repos.fetch_top_repos")
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_main(mock_open_file, mock_makedirs, mock_fetch):
    # Setup mock to return a predictable list of repos for each language
    def mock_fetch_func(lang, count):
        return [{"name": f"user/{lang}_repo", "url": f"https://github.com/user/{lang}_repo.git"}]

    mock_fetch.side_effect = mock_fetch_func

    # Run the main function
    main()

    # Check that fetch_top_repos was called 5 times (for the 5 languages)
    assert mock_fetch.call_count == 5

    # Check that os.makedirs was called correctly
    mock_makedirs.assert_called_once_with("data", exist_ok=True)

    # Check that open was called correctly
    mock_open_file.assert_called_once_with("data/target_repos.json", "w")

    # Check that the file was written to
    # the json.dump method writes the serialized string to the file
    # we can gather all the written chunks to verify the content
    written_content = "".join(call.args[0] for call in mock_open_file().write.call_args_list)

    # Verify the written content is valid JSON and contains the expected data
    saved_repos = json.loads(written_content)
    assert len(saved_repos) == 5
    languages = ["python", "javascript", "go", "java", "ruby"]

    for i, lang in enumerate(languages):
        assert saved_repos[i]["name"] == f"user/{lang}_repo"
        assert saved_repos[i]["url"] == f"https://github.com/user/{lang}_repo.git"
