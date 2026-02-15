import pandas as pd

def min_max_normalize(series: pd.Series) -> pd.Series:
    """Normalize series to [0,1] using min-max."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(0, index=series.index)
    return (series - min_val) / (max_val - min_val)

def z_score_normalize(series: pd.Series) -> pd.Series:
    """Normalize using z-score."""
    mean = series.mean()
    std = series.std()
    if std == 0:
        return pd.Series(0, index=series.index)
    return (series - mean) / std

# Choose your preferred method
normalize = min_max_normalize