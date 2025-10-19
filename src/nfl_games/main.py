
""" 
main.py
A simple NFL game outcome prediction model using Random Forest.

Brendan Dileo, October 2025
"""

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load data
data_path = "data/spreadspoke_scores.csv"
df = pd.read_csv(data_path)

print("Data loaded successfully!")
print(f"Rows: {len(df)}, Columns: {len(df.columns)}\n")

print(df.head())

print("\nColumns:")
print(df.columns.tolist())

# Create label for home team wins
df = df.dropna(subset=["score_home", "score_away"])
df["home_team_won"] = (df["score_home"] > df["score_away"]).astype(int)

print("\nAdded target column 'home_team_won'")
print(df[["team_home", "team_away", "score_home", "score_away", "home_team_won"]].head())

print("\nHome win %:", round(df["home_team_won"].mean() * 100, 2), "%")


# Encode team names as numbers
enc = LabelEncoder()
df["home_enc"] = enc.fit_transform(df["team_home"])
df["away_enc"] = enc.fit_transform(df["team_away"])
df["favorite_enc"] = enc.fit_transform(df["team_favorite_id"])

# Replace missing spread values with 0
df["spread_favorite"] = df["spread_favorite"].fillna(0)

# Feature set
X = df[["home_enc", "away_enc", "favorite_enc", "spread_favorite"]]
y = df["home_team_won"]


# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# Predict and evaluate
preds = model.predict(X_test)
acc = accuracy_score(y_test, preds)

print(f"\nModel trained! Accuracy: {acc * 100:.2f}%")
