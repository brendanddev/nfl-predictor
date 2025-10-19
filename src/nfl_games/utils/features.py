
""" 
features.py

Brendan Dileo, October 2025
"""

from sklearn.preprocessing import LabelEncoder

def encode_features(df):
    encoder = LabelEncoder()
    df["home_team_encoded"] = encoder.fit_transform(df["team_home"])
    df["away_team_encoded"] = encoder.fit_transform(df["team_away"])

    X = df[["home_team_encoded", "away_team_encoded", "spread_favorite"]]
    y = df["home_team_won"]

    return X, y