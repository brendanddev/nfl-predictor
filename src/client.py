
""" 
client.py
A client for interacting with the Sleeper API.

Brendan Dileo, August 2025
"""

import requests
import json
from src.config import BASE_URL, USER_ID, LEAGUE_ID


class SleeperClient:
    
    def __init__(self, base_url=BASE_URL, user_id=USER_ID, league_id=LEAGUE_ID):
        self.base_url = base_url
        self.user_id = user_id
        self.league_id = league_id
        self.players_map = {}
        self.load_players("data/players.json")

    def _get(self, endpoint: str, params=None, headers=None):
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"GET request failed: {e}")
            return None
    
    def load_players(self, filename="players.json"):
        try:
            with open(filename, "r") as file:
                self.players_map = json.load(file)
        except FileNotFoundError:
            print(f"File {filename} not found.")
            self.players_map = {}
    
    def get_player_name(self, player_id):
        return self.players_map.get(player_id, {}).get("full_name", "Unknown")
        
    def pretty_print(self, data):
        print(json.dumps(data, indent=4))
    
    def get_user(self, identifier: str):
        return self._get(f"user/{identifier}")
    
    def get_league(self, league_id=None):
        league_id = league_id or self.league_id
        return self._get(f"league/{league_id}")
    
    def get_rosters(self, league_id=None):
        league_id = league_id or self.league_id
        return self._get(f"league/{league_id}/rosters")
    
    def get_trending_players(self, type="add", lookback_hours=24, limit=25):
        params = { "type": type, "lookback_hours": lookback_hours, "limit": limit }
        return self._get(f"players/nfl/trending/{type}", params=params)
    

    # TODO: Implement these functions
    
    # Get best performing players
    # Get best performing unclaimed players
    # Get average number of players per position per team
    # Get best peforming players per position
    # Get best performing teams
    