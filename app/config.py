import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Epoch info
EPOCH_ID = os.getenv("EPOCH_ID", "2026-04")
SNAPSHOT_TIMESTAMP = os.getenv("SNAPSHOT_TIMESTAMP", None)

# API Keys
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
SEMANTIC_SCHOLAR_KEY = os.getenv("SEMANTIC_SCHOLAR_KEY", "")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

# Rate limiting (1 request per second as specified)
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "1"))

# Weights for intelligence sub-scores
INTELLIGENCE_WEIGHTS = {
    "arena": 0.30,
    "mmlu": 0.20,
    "gsm8k": 0.10,
    "humaneval": 0.15,
    "multimodal": 0.15,
    "robustness": 0.10,
}

# Weights for adoption sub-scores
ADOPTION_WEIGHTS = {
    "downloads": 0.40,
    "github_growth": 0.20,
    "citation_velocity": 0.20,
    "release_frequency": 0.20,
}

# Weights for momentum sub-scores
MOMENTUM_WEIGHTS = {
    "elo_delta": 0.30,
    "benchmark_delta": 0.30,
    "download_growth": 0.25,
    "citation_growth": 0.15,
}

# Tier weights for final CIS aggregation
TIER_WEIGHTS = {
    "A": 0.50,
    "B": 0.35,
    "C": 0.15,
}

# How to combine model-level scores into a final model score
MODEL_SCORE_WEIGHTS = {
    "intelligence": 0.5,
    "adoption": 0.3,
    "momentum": 0.2,
}

# Paths
RAW_DATA_ARCHIVE_DIR = "epochs/raw"
SNAPSHOT_DIR = "epochs"
MODELS_REGISTRY_PATH = "app/models_registry.json"
