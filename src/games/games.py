
""" 
games.py

Brendan Dileo, October 2025
"""

import pandas as pd
import nfl_data_py as nfl
from sklearn.ensemble import GradientBoostingClassifier


games = nfl.import_schedules([2020, 2021, 2022, 2023])
team_stats = nfl.import_team_desc()

