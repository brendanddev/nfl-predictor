
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

# Sidebar for user input
st.sidebar.header("User & League Settings")
username = st.sidebar.text_input("Sleeper Username", value="sleeperuser")
league_id = st.sidebar.text_input("League ID", value=client.league_id)

# Fetch user info
if st.sidebar.button("Get User Info"):
    stu.st_user_info(client, username)

# Fetch league info
if st.sidebar.button("Get League Info"):
    league = client.get_league(league_id)
    st.subheader("League Info")
    st.json(league)