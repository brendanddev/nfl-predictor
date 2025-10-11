
""" 
test.py
Defines simple tests for the SleeperClient.

Brendan Dileo, September 2025
"""

from src.fantasy.client import SleeperClient

client = SleeperClient()
client.load_players("data/players.json")