#!/usr/bin/env python3
"""
AIGI Index Engine - Layer 1
Computes Composite Intelligence Score from public data.
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import (
    EPOCH_ID, SNAPSHOT_TIMESTAMP, RAW_DATA_ARCHIVE_DIR,
    MODEL_SCORE_WEIGHTS
)
from app.data_sources import (
    fetch_arena_scores, fetch_hf_downloads, fetch_github_stats,
    fetch_citations, get_mock_all_data
)
from app.data_sources.benchmarks import fetch_all_benchmarks
from app.scoring.normalization import normalize
from app.scoring.intelligence import compute_intelligence_score
from app.scoring.adoption import compute_adoption_score
from app.scoring.momentum import compute_momentum_score
from app.scoring.cis import compute_model_score, compute_cis
from app.utils.hashing import hash_dataset
from app.utils.ipfs import upload_to_ipfs
from app.utils.snapshot import save_snapshot

def load_model_registry():
    with open("app/models_registry.json", "r") as f:
        return json.load(f)

def fetch_all_data():
    """
    Returns a dictionary with dataframes for current and previous metrics.
    Now uses real data sources!
    """
    print("🌐 Fetching real data from APIs...")
    
    # Fetch real data
    print("\n📊 Fetching LMArena scores...")
    arena_df = fetch_arena_scores()
    
    print("\n📚 Fetching benchmark data (MMLU, GSM8K, HumanEval)...")
    benchmarks = fetch_all_benchmarks()
    
    print("\n🤗 Fetching Hugging Face downloads...")
    downloads_df = fetch_hf_downloads()
    
    print("\n🐙 Fetching GitHub stats...")
    github_df = fetch_github_stats()
    
    print("\n📖 Fetching citation counts...")
    citations_df = fetch_citations()
    
    current = {
        "arena": arena_df,
        "mmlu": benchmarks['mmlu'],
        "gsm8k": benchmarks['gsm8k'],
        "humaneval": benchmarks['humaneval'],
        "downloads": downloads_df,
        "github": github_df,
        "citations": citations_df,
    }
    
    # For previous data, we'll use the same data (momentum will be zero)
    # In production, you'd load from previous epoch snapshot
    print("\n📦 Using current data for previous (momentum will be zero)")
    previous = {
        "arena": arena_df.copy(),
        "mmlu": benchmarks['mmlu'].copy(),
        "gsm8k": benchmarks['gsm8k'].copy(),
        "humaneval": benchmarks['humaneval'].copy(),
        "downloads": downloads_df.copy(),
        "citations": citations_df.copy(),
    }
    
    return current, previous

def merge_dataframes(registry, current, previous):
    """
    Merge registry with current and previous metrics.
    """
    df = pd.DataFrame(registry)
    print(f"Loaded {len(df)} models from registry")
    
    # Merge current metrics one by one
    metrics = ["arena", "mmlu", "gsm8k", "humaneval", "multimodal", "robustness",
               "downloads", "github", "citations", "release"]
    
    for metric in metrics:
        if metric in current:
            curr_df = current[metric].copy()
            
            # Ensure we only have model and value columns
            if len(curr_df.columns) > 2:
                print(f"  Warning: {metric} has {len(curr_df.columns)} columns, expected 2")
            
            # Rename the value column to the metric name
            value_cols = [col for col in curr_df.columns if col != 'model']
            if len(value_cols) == 1:
                curr_df = curr_df.rename(columns={value_cols[0]: metric})
            elif len(value_cols) > 1:
                # Take only the first value column
                curr_df = curr_df[['model', value_cols[0]]].rename(columns={value_cols[0]: metric})
            
            # Ensure the value column contains only scalars (not dicts/lists)
            if metric in curr_df.columns:
                # Convert any non-scalar values to None
                curr_df[metric] = curr_df[metric].apply(
                    lambda x: x if isinstance(x, (int, float, type(None))) or pd.isna(x) else None
                )
            
            df = df.merge(curr_df, left_on="name", right_on="model", how="left")
            
            # Drop duplicate model column if it exists
            if 'model' in df.columns:
                df = df.drop(columns=['model'])
    
    # For previous values
    prev_metrics = {
        "arena": "elo",
        "mmlu": "mmlu",
        "gsm8k": "gsm8k",
        "humaneval": "humaneval",
        "downloads": "downloads",
        "citations": "citation_velocity"
    }
    
    for metric, colname in prev_metrics.items():
        if metric in previous:
            prev_df = previous[metric].copy()
            
            # Rename the value column to prev_{metric}
            value_cols = [col for col in prev_df.columns if col != 'model']
            if len(value_cols) == 1:
                prev_df = prev_df.rename(columns={value_cols[0]: f"prev_{metric}"})
            elif len(value_cols) > 1:
                prev_df = prev_df[['model', value_cols[0]]].rename(columns={value_cols[0]: f"prev_{metric}"})
            
            # Ensure scalar values only
            prev_col = f"prev_{metric}"
            if prev_col in prev_df.columns:
                prev_df[prev_col] = prev_df[prev_col].apply(
                    lambda x: x if isinstance(x, (int, float, type(None))) or pd.isna(x) else None
                )
            
            df = df.merge(prev_df, left_on="name", right_on="model", how="left")
            
            if 'model' in df.columns:
                df = df.drop(columns=['model'])
    
    # Compute deltas
    if 'arena' in df.columns and 'prev_arena' in df.columns:
        df["elo_delta"] = df["arena"] - df["prev_arena"]
    
    # Compute benchmark and its delta
    if all(col in df.columns for col in ['mmlu', 'gsm8k', 'humaneval']):
        df["benchmark"] = (df["mmlu"] + df["gsm8k"] + df["humaneval"]) / 3
    
    if all(col in df.columns for col in ['prev_mmlu', 'prev_gsm8k', 'prev_humaneval']):
        df["prev_benchmark"] = (df["prev_mmlu"] + df["prev_gsm8k"] + df["prev_humaneval"]) / 3
    
    if 'benchmark' in df.columns and 'prev_benchmark' in df.columns:
        df["benchmark_delta"] = df["benchmark"] - df["prev_benchmark"]
    
    if 'downloads' in df.columns and 'prev_downloads' in df.columns:
        df["download_growth"] = df["downloads"] - df["prev_downloads"]
    
    if 'citations' in df.columns and 'prev_citations' in df.columns:
        df["citation_growth"] = df["citations"] - df["prev_citations"]
    
    print(f"Merged data: {df.shape[0]} rows, {df.shape[1]} columns")
    return df

def normalize_all(df):
    """Apply normalization to all metric columns."""
    metric_cols = ["arena", "mmlu", "gsm8k", "humaneval", "multimodal", "robustness",
                   "downloads", "github", "citations", "release",
                   "elo_delta", "benchmark_delta", "download_growth", "citation_growth"]
    for col in metric_cols:
        if col in df.columns:
            df[f"{col}_norm"] = normalize(df[col])
    return df   

def main():
    print("🚀 AIGI Index Engine - Layer 1")
    print(f"Epoch: {EPOCH_ID}")

    # Load model registry
    registry = load_model_registry()
    print(f"Loaded {len(registry)} models.")

    # Fetch data (mock)
    current, previous = fetch_all_data()

    # Merge into one dataframe
    df = merge_dataframes(registry, current, previous)
    print("Data merged.")

    # Normalize all metrics
    df = normalize_all(df)
    print("Normalization complete.")

    # Compute intelligence score per model
    df["intelligence_score"] = compute_intelligence_score(df)
    # Compute adoption score
    df["adoption_score"] = compute_adoption_score(df)
    # Compute momentum score
    df["momentum_score"] = compute_momentum_score(df)

    # Compute final model score (weighted combination)
    df["model_score"] = df.apply(compute_model_score, axis=1)

    # Compute CIS
    cis = compute_cis(df)
    print(f"\n📊 Composite Intelligence Score (CIS): {cis:.4f}")

    # Prepare output snapshot
    timestamp = SNAPSHOT_TIMESTAMP or datetime.utcnow().isoformat() + "Z"
    snapshot = {
        "epoch_id": EPOCH_ID,
        "timestamp": timestamp,
        "cis": cis,
        "models": df[["name", "tier", "intelligence_score", "adoption_score",
                      "momentum_score", "model_score"]].to_dict(orient="records"),
        "engine_version": "1.0.0",
    }

    # Save to file
    filepath = save_snapshot(snapshot, EPOCH_ID, timestamp)

    # Hash the snapshot
    snapshot_hash = hash_dataset(snapshot)
    print(f"Snapshot SHA256: {snapshot_hash}")

    # Upload to IPFS (optional)
    ipfs_hash = upload_to_ipfs(filepath)
    print(f"IPFS CID: {ipfs_hash}")

    print("\n✅ Epoch complete.")

if __name__ == "__main__":
    main()