from .mock_data import get_mock_all_data

def fetch_arena_scores():
    """
    Fetch LMSYS Chatbot Arena Elo ratings.
    For now, returns mock data.
    """
    data = get_mock_all_data()
    return data["arena"]