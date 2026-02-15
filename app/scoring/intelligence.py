import pandas as pd
from ..config import INTELLIGENCE_WEIGHTS

def compute_intelligence_score(df: pd.DataFrame) -> pd.Series:
    """
    Expects df with normalized columns for intelligence metrics.
    """
    available_cols = df.columns.tolist()
    score = pd.Series(0, index=df.index)
    
    # Map of expected column names to weight keys
    col_map = {
        'arena_norm': 'arena',
        'mmlu_norm': 'mmlu',
        'gsm8k_norm': 'gsm8k',
        'humaneval_norm': 'humaneval',
        'multimodal_norm': 'multimodal',
        'robustness_norm': 'robustness'
    }
    
    for col, weight_key in col_map.items():
        if col in available_cols:
            score += INTELLIGENCE_WEIGHTS[weight_key] * df[col]
    
    return score * 100