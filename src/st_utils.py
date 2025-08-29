
""" 
st_utils.py 
Defines utility functions for displaying SleeperClient data in a Streamlit dashboard.

Brendan Dileo, August 2025
"""


import streamlit as st
from src.client import SleeperClient
from collections import Counter, defaultdict

@st.cache_data(ttl=600)
def get_user_cached(_client, identifier: str):
    return _client.get_user(identifier)

@st.cache_data(ttl=600)
def get_league_cached(_client, league_id=None):
    return _client.get_league(league_id)

@st.cache_data(ttl=600)
def get_rosters_cached(_client, league_id=None):
    return _client.get_rosters(league_id)

@st.cache_data(ttl=600)
def get_trending_players_cached(_client, type="add", limit=10):
    return _client.get_trending_players(type=type, limit=limit)



def st_user_info(user):
    if not user: 
        st.error("User not found")
        return
    
    st.subheader("User Info")
    if user["avatar"]:
        st.image(f"https://sleepercdn.com/avatars/{user['avatar']}", width=100)
    
    st.write(f"**Display Name:** {user['display_name']}")
    st.write(f"**Username:** {user['username']}")
    st.write(f"**User ID:** {user['user_id']}\n")

def st_league_info(league):
    if not league:
        st.error("League not found")
        return
    
    st.subheader("League Info")
    st.write(f"**League Name:** {league['name']}")
    st.write(f"**Status:** {league['status']}")
    st.write(f"**Season:** {league['season']}")
    st.write(f"**Season Type:** {league['season_type']}")
    st.write(f"**Sport:** {league['sport']}")
    st.write(f"**Total Rosters:** {league['total_rosters']}\n")

def st_rosters(rosters, client: SleeperClient):
    if not rosters:
        st.error("No rosters found")
        return
    
    st.subheader("Rosters")
    for roster in rosters:
        owner_id = roster["owner_id"]
        owner = client.get_user(owner_id)["display_name"]
        player_ids = roster["players"]
        
        grouped = defaultdict(list)
        for pid in player_ids:
            player_name = client.get_player_name(pid)
            player_info = client.get_player(pid)
            pos = player_info.get("position", "UNK")
            grouped[pos].append(player_name)

        counts = Counter([client.get_player(pid).get("position", "UNK") for pid in player_ids])
        total_players = len(player_ids)

        with st.expander(f"Roster {roster['roster_id']} - {owner}"):
            st.write(f"**Total Players:** {total_players}")
            st.write("**By Position:** " + ", ".join([f"{pos}: {cnt}" for pos, cnt in counts.items()]))

            for pos, names in grouped.items():
                st.markdown(f"**{pos}**: {', '.join(names)}")

def st_team_names(rosters, client: SleeperClient):
    if not rosters:
        st.error("No rosters found")
        return

    st.subheader("Team Names")
    for roster in rosters:
        owner_id = roster["owner_id"]
        owner = client.get_user(owner_id)["display_name"]
        st.write(f"**Roster ID:** {roster['roster_id']} - **Owner:** {owner}")

def st_trending_players(trending, client: SleeperClient):
    if not trending:
        st.error("No trending players found")
        return
    
    st.subheader("Trending Players")
    for player in trending:
        name = client.get_player_name(player["player_id"])
        st.write(f"**{name}** - Count: {player['count']}")