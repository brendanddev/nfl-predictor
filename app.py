
""" 
app.py
Provides a command line example of using the SleeperClient.

Brendan Dileo, August 2025
"""

from src.client import SleeperClient

client = SleeperClient()
client.load_players("data/players.json")

user = client.get_user("brendandileo")
client.pretty_print(user)

trending = client.get_trending_players(type="add", limit=10)
for player in trending:
    name = client.get_player_name(player["player_id"])
    print(f"{name} - Count: {player['count']}")