import pandas as pd
from ..config import ADOPTION_WEIGHTS

def compute_adoption_score(df: pd.DataFrame) -> pd.Series:
    """
    Expects df with columns: downloads_norm, github_norm,
    citations_norm, release_norm.
    """
    # Check which columns actually exist
    available_cols = df.columns.tolist()
    
    # Initialize score as 0
    score = pd.Series(0, index=df.index)
    
    # Add each component if the column exists
    if 'downloads_norm' in available_cols:
        score += ADOPTION_WEIGHTS["downloads"] * df["downloads_norm"]
    
    if 'github_norm' in available_cols:
        score += ADOPTION_WEIGHTS["github_growth"] * df["github_norm"]
    
    # Note: citations column is 'citations_norm', not 'citation_norm'
    if 'citations_norm' in available_cols:
        score += ADOPTION_WEIGHTS["citation_velocity"] * df["citations_norm"]
    
    if 'release_norm' in available_cols:
        score += ADOPTION_WEIGHTS["release_frequency"] * df["release_norm"]
    
    return score * 100