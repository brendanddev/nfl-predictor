
""" 
main.py
An improved NFL game outcome prediction model using multiple classifiers.

Brendan Dileo, October 2025
"""

from utils.load_data import load_data_with_nflfastr
from utils.preprocess import preprocess
from utils.features import encode_features
from models.train_model import train_model
from models.predict import interactive_predict, predict_current_week
from models.ensemble import create_ensemble
from utils.save_model import save_model, load_model, get_latest_model, list_saved_models
from sklearn.preprocessing import LabelEncoder
import pandas as pd

def main():
    print("="*60)
    print("NFL Game Predictor - WITH nflfastR EPA DATA")
    print("="*60)
    
    # Check for existing saved models
    latest_model = get_latest_model()
    
    if latest_model:
        print(f"\nFound saved model: {latest_model}")
        use_saved = input("Load saved model? (y/n, default=n): ").strip().lower()
        
        if use_saved == 'y':
            # Load saved model
            prediction_model, encoder = load_model(latest_model)
            
            # Still need to load data for predictions
            df = load_data_with_nflfastr(
                seasons=list(range(2015, 2025)),
                cache=True,
                use_nflfastr=True
            )
            if df is None:
                return
            df = preprocess(df)
            
            print("\n✓ Model loaded successfully! Ready for predictions.")
            
            # Skip to prediction menu
            run_prediction_menu(prediction_model, df, encoder)
            return
    
    # Train new model
    print("\nTraining new model with nflfastR data...")
    
    # Ask if user wants to use nflfastR data
    print("\n" + "="*60)
    print("nflfastR DATA OPTIONS")
    print("="*60)
    print("nflfastR provides advanced EPA (Expected Points Added) metrics")
    print("- First download takes 2-5 minutes (~300MB)")
    print("- Subsequent runs are fast (uses cache)")
    print("- Expected accuracy boost: +3-5%")
    
    use_nflfastr = input("\nLoad nflfastR EPA data? (y/n, default=y): ").strip().lower()
    use_nflfastr = use_nflfastr != 'n'
    
    # Load data with or without nflfastR
    df = load_data_with_nflfastr(
        seasons=list(range(2015, 2025)),
        cache=True,
        use_nflfastr=use_nflfastr
    )
    
    if df is None:
        return
    
    # Preprocess
    df = preprocess(df)
    
    # Feature engineering (returns df for time-based splitting)
    X, y, df_processed = encode_features(df)
    
    # If we have EPA data, filter to games with EPA features (2015+)
    if use_nflfastr and 'home_rolling_epa' in df_processed.columns:
        has_epa = df_processed['home_rolling_epa'].notna()
        
        if has_epa.sum() > 0:
            print(f"\n✓ Filtering to {has_epa.sum():,} games with EPA data (2015+)")
            X = X[has_epa]
            y = y[has_epa]
            df_processed = df_processed[has_epa]
        else:
            print("\n⚠ No EPA data found. Training without EPA features.")
    
    print(f"\n{'='*60}")
    print(f"FEATURE SUMMARY")
    print(f"{'='*60}")
    print(f"Total features: {X.shape[1]}")
    print(f"Total games: {len(X):,}")
    print(f"\nFeature names:")
    for i, col in enumerate(X.columns, 1):
        print(f"  {i:2d}. {col}")
    
    # Create encoder for predictions
    all_teams = pd.concat([df["team_home"], df["team_away"]]).unique()
    encoder = LabelEncoder()
    encoder.fit(all_teams)
    
    # Train models (set tune_rf=True to enable hyperparameter tuning - takes longer)
    # Use test_seasons=2 for more reliable testing (tests on 2023-2024 instead of just 2024)
    print(f"\n{'='*60}")
    print("TRAINING MODELS")
    print(f"{'='*60}")
    
    best_model, all_models, X_train, X_test, y_train, y_test = train_model(
        X, y, df_processed, tune_rf=False, test_seasons=2
    )
    
    # Create ensemble model if multiple models available
    if len(all_models) > 1:
        ensemble_model = create_ensemble(all_models, X_test, y_test)
        print("\n✓ Using ensemble model for predictions (combines all models)")
        prediction_model = ensemble_model
    else:
        print(f"\n✓ Using {list(all_models.keys())[0]} for predictions")
        prediction_model = best_model
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    
    # Ask to save model
    save_choice = input("\nSave this model for future use? (y/n, default=y): ").strip().lower()
    if save_choice != 'n':
        save_model(prediction_model, encoder)
    
    # Run prediction menu
    run_prediction_menu(prediction_model, df, encoder)


def run_prediction_menu(prediction_model, df, encoder):
    """Run the interactive prediction menu."""
    while True:
        print("\n" + "="*60)
        print("What would you like to do?")
        print("="*60)
        print("1. Predict a specific matchup")
        print("2. Predict current week games")
        print("3. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            interactive_predict(prediction_model, df, encoder)
        elif choice == "2":
            season = input("Enter season year (default=2025): ").strip()
            season = int(season) if season else 2025
            week = input("Enter week number (default=8): ").strip()
            week = int(week) if week else 8
            predict_current_week(prediction_model, df, encoder, season, week)
        elif choice == "3":
            print("\nThanks for using NFL Game Predictor!")
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()