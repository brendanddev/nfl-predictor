
""" 
app.py
Main application file for the Fantasy Football Analyzer.

Brendan Dileo, August 2025
"""

from src.api import get_user, pretty_print_json, get_league
from src.config import USER_ID, LEAGUE_ID
from src.analyzer import FantasyAnalyzer


def main():
    
    # Create analyzer instance
    analyzer = FantasyAnalyzer()
    
    # User info
    print("------ USER INFO ------")
    user = get_user(USER_ID)
    pretty_print_json(user.json())
    
    # League info
    print("------ LEAGUE INFO ------")
    league = get_league(LEAGUE_ID)
    pretty_print_json(league.json())
    
if __name__ == "__main__":
    main()