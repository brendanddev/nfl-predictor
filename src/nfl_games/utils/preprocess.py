
""" 
preprocess.py

Brendan Dileo, October 2025
"""


def preprocess(df):
    # Make a safe copy
    df = df.copy()
    df.loc[:, "home_team_won"] = (df["score_home"] > df["score_away"]).astype(int)
    print("Preprocessing complete. Added 'home_team_won' column.")
    return df
