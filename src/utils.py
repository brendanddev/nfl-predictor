
""" 
utils.py
Defines utility functions for displaying SleeperClient data.

Brendan Dileo, August 2025
"""


from src.client import SleeperClient


def print_user_info(client: SleeperClient, identifier: str):
    user = client.get_user(identifier)
    if user:
        display_name = user["display_name"]
        username = user["username"]
        user_id = user["user_id"]
        
        print("User Info")
        print(f"Display Name: {display_name}")
        print(f"Username: {username}")
        print(f"User ID: {user_id}\n")

def print_league_info(client: SleeperClient):
    league = client.get_league()
    league_name = league["name"]
    league_status = league["status"]
    league_season = league["season"]
    league_season_type = league["season_type"]
    league_sport = league["sport"]
    total_rosters = league["total_rosters"]

    print(f"League Name: {league_name}")
    print(f"Status: {league_status}")
    print(f"Season: {league_season}")
    print(f"Season Type: {league_season_type}")
    print(f"Sport: {league_sport}")
    print(f"Total Rosters: {total_rosters}\n")

def print_team_names(client: SleeperClient):
    rosters = client.get_rosters()
    for roster in rosters:
        owner_id = roster["owner_id"]
        owner = client.get_user(owner_id)["display_name"]
        print(f"Roster ID: {roster['roster_id']} - Owner: {owner}")

def print_rosters(client: SleeperClient):
    rosters = client.get_rosters()
    for roster in rosters:
        owner_id = roster["owner_id"]
        owner = client.get_user(owner_id)["display_name"]
        player_ids = roster["players"]
        players = [client.get_player_name(pid) for pid in player_ids]
        
        print(f"Roster ID: {roster['roster_id']} - Owner: {owner}")
        print(f"Players: {', '.join(players)}\n")

def print_trending_players(client: SleeperClient, type="add", limit=10):
    trending = client.get_trending_players(type=type, limit=limit)
    for player in trending:
        name = client.get_player_name(player["player_id"])
        print(f"{name} - Count: {player['count']}")

def print_top_performers(client: SleeperClient, week=1, limit=10):
    top_performers = client.get_top_performers(week=week, limit=limit)
    print(f"\n=== Top Performers Week {week} ===")
    for performer in top_performers:
        print(f"{performer['full_name']} ({performer['position']}, {performer['team']}): {performer['points']} pts")

def print_top_performing_teams(client: SleeperClient, week=1, limit=10):
    top_teams = client.get_top_performing_teams(week=week, limit=limit)
    print(f"\n=== Best Performing Teams Week {week} ===")
    for team in top_teams:
        print(f"{team['owner_name']}: {team['points']} pts")

def print_top_performers_by_position(client: SleeperClient, week=1, position="WR", limit=10):
    top_performers = client.get_top_performers_by_position(week=week, position=position, limit=limit)
    print(f"\n=== Top {position} Performers Week {week} ===")
    for performer in top_performers:
        print(f"{performer['full_name']} ({performer['team']}): {performer['points']} pts")
    
def print_average_roster_composition(client: SleeperClient):
    avg_comp = client.get_average_roster_composition()
    print("\n=== Average Roster Composition ===")
    for position, avg in avg_comp.items():
        print(f"{position}: {avg:.2f}")