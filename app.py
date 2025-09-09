
""" 
app.py
Provides a command line example of using the SleeperClient.

Brendan Dileo, August 2025
"""

from src.client import SleeperClient
from src.utils import print_player_stats, print_average_points_by_position, print_average_roster_composition, print_rosters, print_team_names, print_league_info, print_user_info, print_trending_players, print_top_performers_by_position, print_top_performers, print_top_performing_teams

client = SleeperClient()
client.load_players("data/players.json")

# print_user_info(client, client.user_id)
# print_league_info(client)
# print_rosters(client)
# print_team_names(client)
# print_trending_players(client, type="add", limit=10)
# print_top_performers(client, week=1, limit=10)
# print_top_performing_teams(client, week=1, limit=10)
# print_top_performers_by_position(client, week=1, position="RB", limit=10)
# print_average_roster_composition(client)
# print_average_points_by_position(client)

print_player_stats(client, "6794", week=1)