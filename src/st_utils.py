
""" 
st_utils.py 
Defines utility functions for displaying SleeperClient data in a Streamlit dashboard.

Brendan Dileo, August 2025
"""


import streamlit as st
from src.client import SleeperClient

@st.cache_data(ttl=600)
def get_user_cached(client: SleeperClient, identifier: str):
    return client.get_user(identifier)

@st.cache_data(ttl=600)
def get_league_cached(client: SleeperClient, league_id=None):
    return client.get_league(league_id)

@st.cache_data(ttl=600)
def get_rosters_cached(client: SleeperClient, league_id=None):
    return client.get_rosters(league_id)

@st.cache_data(ttl=600)
def get_trending_players_cached(client: SleeperClient, type="add", limit=10):
    return client.get_trending_players(type=type, limit=limit)



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
        players = [client.get_player_name(pid) for pid in player_ids]
        
        st.write(f"**Roster ID:** {roster['roster_id']} - **Owner:** {owner}")
        st.write(f"**Players:** {', '.join(players)}\n")


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