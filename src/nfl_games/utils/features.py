
""" 
features.py

Brendan Dileo, October 2025
"""

import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Last N games to consider for rolling stats (average points, win %, stuff like that)
ROLLING_WINDOW = 3

# Only use data from this season onward for rolling calculations
# This helps avoid issues with historical data inconsistencies
# Cane be adjusted as needed
MODERN_START_YEAR = 2002


def add_rolling_features(df, window=ROLLING_WINDOW):
    df = df.sort_values("schedule_date").copy()
    
    # Filter to modern seasons
    df = df[df["schedule_season"] >= MODERN_START_YEAR].copy()

    # Initialize columns
    df.loc[:, "home_avg_points"] = 0.0
    df.loc[:, "away_avg_points"] = 0.0
    df.loc[:, "home_win_pct"] = 0.0
    df.loc[:, "away_win_pct"] = 0.0

    # Get all unique teams
    teams = pd.concat([df["team_home"], df["team_away"]]).unique()

    for team in teams:
        # All games for this team
        team_games = df[(df["team_home"] == team) | (df["team_away"] == team)].copy()

        # Points scored from this team’s perspective
        team_games["points_scored"] = team_games.apply(
            lambda row: row["score_home"] if row["team_home"] == team else row["score_away"], axis=1
        )
        # Did this team win?
        team_games["won"] = team_games.apply(
            lambda row: 1 if ((row["team_home"] == team and row["score_home"] > row["score_away"]) or
                              (row["team_away"] == team and row["score_away"] > row["score_home"])) else 0, axis=1
        )

        # Rolling calculations with shift(1) to avoid future leakage
        team_games["rolling_avg_points"] = team_games["points_scored"].shift(1).rolling(window).mean()
        team_games["rolling_win_pct"] = team_games["won"].shift(1).rolling(window).mean()

        # Map back to original df
        for idx, row in team_games.iterrows():
            if row["team_home"] == team:
                df.loc[idx, "home_avg_points"] = row["rolling_avg_points"]
                df.loc[idx, "home_win_pct"] = row["rolling_win_pct"]
            if row["team_away"] == team:
                df.loc[idx, "away_avg_points"] = row["rolling_avg_points"]
                df.loc[idx, "away_win_pct"] = row["rolling_win_pct"]

    # Fill NaN for first few games
    df[["home_avg_points", "away_avg_points", "home_win_pct", "away_win_pct"]] = \
        df[["home_avg_points", "away_avg_points", "home_win_pct", "away_win_pct"]].fillna(0)

    return df


def encode_features(df):
    """
    Encodes teams and prepares feature matrix X and target y.
    """
    # Consistent encoding across home and away
    all_teams = pd.concat([df["team_home"], df["team_away"]]).unique()
    encoder = LabelEncoder()
    encoder.fit(all_teams)

    df.loc[:, "home_team_encoded"] = encoder.transform(df["team_home"])
    df.loc[:, "away_team_encoded"] = encoder.transform(df["team_away"])

    # Add rolling features
    df = add_rolling_features(df)

    # Fill missing spreads with 0
    df["spread_favorite"] = df["spread_favorite"].fillna(0)

    # Features
    X = df[[
        "home_team_encoded",
        "away_team_encoded",
        "spread_favorite",
        "home_avg_points",
        "away_avg_points",
        "home_win_pct",
        "away_win_pct"
    ]]
    y = df["home_team_won"]

    return X, y