
""" 
dashboard.py
Fantasy Football Analuzer Dashboard using Streamlit.

Streamlit Documentation: https://docs.streamlit.io/

Brendan Dileo, August 2025
"""

import streamlit as st
from src.fantasy.client import SleeperClient
import src.fantasy.st_utils as stu
import time

client = SleeperClient()

st.title("Fantasy Football Analyzer Dashboard")
username = st.text_input("Sleeper Username", value="sleeperuser")
league_id = st.text_input("League ID", value=client.league_id)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["User Info", "League Info", "Rosters", "Trending Players", "Analysis"])

with tab1:
    if username:
        with st.spinner("Loading user info..."):
            user_data = stu.get_user_cached(client, username)
            time.sleep(1)
        stu.st_user_info(user_data)
    else:
        st.info("Enter a Sleeper username in the sidebar to view user info.")

with tab2:
    if league_id:
        with st.spinner("Loading league info..."):
            league_data = stu.get_league_cached(client, league_id)
            time.sleep(1)
        stu.st_league_info(league_data)
    else:
        st.info("Enter a League ID in the sidebar to view league info.")

with tab3:
    with st.spinner("Loading rosters..."):
        rosters_data = stu.get_rosters_cached(client, league_id)
        time.sleep(1)
    stu.st_rosters(rosters_data, client)

with tab4:
    trend_type = st.selectbox("Trend Type", options=["add", "drop", "claim"])
    limit = st.slider("Number of Players", min_value=5, max_value=50, value=10)
    
    with st.spinner("Loading trending players..."):
        trending_data = stu.get_trending_players_cached(client, type=trend_type, limit=limit)
        time.sleep(1)
    stu.st_trending_players(trending_data, client)

with tab5:
    st.header("Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.spinner("Loading top performers..."):
            top_performers = client.get_top_performers(week=1, limit=10, league_id=league_id)
            time.sleep(1)
        stu.st_top_performers(top_performers, week=1)
    
    with col2:
        with st.spinner("Loading top performing teams..."):
            top_teams = client.get_top_performing_teams(week=1, limit=10, league_id=league_id)
            time.sleep(1)
        stu.st_top_performing_teams(top_teams, week=1)
    
    col3, col4 = st.columns(2)
    
    with col3:
        position = st.selectbox("Position", options=["QB", "RB", "WR", "TE", "K", "DEF"])
        with st.spinner(f"Loading top {position} performers..."):
            top_position_performers = client.get_top_performers_by_position(week=1, position=position, limit=10, league_id=league_id)
            time.sleep(1)
        stu.st_top_performers(top_position_performers, week=1)
    
    with col4:
        with st.spinner("Calculating average roster composition..."):
            avg_composition = client.get_average_roster_composition(league_id=league_id)
            time.sleep(1)
        stu.st_average_roster_composition(avg_composition)