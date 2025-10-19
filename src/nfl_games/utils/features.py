
"""
features.py
Defines feature engineering functions for NFL game data.

Handles creating additional features from raw NFL game data, including rolling statistics for 
offense, defense, and team performance trends. These features are used as input to the machine 
learning model.

Brendan Dileo, October 2025
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

# Last N games to consider for rolling statistics
ROLLING_WINDOW = 3

# Only use data from this season onward to avoid inconsistencies in historical data
MODERN_START_YEAR = 2002


def add_rolling_features(df, window=ROLLING_WINDOW):
    """
    Adds rolling statistics for each team using efficient vectorized operations:
    - Offensive: average points scored in the last N games
    - Defensive: average points allowed in the last N games
    - Win percentage: proportion of games won in the last N games
    - Momentum: trend in recent performance
    Also adds difference features from the perspective of the home team.

    Args:
        df (pd.DataFrame): Raw game data with columns like 'team_home', 'score_home', etc.
        window (int): Number of games to consider for rolling calculations

    Returns:
        pd.DataFrame: DataFrame with new rolling and difference features
    """
    
    # Sort by date to ensure chronological order
    df = df.sort_values("schedule_date").copy()
    
    # Keep only modern seasons
    df = df[df["schedule_season"] >= MODERN_START_YEAR].copy()
    
    # Convert date to datetime for rest days calculation
    df['schedule_date'] = pd.to_datetime(df['schedule_date'])
    
    # Initialize columns
    rolling_cols = ["home_avg_points", "away_avg_points",
                    "home_avg_allowed", "away_avg_allowed",
                    "home_win_pct", "away_win_pct",
                    "home_rest_days", "away_rest_days",
                    "home_momentum", "away_momentum"]
    
    for col in rolling_cols:
        df[col] = np.nan
    
    teams = pd.concat([df["team_home"], df["team_away"]]).unique()
    
    # Process each team efficiently
    for team in teams:
        # Get all games for this team
        home_mask = df["team_home"] == team
        away_mask = df["team_away"] == team
        team_mask = home_mask | away_mask
        
        team_indices = df[team_mask].index
        
        # Calculate points scored, allowed, and wins
        points_scored = np.where(home_mask, df["score_home"], 
                                np.where(away_mask, df["score_away"], np.nan))
        points_allowed = np.where(home_mask, df["score_away"],
                                 np.where(away_mask, df["score_home"], np.nan))
        won = ((home_mask & (df["score_home"] > df["score_away"])) |
               (away_mask & (df["score_away"] > df["score_home"]))).astype(float)
        
        # Create series for this team only
        team_points_scored = pd.Series(points_scored[team_mask], index=team_indices)
        team_points_allowed = pd.Series(points_allowed[team_mask], index=team_indices)
        team_won = pd.Series(won[team_mask], index=team_indices)
        team_dates = df.loc[team_indices, 'schedule_date']
        
        # Calculate rest days (days since last game)
        rest_days = team_dates.diff().dt.days
        
        # Calculate rolling stats with expanding window for first few games
        rolling_avg_points = team_points_scored.shift(1).rolling(window, min_periods=1).mean()
        rolling_avg_allowed = team_points_allowed.shift(1).rolling(window, min_periods=1).mean()
        rolling_win_pct = team_won.shift(1).rolling(window, min_periods=1).mean()
        
        # Calculate momentum (trend in last N games) - positive means improving
        # Compare recent avg to previous avg
        recent_points = team_points_scored.shift(1).rolling(window, min_periods=1).mean()
        older_points = team_points_scored.shift(window+1).rolling(window, min_periods=1).mean()
        momentum = recent_points - older_points
        
        # Map back to main dataframe
        df.loc[home_mask & team_mask, "home_avg_points"] = rolling_avg_points[home_mask & team_mask].values
        df.loc[home_mask & team_mask, "home_avg_allowed"] = rolling_avg_allowed[home_mask & team_mask].values
        df.loc[home_mask & team_mask, "home_win_pct"] = rolling_win_pct[home_mask & team_mask].values
        df.loc[home_mask & team_mask, "home_rest_days"] = rest_days[home_mask & team_mask].values
        df.loc[home_mask & team_mask, "home_momentum"] = momentum[home_mask & team_mask].values
        
        df.loc[away_mask & team_mask, "away_avg_points"] = rolling_avg_points[away_mask & team_mask].values
        df.loc[away_mask & team_mask, "away_avg_allowed"] = rolling_avg_allowed[away_mask & team_mask].values
        df.loc[away_mask & team_mask, "away_win_pct"] = rolling_win_pct[away_mask & team_mask].values
        df.loc[away_mask & team_mask, "away_rest_days"] = rest_days[away_mask & team_mask].values
        df.loc[away_mask & team_mask, "away_momentum"] = momentum[away_mask & team_mask].values
    
    # Fill remaining NaNs with neutral values
    df["home_avg_points"] = df["home_avg_points"].fillna(21)  # NFL average ~21 points
    df["away_avg_points"] = df["away_avg_points"].fillna(21)
    df["home_avg_allowed"] = df["home_avg_allowed"].fillna(21)
    df["away_avg_allowed"] = df["away_avg_allowed"].fillna(21)
    df["home_win_pct"] = df["home_win_pct"].fillna(0.5)
    df["away_win_pct"] = df["away_win_pct"].fillna(0.5)
    df["home_rest_days"] = df["home_rest_days"].fillna(7)  # Typical week rest
    df["away_rest_days"] = df["away_rest_days"].fillna(7)
    df["home_momentum"] = df["home_momentum"].fillna(0)
    df["away_momentum"] = df["away_momentum"].fillna(0)
    
    # Create difference features
    df["avg_points_diff"] = df["home_avg_points"] - df["away_avg_points"]
    df["avg_allowed_diff"] = df["away_avg_allowed"] - df["home_avg_allowed"]
    df["win_pct_diff"] = df["home_win_pct"] - df["away_win_pct"]
    df["rest_days_diff"] = df["home_rest_days"] - df["away_rest_days"]
    df["momentum_diff"] = df["home_momentum"] - df["away_momentum"]
    
    return df


def calculate_home_field_advantage(df):
    """
    Calculate historical home field advantage for each team.
    This represents how much better each team performs at home vs away.
    
    Args:
        df (pd.DataFrame): Game data with scores
        
    Returns:
        dict: Mapping of team name to home field advantage score
    """
    teams = pd.concat([df["team_home"], df["team_away"]]).unique()
    home_advantage = {}
    
    for team in teams:
        # Home games
        home_games = df[df["team_home"] == team]
        home_win_pct = (home_games["score_home"] > home_games["score_away"]).mean()
        
        # Away games
        away_games = df[df["team_away"] == team]
        away_win_pct = (away_games["score_away"] > away_games["score_home"]).mean()
        
        # Home advantage is difference in win percentage
        home_advantage[team] = home_win_pct - away_win_pct
    
    return home_advantage


def add_weather_features(df):
    """
    Process and add weather-related features.
    
    Args:
        df (pd.DataFrame): Game data with weather columns
        
    Returns:
        pd.DataFrame: DataFrame with processed weather features
    """
    # Temperature - fill missing with 70 (typical dome/pleasant weather)
    df["weather_temperature"] = pd.to_numeric(df["weather_temperature"], errors='coerce').fillna(70)
    
    # Wind - fill missing with 0 (dome or calm)
    df["weather_wind_mph"] = pd.to_numeric(df["weather_wind_mph"], errors='coerce').fillna(0)
    
    # Humidity - fill missing with 50 (neutral)
    df["weather_humidity"] = pd.to_numeric(df["weather_humidity"], errors='coerce').fillna(50)
    
    # Create weather severity flags
    df["extreme_cold"] = (df["weather_temperature"] < 32).astype(int)  # Freezing
    df["extreme_heat"] = (df["weather_temperature"] > 85).astype(int)  # Very hot
    df["high_wind"] = (df["weather_wind_mph"] > 15).astype(int)  # Windy
    
    # Parse weather detail for precipitation
    df["weather_detail"] = df["weather_detail"].fillna("").astype(str).str.lower()
    df["is_rainy"] = df["weather_detail"].str.contains("rain|showers", case=False).astype(int)
    df["is_snowy"] = df["weather_detail"].str.contains("snow|flurr", case=False).astype(int)
    
    # Combined bad weather indicator
    df["bad_weather"] = ((df["extreme_cold"] == 1) | 
                         (df["high_wind"] == 1) | 
                         (df["is_rainy"] == 1) | 
                         (df["is_snowy"] == 1)).astype(int)
    
    return df


def encode_features(df):
    """
    Prepares feature matrix (X) and target vector (y) for modeling.
    Steps:
    1. Encode team names as numeric labels.
    2. Add rolling offensive/defensive stats and difference features.
    3. Calculate home field advantage.
    4. Add weather features.
    5. Add playoff and neutral site indicators.
    6. Add interaction features.
    7. Fill missing spread values.
    8. Assemble final feature matrix.

    Args:
        df (pd.DataFrame): Raw game data

    Returns:
        X (pd.DataFrame): Features for model training
        y (pd.Series): Target labels (home team win)
        df (pd.DataFrame): Full dataframe for time-based splitting
    """
    
    # Encode all teams consistently
    all_teams = pd.concat([df["team_home"], df["team_away"]]).unique()
    encoder = LabelEncoder()
    encoder.fit(all_teams)
    
    df["home_team_encoded"] = encoder.transform(df["team_home"])
    df["away_team_encoded"] = encoder.transform(df["team_away"])
    
    # Add rolling stats & difference features
    df = add_rolling_features(df)
    
    # Calculate home field advantage
    home_adv_dict = calculate_home_field_advantage(df)
    df["home_field_advantage"] = df["team_home"].map(home_adv_dict)
    
    # Add weather features
    df = add_weather_features(df)
    
    # Add playoff indicator (playoff games are different)
    df["is_playoff"] = df["schedule_playoff"].fillna(0).astype(int)
    
    # Add neutral site indicator (Super Bowl, London games, etc.)
    df["is_neutral_site"] = df["stadium_neutral"].fillna(0).astype(int)
    
    # Fill missing spread and over/under values (convert to numeric first)
    df["spread_favorite"] = pd.to_numeric(df["spread_favorite"], errors='coerce').fillna(0)
    df["over_under_line"] = pd.to_numeric(df["over_under_line"], errors='coerce')
    df["over_under_line"] = df["over_under_line"].fillna(df["over_under_line"].median())
    
    # Create interaction features
    df["spread_strength_interaction"] = df["spread_favorite"] * df["avg_points_diff"]
    df["spread_defense_interaction"] = df["spread_favorite"] * df["avg_allowed_diff"]
    df["weather_offense_interaction"] = df["bad_weather"] * df["avg_points_diff"]
    
    # Over/under can predict game style (high scoring vs defensive)
    df["over_under_normalized"] = (df["over_under_line"] - df["over_under_line"].mean()) / df["over_under_line"].std()
    
    # Select final columns for training
    feature_cols = [
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
        "win_pct_diff",
        "home_field_advantage",
        "home_rest_days",
        "away_rest_days",
        "rest_days_diff",
        "home_momentum",
        "away_momentum",
        "momentum_diff",
        "spread_strength_interaction",
        "spread_defense_interaction",
        # Weather features
        "weather_temperature",
        "weather_wind_mph",
        "weather_humidity",
        "extreme_cold",
        "extreme_heat",
        "high_wind",
        "is_rainy",
        "is_snowy",
        "bad_weather",
        "weather_offense_interaction",
        # Game context features
        "is_playoff",
        "is_neutral_site",
        "over_under_line",
        "over_under_normalized"
    ]
    
    X = df[feature_cols]
    y = df["home_team_won"]
    
    return X, y, df  # Return df for time-based splitting