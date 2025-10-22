
""" 
load_data.py
Loads NFL game data from spreadspoke CSV and optionally merges with nflfastR data.

Brendan Dileo, October 2025
"""

import pandas as pd
import numpy as np

# Spreadspoke dataset path
DATA_PATH = "data/spreadspoke_scores.csv"

# Check if nfl_data_py is available
try:
    import nfl_data_py as nfl
    NFL_DATA_AVAILABLE = True
except ImportError:
    NFL_DATA_AVAILABLE = False


def load_data():
    """Load the base spreadspoke dataset."""
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"Data loaded successfully! Rows: {len(df)}, Columns: {len(df.columns)}")
        return df
    except FileNotFoundError:
        print("CSV file not found.")
        return None


def download_nflfastr_data(seasons=None, cache=True):
    """
    Download play-by-play data from nflfastR.
    
    Args:
        seasons: List of seasons to download (e.g., [2020, 2021, 2022])
                 If None, downloads 2015-2024
        cache: Whether to cache data locally (faster on subsequent runs)
        
    Returns:
        pd.DataFrame: Play-by-play data
    """
    if not NFL_DATA_AVAILABLE:
        raise ImportError("nfl_data_py is required. Install with: pip install nfl_data_py")
    
    if seasons is None:
        # Default to recent seasons (nflfastR data is best from 2015+)
        seasons = list(range(2015, 2025))
    
    print(f"Downloading nflfastR data for seasons: {seasons[0]}-{seasons[-1]}")
    print("This will download directly from GitHub...")
    print("Please be patient - this may take a few minutes...")
    
    # Direct download approach - more reliable than cache-based approach
    all_pbp = []
    
    for season in seasons:
        try:
            url = f'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.parquet'
            print(f"  Downloading {season}...", end=" ", flush=True)
            
            # Download directly using pandas
            season_pbp = pd.read_parquet(url)
            all_pbp.append(season_pbp)
            print(f"✓ ({len(season_pbp):,} plays)")
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            # Continue to try other seasons
            continue
    
    if not all_pbp:
        # If direct download fails, try the nfl_data_py library as backup
        print("\nDirect download failed. Trying nfl_data_py library...")
        try:
            pbp_data = nfl.import_pbp_data(seasons, cache=False)
            print(f"✓ Downloaded {len(pbp_data):,} plays via library")
            return pbp_data
        except:
            raise ValueError(
                "Failed to download nflfastR data. Please try:\n"
                "1. pip install --upgrade nfl_data_py pandas pyarrow\n"
                "2. Check your internet connection\n"
                "3. Try again later (GitHub rate limiting)\n"
                "4. Or use the model without EPA features (answer 'n' when prompted)"
            )
    
    # Combine all seasons
    pbp_data = pd.concat(all_pbp, ignore_index=True)
    print(f"\n✓ Successfully downloaded {len(pbp_data):,} total plays from {len(all_pbp)} seasons")
    
    return pbp_data

def aggregate_team_stats(pbp_data):
    """
    Aggregate play-by-play data into game-level team statistics.
    
    Creates advanced metrics like EPA (Expected Points Added), success rate,
    explosive play rate, etc. for each team in each game.
    
    Args:
        pbp_data: Play-by-play DataFrame from nflfastR
        
    Returns:
        pd.DataFrame: Game-level team statistics
    """
    
    # Filter to regular plays (exclude penalties, timeouts, etc.)
    plays = pbp_data[
        (pbp_data['play_type'].isin(['run', 'pass'])) &
        (pbp_data['epa'].notna())
    ].copy()
    
    print(f"Analyzing {len(plays):,} offensive plays...")
    
    # Create game identifier
    plays['game_id'] = plays['game_id'].astype(str)
    
    # First, get game context (season, week, home/away teams) separately
    game_context = plays.groupby('game_id').agg({
        'season': 'first',
        'week': 'first',
        'home_team': 'first',
        'away_team': 'first'
    }).reset_index()
    
    # Calculate stats for OFFENSE (posteam)
    offense_stats = plays.groupby(['game_id', 'posteam']).agg({
        # EPA metrics
        'epa': ['mean', 'sum', 'std'],
        
        # Success rate (positive EPA plays)
        'success': 'mean',
        
        # Play type breakdown
        'pass_attempt': 'sum',
        'rush_attempt': 'sum',
        
        # Explosive plays (20+ yard gains)
        'yards_gained': lambda x: (x >= 20).sum(),
        
        # Scoring
        'touchdown': 'sum',
        
        # Turnovers
        'interception': 'sum',
        'fumble_lost': 'sum'
    }).reset_index()
    
    # Flatten column names
    offense_stats.columns = [
        'game_id', 'team',
        'epa_per_play', 'epa_total', 'epa_std',
        'success_rate',
        'pass_attempts', 'rush_attempts',
        'explosive_plays',
        'touchdowns',
        'interceptions', 'fumbles_lost'
    ]
    
    # Add total turnovers
    offense_stats['turnovers'] = (
        offense_stats['interceptions'] + offense_stats['fumbles_lost']
    )
    
    # Calculate passing stats separately
    pass_plays = plays[plays['pass_attempt'] == 1].groupby(['game_id', 'posteam']).agg({
        'epa': 'mean',
        'success': 'mean',
        'air_yards': 'mean',
        'yards_after_catch': 'mean',
        'complete_pass': 'mean'
    }).reset_index()
    
    pass_plays.columns = [
        'game_id', 'team',
        'pass_epa', 'pass_success_rate', 
        'avg_air_yards', 'avg_yac', 'completion_pct'
    ]
    
    # Calculate rushing stats separately
    rush_plays = plays[plays['rush_attempt'] == 1].groupby(['game_id', 'posteam']).agg({
        'epa': 'mean',
        'success': 'mean',
        'yards_gained': 'mean'
    }).reset_index()
    
    rush_plays.columns = [
        'game_id', 'team',
        'rush_epa', 'rush_success_rate', 'avg_rush_yards'
    ]
    
    # Merge all offensive stats (without game_context yet)
    team_stats = offense_stats.merge(
        pass_plays, on=['game_id', 'team'], how='left'
    ).merge(
        rush_plays, on=['game_id', 'team'], how='left'
    )
    
    # Fill NaN values for games with no pass/rush attempts
    fill_cols = ['pass_epa', 'pass_success_rate', 'avg_air_yards', 'avg_yac', 
                 'completion_pct', 'rush_epa', 'rush_success_rate', 'avg_rush_yards']
    team_stats[fill_cols] = team_stats[fill_cols].fillna(0)
    
    # Calculate stats for DEFENSE (defteam) - opponent's EPA
    defense_stats = plays.groupby(['game_id', 'defteam']).agg({
        'epa': 'mean',
        'success': 'mean',
        'sack': 'sum',
        'interception': 'sum',
        'fumble_forced': 'sum'
    }).reset_index()
    
    defense_stats.columns = [
        'game_id', 'team',
        'def_epa_allowed', 'def_success_rate_allowed',
        'sacks', 'def_interceptions', 'forced_fumbles'
    ]
    
    # Merge offense and defense
    team_stats = team_stats.merge(
        defense_stats, on=['game_id', 'team'], how='left'
    )
    
    # Add defensive turnovers created
    team_stats['def_turnovers_created'] = (
        team_stats['def_interceptions'] + team_stats['forced_fumbles']
    )
    
    # **CRITICAL FIX: Merge game_context ONCE at the very end**
    # This was being merged twice in the original code, causing duplicate columns
    team_stats = team_stats.merge(game_context, on='game_id', how='left')
    
    print(f"✓ Aggregated stats for {len(team_stats)} team-games")
    
    return team_stats


def merge_with_spreadspoke(spreadspoke_df, nflfastr_stats):
    """
    Merge nflfastR statistics with the existing spreadspoke dataset.
    
    Args:
        spreadspoke_df: Original spreadspoke DataFrame
        nflfastr_stats: Aggregated nflfastR team statistics
        
    Returns:
        pd.DataFrame: Merged dataset with both sources
    """
    
    print("Merging nflfastR data with spreadspoke dataset...")
    
    # Standardize team names (nflfastR uses abbreviations)
    team_name_map = {
        'ARI': 'Arizona Cardinals',
        'ATL': 'Atlanta Falcons',
        'BAL': 'Baltimore Ravens',
        'BUF': 'Buffalo Bills',
        'CAR': 'Carolina Panthers',
        'CHI': 'Chicago Bears',
        'CIN': 'Cincinnati Bengals',
        'CLE': 'Cleveland Browns',
        'DAL': 'Dallas Cowboys',
        'DEN': 'Denver Broncos',
        'DET': 'Detroit Lions',
        'GB': 'Green Bay Packers',
        'HOU': 'Houston Texans',
        'IND': 'Indianapolis Colts',
        'JAX': 'Jacksonville Jaguars',
        'KC': 'Kansas City Chiefs',
        'LAC': 'Los Angeles Chargers',
        'LA': 'Los Angeles Rams',
        'LV': 'Las Vegas Raiders',
        'MIA': 'Miami Dolphins',
        'MIN': 'Minnesota Vikings',
        'NE': 'New England Patriots',
        'NO': 'New Orleans Saints',
        'NYG': 'New York Giants',
        'NYJ': 'New York Jets',
        'PHI': 'Philadelphia Eagles',
        'PIT': 'Pittsburgh Steelers',
        'SEA': 'Seattle Seahawks',
        'SF': 'San Francisco 49ers',
        'TB': 'Tampa Bay Buccaneers',
        'TEN': 'Tennessee Titans',
        'WAS': 'Washington Commanders',
        # Historical names
        'OAK': 'Oakland Raiders',
        'SD': 'San Diego Chargers',
        'STL': 'St. Louis Rams'
    }
    
    # Convert team abbreviations to full names
    nflfastr_stats['team'] = nflfastr_stats['team'].map(team_name_map)
    nflfastr_stats['home_team'] = nflfastr_stats['home_team'].map(team_name_map)
    nflfastr_stats['away_team'] = nflfastr_stats['away_team'].map(team_name_map)
    
    # Create separate dataframes for home and away teams
    home_stats = nflfastr_stats[
        nflfastr_stats['team'] == nflfastr_stats['home_team']
    ].copy()
    
    away_stats = nflfastr_stats[
        nflfastr_stats['team'] == nflfastr_stats['away_team']
    ].copy()
    
    # Rename columns to indicate home/away
    home_cols = {col: f'home_{col}' for col in home_stats.columns 
                 if col not in ['game_id', 'season', 'week', 'home_team', 'away_team']}
    away_cols = {col: f'away_{col}' for col in away_stats.columns 
                 if col not in ['game_id', 'season', 'week', 'home_team', 'away_team']}
    
    home_stats = home_stats.rename(columns=home_cols)
    away_stats = away_stats.rename(columns=away_cols)
    
    # Merge home and away into single game row
    game_stats = home_stats.merge(
        away_stats,
        on=['game_id', 'season', 'week', 'home_team', 'away_team'],
        how='outer'
    )
    
    # Convert week to string to match spreadspoke format
    game_stats['week'] = game_stats['week'].astype(str)
    
    # Merge with spreadspoke data
    merged_df = spreadspoke_df.merge(
        game_stats,
        left_on=['schedule_season', 'schedule_week', 'team_home', 'team_away'],
        right_on=['season', 'week', 'home_team', 'away_team'],
        how='left'
    )
    
    # Drop duplicate columns
    merged_df = merged_df.drop(columns=['season', 'week', 'home_team', 'away_team', 'game_id'], 
                                errors='ignore')
    
    # Count how many games got nflfastR data
    n_matched = merged_df['home_epa_per_play'].notna().sum()
    n_total = len(merged_df)
    print(f"✓ Matched nflfastR data for {n_matched:,}/{n_total:,} games ({n_matched/n_total*100:.1f}%)")
    
    return merged_df


def load_data_with_nflfastr(seasons=None, cache=True, use_nflfastr=True):
    """
    Complete pipeline: load spreadspoke data and optionally merge nflfastR data.
    
    Args:
        seasons: List of seasons for nflfastR (None = 2015-2024)
        cache: Whether to cache nflfastR downloads
        use_nflfastr: Whether to load nflfastR data (False = spreadspoke only)
        
    Returns:
        pd.DataFrame: Dataset with or without nflfastR features
    """
    
    # Load base spreadspoke data
    df = load_data()
    if df is None:
        return None
    
    # Optionally add nflfastR data
    if use_nflfastr:
        if not NFL_DATA_AVAILABLE:
            print("\nWARNING: nfl_data_py not installed!")
            print("Install with: pip install nfl_data_py")
            print("Continuing with spreadspoke data only...\n")
            return df
        
        print("\n" + "="*60)
        print("LOADING nflfastR DATA")
        print("="*60)
        
        try:
            # Download play-by-play data
            pbp_data = download_nflfastr_data(seasons, cache)
            
            # Check if data was actually downloaded
            if pbp_data is None or len(pbp_data) == 0:
                print("\n⚠ No data returned from nflfastR")
                print("Continuing with spreadspoke data only...\n")
                return df
            
            # Aggregate into game-level stats
            team_stats = aggregate_team_stats(pbp_data)
            
            # Merge with spreadspoke
            df = merge_with_spreadspoke(df, team_stats)
            
            print("\n✓ nflfastR data integration complete!")
            print(f"✓ Added {len([col for col in df.columns if 'epa' in col.lower()])} EPA-related features")
            
        except ImportError as e:
            print(f"\n⚠ Import error: {e}")
            print("Make sure nfl_data_py is installed: pip install nfl_data_py")
            print("Continuing with spreadspoke data only...\n")
        except ValueError as e:
            print(f"\n⚠ Data error: {e}")
            print("This might be a connection issue. Try again later.")
            print("Continuing with spreadspoke data only...\n")
        except Exception as e:
            print(f"\n⚠ Unexpected error loading nflfastR data: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            print("\nFull traceback:")
            traceback.print_exc()
            print("\nContinuing with spreadspoke data only...\n")
    
    return df