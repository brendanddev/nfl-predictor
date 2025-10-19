
""" 
config.py
Loads configuration variables from environment variables.

Brendan Dileo, August 2025
"""

import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL")
ALT_URL = os.getenv("ALTERNATE_URL")
USER_ID = os.getenv("USER_ID")
LEAGUE_ID = os.getenv("LEAGUE_ID")

if not BASE_URL or not ALT_URL or not USER_ID or not LEAGUE_ID:
    raise ValueError("One or more environment variables are missing. Please check your .env file.")