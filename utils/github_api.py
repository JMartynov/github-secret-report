import json
import urllib.request
import urllib.error

def fetch_github_search_repos(query, sort, order="desc", per_page=100):
    """
    Fetches repositories from GitHub search API.
    Raises urllib.error.URLError or json.JSONDecodeError on failure.
    """
    url = f"https://api.github.com/search/repositories?q={query}&sort={sort}&order={order}&per_page={per_page}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        return data.get("items", [])
