
"""
features.py
Defines feature engineering functions for NFL game data.

Handles creating additional features from raw NFL game data, including rolling statistics for 
offense, defense, and team performance trends. These features are used as input to the machine 
learning model.

Brendan Dileo, October 2025
"""

import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Last N games to consider for rolling statistics (e.g., avg points, win percentage)
ROLLING_WINDOW = 3

# Only use data from this season onward to avoid inconsistencies in historical data
MODERN_START_YEAR = 2002


def add_rolling_features(df, window=ROLLING_WINDOW):
    """
    Adds rolling statistics for each team:
    - Offensive: average points scored in the last N games
    - Defensive: average points allowed in the last N games
    - Win percentage: proportion of games won in the last N games
    Also adds difference features from the perspective of the home team:
    - avg_points_diff: home vs away avg points scored
    - avg_allowed_diff: away vs home avg points allowed
    - win_pct_diff: home vs away win percentage

    Args:
        df (pd.DataFrame): Raw game data with columns like 'team_home', 'score_home', etc.
        window (int): Number of games to consider for rolling calculations

    Returns:
        pd.DataFrame: DataFrame with new rolling and difference features
    """

    # Sort by date to ensure chronological order for rolling calculations
    df = df.sort_values("schedule_date").copy()

    # Keep only modern seasons (optional but improves model quality)
    df = df[df["schedule_season"] >= MODERN_START_YEAR].copy()

    # Initialize new columns for rolling stats
    cols = ["home_avg_points", "away_avg_points",
            "home_avg_allowed", "away_avg_allowed",
            "home_win_pct", "away_win_pct"]
    for c in cols:
        df.loc[:, c] = 0.0

    # Get list of all unique NFL teams
    teams = pd.concat([df["team_home"], df["team_away"]]).unique()

    # Loop over each team to calculate rolling stats
    for team in teams:
        # Extract all games involving this team
        team_games = df[(df["team_home"] == team) | (df["team_away"] == team)].copy()

        # Points scored by this team in each game
        team_games["points_scored"] = team_games.apply(
            lambda row: row["score_home"] if row["team_home"] == team else row["score_away"], axis=1
        )

        # Points allowed by this team in each game
        team_games["points_allowed"] = team_games.apply(
            lambda row: row["score_away"] if row["team_home"] == team else row["score_home"], axis=1
        )

        # Did this team win the game? 1 = win, 0 = loss
        team_games["won"] = team_games.apply(
            lambda row: 1 if ((row["team_home"] == team and row["score_home"] > row["score_away"]) or
                              (row["team_away"] == team and row["score_away"] > row["score_home"])) else 0, axis=1
        )

        # Compute rolling averages with shift(1) to avoid using the current game
        team_games["rolling_avg_points"] = team_games["points_scored"].shift(1).rolling(window).mean()
        team_games["rolling_avg_allowed"] = team_games["points_allowed"].shift(1).rolling(window).mean()
        team_games["rolling_win_pct"] = team_games["won"].shift(1).rolling(window).mean()

        # Map rolling stats back to the main dataframe
        for idx, row in team_games.iterrows():
            if row["team_home"] == team:
                df.loc[idx, "home_avg_points"] = row["rolling_avg_points"]
                df.loc[idx, "home_avg_allowed"] = row["rolling_avg_allowed"]
                df.loc[idx, "home_win_pct"] = row["rolling_win_pct"]
            if row["team_away"] == team:
                df.loc[idx, "away_avg_points"] = row["rolling_avg_points"]
                df.loc[idx, "away_avg_allowed"] = row["rolling_avg_allowed"]
                df.loc[idx, "away_win_pct"] = row["rolling_win_pct"]

    # Fill NaN values for the first few games where rolling stats are not available
    df[cols] = df[cols].fillna(0)

    # Create difference features for model to learn matchup context
    df["avg_points_diff"] = df["home_avg_points"] - df["away_avg_points"]
    df["avg_allowed_diff"] = df["away_avg_allowed"] - df["home_avg_allowed"]  # home perspective
    df["win_pct_diff"] = df["home_win_pct"] - df["away_win_pct"]

    return df


def encode_features(df):
    """
    Prepares feature matrix (X) and target vector (y) for modeling.
    Steps:
    1. Encode team names as numeric labels.
    2. Add rolling offensive/defensive stats and difference features.
    3. Fill missing spread values (Vegas odds).
    4. Assemble final feature matrix.

    Args:
        df (pd.DataFrame): Raw game data

    Returns:
        X (pd.DataFrame): Features for model training
        y (pd.Series): Target labels (home team win)
    """

    # Encode all teams consistently
    all_teams = pd.concat([df["team_home"], df["team_away"]]).unique()
    encoder = LabelEncoder()
    encoder.fit(all_teams)

    df.loc[:, "home_team_encoded"] = encoder.transform(df["team_home"])
    df.loc[:, "away_team_encoded"] = encoder.transform(df["team_away"])

    # Add rolling stats & difference features
    df = add_rolling_features(df)

    # Fill missing spread values with 0 (assume neutral spread if missing)
    df["spread_favorite"] = df["spread_favorite"].fillna(0)

    # Select final columns for training
    X = df[[
        "home_team_encoded",
        "away_team_encoded",
        "spread_favorite",
        "home_avg_points",
        "away_avg_points",
        "home_avg_allowed",
        "away_avg_allowed",
        "home_win_pct",
        "away_win_pct",
        "avg_points_diff",
        "avg_allowed_diff",
        "win_pct_diff"
    ]]
    y = df["home_team_won"]

    return X, y
