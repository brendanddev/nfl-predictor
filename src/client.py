
""" 
client.py

"""

import requests
import json
from config import BASE_URL, USER_ID, LEAGUE_ID


class SleeperClient:
    
    def __init__(self, base_url=BASE_URL, user_id=USER_ID, league_id=LEAGUE_ID):
        self.base_url = base_url
        self.user_id = user_id
        self.league_id = league_id

    def _get(self, endpoint: str, params=None, headers=None):
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"GET request failed: {e}")
            return None
        
    def pretty_print(self, data):
        print(json.dumps(data, indent=4))
    
    def get_user(self, identifier: str):
        return self._get(f"user/{identifier}")