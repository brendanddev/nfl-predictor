
""" 
client.py

"""

import requests
from config import BASE_URL, USER_ID, LEAGUE_ID


class SleeperClient:
    
    def __init__(self):
        self.url = BASE_URL
        self.user_id = USER_ID
        self.league_id = LEAGUE_ID

    def get(self, params=None, headers=None):
        try: 
            response = requests.get(self.url, params=params, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"GET request failed: {e}")
            return None