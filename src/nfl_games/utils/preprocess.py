
"""
preprocess.py
Adds target variable for NFL game outcomes.

Handles simple preprocessing steps for NFL game data, by creating the target column
'home_team_won' indicating if the home team won the game.

Brendan Dileo, October 2025
"""

def preprocess(df):
    # Make a safe copy to avoid modifying original DataFrame
    df = df.copy()

    # Add target column: 1 if home team won, 0 otherwise
    df.loc[:, "home_team_won"] = (df["score_home"] > df["score_away"]).astype(int)

    print("Preprocessing complete. Added 'home_team_won' column.")
    return df
