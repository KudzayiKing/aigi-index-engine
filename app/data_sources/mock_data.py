import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_mock_all_data():
    """
    Returns a dictionary with mock dataframes for all sources.
    Each dataframe has a 'model' column matching registry names.
    """
    np.random.seed(42)  # deterministic for testing
    models = ["gpt-4", "claude-3-opus", "llama-3-70b", "mistral-large", "gemini-1.5-pro"]

    # Arena Elo
    arena_df = pd.DataFrame({
        "model": models,
        "elo": [1250, 1240, 1180, 1150, 1220]
    })

    # MMLU scores (0-100)
    mmlu_df = pd.DataFrame({
        "model": models,
        "mmlu": [86.4, 85.9, 82.1, 80.5, 84.0]
    })

    # GSM8K (0-100)
    gsm8k_df = pd.DataFrame({
        "model": models,
        "gsm8k": [92.0, 91.5, 88.0, 86.5, 90.0]
    })

    # HumanEval (0-100)
    humaneval_df = pd.DataFrame({
        "model": models,
        "humaneval": [85.0, 84.0, 80.0, 78.0, 83.0]
    })

    # Multimodal score (0-100, placeholder)
    multimodal_df = pd.DataFrame({
        "model": models,
        "multimodal": [75.0, 80.0, 70.0, 68.0, 82.0]
    })

    # Robustness score (0-100)
    robustness_df = pd.DataFrame({
        "model": models,
        "robustness": [88.0, 89.0, 85.0, 84.0, 87.0]
    })

    # Downloads (Hugging Face) - millions
    downloads_df = pd.DataFrame({
        "model": models,
        "downloads": [15.2, 10.5, 45.0, 22.0, 18.3]
    })

    # GitHub activity (stars, forks, commits - combined index)
    github_df = pd.DataFrame({
        "model": models,
        "github_growth": [1200, 800, 5000, 2300, 950]  # some metric
    })

    # Citations (Semantic Scholar)
    citations_df = pd.DataFrame({
        "model": models,
        "citation_velocity": [450, 380, 1200, 210, 670]
    })

    # Release frequency (number of updates in last 6 months)
    release_df = pd.DataFrame({
        "model": models,
        "release_frequency": [4, 3, 6, 5, 2]
    })

    # Previous epoch values for momentum (deltas)
    # We'll simulate a 5% increase across the board for simplicity
    prev_elo = [1190, 1180, 1120, 1090, 1160]
    prev_mmlu = [82.0, 81.5, 78.0, 76.0, 80.0]
    prev_gsm8k = [87.0, 86.5, 83.0, 81.5, 85.0]
    prev_humaneval = [80.0, 79.0, 75.0, 73.0, 78.0]
    prev_downloads = [14.0, 9.8, 42.0, 20.0, 17.0]
    prev_citations = [420, 350, 1100, 190, 620]

    # Combine into a dictionary
    mock_data = {
        "arena": arena_df,
        "mmlu": mmlu_df,
        "gsm8k": gsm8k_df,
        "humaneval": humaneval_df,
        "multimodal": multimodal_df,
        "robustness": robustness_df,
        "downloads": downloads_df,
        "github": github_df,
        "citations": citations_df,
        "release": release_df,
        # Previous values (for momentum)
        "prev_elo": pd.DataFrame({"model": models, "elo": prev_elo}),
        "prev_mmlu": pd.DataFrame({"model": models, "mmlu": prev_mmlu}),
        "prev_gsm8k": pd.DataFrame({"model": models, "gsm8k": prev_gsm8k}),
        "prev_humaneval": pd.DataFrame({"model": models, "humaneval": prev_humaneval}),
        "prev_downloads": pd.DataFrame({"model": models, "downloads": prev_downloads}),
        "prev_citations": pd.DataFrame({"model": models, "citation_velocity": prev_citations}),
    }
    return mock_data