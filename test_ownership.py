#!/usr/bin/env python3
"""
Test ownership values being generated
"""

import pandas as pd
from utils import ownership_proxy

def main():
    # Load DraftKings data
    dk_df = pd.read_csv('DKSalaries.csv')
    
    # Rename columns to match what utils expects
    dk_df = dk_df.rename(columns={
        'Position': 'pos',
        'Name': 'name',
        'Salary': 'salary',
        'TeamAbbrev': 'team'
    })
    
    # Generate ownership
    own_df = ownership_proxy(dk_df)
    
    print("=== Ownership Distribution ===")
    print(f"Total players: {len(own_df)}")
    print(f"Ownership range: {own_df['own'].min():.1f}% - {own_df['own'].max():.1f}%")
    print(f"Mean ownership: {own_df['own'].mean():.1f}%")
    print(f"Median ownership: {own_df['own'].median():.1f}%")
    
    print("\n=== Ownership Breakdown ===")
    print(f"Under 5%: {(own_df['own'] < 5).sum()}")
    print(f"5-10%: {((own_df['own'] >= 5) & (own_df['own'] < 10)).sum()}")
    print(f"10-15%: {((own_df['own'] >= 10) & (own_df['own'] < 15)).sum()}")
    print(f"15-20%: {((own_df['own'] >= 15) & (own_df['own'] < 20)).sum()}")
    print(f"20%+: {(own_df['own'] >= 20).sum()}")
    
    print("\n=== Sample Players ===")
    sample = own_df.head(20)
    for _, row in sample.iterrows():
        print(f"{row['name']}: {row['own']:.1f}%")
    
    # Test lineup ownership
    print("\n=== Lineup Ownership Test ===")
    # Simulate a typical lineup: QB + 2 WR + 2 RB + TE + DST + 2 WR
    typical_lineup = own_df.head(9)  # Just take first 9 for testing
    total_ownership = typical_lineup['own'].sum()
    low_owned = (typical_lineup['own'] < 5).sum()
    sub10 = (typical_lineup['own'] < 10).sum()
    
    print(f"Typical lineup total ownership: {total_ownership:.1f}%")
    print(f"Low owned (<5%): {low_owned}")
    print(f"Sub 10%: {sub10}")
    
    # Check if it would pass validation
    cum_own_cap = 125
    min_low_owned = 1
    min_sub10 = 2
    
    print(f"\n=== Validation Results ===")
    print(f"Cumulative ownership <= {cum_own_cap}%: {total_ownership <= cum_own_cap}")
    print(f"Low owned >= {min_low_owned}: {low_owned >= min_low_owned}")
    print(f"Sub 10% >= {min_sub10}: {sub10 >= min_sub10}")
    
    if total_ownership <= cum_own_cap and low_owned >= min_low_owned and sub10 >= min_sub10:
        print("✅ Lineup would pass validation!")
    else:
        print("❌ Lineup would fail validation")

if __name__ == "__main__":
    main()
