
""" 
st_utils.py 
Defines utility functions for displaying SleeperClient data in a Streamlit dashboard.

Brendan Dileo, August 2025
"""


import streamlit as st
from src.client import SleeperClient

def st_user_info(client: SleeperClient, identifier: str):
    user = client.get_user(identifier)
    if not user: 
        st.error("User not found")
        return
    
    st.subheader("User Info")
    if user["avatar"]:
        st.image(f"https://sleepercdn.com/avatars/{user['avatar']}", width=100)
    
    st.write(f"**Display Name:** {user['display_name']}")
    st.write(f"**Username:** {user['username']}")
    st.write(f"**User ID:** {user['user_id']}\n")


def st_league_info(client: SleeperClient, league_id=None):
    league = client.get_league(league_id)
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