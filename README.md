# NFL Predictor

NFL Predictor is a Python project for predicting NFL game outcomes using historical data and machine learning. It also includes a **unofficial Python wrapper** for the Sleeper fantasy football API.
It provides a modular framework to preprocess data, engineer features, train models, and evaluate predictions.

---

## Overview

NFL Predictor focuses on:
- Predicting home team wins for NFL games using historical game data.
- Using rolling statistics (points scored, points allowed, win percentages) as predictive features.
- Evaluating model performance and inspecting feature importance.
- Easily extending the pipeline with new features, models, or data sources.

The Sleeper Client API Wrapper allows users to:
- Fetch user profiles, league info, team rosters, and trending players.
- Explore data via a Streamlit dashboard for interactive exploration (top performers, team insights, trending players).

---

## Features

- NFL Game Prediction
  - Train models to predict home team wins.
  - Modular ML pipeline (Random Forest; expandable to XGBoost/LightGBM).
  - Feature engineering includes:
    - Rolling statistics for last N games (offense, defense, win %)
    - Difference features: home vs away
    - Team encoding and Vegas spreads
  - Evaluate model accuracy and inspect feature importances.
- Optional Fantasy Utilities (Sleeper API)
  - Fetch user profiles, league info, team rosters, and trending players.
  - Streamlit dashboard for interactive exploration (top performers, team insights, trending players).


> ⚠️ Disclaimer: This project is **not affiliated with Sleeper**.
> It uses Sleeper’s **read-only public API**, documented here: [https://docs.sleeper.com/](https://docs.sleeper.com/).

---

## Installation

```bash
git clone https://github.com/brendanddev/nfl-predictor
cd nfl-predictor
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

---
