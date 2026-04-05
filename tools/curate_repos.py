import json
import urllib.request
import os

def fetch_top_repos(language, count=100):
    url = f"https://api.github.com/search/repositories?q=language:{language}&sort=stars&order=desc&per_page={count}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return [{"name": item["full_name"], "url": item["clone_url"]} for item in data.get("items", [])]
    except Exception as e:
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