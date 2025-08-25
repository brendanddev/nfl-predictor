
""" 
analyzer.py

Brendan Dileo, August 2025
"""

from src.config import USER_ID, LEAGUE_ID
from src.api import *


class FantasyAnalyzer:
    
    def __init__(self, league_id=LEAGUE_ID):
        self.league_id = league_id
        self.league_data = None
        self.rosters = None
        self.users = None
        self.load_league_data()
    
    def load_league_data(self):
        """Load basic league data"""
        league_resp = get_league(self.league_id)
        rosters_resp = get_league_rosters(self.league_id)
        users_resp = get_all_users(self.league_id)
        
        if league_resp and rosters_resp and users_resp:
            self.league_data = league_resp.json()
            self.rosters = rosters_resp.json()
            self.users = users_resp.json()