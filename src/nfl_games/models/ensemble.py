
"""
ensemble.py
Combines predictions from multiple models for better accuracy.

Brendan Dileo, October 2025
"""

import numpy as np
from sklearn.metrics import accuracy_score, roc_auc_score


class EnsembleModel:
    """
    Ensemble model that combines predictions from multiple models.
    Uses weighted averaging based on individual model performance.
    """
    
    def __init__(self, models, weights=None):
        """
        Args:
            models: List of trained models
            weights: List of weights for each model (default: equal weights)
        """
        self.models = models
        if weights is None:
            self.weights = [1.0 / len(models)] * len(models)
        else:
            # Normalize weights to sum to 1
            total = sum(weights)
            self.weights = [w / total for w in weights]
    
    def predict_proba(self, X):
        """
        Get weighted average of probability predictions.
        
        Args:
            X: Feature matrix
            
        Returns:
            Array of probabilities
        """
        predictions = []
        for model in self.models:
            predictions.append(model.predict_proba(X))
        
        # Weighted average
        ensemble_proba = np.zeros_like(predictions[0])
        for pred, weight in zip(predictions, self.weights):
            ensemble_proba += pred * weight
        
        return ensemble_proba
    
    def predict(self, X):
        """Get class predictions."""
        proba = self.predict_proba(X)
        return (proba[:, 1] > 0.5).astype(int)


def create_ensemble(all_models, X_test, y_test):
    """
    Create an ensemble from all trained models.
    Weights models by their individual accuracy.
    
    Args:
        all_models: Dict of {'model_name': model}
        X_test: Test features
        y_test: Test labels
        
    Returns:
        EnsembleModel: Weighted ensemble
    """
    
    models = []
    weights = []
    
    print("\n" + "="*60)
    print("CREATING ENSEMBLE MODEL")
    print("="*60)
    
    for name, model in all_models.items():
        models.append(model)
        
        # Calculate accuracy for weighting
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        weights.append(acc)
        
        print(f"{name}: accuracy={acc:.4f}, weight={acc:.4f}")
    
    # Create ensemble
    ensemble = EnsembleModel(models, weights)
    
    # Evaluate ensemble
    ensemble_preds = ensemble.predict(X_test)
    ensemble_proba = ensemble.predict_proba(X_test)[:, 1]
    
    ensemble_acc = accuracy_score(y_test, ensemble_preds)
    ensemble_auc = roc_auc_score(y_test, ensemble_proba)
    
    print(f"\nEnsemble: accuracy={ensemble_acc:.4f}, auc={ensemble_auc:.4f}")
    print("="*60)
    
    return ensemble
