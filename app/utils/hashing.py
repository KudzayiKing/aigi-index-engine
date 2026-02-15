import hashlib
import json

def hash_dataset(data) -> str:
    """Return SHA256 hex digest of a JSON-serializable object."""
    encoded = json.dumps(data, sort_keys=True, default=str).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()