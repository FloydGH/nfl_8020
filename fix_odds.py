#!/usr/bin/env python3
"""
Fix odds file to ensure consistent team names and match weekly inputs
"""

import pandas as pd

def main():
    # Load weekly inputs to see what games we need
    weekly_df = pd.read_csv('out/week01/weekly_inputs.csv')
    
    # Load current odds
    odds_df = pd.read_csv('out/week01/odds.csv')
    
    # Create a mapping from team abbreviations to full names
    team_mapping = {
        'KC': 'Kansas City Chiefs', 'BAL': 'Baltimore Ravens',
        'PHI': 'Philadelphia Eagles', 'GB': 'Green Bay Packers',
        'ATL': 'Atlanta Falcons', 'PIT': 'Pittsburgh Steelers',
        'BUF': 'Buffalo Bills', 'ARI': 'Arizona Cardinals',
        'CHI': 'Chicago Bears', 'TEN': 'Tennessee Titans',
        'CIN': 'Cincinnati Bengals', 'NE': 'New England Patriots',
        'IND': 'Indianapolis Colts', 'HOU': 'Houston Texans',
        'MIA': 'Miami Dolphins', 'JAX': 'Jacksonville Jaguars',
        'NO': 'New Orleans Saints', 'CAR': 'Carolina Panthers',
        'NYG': 'New York Giants', 'MIN': 'Minnesota Vikings',
        'LAC': 'Los Angeles Chargers', 'LV': 'Las Vegas Raiders',
        'SEA': 'Seattle Seahawks', 'DEN': 'Denver Broncos',
        'CLE': 'Cleveland Browns', 'DAL': 'Dallas Cowboys',
        'TB': 'Tampa Bay Buccaneers', 'WAS': 'Washington Commanders',
        'DET': 'Detroit Lions', 'LA': 'Los Angeles Rams',
        'SF': 'San Francisco 49ers', 'NYJ': 'New York Jets'
    }
    
    # Create corrected odds data
    corrected_odds = []
    
    for _, row in weekly_df.iterrows():
        home_team = row['home_team']
        away_team = row['away_team']
        
        # Find matching odds row
        matching_odds = None
        for _, odds_row in odds_df.iterrows():
            home_match = False
            away_match = False
            
            # Check if home team matches
            if (odds_row['home_team_name'] == team_mapping.get(home_team, home_team) or 
                odds_row['home_team_name'] == home_team):
                home_match = True
            
            # Check if away team matches
            if (odds_row['away_team_name'] == team_mapping.get(away_team, away_team) or 
                odds_row['away_team_name'] == away_team):
                away_match = True
            
            if home_match and away_match:
                matching_odds = odds_row
                break
        
        if matching_odds is not None:
            # Use existing odds data
            corrected_odds.append({
                'home_team_name': team_mapping[home_team],
                'away_team_name': team_mapping[away_team],
                'ou_consensus': matching_odds['ou_consensus'],
                'spread_home_consensus': matching_odds['spread_home_consensus']
            })
        else:
            # Generate reasonable proxy odds if no match found
            print(f"Warning: No odds found for {away_team} @ {home_team}, using proxy")
            corrected_odds.append({
                'home_team_name': team_mapping[home_team],
                'away_team_name': team_mapping[away_team],
                'ou_consensus': 45.0,  # Default OU
                'spread_home_consensus': 0.0  # Default spread
            })
    
    # Save corrected odds
    corrected_df = pd.DataFrame(corrected_odds)
    corrected_df.to_csv('out/week01/odds.csv', index=False)
    
    print(f"Corrected odds for {len(corrected_odds)} games")
    print("Sample corrected odds:")
    print(corrected_df.head())
    
    # Verify all games are covered
    print(f"\nVerification:")
    print(f"Weekly inputs: {len(weekly_df)} games")
    print(f"Corrected odds: {len(corrected_df)} games")

if __name__ == "__main__":
    main()
