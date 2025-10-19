
""" 
main.py
A simple NFL game outcome prediction model using Random Forest.

Brendan Dileo, October 2025
"""

from utils.load_data import load_data
from utils.preprocess import preprocess
from utils.features import encode_features
from models.train_model import train_model

def main():
    df = load_data()
    if df is None:
        return

    df = preprocess(df)
    X, y = encode_features(df)
    model = train_model(X, y)

if __name__ == "__main__":
    main()
