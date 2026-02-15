from .mock_data import get_mock_all_data

def fetch_hf_downloads():
    """
    Fetch Hugging Face download statistics for models.
    For now, returns mock data.
    """
    data = get_mock_all_data()
    return data["downloads"]

def fetch_hf_metadata():
    """
    Fetch additional Hugging Face metadata if needed.
    """
    # Placeholder for future implementation
    pass