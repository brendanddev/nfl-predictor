
"""
train_model.py
Trains multiple models on NFL game data with proper time-based validation.

Handles splitting data chronologically, training multiple classifiers (Random Forest, XGBoost, 
LightGBM), hyperparameter tuning, and evaluating model accuracy.

Brendan Dileo, October 2025
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit

# Try to import XGBoost and LightGBM, handle if not installed
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except (ImportError, Exception) as e:
    XGBOOST_AVAILABLE = False
    print(f"XGBoost not available: {str(e)[:100]}")
    print("Install with: pip install xgboost")
    print("Mac users may also need: brew install libomp")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except (ImportError, Exception) as e:
    LIGHTGBM_AVAILABLE = False
    print(f"LightGBM not available: {str(e)[:100]}")
    print("Install with: pip install lightgbm")


def time_based_split(X, y, df, test_seasons=1):
    """
    Split data based on time (seasons) rather than random sampling.
    This prevents future data leakage.
    
    Args:
        X: Feature matrix
        y: Target vector
        df: Original dataframe with schedule_season column
        test_seasons: Number of most recent seasons to use for testing
        
    Returns:
        X_train, X_test, y_train, y_test
    """
    # Get the most recent seasons for testing
    max_season = df['schedule_season'].max()
    test_season_start = max_season - test_seasons + 1
    
    # Create masks
    train_mask = df['schedule_season'] < test_season_start
    test_mask = df['schedule_season'] >= test_season_start
    
    X_train = X[train_mask]
    X_test = X[test_mask]
    y_train = y[train_mask]
    y_test = y[test_mask]
    
    print(f"Training on seasons up to {test_season_start - 1}")
    print(f"Testing on seasons {test_season_start} to {max_season}")
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    return X_train, X_test, y_train, y_test


def train_random_forest(X_train, y_train, X_test, y_test, tune=False):
    """Train Random Forest with optional hyperparameter tuning."""
    
    if tune:
        print("\nTuning Random Forest hyperparameters...")
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 20, 30, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        rf = RandomForestClassifier(random_state=42)
        grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='accuracy', n_jobs=-1, verbose=1)
        grid_search.fit(X_train, y_train)
        
        print(f"Best parameters: {grid_search.best_params_}")
        model = grid_search.best_estimator_
    else:
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
    
    return model


def train_xgboost(X_train, y_train, X_test, y_test):
    """Train XGBoost classifier."""
    
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss'
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    return model


def train_lightgbm(X_train, y_train, X_test, y_test):
    """Train LightGBM classifier."""
    
    model = lgb.LGBMClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbose=-1
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        eval_metric='binary_logloss'
    )
    
    return model


def evaluate_model(model, X_test, y_test, model_name="Model"):
    """Evaluate model performance with multiple metrics."""
    
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, preds)
    auc = roc_auc_score(y_test, probs)
    
    print(f"\n{model_name} Results:")
    print(f"Accuracy: {acc * 100:.2f}%")
    print(f"ROC-AUC: {auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, preds, target_names=['Away Win', 'Home Win']))
    
    return acc, auc


def train_model(X, y, df, tune_rf=False, test_seasons=2):
    """
    Trains multiple models and compares their performance.
    
    Args:
        X (pd.DataFrame): Feature matrix
        y (pd.Series): Target labels
        df (pd.DataFrame): Original dataframe for time-based splitting
        tune_rf (bool): Whether to tune Random Forest hyperparameters
        test_seasons (int): Number of recent seasons to use for testing (default=2)
        
    Returns:
        dict: Dictionary of trained models
    """
    
    # Use time-based split instead of random split
    X_train, X_test, y_train, y_test = time_based_split(X, y, df, test_seasons=test_seasons)
    
    models = {}
    results = {}
    
    # Train Random Forest
    print("\n" + "="*50)
    print("Training Random Forest...")
    print("="*50)
    rf_model = train_random_forest(X_train, y_train, X_test, y_test, tune=tune_rf)
    models['Random Forest'] = rf_model
    acc, auc = evaluate_model(rf_model, X_test, y_test, "Random Forest")
    results['Random Forest'] = {'accuracy': acc, 'auc': auc}
    
    # Display feature importances for Random Forest
    feature_importances = pd.Series(rf_model.feature_importances_, index=X.columns)
    feature_importances = feature_importances.sort_values(ascending=False)
    print("\nTop 10 Feature Importances (Random Forest):")
    print(feature_importances.head(10))
    
    # Train XGBoost if available
    if XGBOOST_AVAILABLE:
        print("\n" + "="*50)
        print("Training XGBoost...")
        print("="*50)
        xgb_model = train_xgboost(X_train, y_train, X_test, y_test)
        models['XGBoost'] = xgb_model
        acc, auc = evaluate_model(xgb_model, X_test, y_test, "XGBoost")
        results['XGBoost'] = {'accuracy': acc, 'auc': auc}
    
    # Train LightGBM if available
    if LIGHTGBM_AVAILABLE:
        print("\n" + "="*50)
        print("Training LightGBM...")
        print("="*50)
        lgb_model = train_lightgbm(X_train, y_train, X_test, y_test)
        models['LightGBM'] = lgb_model
        acc, auc = evaluate_model(lgb_model, X_test, y_test, "LightGBM")
        results['LightGBM'] = {'accuracy': acc, 'auc': auc}
    
    # Print summary comparison
    print("\n" + "="*50)
    print("MODEL COMPARISON SUMMARY")
    print("="*50)
    results_df = pd.DataFrame(results).T
    results_df = results_df.sort_values('accuracy', ascending=False)
    print(results_df)
    
    # Return best model
    best_model_name = results_df.index[0]
    print(f"\nBest Model: {best_model_name} with {results_df.loc[best_model_name, 'accuracy']*100:.2f}% accuracy")
    
    return models[best_model_name], models