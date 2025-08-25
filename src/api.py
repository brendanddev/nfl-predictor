
""" 
api.py
Provides a wrapper for the Sleeper API allowing retrieval of fantasy football data.
This is designed to work with a USER_ID stored in an environment variable but can
also accept alternative identifiers where needed.

See https://docs.sleeper.com/ for API documentation.

Brendan Dileo, August 2025
"""

import requests
import json

BASE_URL = "https://api.sleeper.app/v1"


def send_get(url, params=None, headers=None):
    """ Sends a GET request to the specified URL with optional parameters and headers """
    try: 
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"GET request failed: {e}")
        return None

def pretty_print_json(data):
    """ Pretty prints JSON data """
    print(json.dumps(data, indent=4))


def get_state():
    """ Retrieves the current state of the NFL """
    url = f"{BASE_URL}/state/nfl"
    return send_get(url)

def get_user(identifier: str):
    """ Retrieves a user object """
    url = f"{BASE_URL}/user/{identifier}"
    return send_get(url)

def get_all_users(league_id):
    """ Retrieves all users in a league """
    url = f"{BASE_URL}/league/{league_id}/users"
    return send_get(url)

def get_user_leagues(user_id, sport="nfl", season="2025"):
    """ Retrieves leagues for a user """
    url = f"{BASE_URL}/user/{user_id}/leagues/{sport}/{season}"
    return send_get(url)
    
def get_league(league_id):
    """ Retrieves a league object """
    url = f"{BASE_URL}/league/{league_id}"
    return send_get(url)

def get_league_rosters(league_id):
    """ Retrieves rosters for a league """
    url = f"{BASE_URL}/league/{league_id}/rosters"
    return send_get(url)

def get_matchups(league_id, week):
    """ Retrieves matchups for a league in a given week """
    url = f"{BASE_URL}/league/{league_id}/matchups/{week}"
    return send_get(url)

def get_user_draft(user_id, sport="nfl", season="2025"):
    """ Retrieves drafts for a user """
    url = f"{BASE_URL}/user/{user_id}/drafts/{sport}/{season}"
    return send_get(url)

def get_trending_players(sport="nfl", type="adds", lookback_hours=24, limit=25):
    """ Retrieves trending players based on adds or drops in the past 24 hours """
    url = f"{BASE_URL}/players/{sport}/trending/{type}"
    params = {
        "lookback_hours": lookback_hours,
        "limit": limit
    }
    return send_get(url, params=params)
    
    