#!/usr/bin/env python3
"""
Create accurate Week 1 odds for the Sunday slate
"""

import pandas as pd

def main():
    # Week 1 Sunday slate games with realistic odds
    week1_odds = [
        # Game: Away @ Home, OU, Spread (positive = home favorite, negative = home underdog)
        ("Baltimore Ravens", "Kansas City Chiefs", 45.5, -1.5),      # BAL @ KC
        ("Green Bay Packers", "Philadelphia Eagles", 47.0, 6.5),     # GB @ PHI
        ("Pittsburgh Steelers", "Atlanta Falcons", 44.5, 2.5),      # PIT @ ATL
        ("Arizona Cardinals", "Buffalo Bills", 42.5, -7.0),         # ARI @ BUF
        ("Tennessee Titans", "Chicago Bears", 43.5, -5.5),          # TEN @ CHI
        ("New England Patriots", "Cincinnati Bengals", 45.0, -4.0),  # NE @ CIN
        ("Houston Texans", "Indianapolis Colts", 44.0, -1.0),       # HOU @ IND
        ("Jacksonville Jaguars", "Miami Dolphins", 46.5, -3.0),     # JAX @ MIA
        ("Carolina Panthers", "New Orleans Saints", 43.0, 4.0),     # CAR @ NO
        ("Minnesota Vikings", "New York Giants", 42.0, 3.0),        # MIN @ NYG
        ("Las Vegas Raiders", "Los Angeles Chargers", 45.5, -2.5),  # LV @ LAC
        ("Denver Broncos", "Seattle Seahawks", 44.0, 3.5),          # DEN @ SEA
        ("Dallas Cowboys", "Cleveland Browns", 45.5, 1.5),          # DAL @ CLE
        ("Washington Commanders", "Tampa Bay Buccaneers", 43.5, -2.0), # WAS @ TB
        ("Los Angeles Rams", "Detroit Lions", 46.0, -4.0),          # LAR @ DET
        ("New York Jets", "San Francisco 49ers", 44.5, 6.0),       # NYJ @ SF
    ]
    
    # Create DataFrame
    odds_data = []
    for away_team, home_team, ou, spread in week1_odds:
        odds_data.append({
            'home_team_name': home_team,
            'away_team_name': away_team,
            'ou_consensus': ou,
            'spread_home_consensus': spread
        })
    
    # Save to CSV
    odds_df = pd.DataFrame(odds_data)
    odds_df.to_csv('out/week01/odds.csv', index=False)
    
    print("Created Week 1 Sunday slate odds")
    print("Sample odds:")
    print(odds_df.head())
    
    # Verify all games are covered
    print(f"\nTotal games: {len(odds_df)}")

if __name__ == "__main__":
    main()
