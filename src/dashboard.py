
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
        stu.st_user_info(client, username)
    else:
        st.info("Enter a Sleeper username in the sidebar to view user info.")

with tab2:
    if league_id:
        stu.st_league_info(client, league_id)
    else:
        st.info("Enter a League ID in the sidebar to view league info.")