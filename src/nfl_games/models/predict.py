
"""
predict.py
Interactive prediction interface for NFL games.

Allows users to input matchup details and get win probability predictions.

Brendan Dileo, October 2025
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder


def get_team_recent_stats(df, team, n_games=3):
    """
    Get recent statistics for a team to use as defaults.
    
    Args:
        df: Full game dataframe
        team: Team name
        n_games: Number of recent games to consider
        
    Returns:
        dict: Recent stats for the team
    """
    # Get all games for this team (most recent first)
    team_games = df[(df["team_home"] == team) | (df["team_away"] == team)].sort_values("schedule_date", ascending=False)
    
    if len(team_games) == 0:
        return None
    
    recent_games = team_games.head(n_games)
    
    # Calculate stats
    points_scored = []
    points_allowed = []
    wins = 0
    
    for _, game in recent_games.iterrows():
        if game["team_home"] == team:
            points_scored.append(game["score_home"])
            points_allowed.append(game["score_away"])
            if game["score_home"] > game["score_away"]:
                wins += 1
        else:
            points_scored.append(game["score_away"])
            points_allowed.append(game["score_home"])
            if game["score_away"] > game["score_home"]:
                wins += 1
    
    return {
        "avg_points": np.mean(points_scored),
        "avg_allowed": np.mean(points_allowed),
        "win_pct": wins / len(recent_games),
        "momentum": np.mean(points_scored[-2:]) - np.mean(points_scored[:2]) if len(points_scored) >= 3 else 0
    }


def get_home_field_advantage(df, team):
    """Calculate home field advantage for a specific team."""
    home_games = df[df["team_home"] == team]
    away_games = df[df["team_away"] == team]
    
    if len(home_games) == 0 or len(away_games) == 0:
        return 0.05  # Default neutral advantage
    
    home_win_pct = (home_games["score_home"] > home_games["score_away"]).mean()
    away_win_pct = (away_games["score_away"] > away_games["score_home"]).mean()
    
    return home_win_pct - away_win_pct


def create_prediction_input(home_team, away_team, df, encoder, 
                            spread=None, weather_temp=70, weather_wind=0,
                            weather_humidity=50, is_playoff=False, 
                            is_neutral=False, over_under=None):
    """
    Create a feature vector for prediction based on user input.
    
    Args:
        home_team: Home team name
        away_team: Away team name
        df: Historical data for calculating team stats
        encoder: Fitted LabelEncoder for teams
        spread: Vegas spread (negative = home favored)
        weather_temp: Temperature in Fahrenheit
        weather_wind: Wind speed in mph
        weather_humidity: Humidity percentage
        is_playoff: Boolean for playoff game
        is_neutral: Boolean for neutral site
        over_under: Vegas over/under line
        
    Returns:
        pd.DataFrame: Single row feature vector ready for prediction
    """
    
    # Get recent stats for both teams
    home_stats = get_team_recent_stats(df, home_team)
    away_stats = get_team_recent_stats(df, away_team)
    
    if home_stats is None or away_stats is None:
        raise ValueError(f"Could not find stats for {home_team} or {away_team}. Check team names.")
    
    # Encode teams
    try:
        home_encoded = encoder.transform([home_team])[0]
        away_encoded = encoder.transform([away_team])[0]
    except:
        raise ValueError(f"Team names not recognized. Available teams: {list(encoder.classes_)}")
    
    # Calculate home field advantage
    home_adv = get_home_field_advantage(df, home_team)
    
    # Default spread and over/under if not provided
    if spread is None:
        # Rough estimate based on point differential
        spread = -(home_stats["avg_points"] - away_stats["avg_points"]) / 2
    
    if over_under is None:
        over_under = home_stats["avg_points"] + away_stats["avg_points"]
    
    # Calculate rest days (assume standard 7 days if unknown)
    rest_days_home = 7
    rest_days_away = 7
    
    # Weather features
    extreme_cold = 1 if weather_temp < 32 else 0
    extreme_heat = 1 if weather_temp > 85 else 0
    high_wind = 1 if weather_wind > 15 else 0
    is_rainy = 0  # User would need to specify
    is_snowy = 0  # User would need to specify
    bad_weather = max(extreme_cold, extreme_heat, high_wind, is_rainy, is_snowy)
    
    # Calculate difference features
    avg_points_diff = home_stats["avg_points"] - away_stats["avg_points"]
    avg_allowed_diff = away_stats["avg_allowed"] - home_stats["avg_allowed"]
    win_pct_diff = home_stats["win_pct"] - away_stats["win_pct"]
    rest_days_diff = rest_days_home - rest_days_away
    momentum_diff = home_stats["momentum"] - away_stats["momentum"]
    
    # Interaction features
    spread_strength_interaction = spread * avg_points_diff
    spread_defense_interaction = spread * avg_allowed_diff
    weather_offense_interaction = bad_weather * avg_points_diff
    
    # Over/under normalized (approximate with mean=45, std=5)
    over_under_normalized = (over_under - 45) / 5
    
    # Create feature dictionary matching training features
    features = {
        "home_team_encoded": home_encoded,
        "away_team_encoded": away_encoded,
        "spread_favorite": spread,
        "home_avg_points": home_stats["avg_points"],
        "away_avg_points": away_stats["avg_points"],
        "home_avg_allowed": home_stats["avg_allowed"],
        "away_avg_allowed": away_stats["avg_allowed"],
        "home_win_pct": home_stats["win_pct"],
        "away_win_pct": away_stats["win_pct"],
        "avg_points_diff": avg_points_diff,
        "avg_allowed_diff": avg_allowed_diff,
        "win_pct_diff": win_pct_diff,
        "home_field_advantage": home_adv,
        "home_rest_days": rest_days_home,
        "away_rest_days": rest_days_away,
        "rest_days_diff": rest_days_diff,
        "home_momentum": home_stats["momentum"],
        "away_momentum": away_stats["momentum"],
        "momentum_diff": momentum_diff,
        "spread_strength_interaction": spread_strength_interaction,
        "spread_defense_interaction": spread_defense_interaction,
        "weather_temperature": weather_temp,
        "weather_wind_mph": weather_wind,
        "weather_humidity": weather_humidity,
        "extreme_cold": extreme_cold,
        "extreme_heat": extreme_heat,
        "high_wind": high_wind,
        "is_rainy": is_rainy,
        "is_snowy": is_snowy,
        "bad_weather": bad_weather,
        "weather_offense_interaction": weather_offense_interaction,
        "is_playoff": int(is_playoff),
        "is_neutral_site": int(is_neutral),
        "over_under_line": over_under,
        "over_under_normalized": over_under_normalized
    }
    
    return pd.DataFrame([features])


def predict_game(model, home_team, away_team, df, encoder, **kwargs):
    """
    Predict the outcome of a game.
    
    Args:
        model: Trained model
        home_team: Home team name
        away_team: Away team name
        df: Historical data
        encoder: Fitted LabelEncoder
        **kwargs: Additional parameters (spread, weather, etc.)
        
    Returns:
        dict: Prediction results with probabilities
    """
    
    # Create feature vector
    X = create_prediction_input(home_team, away_team, df, encoder, **kwargs)
    
    # Get prediction and probabilities
    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]
    
    home_win_prob = probabilities[1] * 100
    away_win_prob = probabilities[0] * 100
    
    result = {
        "home_team": home_team,
        "away_team": away_team,
        "predicted_winner": home_team if prediction == 1 else away_team,
        "home_win_probability": home_win_prob,
        "away_win_probability": away_win_prob,
        "confidence": max(home_win_prob, away_win_prob)
    }
    
    return result


def interactive_predict(model, df, encoder):
    """
    Interactive command-line interface for predictions.
    
    Args:
        model: Trained model
        df: Historical data
        encoder: Fitted LabelEncoder
    """
    
    print("\n" + "="*60)
    print("NFL GAME PREDICTION INTERFACE")
    print("="*60)
    print("\nAvailable teams:")
    teams = sorted(encoder.classes_)
    for i, team in enumerate(teams, 1):
        print(f"  {i}. {team}", end="   ")
        if i % 3 == 0:
            print()
    print("\n")
    
    while True:
        try:
            # Get teams
            home_team = input("Enter home team name (or 'quit' to exit): ").strip()
            if home_team.lower() == 'quit':
                break
            
            away_team = input("Enter away team name: ").strip()
            
            # Optional parameters
            print("\nOptional parameters (press Enter to use defaults):")
            
            spread_input = input("Vegas spread (negative = home favored, default=calculated): ").strip()
            spread = float(spread_input) if spread_input else None
            
            temp_input = input("Temperature in °F (default=70): ").strip()
            temp = float(temp_input) if temp_input else 70
            
            wind_input = input("Wind speed in mph (default=0): ").strip()
            wind = float(wind_input) if wind_input else 0
            
            playoff_input = input("Is this a playoff game? (y/n, default=n): ").strip().lower()
            is_playoff = playoff_input == 'y'
            
            # Make prediction
            result = predict_game(
                model, home_team, away_team, df, encoder,
                spread=spread,
                weather_temp=temp,
                weather_wind=wind,
                is_playoff=is_playoff
            )
            
            # Display results
            print("\n" + "="*60)
            print("PREDICTION RESULTS")
            print("="*60)
            print(f"{result['home_team']} (Home) vs {result['away_team']} (Away)")
            print(f"\nPredicted Winner: {result['predicted_winner']}")
            print(f"\nWin Probabilities:")
            print(f"  {result['home_team']}: {result['home_win_probability']:.1f}%")
            print(f"  {result['away_team']}: {result['away_win_probability']:.1f}%")
            print(f"\nConfidence: {result['confidence']:.1f}%")
            print("="*60 + "\n")
            
        except ValueError as e:
            print(f"\nError: {e}\n")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}\n")


def predict_current_week(model, df, encoder, season=2025, week=8):
    """
    Predict outcomes for a specific week of games.
    
    Args:
        model: Trained model
        df: Historical data
        encoder: Fitted LabelEncoder
        season: Season year
        week: Week number
    """
    
    # Convert week to string to match dataset format
    week_str = str(week)
    
    # Get games for that week
    week_games = df[(df["schedule_season"] == season) & 
                    (df["schedule_week"] == week_str)]
    
    if len(week_games) == 0:
        # Show what data is available
        available_seasons = sorted(df["schedule_season"].unique())
        print(f"\nNo games found for {season} Week {week}")
        print(f"\nAvailable seasons in dataset: {available_seasons[0]} to {available_seasons[-1]}")
        
        # Show available weeks for this season if season exists
        season_data = df[df["schedule_season"] == season]
        if len(season_data) > 0:
            available_weeks = sorted(season_data["schedule_week"].unique(), key=lambda x: int(x) if x.isdigit() else 0)
            print(f"Available weeks for {season}: {available_weeks}")
        else:
            print(f"\nNo data for season {season}. Try season {available_seasons[-1]} or earlier.")
        return
    
    print(f"\n{'='*60}")
    print(f"PREDICTIONS FOR {season} WEEK {week}")
    print(f"{'='*60}\n")
    
    for _, game in week_games.iterrows():
        try:
            result = predict_game(
                model,
                game["team_home"],
                game["team_away"],
                df,
                encoder,
                spread=game.get("spread_favorite"),
                weather_temp=game.get("weather_temperature", 70),
                weather_wind=game.get("weather_wind_mph", 0),
                is_playoff=game.get("schedule_playoff", False)
            )
            
            print(f"{result['home_team']} vs {result['away_team']}")
            print(f"  Predicted: {result['predicted_winner']} ({result['confidence']:.1f}% confidence)")
            
            # Show actual result if game is complete
            if pd.notna(game["score_home"]) and pd.notna(game["score_away"]):
                actual_winner = game["team_home"] if game["score_home"] > game["score_away"] else game["team_away"]
                correct = "✓" if actual_winner == result['predicted_winner'] else "✗"
                print(f"  Actual: {actual_winner} ({game['score_home']}-{game['score_away']}) {correct}")
            
            print()
            
        except Exception as e:
            print(f"Error predicting {game['team_home']} vs {game['team_away']}: {e}\n")