# Fantasy Analyzer

Fantasy Analyzer is an **unofficial Python wrapper** for the Sleeper fantasy football API.
It allows you to easily fetch user, league, roster, and matchup data for analysis and tracking.

> ⚠️ Disclaimer: This project is **not affiliated with Sleeper**.
> It uses Sleeper’s **read-only public API**, documented here: [https://docs.sleeper.com/](https://docs.sleeper.com/).

---

## Overview

Fantasy Analyzer helps fantasy football managers and analysts to:

- Fetch and inspect user profiles, including display names and avatars.
- Explore league details (status, season, total rosters, etc.).
- View team rosters with player names.
- Track trending NFL players over time (adds, drops, trades).
- Use a clean **Streamlit dashboard** for interactive exploration.

The library is split into:

- `client.py` → Core API wrapper for Sleeper endpoints.  
- `utils.py` → CLI-friendly functions (`print_user_info`, `print_league_info`, etc.).  
- `st_utils.py` → Streamlit helpers (`st_user_info`, `st_league_info`, `st_rosters`, `st_trending_players`).  
- `dashboard.py` → Interactive Streamlit app with tabs and reactive updates.

--- 

## Features


---