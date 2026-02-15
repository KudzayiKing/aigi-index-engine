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
    For v1, we use mock data. Replace with real API calls later.
    """
    mock = get_mock_all_data()
    # Current data
    current = {
        "arena": mock["arena"],
        "mmlu": mock["mmlu"],
        "gsm8k": mock["gsm8k"],
        "humaneval": mock["humaneval"],
        "multimodal": mock["multimodal"],
        "robustness": mock["robustness"],
        "downloads": mock["downloads"],
        "github": mock["github"],
        "citations": mock["citations"],
        "release": mock["release"],
    }
    # Previous data (for momentum)
    previous = {
        "arena": mock["prev_elo"].rename(columns={"elo": "elo"}),
        "mmlu": mock["prev_mmlu"].rename(columns={"mmlu": "mmlu"}),
        "gsm8k": mock["prev_gsm8k"].rename(columns={"gsm8k": "gsm8k"}),
        "humaneval": mock["prev_humaneval"].rename(columns={"humaneval": "humaneval"}),
        # For benchmark delta, we need a composite previous benchmark score
        # We'll compute it later from these.
        "downloads": mock["prev_downloads"].rename(columns={"downloads": "downloads"}),
        "citations": mock["prev_citations"].rename(columns={"citation_velocity": "citation_velocity"}),
    }
    return current, previous

def merge_dataframes(registry, current, previous):
    """
    Debug version to see what columns are being created.
    """
    df = pd.DataFrame(registry)
    print("Step 0 - Registry columns:", df.columns.tolist())
    print("Step 0 - Registry data:\n", df)
    
    # Merge current metrics one by one
    metrics = ["arena", "mmlu", "gsm8k", "humaneval", "multimodal", "robustness",
               "downloads", "github", "citations", "release"]
    
    for metric in metrics:
        if metric in current:
            curr_df = current[metric]
            print(f"\nStep 1 - Merging {metric}")
            print(f"Current {metric} df:\n", curr_df)
            
            # Rename the value column to the metric name
            value_cols = [col for col in curr_df.columns if col != 'model']
            if len(value_cols) == 1:
                curr_df = curr_df.rename(columns={value_cols[0]: metric})
            
            df = df.merge(curr_df, left_on="name", right_on="model", how="left")
            print(f"After merge, columns: {df.columns.tolist()}")
            
            # Drop duplicate model column if it exists
            if 'model' in df.columns:
                df = df.drop(columns=['model'])
                print(f"Dropped 'model' column, now: {df.columns.tolist()}")
    
    print("\nStep 2 - After all current merges, columns:", df.columns.tolist())
    
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
            prev_df = previous[metric]
            print(f"\nStep 3 - Merging previous {metric}")
            print(f"Previous {metric} df:\n", prev_df)
            
            # Rename the value column to prev_{metric}
            value_cols = [col for col in prev_df.columns if col != 'model']
            if len(value_cols) == 1:
                prev_df = prev_df.rename(columns={value_cols[0]: f"prev_{metric}"})
            
            df = df.merge(prev_df, left_on="name", right_on="model", how="left")
            print(f"After prev merge, columns: {df.columns.tolist()}")
            
            if 'model' in df.columns:
                df = df.drop(columns=['model'])
                print(f"Dropped 'model' column, now: {df.columns.tolist()}")
    
    print("\nStep 4 - Final columns before delta computation:", df.columns.tolist())
    print("Step 4 - Data types:\n", df.dtypes)
    
    # Now compute deltas (check if columns exist first)
    if 'arena' in df.columns and 'prev_arena' in df.columns:
        df["elo_delta"] = df["arena"] - df["prev_arena"]
        print("✓ Created elo_delta")
    else:
        print("✗ Missing 'arena' or 'prev_arena' columns")
        if 'arena' not in df.columns:
            print("  - 'arena' column missing")
        if 'prev_arena' not in df.columns:
            print("  - 'prev_arena' column missing")
    
    # Compute benchmark and its delta
    if all(col in df.columns for col in ['mmlu', 'gsm8k', 'humaneval']):
        df["benchmark"] = (df["mmlu"] + df["gsm8k"] + df["humaneval"]) / 3
        print("✓ Created benchmark")
    else:
        print("✗ Missing benchmark component columns")
    
    if all(col in df.columns for col in ['prev_mmlu', 'prev_gsm8k', 'prev_humaneval']):
        df["prev_benchmark"] = (df["prev_mmlu"] + df["prev_gsm8k"] + df["prev_humaneval"]) / 3
        print("✓ Created prev_benchmark")
    
    if 'benchmark' in df.columns and 'prev_benchmark' in df.columns:
        df["benchmark_delta"] = df["benchmark"] - df["prev_benchmark"]
        print("✓ Created benchmark_delta")
    
    if 'downloads' in df.columns and 'prev_downloads' in df.columns:
        df["download_growth"] = df["downloads"] - df["prev_downloads"]
        print("✓ Created download_growth")
    
    if 'citations' in df.columns and 'prev_citations' in df.columns:
        df["citation_growth"] = df["citations"] - df["prev_citations"]
        print("✓ Created citation_growth")
    
    print("\nStep 5 - Final dataframe shape:", df.shape)
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
    # Normalize all metrics
    df = normalize_all(df)
    print("Normalization complete.")
    
    # DEBUG: Print available normalized columns
    norm_cols = [col for col in df.columns if '_norm' in col]
    print("Available normalized columns:", norm_cols)   
    
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