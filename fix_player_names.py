#!/usr/bin/env python3
"""
Fix player name mismatches between stacks and DraftKings file
"""

import pandas as pd
import re

def create_name_mapping(dk_df):
    """Create a mapping from simplified names to full DraftKings names"""
    mapping = {}
    
    for _, row in dk_df.iterrows():
        dk_name = row['Name']
        # Create simplified versions
        simplified = dk_name
        
        # Remove "Sr.", "Jr.", "III", "IV", etc.
        simplified = re.sub(r'\s+(Sr\.|Jr\.|I{2,}|IV|V|VI+)$', '', simplified)
        
        # Remove extra spaces
        simplified = simplified.strip()
        
        # Map simplified to full name
        mapping[simplified] = dk_name
        
        # Also map the original name to itself
        mapping[dk_name] = dk_name
    
    return mapping

def fix_stacks_file(stacks_path, dk_path, output_path):
    """Fix player names in stacks file to match DraftKings names"""
    
    # Load data
    stacks_df = pd.read_csv(stacks_path)
    dk_df = pd.read_csv(dk_path)
    
    # Create name mapping
    name_mapping = create_name_mapping(dk_df)
    
    print(f"Created name mapping with {len(name_mapping)} entries")
    print("Sample mappings:")
    for i, (simple, full) in enumerate(list(name_mapping.items())[:10]):
        print(f"  {simple} -> {full}")
    
    # Fix QB names
    stacks_df['qb'] = stacks_df['qb'].map(lambda x: name_mapping.get(x, x))
    
    # Fix stack names (these are lists, so we need to handle them carefully)
    def fix_stack_names(stack_str):
        try:
            # Parse the string representation of the list
            if pd.isna(stack_str) or stack_str == '':
                return stack_str
            
            # Remove quotes and brackets, split by comma
            clean_str = stack_str.strip("[]'\"")
            names = [name.strip().strip("'\"") for name in clean_str.split(',')]
            
            # Fix each name
            fixed_names = [name_mapping.get(name, name) for name in names]
            
            # Return as string representation
            return str(fixed_names)
        except:
            return stack_str
    
    stacks_df['stack'] = stacks_df['stack'].apply(fix_stack_names)
    
    # Fix bringback names
    stacks_df['bringback'] = stacks_df['bringback'].map(lambda x: name_mapping.get(x, x))
    
    # Check for any remaining mismatches
    print("\nChecking for remaining name mismatches...")
    all_names = set()
    all_names.update(stacks_df['qb'].dropna())
    all_names.update(stacks_df['bringback'].dropna())
    
    # Extract names from stack column
    for stack_str in stacks_df['stack'].dropna():
        try:
            clean_str = stack_str.strip("[]'\"")
            names = [name.strip().strip("'\"") for name in clean_str.split(',')]
            all_names.update(names)
        except:
            pass
    
    dk_names = set(dk_df['Name'])
    missing_names = all_names - dk_names
    
    if missing_names:
        print(f"WARNING: {len(missing_names)} names still don't match DraftKings:")
        for name in sorted(missing_names):
            print(f"  {name}")
    else:
        print("All names now match DraftKings!")
    
    # Save fixed file
    stacks_df.to_csv(output_path, index=False)
    print(f"\nFixed stacks saved to: {output_path}")
    
    return stacks_df

if __name__ == "__main__":
    # Fix the stacks file
    fixed_stacks = fix_stacks_file(
        'out/week01/core_stacks.csv',
        'DKSalaries.csv',
        'out/week01/core_stacks_fixed.csv'
    )
    
    print(f"\nFixed stacks preview:")
    print(fixed_stacks[['qb', 'stack', 'bringback']].head())
