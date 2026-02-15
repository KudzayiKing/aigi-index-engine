from .mock_data import get_mock_all_data

def fetch_github_stats():
    """
    Fetch GitHub statistics (stars, forks, commits) for models.
    For now, returns mock data.
    """
    data = get_mock_all_data()
    return data["github"]