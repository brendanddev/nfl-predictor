
""" 
api.py

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

if __name__ == "__main__":
    main()
    
    