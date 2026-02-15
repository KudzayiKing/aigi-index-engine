import requests
import pandas as pd
import json
import time
from ..config import HUGGINGFACE_TOKEN, RATE_LIMIT

def fetch_hf_downloads():
    """
    Fetch real Hugging Face download statistics for models.
    Uses your Hugging Face token for higher rate limits.
    """
    with open('app/models_registry.json', 'r') as f:
        registry = json.load(f)
    
    headers = {}
    if HUGGINGFACE_TOKEN and HUGGINGFACE_TOKEN != "your_huggingface_token_here":
        headers['Authorization'] = f'Bearer {HUGGINGFACE_TOKEN}'
        print("🤗 Using authenticated Hugging Face API")
    else:
        print("⚠️ No Hugging Face token - using unauthenticated (limited)")
    
    data = []
    for model in registry:
        hf_repo = model.get('hf_repo')
        model_name = model['name']
        
        if hf_repo and hf_repo != "None" and hf_repo is not None:
            downloads = fetch_repo_downloads(hf_repo, headers)
            data.append({
                'model': model_name,
                'downloads': downloads
            })
        else:
            # No HF repo for this model
            data.append({
                'model': model_name,
                'downloads': 0
            })
        
        # Rate limiting
        time.sleep(1.0 / RATE_LIMIT)
    
    return pd.DataFrame(data)

def fetch_repo_downloads(repo_id: str, headers: dict) -> int:
    """
    Fetch download count for a Hugging Face model.
    """
    try:
        # Hugging Face API endpoint
        url = f"https://huggingface.co/api/models/{repo_id}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Total downloads across all versions
            downloads = data.get('downloads', 0)
            if downloads > 0:
                print(f"  ✅ {repo_id}: {downloads:,} downloads")
            return downloads
        elif response.status_code == 401:
            print(f"  ⚠️ Authentication failed for {repo_id} - check token")
            return 0
        elif response.status_code == 404:
            print(f"  ⚠️ Repo not found: {repo_id}")
            return 0
        else:
            print(f"  ⚠️ Got status {response.status_code} for {repo_id}")
            return 0
            
    except Exception as e:
        print(f"  Error fetching {repo_id}: {e}")
        return 0

def fetch_trending_downloads(limit: int = 30):
    """
    Alternative: Fetch trending models as a backup.
    """
    try:
        url = "https://huggingface.co/api/trending"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            models = []
            downloads = []
            
            for item in data.get('trending', [])[:limit]:
                models.append(item['repoId'])
                downloads.append(item.get('downloads', 0))
            
            return pd.DataFrame({
                'model': models,
                'downloads': downloads
            })
    except Exception as e:
        print(f"Error fetching trending: {e}")
        return pd.DataFrame(columns=['model', 'downloads'])
