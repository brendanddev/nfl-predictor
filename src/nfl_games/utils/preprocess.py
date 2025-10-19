
""" 
preprocess.py

Brendan Dileo, October 2025
"""

def preprocess(df):
    # Drop rows missing scores
    df = df.dropna(subset=["score_home", "score_away"])

    # Add target column: 1 if home team won, else 0
    df["home_team_won"] = (df["score_home"] > df["score_away"]).astype(int)

    print("Preprocessing complete. Added 'home_team_won' column.")
    return df
