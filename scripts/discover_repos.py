import json
import urllib.error
import os
import random
from utils.github_api import fetch_github_search_repos

def fetch_random_repos(count=20):
    # Fetch random repos using a keyword like "python", "js", or "api" 
    # to avoid empty or junk repos, sort by recent updates.
    keywords = ["api", "backend", "frontend", "cli", "web", "tool", "library"]
    keyword = random.choice(keywords)
    
    try:
        items = fetch_github_search_repos(query=keyword, sort="updated", per_page=100)
        # Pick a random subset of count
        if len(items) > count:
            items = random.sample(items, count)

        return [{"name": item["full_name"], "url": item["clone_url"], "status": "Hasn't yet validated"} for item in items]
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"Failed to fetch repos: {e}")
        return []

def main(repos_file="data/target_repos.json"):
    # Load existing repos
    if os.path.exists(repos_file):
        with open(repos_file, 'r') as f:
            existing_repos = json.load(f)
    else:
        existing_repos = []

    existing_urls = {repo["url"] for repo in existing_repos}

    print(f"Discovering 20 new repositories...")
    new_repos = fetch_random_repos(20)

    added_count = 0
    for repo in new_repos:
        if repo["url"] not in existing_urls:
            existing_repos.append(repo)
            existing_urls.add(repo["url"])
            added_count += 1

    if added_count > 0:
        os.makedirs(os.path.dirname(repos_file), exist_ok=True)
        with open(repos_file, 'w') as f:
            json.dump(existing_repos, f, indent=4)
        print(f"Added {added_count} new unique repositories to {repos_file}")
    else:
        print("No new unique repositories found.")

if __name__ == "__main__":
    main()