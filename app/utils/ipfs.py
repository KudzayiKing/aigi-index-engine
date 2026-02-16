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
        try:
            result = subprocess.run(["ipfs", "add", "-Q", filepath], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print("⚠️ IPFS upload failed (command returned non-zero exit code).")
                return "QmMockHash_IPFS_Failed"
        except FileNotFoundError:
            print("⚠️ IPFS CLI not found. Skipping upload.")
            return "QmMockHash_IPFS_Not_Found"
        except Exception as e:
            print(f"⚠️ IPFS upload error: {e}")
            return "QmMockHash_Error"