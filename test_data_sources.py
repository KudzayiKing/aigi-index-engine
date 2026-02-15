#!/usr/bin/env python3
"""
Test each data source individually.
"""

from app.data_sources import (
    fetch_arena_scores,
    fetch_hf_downloads,
    fetch_github_stats,
    fetch_citations
)

def test_source(name, func):
    print(f"\n📡 Testing {name}...")
    try:
        df = func()
        print(f"✅ Success! Shape: {df.shape}")
        print(df.head())
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing data sources...")
    
    tests = [
        ("LMSYS Arena", fetch_arena_scores),
        ("Hugging Face", fetch_hf_downloads),
        ("GitHub Stats", fetch_github_stats),
        ("Citations", fetch_citations),
    ]
    
    results = []
    for name, func in tests:
        results.append(test_source(name, func))
    
    print(f"\n📊 Summary: {sum(results)}/{len(results)} passed")