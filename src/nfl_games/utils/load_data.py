
""" 
load_data.py

Brendan Dileo, October 2025
"""

import pandas as pd
import numpy as np

DATA_PATH = "data/spreadspoke_scores.csv"

def load_data():
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"Data loaded successfully! Rows: {len(df)}, Columns: {len(df.columns)}")
        return df
    except FileNotFoundError:
        print("CSV file not found.")
        return None

def load_nflfastr_data():
    try:
        import nfl_data_py as nfl
        NFL_DATA_AVAILABLE = True
    except ImportError as e:
        NFL_DATA_AVAILABLE = False
        print(f"nfl_data_py not available: {str(e)[:100]}")
        return None
    
    if not NFL_DATA_AVAILABLE:
        raise ImportError("nfl_data_py is not installed. Please install it with: pip install nfl_data_py")
    
    if seasons is None:
        seasons = list(range(2015, 2025))

    print(f"Downloading nflfastR data for seasons: {seasons[0]}-{seasons[-1]}")
    print("This may take a few minutes on first run...")
    
    # Download play-by-play data
    pbp_data = nfl.import_pbp_data(seasons)
    
    print(f"Downloaded {len(pbp_data):,} plays")
    
    return pbp_data

