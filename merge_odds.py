#!/usr/bin/env python3
"""
Manually merge odds data into weekly inputs
"""

import pandas as pd

def main():
    # Load weekly inputs
    weekly_df = pd.read_csv('out/week01/weekly_inputs.csv')
    
    # Load odds
    odds_df = pd.read_csv('out/week01/odds.csv')
    
    # Create team mapping
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
    
    # Merge odds data
    for idx, row in weekly_df.iterrows():
        home_team = row['home_team']
        away_team = row['away_team']
        
        # Find matching odds row
        for _, odds_row in odds_df.iterrows():
            if (odds_row['home_team_name'] == team_mapping[home_team] and 
                odds_row['away_team_name'] == team_mapping[away_team]):
                weekly_df.loc[idx, 'ou'] = odds_row['ou_consensus']
                weekly_df.loc[idx, 'spread_home'] = odds_row['spread_home_consensus']
                break
    
    # Save updated weekly inputs
    weekly_df.to_csv('out/week01/weekly_inputs.csv', index=False)
    
    print("Merged odds data into weekly inputs")
    print("Sample updated data:")
    print(weekly_df[['home_team', 'away_team', 'ou', 'spread_home']].head())

if __name__ == "__main__":
    main()
