
""" 
app.py
Provides a command line example of using the SleeperClient.

Brendan Dileo, August 2025
"""

from src.client import SleeperClient
from src.utils import print_rosters, print_team_names, print_league_info, print_user_info, print_trending_players

client = SleeperClient()
client.load_players("data/players.json")

# print_user_info(client, client.user_id)
# print_league_info(client)
# print_rosters(client)
# print_team_names(client)
# print_trending_players(client, type="add", limit=10)


# top_peformers = client.get_top_performers(week=1, limit=10)
# print("Top Performers")
# for performer in top_peformers:
#     print(f"{performer['full_name']} ({performer['position']}, {performer['team']}): {performer['points']} points")
