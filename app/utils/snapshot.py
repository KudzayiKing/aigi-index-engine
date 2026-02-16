import os
import json
from datetime import datetime
from ..config import SNAPSHOT_DIR

def save_snapshot(data, epoch_id: str, timestamp: str = None):
    """Save snapshot JSON to epochs/ folder."""
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Sanitize timestamp for use in filename (replace colons with hyphens)
    safe_timestamp = timestamp.replace(":", "-")

    filename = f"{epoch_id}_{safe_timestamp}.json"
    filepath = os.path.join(SNAPSHOT_DIR, filename)
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"Snapshot saved to {filepath}")
    return filepath