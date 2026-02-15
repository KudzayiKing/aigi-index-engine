import requests
import pandas as pd
import time
import pickle
import io
import os
import json
from datetime import datetime, timedelta

def fetch_arena_scores_internal():
    """
    Internal function to fetch the latest Elo scores from LMArena PKL files.
    """
    try:
        # Try to get the latest PKL file
        return fetch_from_lmarena_pkl()
    except Exception as e:
        print(f"Error fetching from LMArena PKL: {e}")
        try:
            # Fallback to older method
            return fetch_from_lmarena_webpage()
        except Exception as e:
            print(f"Error fetching from webpage: {e}")
            return pd.DataFrame(columns=['model', 'elo'])

def fetch_from_lmarena_pkl():
    """
    Fetch the latest Elo results from the PKL files in the LMArena space.
    """
    # Base URL for raw files in the space
    base_url = "https://huggingface.co/spaces/lmarena-ai/lmarena-leaderboard/resolve/main"
    
    # List of recent PKL files (you can update this list periodically)
    pkl_files = [
        "elo_results_20240629.pkl",
        "elo_results_20240626.pkl",
        "elo_results_20240623.pkl",
        "elo_results_20240621.pkl",
        "elo_results_20240617.pkl",
        "elo_results_20240611.pkl",
        "elo_results_20240606.pkl",
        "elo_results_20240602.pkl",
        "elo_results_20240527.pkl",
        "elo_results_20240520.pkl",
        "elo_results_20240519.pkl",
        "elo_results_20240516.pkl",
        "elo_results_20240515.pkl",
    ]
    
    # Try each file from newest to oldest
    for pkl_file in pkl_files:
        url = f"{base_url}/{pkl_file}"
        try:
            print(f"  Trying PKL: {pkl_file}")
            
            # Download the PKL file
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Load the pickle data
                pkl_data = pickle.loads(response.content)
                
                # The PKL structure might vary - let's explore common patterns
                if isinstance(pkl_data, dict):
                    # Try to extract model names and Elo scores
                    if 'models' in pkl_data and 'elo' in pkl_data:
                        # Format: {'models': [...], 'elo': [...]}
                        df = pd.DataFrame({
                            'model': pkl_data['models'],
                            'elo': pkl_data['elo']
                        })
                        print(f"  ✅ Success! Found {len(df)} models")
                        return df
                    
                    elif 'results' in pkl_data:
                        # Try to parse results dictionary
                        results = pkl_data['results']
                        if isinstance(results, dict):
                            models = []
                            elos = []
                            for model, stats in results.items():
                                if isinstance(stats, dict) and 'elo' in stats:
                                    models.append(model)
                                    elos.append(stats['elo'])
                            
                            if models:
                                df = pd.DataFrame({'model': models, 'elo': elos})
                                print(f"  ✅ Success! Found {len(df)} models")
                                return df
                
                elif isinstance(pkl_data, list):
                    # Try to parse as list of dictionaries
                    models = []
                    elos = []
                    for item in pkl_data:
                        if isinstance(item, dict):
                            # Look for model name and elo in each dict
                            model = item.get('model') or item.get('name') or item.get('Model')
                            elo = item.get('elo') or item.get('Elo') or item.get('rating')
                            if model and elo:
                                models.append(model)
                                elos.append(elo)
                    
                    if models:
                        df = pd.DataFrame({'model': models, 'elo': elos})
                        print(f"  ✅ Success! Found {len(df)} models")
                        return df
                
                # If we couldn't parse but got data, let's see what we have
                print(f"  ⚠️ Unknown PKL structure, trying to convert...")
                # Try to convert to DataFrame directly
                df = pd.DataFrame(pkl_data)
                if len(df.columns) >= 2:
                    # Use first two columns
                    df = df.iloc[:, [0, 1]].rename(
                        columns={df.columns[0]: 'model', df.columns[1]: 'elo'}
                    )
                    print(f"  ✅ Success! Found {len(df)} models")
                    return df
                    
        except Exception as e:
            print(f"  ❌ Failed to load {pkl_file}: {e}")
            continue
    
    # If all PKL files fail, try the CSV fallback
    return fetch_from_csv_fallback()

def fetch_from_csv_fallback():
    """
    Fallback: Try to fetch from CSV if available.
    """
    csv_url = "https://huggingface.co/spaces/lmarena-ai/lmarena-leaderboard/raw/main/arena_hard_auto_leaderboard_v0.1.csv"
    try:
        print(f"  Trying CSV fallback...")
        df = pd.read_csv(csv_url)
        
        # Try to identify model and score columns
        for col in df.columns:
            if 'model' in col.lower() or 'name' in col.lower():
                model_col = col
            if 'score' in col.lower() or 'elo' in col.lower() or 'rating' in col.lower():
                score_col = col
        
        if 'model_col' in locals() and 'score_col' in locals():
            result = df[[model_col, score_col]].rename(
                columns={model_col: 'model', score_col: 'elo'}
            )
            print(f"  ✅ Found {len(result)} models in CSV")
            return result
    except:
        pass
    
    raise Exception("All data sources failed")

def fetch_from_lmarena_webpage():
    """
    Last resort: Try to scrape the webpage.
    """
    url = "https://huggingface.co/spaces/lmarena-ai/lmarena-leaderboard"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # The actual data is likely loaded via JavaScript, so scraping may not work
        # This is a placeholder for completeness
        pass
    except:
        pass
    
    raise Exception("Webpage scraping not implemented - PKL files are the primary source")

def fetch_arena_scores():
    """
    Public function with caching.
    """
    cache_file = "cache/arena_scores.json"
    os.makedirs("cache", exist_ok=True)
    
    # Check cache (6 hours)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cache = json.load(f)
            cache_time = datetime.fromisoformat(cache['timestamp'])
            if datetime.now() - cache_time < timedelta(hours=6):
                print("📦 Using cached arena scores")
                return pd.DataFrame(cache['data'])
        except Exception as e:
            print(f"Cache read failed: {e}")
    
    # Fetch fresh data
    print("🌐 Fetching fresh arena scores from LMArena PKL files...")
    df = fetch_arena_scores_internal()
    
    # Save to cache if we got data
    if not df.empty:
        try:
            cache = {
                'timestamp': datetime.now().isoformat(),
                'data': df.to_dict('records')
            }
            with open(cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
            print(f"💾 Cached {len(df)} model scores")
        except Exception as e:
            print(f"Cache write failed: {e}")
    
    return df
