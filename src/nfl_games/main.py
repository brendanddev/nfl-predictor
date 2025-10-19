
""" 
main.py
An improved NFL game outcome prediction model using multiple classifiers.

Brendan Dileo, October 2025
"""

from utils.load_data import load_data
from utils.preprocess import preprocess
from utils.features import encode_features
from models.train_model import train_model
from models.predict import interactive_predict, predict_current_week
from sklearn.preprocessing import LabelEncoder
import pandas as pd

def main():
    print("="*60)
    print("NFL Game Predictor")
    print("="*60)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Preprocess
    df = preprocess(df)
    
    # Feature engineering (returns df for time-based splitting)
    X, y, df_processed = encode_features(df)
    
    print(f"\nTotal features: {X.shape[1]}")
    print(f"Feature names: {list(X.columns)}")
    
    # Train models (set tune_rf=True to enable hyperparameter tuning - takes longer)
    # Use test_seasons=2 for more reliable testing (tests on 2024-2025 instead of just 2025)
    best_model, all_models = train_model(X, y, df_processed, tune_rf=False, test_seasons=2)
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    
    # Create encoder for predictions
    all_teams = pd.concat([df["team_home"], df["team_away"]]).unique()
    encoder = LabelEncoder()
    encoder.fit(all_teams)
    
    # Interactive prediction menu
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
            interactive_predict(best_model, df, encoder)
        elif choice == "2":
            season = input("Enter season year (default=2025): ").strip()
            season = int(season) if season else 2025
            week = input("Enter week number (default=8): ").strip()
            week = int(week) if week else 8
            predict_current_week(best_model, df, encoder, season, week)
        elif choice == "3":
            print("\nThanks for using NFL Game Predictor!")
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()