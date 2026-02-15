import pandas as pd
from ..config import MOMENTUM_WEIGHTS

def compute_momentum_score(df: pd.DataFrame) -> pd.Series:
    """
    Expects df with normalized columns for momentum metrics.
    """
    available_cols = df.columns.tolist()
    score = pd.Series(0, index=df.index)
    
    col_map = {
        'elo_delta_norm': 'elo_delta',
        'benchmark_delta_norm': 'benchmark_delta',
        'download_growth_norm': 'download_growth',
        'citation_growth_norm': 'citation_growth'
    }
    
    for col, weight_key in col_map.items():
        if col in available_cols:
            score += MOMENTUM_WEIGHTS[weight_key] * df[col]
    
    return score * 100