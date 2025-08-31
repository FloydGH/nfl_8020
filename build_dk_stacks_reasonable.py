#!/usr/bin/env python3
"""
Build reasonable number of stacks for games available in DraftKings file
"""

import pandas as pd
import itertools
import random

def extract_games_from_dk(dk_df):
    """Extract games from DraftKings file"""
    games = {}
    
    for _, row in dk_df.iterrows():
        game_info = row['Game Info']
        if pd.isna(game_info) or game_info == 'Game Info':
            continue
            
        # Parse game info like "CIN@CLE 09/07/2025 01:00PM ET"
        parts = game_info.split()
        if len(parts) >= 1:
            teams = parts[0].split('@')
            if len(teams) == 2:
                away_team = teams[0]
                home_team = teams[1]
                game_key = f"{away_team}@{home_team}"
                
                if game_key not in games:
                    games[game_key] = {
                        'away_team': away_team,
                        'home_team': home_team,
                        'away_players': [],
                        'home_players': []
                    }
                
                # Add player to appropriate team
                player = {
                    'name': row['Name'],
                    'pos': row['Position'],
                    'salary': row['Salary'],
                    'team': row['TeamAbbrev']
                }
                
                if row['TeamAbbrev'] == away_team:
                    games[game_key]['away_players'].append(player)
                elif row['TeamAbbrev'] == home_team:
                    games[game_key]['home_players'].append(player)
    
    return games

def build_reasonable_stacks_for_game(game_data, game_id, max_stacks_per_team=20):
    """Build a reasonable number of stacks for a specific game"""
    stacks = []
    
    # Get QBs
    away_qbs = [p for p in game_data['away_players'] if p['pos'] == 'QB']
    home_qbs = [p for p in game_data['home_players'] if p['pos'] == 'QB']
    
    # Get top pass-catchers by salary (proxy for quality)
    away_pass_catchers = sorted([p for p in game_data['away_players'] if p['pos'] in ['WR', 'TE']], 
                               key=lambda x: x['salary'], reverse=True)[:8]  # Top 8 by salary
    home_pass_catchers = sorted([p for p in game_data['home_players'] if p['pos'] in ['WR', 'TE']], 
                               key=lambda x: x['salary'], reverse=True)[:8]  # Top 8 by salary
    
    # Build stacks for away team
    for qb in away_qbs:
        # Limit combinations to avoid explosion
        pc_combinations = list(itertools.combinations(away_pass_catchers, 2))[:max_stacks_per_team//2]
        
        for pc1, pc2 in pc_combinations:
            # Get top bringbacks by salary
            top_bringbacks = sorted(home_pass_catchers, key=lambda x: x['salary'], reverse=True)[:4]
            
            for br in top_bringbacks:
                stack = {
                    'game_id': game_id,
                    'tier': 'B',  # Default tier
                    'qb': qb['name'],
                    'team_qb': qb['team'],
                    'stack': [pc1['name'], pc2['name']],
                    'bringback': br['name'],
                    'opp_team': br['team']
                }
                stacks.append(stack)
    
    # Build stacks for home team
    for qb in home_qbs:
        # Limit combinations to avoid explosion
        pc_combinations = list(itertools.combinations(home_pass_catchers, 2))[:max_stacks_per_team//2]
        
        for pc1, pc2 in pc_combinations:
            # Get top bringbacks by salary
            top_bringbacks = sorted(away_pass_catchers, key=lambda x: x['salary'], reverse=True)[:4]
            
            for br in top_bringbacks:
                stack = {
                    'game_id': game_id,
                    'tier': 'B',  # Default tier
                    'qb': qb['name'],
                    'team_qb': qb['team'],
                    'stack': [pc1['name'], pc2['name']],
                    'bringback': br['name'],
                    'opp_team': br['team']
                }
                stacks.append(stack)
    
    return stacks

def main():
    # Load DraftKings data
    dk_df = pd.read_csv('DKSalaries.csv')
    
    # Extract games
    games = extract_games_from_dk(dk_df)
    
    print(f"Found {len(games)} games in DraftKings file:")
    for game_key, game_data in games.items():
        print(f"  {game_key}: {len(game_data['away_players'])} away players, {len(game_data['home_players'])} home players")
    
    # Build stacks for each game
    all_stacks = []
    for game_key, game_data in games.items():
        game_id = f"dk_{game_key.replace('@', '_')}"
        stacks = build_reasonable_stacks_for_game(game_data, game_id, max_stacks_per_team=20)
        all_stacks.extend(stacks)
        print(f"  {game_key}: Created {len(stacks)} stacks")
    
    # Convert to DataFrame
    stacks_df = pd.DataFrame(all_stacks)
    
    # Save stacks
    output_path = 'out/week01/dk_stacks_reasonable.csv'
    stacks_df.to_csv(output_path, index=False)
    print(f"\nCreated {len(all_stacks)} total stacks")
    print(f"Saved to: {output_path}")
    
    # Show sample stacks
    print("\nSample stacks:")
    print(stacks_df.head(10))
    
    return stacks_df

if __name__ == "__main__":
    main()
