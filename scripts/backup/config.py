"""
Configuration file for the Avatar: Ash & Fire Box Office Prediction Project
"""

import os
from pathlib import Path

# Project Paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results"

# Create directories if they don't exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, RESULTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Model Parameters
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5

# Feature Engineering Parameters
TARGET_VARIABLE = 'first_week_income'

# Stacking and Ensemble Parameters
STACK_CV_FOLDS = 5
N_ESTIMATORS_DEFAULT = 100

# API Keys
TMDB_API_KEY = os.getenv('TMDB_API_KEY', 'd429e3e7a57fe68708d1380b99dbdf43')
OMDB_API_KEY = os.getenv('OMDB_API_KEY', '')

# Movie-specific information
MOVIE_INFO = {
    'title': 'Avatar: Ash & Fire',
    'expected_release_date': '2025-12-18',  # Update with actual date
    'franchise': 'Avatar',
    'genre': ['Action', 'Adventure', 'Sci-Fi'],
    'production_budget': None,  # To be filled
    'director': 'James Cameron',
    'studio': '20th Century Studios'
}
