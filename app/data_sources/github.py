import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from ..config import GITHUB_TOKEN

# Then in fetch_repo_stats function, add the token to headers:
headers = {}
if GITHUB_TOKEN:
    headers['Authorization'] = f'token {GITHUB_TOKEN}'


def fetch_github_stats():
    """
    Fetch GitHub statistics for models with GitHub repos.
    """
    with open('app/models_registry.json', 'r') as f:
        registry = json.load(f)
    
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    } if GITHUB_TOKEN != "your_github_token_here" else {}
    
    data = []
    for model in registry:
        github_repo = model.get('github_repo')
        if github_repo:
            stats = fetch_repo_stats(github_repo, headers)
            data.append({
                'model': model['name'],
                'github_growth': stats['growth_score'],
                'stars': stats['stars'],
                'forks': stats['forks'],
                'commits_30d': stats['commits_30d']
            })
            time.sleep(1)  # Rate limiting
    
    return pd.DataFrame(data)

def fetch_repo_stats(repo_full_name: str, headers: dict) -> dict:
    """
    Fetch comprehensive stats for a GitHub repo.
    """
    base_url = f"https://api.github.com/repos/{repo_full_name}"
    
    try:
        # Get basic repo info
        repo_response = requests.get(base_url, headers=headers, timeout=10)
        if repo_response.status_code != 200:
            return {'growth_score': 0, 'stars': 0, 'forks': 0, 'commits_30d': 0}
        
        repo_data = repo_response.json()
        stars = repo_data.get('stargazers_count', 0)
        forks = repo_data.get('forks_count', 0)
        
        # Get recent commit activity
        since = (datetime.now() - timedelta(days=30)).isoformat()
        commits_url = f"{base_url}/commits?since={since}&per_page=100"
        commits_response = requests.get(commits_url, headers=headers, timeout=10)
        
        commits_30d = len(commits_response.json()) if commits_response.status_code == 200 else 0
        
        # Calculate growth score (custom metric)
        # You can adjust this formula based on what matters
        growth_score = (stars * 0.5) + (forks * 0.3) + (commits_30d * 20)
        
        return {
            'growth_score': growth_score,
            'stars': stars,
            'forks': forks,
            'commits_30d': commits_30d
        }
        
    except Exception as e:
        print(f"Error fetching {repo_full_name}: {e}")
        return {'growth_score': 0, 'stars': 0, 'forks': 0, 'commits_30d': 0}

def fetch_github_trending():
    """
    Alternative: Fetch trending repositories.
    """
    try:
        url = "https://api.github.com/search/repositories"
        params = {
            'q': 'language:python OR language:jupyter-notebook topic:ai topic:machine-learning',
            'sort': 'stars',
            'order': 'desc',
            'per_page': 10
        }
        
        headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN != "your_github_token_here" else {}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            models = []
            growth = []
            
            for item in data.get('items', []):
                models.append(item['full_name'])
                # Calculate growth score
                growth.append(
                    item['stargazers_count'] * 0.5 + 
                    item['forks_count'] * 0.3 +
                    item.get('open_issues_count', 0) * 0.2
                )
            
            return pd.DataFrame({
                'model': models,
                'github_growth': growth
            })
    except Exception as e:
        print(f"Error fetching trending: {e}")
        return pd.DataFrame(columns=['model', 'github_growth'])