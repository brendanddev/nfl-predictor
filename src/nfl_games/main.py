
""" 
main.py
An improved NFL game outcome prediction model using multiple classifiers.

Brendan Dileo, October 2025
"""

from utils.load_data import load_data
from utils.preprocess import preprocess
from utils.features import encode_features
from models.train_model import train_model

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
    X, y, df = encode_features(df)
    
    print(f"\nTotal features: {X.shape[1]}")
    print(f"Feature names: {list(X.columns)}")
    
    # Train models
    best_model, all_models = train_model(X, y, df, tune_rf=False, test_seasons=2)
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)

if __name__ == "__main__":
    main()