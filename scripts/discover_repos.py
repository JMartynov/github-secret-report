import json
import urllib.request
import urllib.error
import os
import random
import time
from scripts.dictionaries import generate_random_query

def fetch_random_repos(count=20, existing_urls=None, max_attempts=10):
    if existing_urls is None:
        existing_urls = set()

    found_repos = []
    attempts = 0
    
    while len(found_repos) < count and attempts < max_attempts:
        attempts += 1
        query = generate_random_query()
        sort_opt = random.choice(["stars", "updated", "forks", ""])
        sort_param = f"&sort={sort_opt}&order=desc" if sort_opt else ""

        url = f"https://api.github.com/search/repositories?q={query}{sort_param}&per_page=100"

        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                items = data.get("items", [])
                random.shuffle(items) # randomize order among top results

                for item in items:
                    clone_url = item["clone_url"]
                    if clone_url not in existing_urls:
                        found_repos.append({"name": item["full_name"], "url": clone_url, "status": "Hasn't yet validated"})
                        existing_urls.add(clone_url)
                        if len(found_repos) >= count:
                            break

            if len(found_repos) < count and attempts < max_attempts:
                # Sleep briefly to avoid aggressive rate limits when looping
                time.sleep(2)
                
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            print(f"Failed to fetch repos (attempt {attempts}): {e}")
            # Backoff on error
            time.sleep(5)

    return found_repos

def main(repos_file="data/target_repos.json"):
    # Load existing repos
    if os.path.exists(repos_file):
        with open(repos_file, 'r') as f:
            existing_repos = json.load(f)
    else:
        existing_repos = []

    existing_urls = {repo["url"] for repo in existing_repos}

    print(f"Discovering 20 new repositories...")
    new_repos = fetch_random_repos(count=20, existing_urls=existing_urls)

    if new_repos:
        existing_repos.extend(new_repos)
        os.makedirs(os.path.dirname(repos_file), exist_ok=True)
        with open(repos_file, 'w') as f:
            json.dump(existing_repos, f, indent=4)
        print(f"Added {len(new_repos)} new unique repositories to {repos_file}")
    else:
        print("No new unique repositories found.")

if __name__ == "__main__":
    main()