#!/usr/bin/env python3
"""
Debug the optimize pipeline step by step
"""

import pandas as pd
from utils import load_dk, ownership_proxy, projection_proxy

def main():
    print("=== Debugging Optimize Pipeline ===\n")
    
    # 1. Load DraftKings data
    print("1. Loading DraftKings data...")
    dk_df = load_dk('DKSalaries.csv')
    print(f"   DraftKings data shape: {dk_df.shape}")
    print(f"   DraftKings columns: {dk_df.columns.tolist()}")
    print(f"   Sample DraftKings data:")
    print(dk_df.head(3))
    print()
    
    # 2. Create proxy projections
    print("2. Creating proxy projections...")
    proj_df = projection_proxy(dk_df)
    print(f"   Projections shape: {proj_df.shape}")
    print(f"   Projections columns: {proj_df.columns.tolist()}")
    print(f"   Sample projections:")
    print(proj_df.head(3))
    print()
    
    # 3. Create proxy ownership
    print("3. Creating proxy ownership...")
    own_df = ownership_proxy(dk_df)
    print(f"   Ownership shape: {own_df.shape}")
    print(f"   Ownership columns: {own_df.columns.tolist()}")
    print(f"   Sample ownership:")
    print(own_df.head(3))
    print()
    
    # 4. Test the merge
    print("4. Testing the merge...")
    print(f"   DK names sample: {dk_df['name'].head(5).tolist()}")
    print(f"   Proj names sample: {proj_df['name'].head(5).tolist()}")
    print(f"   Own names sample: {own_df['name'].head(5).tolist()}")
    
    # Check for any name mismatches
    dk_names = set(dk_df['name'])
    proj_names = set(proj_df['name'])
    own_names = set(own_df['name'])
    
    print(f"\n   DK names count: {len(dk_names)}")
    print(f"   Proj names count: {len(proj_names)}")
    print(f"   Own names count: {len(own_names)}")
    
    if dk_names != proj_names:
        print(f"   WARNING: DK and Proj names don't match!")
        missing_in_proj = dk_names - proj_names
        missing_in_dk = proj_names - dk_names
        if missing_in_proj:
            print(f"   Names in DK but not in Proj: {list(missing_in_proj)[:5]}")
        if missing_in_dk:
            print(f"   Names in Proj but not in DK: {list(missing_in_dk)[:5]}")
    
    if dk_names != own_names:
        print(f"   WARNING: DK and Own names don't match!")
        missing_in_own = dk_names - own_names
        missing_in_dk_own = own_names - dk_names
        if missing_in_own:
            print(f"   Names in DK but not in Own: {list(missing_in_own)[:5]}")
        if missing_in_dk_own:
            print(f"   Names in Own but not in DK: {list(missing_in_dk_own)[:5]}")
    
    print()
    
    # 5. Test the build_player_rows logic
    print("5. Testing build_player_rows logic...")
    try:
        # Simulate the merge from build_player_rows
        df = dk_df.merge(proj_df, on=["name","team","pos"], how="left")
        print(f"   Merge successful! Result shape: {df.shape}")
        
        if own_df is not None:
            df = df.merge(own_df[["name","own"]], on="name", how="left")
            print(f"   Ownership merge successful! Final shape: {df.shape}")
        
        # Check for any NaN values
        nan_counts = df.isna().sum()
        print(f"   NaN counts per column:")
        for col, count in nan_counts.items():
            if count > 0:
                print(f"     {col}: {count}")
        
        print(f"   Sample final data:")
        print(df.head(3))
        
    except Exception as e:
        print(f"   ERROR in merge: {e}")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    main()
