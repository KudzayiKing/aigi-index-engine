import pandas as pd
from ..config import TIER_WEIGHTS, MODEL_SCORE_WEIGHTS

def compute_model_score(row: pd.Series) -> float:
    """Combine intelligence, adoption, momentum into a single model score."""
    score = 0
    # Check which scores exist and add them with their weights
    if 'intelligence_score' in row.index and pd.notna(row['intelligence_score']):
        score += MODEL_SCORE_WEIGHTS["intelligence"] * row["intelligence_score"]
    if 'adoption_score' in row.index and pd.notna(row['adoption_score']):
        score += MODEL_SCORE_WEIGHTS["adoption"] * row["adoption_score"]
    if 'momentum_score' in row.index and pd.notna(row['momentum_score']):
        score += MODEL_SCORE_WEIGHTS["momentum"] * row["momentum_score"]
    return score

def compute_cis(df: pd.DataFrame) -> float:
    """
    df must have columns: 'tier', 'model_score'.
    Returns Composite Intelligence Score.
    """
    cis = 0.0
    for tier, weight in TIER_WEIGHTS.items():
        tier_df = df[df["tier"] == tier]
        if len(tier_df) == 0:
            continue
        # Equal weight within tier
        equal_weight = weight / len(tier_df)
        cis += (tier_df["model_score"] * equal_weight).sum()
    return cis