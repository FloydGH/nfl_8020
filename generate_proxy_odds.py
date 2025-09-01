#!/usr/bin/env python3
"""
Generate proxy odds data for games in weekly inputs
"""

import pandas as pd
import random

def main():
    # Load weekly inputs to see what games we have
    weekly_df = pd.read_csv('out/week01/weekly_inputs.csv')
    
    # Create proxy odds data
    proxy_odds = []
    
    for _, row in weekly_df.iterrows():
        home_team = row['home_team']
        away_team = row['away_team']
        
        # Generate realistic proxy odds
        # OU: typically 40-50 points for most games
        ou = random.uniform(42, 48)
        
        # Spread: typically -7 to +7 for most games
        spread = random.uniform(-7, 7)
        
        # Convert team abbreviations to full names for consistency
        team_names = {
            'KC': 'Kansas City Chiefs', 'BAL': 'Baltimore Ravens',
            'PHI': 'Philadelphia Eagles', 'GB': 'Green Bay Packers',
            'ATL': 'Atlanta Falcons', 'PIT': 'Pittsburgh Steelers',
            'BUF': 'Buffalo Bills', 'ARI': 'Arizona Cardinals',
            'CHI': 'Chicago Bears', 'TEN': 'Tennessee Titans',
            'CIN': 'Cincinnati Bengals', 'NE': 'New England Patriots',
            'IND': 'Indianapolis Colts', 'HOU': 'Houston Texans',
            'MIA': 'Miami Dolphins', 'JAX': 'Jacksonville Jaguars',
            'NO': 'New Orleans Saints', 'CAR': 'Carolina Panthers'
        }
        
        home_name = team_names.get(home_team, home_team)
        away_name = team_names.get(away_team, away_team)
        
        proxy_odds.append({
            'home_team_name': home_name,
            'away_team_name': away_name,
            'ou_consensus': round(ou, 1),
            'spread_home_consensus': round(spread, 1)
        })
    
    # Save proxy odds
    proxy_df = pd.DataFrame(proxy_odds)
    proxy_df.to_csv('out/week01/odds.csv', index=False)
    
    print(f"Generated proxy odds for {len(proxy_odds)} games")
    print("Sample proxy odds:")
    print(proxy_df.head())

if __name__ == "__main__":
    main()
