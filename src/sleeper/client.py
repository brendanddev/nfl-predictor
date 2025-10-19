
""" 
client.py
A client for interacting with the Sleeper API.

Brendan Dileo, August 2025
"""

import time
from typing import Counter
import requests
import json
from src.fantasy.config import BASE_URL, ALT_URL, USER_ID, LEAGUE_ID


class SleeperClient:
    
    def __init__(self, base_url=BASE_URL, alt_url=ALT_URL,user_id=USER_ID, league_id=LEAGUE_ID):
        self.base_url = base_url
        self.alt_url = alt_url
        self.user_id = user_id
        self.league_id = league_id
        self.players_map = {}
        self.load_players("data/players.json")
        self.cache = {}
        self.default_ttl = 600

    def _get(self, endpoint: str, params=None, headers=None, base_url=None):
        url = f"{(base_url or self.base_url).rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"GET request failed: {e}")
            return None
    
    def _get_cached(self, endpoint: str, params=None, ttl=None, base_url=None):
        ttl = ttl or self.default_ttl
        key = f"{endpoint}-{json.dumps(params, sort_keys=True)}"
        cached = self.cache.get(key)
        
        if cached:
            result, timestamp = cached
            if time.time() - timestamp < ttl:
                return result
        
        result = self._get(endpoint, params=params, base_url=base_url)
        if result is not None:
            self.cache[key] = (result, time.time())
        return result
    
    
    def load_players(self, filename="players.json"):
        try:
            with open(filename, "r") as file:
                self.players_map = json.load(file)
        except FileNotFoundError:
            print(f"File {filename} not found.")
            self.players_map = {}
    
    def get_player(self, player_id):
        return self.players_map.get(player_id, {})
    
    def get_player_name(self, player_id):
        return self.players_map.get(player_id, {}).get("full_name", "Unknown")
        
    def pretty_print(self, data):
        print(json.dumps(data, indent=4))
    
    def get_user(self, identifier: str):
        return self._get_cached(f"user/{identifier}")
    
    def get_league(self, league_id=None):
        league_id = league_id or self.league_id
        return self._get_cached(f"league/{league_id}")
    
    def get_rosters(self, league_id=None):
        league_id = league_id or self.league_id
        return self._get_cached(f"league/{league_id}/rosters")
    
    def get_weekly_matchups(self, league_id=None, week=None):
        league_id = league_id or self.league_id
        return self._get_cached(f"league/{league_id}/matchups/{week}")
    
    def get_player_stats(self, player_id, week=None, season=2025):
        params = {
            "season_type": "regular",
            "season": season,
            "grouping": "week"
        }

        data = self._get_cached(
            f"stats/nfl/player/{player_id}",
            params=params,
            base_url=self.alt_url
        )

        if not data:
            return {}

        if week:
            week_str = str(week)
            week_data = data.get(week_str)
            if week_data and "stats" in week_data:
                return week_data["stats"]
            return {}

        result = {}
        for w, week_data in data.items():
            if week_data and "stats" in week_data:
                result[w] = week_data["stats"]
        return result
    
    def get_trending_players(self, type="add", lookback_hours=24, limit=25):
        params = { "type": type, "lookback_hours": lookback_hours, "limit": limit }
        return self._get_cached(f"players/nfl/trending/{type}", params=params)
    
    def get_top_performers(self, week=None, limit=10, league_id=None):
        weekly_stats = self.get_player_stats_for_week(week=week, league_id=league_id)
        if not weekly_stats:
            return []
        top_performers = sorted(weekly_stats, key=lambda x: x["points"], reverse=True)
        return top_performers[:limit]
    
    def get_top_performing_teams(self, week=None, limit=10, league_id=None):
        week = week or 1
        league_id = league_id or self.league_id
        
        matchups = self.get_weekly_matchups(league_id=league_id, week=week)
        if not matchups:
            return []
        
        rosters = self.get_rosters(league_id=league_id)
        roster_map = {roster["roster_id"]: roster for roster in rosters}
        
        team_scores = []
        for matchup in matchups:
            roster_id = matchup["roster_id"]
            points = matchup["points"]
            
            roster_info = roster_map.get(roster_id, {})
            owner_id = roster_info.get("owner_id", "Unknown")
            owner_name = self.get_user(owner_id).get("display_name", "Unknown")
            
            team_scores.append({
                "roster_id": roster_id,
                "owner_name": owner_name,
                "points": points
            })
        
        return sorted(team_scores, key=lambda x: x["points"], reverse=True)[:limit]

    def get_top_performers_by_position(self, week=None, position=None, limit=10, league_id=None):
        weekly_stats = self.get_player_stats_for_week(week=week, league_id=league_id)
        if not weekly_stats:
            return []
        
        if position:
            weekly_stats = [stat for stat in weekly_stats if stat["position"] == position]
        
        top_performers = sorted(weekly_stats, key=lambda x: x["points"], reverse=True)
        return top_performers[:limit]
    
    def get_average_roster_composition(self, league_id=None):
        league_id = league_id or self.league_id
        rosters = self.get_rosters(league_id=league_id)
        if not rosters:
            return {}
        
        total_counts = Counter()
        num_teams = len(rosters)
        
        for roster in rosters:
            pos_counts = Counter()
            player_ids = roster.get("players", [])
            
            for pid in player_ids:
                player = self.get_player(pid)
                pos = player.get("position", "UNK")
                pos_counts[pos] += 1
            
            total_counts.update(pos_counts)
            
        avg_composition = {
            pos: total / num_teams
            for pos, total in total_counts.items()
        }
        return avg_composition

    def get_average_points_by_position(self, week=None, league_id=None):
        league_id = league_id or self.league_id
        week = week or 1
        
        matchups = self.get_weekly_matchups(league_id=league_id, week=week)
        if not matchups:
            return {}

        total_points = Counter()
        position_counts = Counter()
        
        for matchup in matchups:
            player_points = matchup.get("players_points", {})
            for pid, points in player_points.items():
                player = self.get_player(pid)
                pos = player.get("position", "UNK")
                total_points[pos] += points
                position_counts[pos] += 1
        
        avg_points = {
            pos: total_points[pos] / position_counts[pos]
            for pos in total_points
        }
        return avg_points    
    
    # TODO: Implement these functions
    # Get best performing unclaimed players