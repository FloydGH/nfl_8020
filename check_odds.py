import pandas as pd
from utils import _nick_to_abbr

# Load data
odds = pd.read_csv('out/week01/odds.csv')
odds['home_abbr'] = odds['home_team_name'].map(_nick_to_abbr)
odds['away_abbr'] = odds['away_team_name'].map(_nick_to_abbr)

# Week 1 games from our schedule
week1_games = [
    ['KC', 'BAL'], ['PHI', 'GB'], ['ATL', 'PIT'], ['BUF', 'ARI'], 
    ['CHI', 'TEN'], ['CIN', 'NE'], ['IND', 'HOU'], ['MIA', 'JAX'], 
    ['NO', 'CAR'], ['NYG', 'MIN'], ['LAC', 'LV'], ['SEA', 'DEN'], 
    ['CLE', 'DAL'], ['TB', 'WAS'], ['DET', 'LA'], ['SF', 'NYJ']
]

print('Looking for Week 1 games in odds data:')
found = 0
for home, away in week1_games:
    matches = odds[(odds['home_abbr'] == home) & (odds['away_abbr'] == away)]
    if len(matches) > 0:
        print(f'✓ {home} vs {away}: {len(matches)} matches')
        print(f'  OU: {matches.iloc[0]["ou_consensus"]}, Spread: {matches.iloc[0]["spread_home_consensus"]}')
        found += 1
    else:
        print(f'✗ {home} vs {away}: No matches')

print(f'\nFound {found}/16 Week 1 games in odds data')

# Check if we can find any games with reversed teams
print('\nChecking for reversed team order...')
found_reversed = 0
for home, away in week1_games:
    matches = odds[(odds['home_abbr'] == away) & (odds['away_abbr'] == home)]
    if len(matches) > 0:
        print(f'✓ {away} vs {home} (reversed): {len(matches)} matches')
        print(f'  OU: {matches.iloc[0]["ou_consensus"]}, Spread: {-matches.iloc[0]["spread_home_consensus"]}')
        found_reversed += 1

print(f'\nFound {found_reversed} additional games with reversed team order')
print(f'Total: {found + found_reversed}/16 Week 1 games')
