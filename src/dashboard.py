
""" 
dashboard.py
A simple Streamlit dashboard for visualizing fantasy football data.

Brendan Dileo, August 2025
"""

import streamlit as st
import pandas as pd

st.title("Fantasy Football Analyzer Dashboard")
week = st.sidebar.number_input("Select Week", min_value=1, max_value=18, value=1)