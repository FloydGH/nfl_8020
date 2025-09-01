#!/usr/bin/env python3
"""
Generate 150 lineups with enhanced salary tier system
"""

import pandas as pd
import random
import collections
import csv
from utils import load_dk, load_optional, lineup_score

def get_opponent_team(qb_team, schedule_df):
    """Get the opponent team for a given QB's team from the schedule"""
    for _, game in schedule_df.iterrows():
        if game['home_team'] == qb_team:
            return game['away_team']
        elif game['away_team'] == qb_team:
            return game['home_team']
    return None

def calculate_dynamic_salary_tiers(dk_df):
    """Calculate dynamic salary tiers based on position percentiles"""
    print("🎯 Calculating dynamic salary tiers for this slate...")
    
    tiers = {}
    for pos in ['QB', 'RB', 'WR', 'TE', 'DST']:
        pos_df = dk_df[dk_df['pos'] == pos]
        if len(pos_df) == 0:
            continue
            
        salaries = pos_df['salary'].sort_values()
        
        # Target distribution: 16-20% slate-premium, 46-50% mid-tier, 28-32% value, 8-10% punts
        # For 9 players: premium = 1-2, mid = 4-5, value = 2-3, punts = 0-1
        
        # To get 16-20% premium, we need top ~2% of salaries (very conservative)
        # To get 46-50% mid, we need top ~8% of salaries (more conservative)
        # To get 28-32% value, we need top ~45% of salaries
        # Bottom ~55% will be punts
        
        p98 = salaries.quantile(0.98)  # Top 2% = premium (16-20% target)
        p92 = salaries.quantile(0.92)  # Top 8% = mid (46-50% target)
        p55 = salaries.quantile(0.55)  # Top 45% = value (28-32% target)
        
        tiers[pos] = {
            'premium': p98,      # Top 2% (16-20% target)
            'mid': p92,          # Top 8% (46-50% target)  
            'value': p55,        # Top 45% (28-32% target)
            'punt': p55          # Bottom 55% (8-10% target)
        }
        
        print(f"{pos}: Premium≥${p98:.0f} (2%), Mid≥${p92:.0f} (8%), Value≥${p55:.0f} (45%), Punt<${p55:.0f}")
    
    return tiers

def get_salary_tier(player, tiers):
    """Get salary tier for a player"""
    pos = player['pos']
    salary = player['salary']
    
    if pos not in tiers:
        return 'mid'
    
    pos_tiers = tiers[pos]
    
    if salary >= pos_tiers['premium']:
        return 'premium'
    elif salary >= pos_tiers['mid']:
        return 'mid'
    elif salary >= pos_tiers['value']:
        return 'value'
    else:
        return 'punt'

def build_enhanced_lineup(players, schedule_df, tiers, max_attempts=1000):
    """
    Build lineup with salary tier awareness
    """
    for attempt in range(max_attempts):
        lu = []
        
        # 1. Pick QB (prefer premium/mid-tier)
        qb_candidates = [p for p in players if p['pos'] == 'QB']
        if not qb_candidates:
            continue
        
        # Sort QBs by tier preference
        qb_candidates.sort(key=lambda x: (
            get_salary_tier(x, tiers) == 'premium',
            get_salary_tier(x, tiers) == 'mid',
            x['salary']
        ), reverse=True)
        
        qb = random.choice(qb_candidates[:10])  # Top 10 by preference
        lu.append(qb)
        qb_team = qb['team']
        
        # 2. Find opponent for bring-back
        opponent_team = get_opponent_team(qb_team, schedule_df)
        if not opponent_team:
            continue
        
        # 3. Add 2 pass catchers from QB's team (stack)
        same_team_pass_catchers = [p for p in players if p['team'] == qb_team and p['pos'] in ['WR', 'TE'] and p not in lu]
        if len(same_team_pass_catchers) < 2:
            continue
        
        # Sort by salary (prefer higher for better allocation)
        same_team_pass_catchers.sort(key=lambda x: x['salary'], reverse=True)
        
        # Add 2 pass catchers
        stack_added = 0
        for player in same_team_pass_catchers:
            if stack_added >= 2:
                break
            lu.append(player)
            stack_added += 1
        
        if stack_added < 2:
            continue
        
        # 4. Add 1 bring-back from opponent (offensive player only)
        opponent_players = [p for p in players if p['team'] == opponent_team and p['pos'] != 'DST' and p not in lu]
        if not opponent_players:
            continue
        
        # Sort by salary and pick one
        opponent_players.sort(key=lambda x: x['salary'], reverse=True)
        bring_back = random.choice(opponent_players[:10])  # Top 10 by salary
        lu.append(bring_back)
        
        # 5. Fill remaining positions with tier awareness
        needed_positions = []
        if sum(1 for p in lu if p['pos'] == 'RB') < 2:
            needed_positions.extend(['RB'] * (2 - sum(1 for p in lu if p['pos'] == 'RB')))
        if sum(1 for p in lu if p['pos'] == 'WR') < 3:
            needed_positions.extend(['WR'] * (3 - sum(1 for p in lu if p['pos'] == 'WR')))
        if sum(1 for p in lu if p['pos'] == 'TE') < 1:
            needed_positions.extend(['TE'] * (1 - sum(1 for p in lu if p['pos'] == 'TE')))
        if sum(1 for p in lu if p['pos'] == 'DST') < 1:
            needed_positions.extend(['DST'] * (1 - sum(1 for p in lu if p['pos'] == 'DST')))
        
        # Fill positions with tier-aware selection
        for pos in needed_positions:
            available = [p for p in players if p['pos'] == pos and p not in lu]
            if not available:
                break
            
            # Sort by tier preference and salary
            available.sort(key=lambda x: (
                get_salary_tier(x, tiers) == 'premium',
                get_salary_tier(x, tiers) == 'mid',
                x['salary']
            ), reverse=True)
            
            # Pick from top portion
            top_portion = min(15, len(available))
            player = random.choice(available[:top_portion])
            lu.append(player)
        
        # 6. Validate lineup
        if len(lu) == 9:
            total_salary = sum(p['salary'] for p in lu)
            if 49600 <= total_salary <= 50000:
                # Check if we have at least one premium WR
                premium_wrs = sum(1 for p in lu if p['pos'] == 'WR' and get_salary_tier(p, tiers) == 'premium')
                if premium_wrs >= 1:
                    return lu
        
        # Reset for next attempt
        lu = []
    
    return None

def format_lineup_for_draftkings(lineup, lineup_num):
    """Format lineup for DraftKings CSV upload"""
    # Map positions to DraftKings format
    qb = next(p for p in lineup if p['pos'] == 'QB')
    rbs = [p for p in lineup if p['pos'] == 'RB']
    wrs = [p for p in lineup if p['pos'] == 'WR']
    tes = [p for p in lineup if p['pos'] == 'TE']
    dst = next(p for p in lineup if p['pos'] == 'DST')
    
    # FLEX can be RB, WR, or TE (pick the one not already used)
    flex_candidates = []
    if len(rbs) > 2:
        flex_candidates.append(rbs[2])
    if len(wrs) > 3:
        flex_candidates.append(wrs[3])
    if len(tes) > 1:
        flex_candidates.append(tes[1])
    
    if not flex_candidates:
        # If no extra players, use the last player of any position
        used_players = [qb] + rbs[:2] + wrs[:3] + tes[:1] + [dst]
        flex = [p for p in lineup if p not in used_players][0]
    else:
        flex = flex_candidates[0]
    
    return {
        "QB": qb['id'],
        "RB": rbs[0]['id'],
        "RB.1": rbs[1]['id'],
        "WR": wrs[0]['id'],
        "WR.1": wrs[1]['id'],
        "WR.2": wrs[2]['id'],
        "TE": tes[0]['id'],
        "FLEX": flex['id'],
        "DST": dst['id'],
        "": "",
        "Instructions": f"Lineup {lineup_num}"
    }

def main():
    print("🚀 GENERATING 150 ENHANCED LINEUPS")
    print("=" * 60)
    
    # Load data
    dk_df = load_dk("DKSalaries.csv")
    proj_df = load_optional("projections.csv")
    own_df = load_optional("ownership.csv")
    schedule_df = pd.read_csv("out/week01/weekly_inputs.csv")
    
    print(f"DK players: {len(dk_df)}")
    print(f"Projections: {len(proj_df)}")
    print(f"Ownership: {len(own_df)}")
    
    # Calculate dynamic salary tiers
    tiers = calculate_dynamic_salary_tiers(dk_df)
    
    # Build players list with IDs
    players = []
    for _, row in dk_df.iterrows():
        proj_row = proj_df[proj_df["name"] == row["name"]]
        own_row = own_df[own_df["name"] == row["name"]]
        
        if not proj_row.empty and not own_row.empty:
            players.append({
                "name": row["name"], "team": row["team"], "pos": row["pos"], 
                "salary": int(row["salary"]), "id": str(row["id"]),
                "proj": float(proj_row.iloc[0]["proj"])
            })
    
    print(f"Valid players: {len(players)}")
    
    # Generate 150 lineups
    lineups = []
    max_attempts = 200000
    
    print(f"\n🔨 Building 150 enhanced lineups...")
    
    for attempt in range(max_attempts):
        if len(lineups) >= 150:
            break
            
        if attempt % 5000 == 0:
            print(f"Attempt {attempt}, lineups: {len(lineups)}")
        
        lu = build_enhanced_lineup(players, schedule_df, tiers)
        
        if lu is None:
            continue
        
        # Calculate score and add
        score = lineup_score(lu, 0.35, 0.03)
        lineups.append((score, lu))
        
        if len(lineups) % 25 == 0:
            print(f"✅ Generated {len(lineups)} lineups...")
    
    print(f"\n🎉 Generated {len(lineups)} lineups!")
    
    # Sort by score
    lineups.sort(key=lambda x: x[0], reverse=True)
    
    # Show top 5
    print("\n🏆 TOP 5 LINEUPS:")
    for i, (score, lu) in enumerate(lineups[:5], 1):
        total_salary = sum(p['salary'] for p in lu)
        total_proj = sum(p['proj'] for p in lu)
        
        print(f"\nLineup {i} (Score: {score:.2f}, Salary: ${total_salary:,}, Proj: {total_proj:.1f}):")
        
        # Show stack info
        qb = lu[0]
        stack_players = [p for p in lu[1:3] if p['team'] == qb['team']]
        bring_back = lu[3]
        
        print(f"  QB: {qb['name']} ({qb['team']}) - ${qb['salary']:,}")
        print(f"  Stack: {[p['name'] for p in stack_players]}")
        print(f"  Bring-back: {bring_back['name']} ({bring_back['team']})")
        
        # Show tier distribution
        tier_counts = collections.Counter([get_salary_tier(p, tiers) for p in lu])
        print(f"  Tiers: {dict(tier_counts)}")
    
    # Export to CSV
    print(f"\n💾 Exporting to CSV...")
    
    with open("out/week01/lineups_150_enhanced.csv", "w", newline='') as f:
        fieldnames = ["QB", "RB", "RB.1", "WR", "WR.1", "WR.2", "TE", "FLEX", "DST", "", "Instructions"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write header row
        writer.writerow({
            "QB": "QB", "RB": "RB", "RB.1": "RB", "WR": "WR", "WR.1": "WR", "WR.2": "WR", 
            "TE": "TE", "FLEX": "FLEX", "DST": "DST", "": "", "Instructions": "Instructions"
        })
        
        # Write instruction rows
        for i in range(1, 6):
            row = {field: "" for field in fieldnames}
            if i == 1:
                row["Instructions"] = "1. Locate the player you want to select in the list below"
            elif i == 2:
                row["Instructions"] = "2. Copy the ID of your player (you can use the Name + ID column or the ID column)"
            elif i == 3:
                row["Instructions"] = "3. Paste the ID into the roster position desired"
            elif i == 4:
                row["Instructions"] = "4. You must include an ID for each player; you cannot use just the player's name"
            elif i == 5:
                row["Instructions"] = "5. You can create up to 500 lineups per file"
            writer.writerow(row)
        
        # Write empty row
        writer.writerow({field: "" for field in fieldnames})
        
        # Write lineup rows
        for i, (score, lu) in enumerate(lineups, 1):
            row = format_lineup_for_draftkings(lu, i)
            writer.writerow(row)
    
    print(f"✅ Exported {len(lineups)} lineups to out/week01/lineups_150_enhanced.csv")
    
    # Final summary
    print(f"\n📊 FINAL SUMMARY:")
    all_salaries = []
    all_8k_plus = 0
    all_tiers = []
    
    for _, lu in lineups:
        salary = sum(p['salary'] for p in lu)
        all_salaries.append(salary)
        all_8k_plus += sum(1 for p in lu if p['salary'] >= 8000)
        all_tiers.extend([get_salary_tier(p, tiers) for p in lu])
    
    avg_salary = sum(all_salaries) / len(all_salaries)
    min_salary = min(all_salaries)
    max_salary = max(all_salaries)
    
    print(f"   Total lineups: {len(lineups)}")
    print(f"   Salary range: ${min_salary:,} - ${max_salary:,}")
    print(f"   Average salary: ${avg_salary:,.0f}")
    print(f"   $8k+ players: {all_8k_plus} ({(all_8k_plus/(len(lineups)*9))*100:.1f}%)")
    
    # Show tier distribution
    tier_counts = collections.Counter(all_tiers)
    total_players = len(all_tiers)
    print(f"   Tier distribution:")
    for tier, count in sorted(tier_counts.items()):
        pct = (count / total_players) * 100
        print(f"     {tier}: {count} ({pct:.1f}%)")

if __name__ == "__main__":
    main()
