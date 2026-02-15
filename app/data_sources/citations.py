from .mock_data import get_mock_all_data

def fetch_citations():
    """
    Fetch citation counts from academic sources.
    For now, returns mock data.
    """
    data = get_mock_all_data()
    return data["citations"]