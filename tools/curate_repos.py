import json
import urllib.error
import os
from utils.github_api import fetch_github_search_repos

def fetch_top_repos(language, count=100):
    try:
        items = fetch_github_search_repos(query=f"language:{language}", sort="stars", per_page=count)
        return [{"name": item["full_name"], "url": item["clone_url"]} for item in items]
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"Failed to fetch repos for {language}: {e}")
        return []

def main():
    languages = ["python", "javascript", "go", "java", "ruby"]
    repos_per_lang = 100
    all_repos = []

    for lang in languages:
        print(f"Fetching top {repos_per_lang} repositories for {lang}...")
        repos = fetch_top_repos(lang, repos_per_lang)
        all_repos.extend(repos)

    os.makedirs("data", exist_ok=True)
    target_file = "data/target_repos.json"
    
    with open(target_file, "w") as f:
        json.dump(all_repos, f, indent=4)
        
    print(f"Saved {len(all_repos)} repositories to {target_file}")

if __name__ == "__main__":
    main()