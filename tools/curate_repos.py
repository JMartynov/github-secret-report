import json
import urllib.request
import urllib.error
import os
from concurrent.futures import ThreadPoolExecutor

def fetch_top_repos(language, count=100):
    url = f"https://api.github.com/search/repositories?q=language:{language}&sort=stars&order=desc&per_page={count}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return [{"name": item["full_name"], "url": item["clone_url"]} for item in data.get("items", [])]
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"Failed to fetch repos for {language}: {e}")
        return []

def main():
    languages = ["python", "javascript", "go", "java", "ruby"]
    repos_per_lang = 100
    all_repos = []

    print(f"Fetching top {repos_per_lang} repositories for {len(languages)} languages concurrently...")

    with ThreadPoolExecutor(max_workers=len(languages)) as executor:
        # Use executor.map to maintain the order of languages
        results = list(executor.map(lambda lang: fetch_top_repos(lang, repos_per_lang), languages))

    for repos in results:
        all_repos.extend(repos)

    os.makedirs("data", exist_ok=True)
    target_file = "data/target_repos.json"
    
    with open(target_file, "w") as f:
        json.dump(all_repos, f, indent=4)
        
    print(f"Saved {len(all_repos)} repositories to {target_file}")

if __name__ == "__main__":
    main()