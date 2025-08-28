
""" 
app.py

Brendan Dileo, August 2025
"""

from src.client import SleeperClient

client = SleeperClient()
user = client.get_user("")
client.pretty_print(user)

trending_players = client.get_trending_players(limit=10)
client.pretty_print(trending_players)