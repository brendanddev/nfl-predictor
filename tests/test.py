
""" 
test.py
Defines simple tests for the SleeperClient.

Brendan Dileo, September 2025
"""

from src.client import SleeperClient

client = SleeperClient()
client.load_players("data/players.json")


avg_comp = client.get_average_roster_composition()
for position, avg in avg_comp.items():
    print(f"{position}: {avg:.2f}")