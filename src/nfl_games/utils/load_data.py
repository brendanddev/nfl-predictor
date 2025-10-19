
""" 
load_data.py

Brendan Dileo, October 2025
"""

import pandas as pd

DATA_PATH = "data/spreadspoke_scores.csv"

def load_data():
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"Data loaded successfully! Rows: {len(df)}, Columns: {len(df.columns)}")
        return df
    except FileNotFoundError:
        print("CSV file not found. Check your path in config.py.")
        return None
