
""" 
dashboard.py
Fantasy Football Analuzer Dashboard using Streamlit.

Streamlit Documentation: https://docs.streamlit.io/

Brendan Dileo, August 2025
"""

import streamlit as st
from client import SleeperClient
import st_utils as stu

client = SleeperClient()

st.title("Fantasy Football Analyzer Dashboard")
username = st.text_input("Sleeper Username", value="sleeperuser")
league_id = st.text_input("League ID", value=client.league_id)

tab1, tab2, tab3, tab4 = st.tabs(["User Info", "League Info", "Rosters", "Trending Players"])

with tab1:
    if username:
        user_data = stu.get_user_cached(client, username)
        stu.st_user_info(user_data)
    else:
        st.info("Enter a Sleeper username in the sidebar to view user info.")

with tab2:
    if league_id:
        league_data = stu.get_league_cached(client, league_id)
        stu.st_league_info(league_data)
    else:
        st.info("Enter a League ID in the sidebar to view league info.")

with tab3:
    rosters_data = stu.get_rosters_cached(client, league_id)
    stu.st_rosters(rosters_data, client)

with tab4:
    trend_type = st.selectbox("Trend Type", options=["add", "drop", "claim"])
    limit = st.slider("Number of Players", min_value=5, max_value=50, value=10)
    trending_data = stu.get_trending_players_cached(client, type=trend_type, limit=limit)
    stu.st_trending_players(trending_data, client)