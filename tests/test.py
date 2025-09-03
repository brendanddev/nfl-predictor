
""" 
test.py
Defines simple tests for the SleeperClient.

Brendan Dileo, September 2025
"""

from src.client import SleeperClient

client = SleeperClient()
client.load_players("data/players.json")

# Fetch and print user info
player = client.get_player("1234")
print(player["full_name"], player["position"], player["team"])


projections = client.get_projections(season=2025, week=1)
print(projections[:10])