#!/usr/bin/env python3
"""
Get the latest AIGI snapshot for oracle consumption.
Returns the raw GitHub URL and IPFS CID if available.
"""

import os
import json
from pathlib import Path

def get_latest_snapshot():
    """Get the latest snapshot file and its metadata."""
    epochs_dir = Path("epochs")
    
    if not epochs_dir.exists():
        return {"error": "epochs directory not found"}
    
    # Get all JSON files sorted by modification time
    json_files = sorted(epochs_dir.glob("*.json"), key=os.path.getmtime, reverse=True)
    
    if not json_files:
        return {"error": "No snapshot files found"}
    
    latest_file = json_files[0]
    
    # Read the snapshot
    with open(latest_file, 'r') as f:
        snapshot_data = json.load(f)
    
    # Generate URLs
    repo = "KudzayiKing/aigi-index-engine"
    branch = "main"
    raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{latest_file}"
    
    return {
        "filename": latest_file.name,
        "path": str(latest_file),
        "raw_url": raw_url,
        "epoch_id": snapshot_data.get("epoch_id"),
        "timestamp": snapshot_data.get("timestamp"),
        "cis": snapshot_data.get("cis"),
        "models_count": len(snapshot_data.get("models", [])),
        "engine_version": snapshot_data.get("engine_version")
    }

if __name__ == "__main__":
    result = get_latest_snapshot()
    print(json.dumps(result, indent=2))
