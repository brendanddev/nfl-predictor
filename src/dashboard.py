
""" 
dashboard.py
A simple Streamlit dashboard for visualizing fantasy football data.

Brendan Dileo, August 2025
"""

import streamlit as st
import pandas as pd
from api import get_user, get_league, get_matchups, USER_ID, LEAGUE_ID

st.title("Fantasy Football Analyzer Dashboard")
week = st.sidebar.number_input("Select Week", min_value=1, max_value=18, value=1)

# User info
user = get_user(USER_ID).json()
st.subheader("User Info")
st.write(f"Name: {user['display_name']}")
st.write(f"User ID: {user['user_id']}")

# League info
league = get_league(LEAGUE_ID).json()
st.subheader("League Info")
st.write(f"League Name: {league['name']}")

# Matchups for selected week
matchups = get_matchups(LEAGUE_ID, week).json()
st.subheader(f"Week {week} Matchups")
for m in matchups:
    st.write(m)

# Button to refresh data
if st.button("Refresh Data"):
    st.experimental_rerun()