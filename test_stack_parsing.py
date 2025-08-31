#!/usr/bin/env python3
"""
Test stack parsing to see what's happening
"""

import pandas as pd
import ast

def main():
    # Load the stacks
    stacks_df = pd.read_csv('out/week01/dk_stacks_reasonable.csv')
    
    print("=== Testing Stack Parsing ===\n")
    print(f"Stacks shape: {stacks_df.shape}")
    print(f"Stacks columns: {stacks_df.columns.tolist()}")
    print()
    
    # Look at a few sample stacks
    print("Sample stacks:")
    for i in range(min(5, len(stacks_df))):
        row = stacks_df.iloc[i]
        print(f"  Stack {i+1}:")
        print(f"    QB: {row['qb']}")
        print(f"    Stack: {row['stack']} (type: {type(row['stack'])})")
        print(f"    Bringback: {row['bringback']}")
        print()
    
    # Test parsing the stack column
    print("Testing stack parsing:")
    for i in range(min(3, len(stacks_df))):
        row = stacks_df.iloc[i]
        stack_str = row['stack']
        
        print(f"  Stack {i+1} string: {repr(stack_str)}")
        
        try:
            # Try to parse as a list
            if isinstance(stack_str, str):
                # Remove quotes and brackets, split by comma
                clean_str = stack_str.strip("[]'\"")
                names = [name.strip().strip("'\"") for name in clean_str.split(',')]
                print(f"    Parsed names: {names}")
                
                # Check if these names exist in DraftKings
                dk_df = pd.read_csv('DKSalaries.csv')
                dk_names = set(dk_df['Name'])
                
                for name in names:
                    if name in dk_names:
                        print(f"      ✓ {name} found in DraftKings")
                    else:
                        print(f"      ✗ {name} NOT found in DraftKings")
            else:
                print(f"    Stack is not a string: {type(stack_str)}")
                
        except Exception as e:
            print(f"    Error parsing: {e}")
        
        print()

if __name__ == "__main__":
    main()
