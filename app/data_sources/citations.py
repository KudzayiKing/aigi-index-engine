import requests
import pandas as pd
import json
import time
from typing import Optional
from ..config import SEMANTIC_SCHOLAR_KEY, RATE_LIMIT

def fetch_citations():
    """
    Fetch real citation counts from Semantic Scholar.
    Uses your authenticated API key for higher rate limits.
    """
    with open('app/models_registry.json', 'r') as f:
        registry = json.load(f)
    
    headers = {}
    if SEMANTIC_SCHOLAR_KEY:
        headers['x-api-key'] = SEMANTIC_SCHOLAR_KEY
        print("📚 Using authenticated Semantic Scholar API (1 req/sec)")
    else:
        print("⚠️ No Semantic Scholar key - using unauthenticated (slower)")
    
    data = []
    for model in registry:
        paper_id = model.get('paper_id')
        model_name = model['name']
        
        if paper_id and paper_id.startswith('arxiv:'):
            arxiv_id = paper_id.replace('arxiv:', '')
            citations = fetch_arxiv_citations(arxiv_id, headers)
        else:
            # Try searching by model name
            citations = search_semantic_scholar(model_name, headers)
        
        data.append({
            'model': model_name,
            'citation_velocity': citations
        })
        
        # Rate limiting - 1 request per second as specified
        time.sleep(1.0 / RATE_LIMIT)
    
    return pd.DataFrame(data)

def fetch_arxiv_citations(arxiv_id: str, headers: dict = None) -> int:
    """
    Fetch citation count for an arXiv paper using Semantic Scholar.
    """
    if headers is None:
        headers = {}
    
    try:
        # Use the Graph API with citationCount field
        url = f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{arxiv_id}"
        params = {'fields': 'citationCount,title,year'}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            citations = data.get('citationCount', 0)
            title = data.get('title', 'Unknown')[:50]
            if citations > 0:
                print(f"  ✅ arXiv:{arxiv_id}: {citations} citations - {title}")
            return citations
        elif response.status_code == 403:
            print(f"  ⚠️ Access forbidden for {arxiv_id} - check API key")
            return 0
        elif response.status_code == 429:
            print(f"  ⚠️ Rate limited for {arxiv_id}")
            time.sleep(2)
            return 0
        else:
            print(f"  ⚠️ Got status {response.status_code} for {arxiv_id}")
            return 0
            
    except Exception as e:
        print(f"  Error fetching arXiv citations for {arxiv_id}: {e}")
        return 0

def search_semantic_scholar(query: str, headers: dict = None) -> int:
    """
    Search for a paper by name and get its citation count.
    """
    if headers is None:
        headers = {}
    
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            'query': query,
            'limit': 1,
            'fields': 'citationCount,title,year'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            papers = data.get('data', [])
            if papers:
                citations = papers[0].get('citationCount', 0)
                title = papers[0].get('title', 'Unknown')[:50]
                if citations > 0:
                    print(f"  ✅ '{query}': {citations} citations - {title}")
                return citations
        elif response.status_code == 403:
            print(f"  ⚠️ Access forbidden for search '{query}'")
        elif response.status_code == 429:
            print(f"  ⚠️ Rate limited on search")
            time.sleep(2)
        
        return 0
        
    except Exception as e:
        print(f"  Error searching for {query}: {e}")
        return 0
