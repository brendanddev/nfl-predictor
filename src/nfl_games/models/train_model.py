
"""
train_model.py
Trains a Random Forest model on NFL game data.

Handles splitting data into training and tests, training a random forest classifier, 
evaluating model accuracy, and printing feature importances.

Brendan Dileo, October 2025
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def train_model(X, y):
    """
    Trains a Random Forest model and evaluates its accuracy.

    Args:
        X (pd.DataFrame): Feature matrix
        y (pd.Series): Target labels

    Returns:
        model (RandomForestClassifier): Trained model
    """

    # Split data into training (80%) and test (20%) sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Initialize and train Random Forest Classifier
    # n_estimators = 100 trees, random_state for reproducibility
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Make predictions and calculate accuracy
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Model trained! Accuracy: {acc * 100:.2f}%")

    # Display feature importances to understand what model is using
    feature_importances = pd.Series(model.feature_importances_, index=X.columns)
    feature_importances = feature_importances.sort_values(ascending=False)
    print("\nFeature Importances:")
    print(feature_importances)

    return model
