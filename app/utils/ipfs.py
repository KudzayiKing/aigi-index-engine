import os
import subprocess
import json

def upload_to_ipfs(filepath: str) -> str:
    """
    Upload a file to IPFS using either ipfshttpclient or command line.
    Returns IPFS hash (CID).
    For testing, you can mock this or skip.
    """
    try:
        # Try using ipfshttpclient
        import ipfshttpclient
        client = ipfshttpclient.connect()
        res = client.add(filepath)
        return res["Hash"]
    except ImportError:
        # Fallback to command line
        result = subprocess.run(["ipfs", "add", "-Q", filepath], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print("IPFS upload failed. Install ipfs or ipfshttpclient.")
            return "QmMockHash"  # placeholder for testing