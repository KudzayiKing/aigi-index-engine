import requests
import pandas as pd
import json
import time
from bs4 import BeautifulSoup
import re
from ..config import RATE_LIMIT

def fetch_all_benchmarks():
    """
    Fetch real benchmark data from various sources.
    Returns separate dataframes for MMLU, GSM8K, and HumanEval.
    """
    mmlu_df = fetch_mmlu_scores()
    gsm8k_df = fetch_gsm8k_scores()
    humaneval_df = fetch_humaneval_scores()
    
    return {
        'mmlu': mmlu_df,
        'gsm8k': gsm8k_df,
        'humaneval': humaneval_df
    }

def fetch_mmlu_scores():
    """
    Fetch MMLU (Massive Multitask Language Understanding) scores.
    Source: Papers with Code
    """
    try:
        url = "https://paperswithcode.com/sota/multi-task-language-understanding-on-mmlu"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table
        table = soup.find('table', {'class': 'table'})
        if not table:
            return pd.DataFrame(columns=['model', 'mmlu'])
        
        rows = table.find_all('tr')[1:21]  # Top 20 models
        
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                model_name = cols[1].text.strip()
                # Extract model name (simplify)
                model_name = re.sub(r'\s+', ' ', model_name).strip()
                
                # Get MMLU score
                score_text = cols[2].text.strip()
                score_match = re.search(r'(\d+\.?\d*)', score_text)
                if score_match:
                    score = float(score_match.group(1))
                    data.append({'model': model_name, 'mmlu': score})
        
        print(f"  ✅ Fetched {len(data)} MMLU scores")
        return pd.DataFrame(data)
        
    except Exception as e:
        print(f"Error fetching MMLU: {e}")
        return pd.DataFrame(columns=['model', 'mmlu'])

def fetch_gsm8k_scores():
    """
    Fetch GSM8K (math reasoning) scores.
    """
    try:
        url = "https://paperswithcode.com/sota/arithmetic-reasoning-on-gsm8k"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', {'class': 'table'})
        if not table:
            return pd.DataFrame(columns=['model', 'gsm8k'])
        
        rows = table.find_all('tr')[1:21]
        
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                model_name = cols[1].text.strip()
                model_name = re.sub(r'\s+', ' ', model_name).strip()
                
                score_text = cols[2].text.strip()
                score_match = re.search(r'(\d+\.?\d*)', score_text)
                if score_match:
                    score = float(score_match.group(1))
                    data.append({'model': model_name, 'gsm8k': score})
        
        print(f"  ✅ Fetched {len(data)} GSM8K scores")
        return pd.DataFrame(data)
        
    except Exception as e:
        print(f"Error fetching GSM8K: {e}")
        return pd.DataFrame(columns=['model', 'gsm8k'])

def fetch_humaneval_scores():
    """
    Fetch HumanEval (code generation) scores.
    """
    try:
        url = "https://paperswithcode.com/sota/code-generation-on-humaneval"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', {'class': 'table'})
        if not table:
            return pd.DataFrame(columns=['model', 'humaneval'])
        
        rows = table.find_all('tr')[1:21]
        
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                model_name = cols[1].text.strip()
                model_name = re.sub(r'\s+', ' ', model_name).strip()
                
                score_text = cols[2].text.strip()
                score_match = re.search(r'(\d+\.?\d*)', score_text)
                if score_match:
                    score = float(score_match.group(1))
                    data.append({'model': model_name, 'humaneval': score})
        
        print(f"  ✅ Fetched {len(data)} HumanEval scores")
        return pd.DataFrame(data)
        
    except Exception as e:
        print(f"Error fetching HumanEval: {e}")
        return pd.DataFrame(columns=['model', 'humaneval'])
