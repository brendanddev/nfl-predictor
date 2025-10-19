
"""
save_model.py
Handles saving and loading trained models and encoders.

Brendan Dileo, October 2025
"""

import pickle
import os
from datetime import datetime


def save_model(model, encoder, filename=None, model_dir="saved_models"):
    """
    Save trained model and encoder to disk.
    
    Args:
        model: Trained model to save
        encoder: LabelEncoder for teams
        filename: Optional filename (default: auto-generated with timestamp)
        model_dir: Directory to save models
        
    Returns:
        str: Path to saved model file
    """
    # Create directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    
    # Generate filename with timestamp if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nfl_model_{timestamp}.pkl"
    
    filepath = os.path.join(model_dir, filename)
    
    # Save both model and encoder together
    model_data = {
        "model": model,
        "encoder": encoder,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(filepath, "wb") as f:
        pickle.dump(model_data, f)
    
    print(f"\n✓ Model saved to: {filepath}")
    return filepath


def load_model(filepath):
    """
    Load a trained model and encoder from disk.
    
    Args:
        filepath: Path to saved model file
        
    Returns:
        tuple: (model, encoder)
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Model file not found: {filepath}")
    
    with open(filepath, "rb") as f:
        model_data = pickle.load(f)
    
    print(f"✓ Model loaded from: {filepath}")
    print(f"  Saved on: {model_data.get('timestamp', 'Unknown')}")
    
    return model_data["model"], model_data["encoder"]


def list_saved_models(model_dir="saved_models"):
    """
    List all saved models in the directory.
    
    Args:
        model_dir: Directory containing saved models
        
    Returns:
        list: List of saved model filenames
    """
    if not os.path.exists(model_dir):
        return []
    
    models = [f for f in os.listdir(model_dir) if f.endswith(".pkl")]
    models.sort(reverse=True)  # Most recent first
    
    return models


def get_latest_model(model_dir="saved_models"):
    """
    Get the path to the most recently saved model.
    
    Args:
        model_dir: Directory containing saved models
        
    Returns:
        str: Path to latest model, or None if no models exist
    """
    models = list_saved_models(model_dir)
    
    if not models:
        return None
    
    return os.path.join(model_dir, models[0])