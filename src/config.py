
""" 
config.py
Loads configuration variables from environment variables.

Brendan Dileo, August 2025
"""

import os
from dotenv import load_dotenv

load_dotenv()
USER_ID = os.getenv("USER_ID")
LEAGUE_ID = os.getenv("LEAGUE_ID")

if not USER_ID:
    raise ValueError("SLEEPER_USER_ID not set in environment variables!")

if not LEAGUE_ID:
    raise ValueError("LEAGUE_ID not set in environment variables!")

print(f"My Sleeper user ID is {USER_ID}")