#!/usr/bin/env python3
"""
Generate 150 lineups using proper stacking rules:
- Double stacks: 2 pass catchers or pass-catching RB
- Bring-backs: players on opposite team as QB
"""

import pandas as pd
import random
import collections
from utils import read_weights, load_dk, load_optional, ownership_proxy, projection_proxy, lineup_score

def get_opponent_team(qb_team, schedule_df):
    """Get the opponent team for a given QB's team from the schedule"""
    for _, game in schedule_df.iterrows():
        if game['home_team'] == qb_team:
            return game['away_team']
        elif game['away_team'] == qb_team:
            return game['home_team']
    return None

def format_lineup_for_display(lineup):
    """Format lineup in the standard DFS format: QB, RB1, RB2, WR1, WR2, WR3, TE1, FLEX, DST"""
    # Sort players by position priority
    qb = [p for p in lineup if p["pos"] == "QB"][0]
    rbs = sorted([p for p in lineup if p["pos"] == "RB"], key=lambda x: x["salary"], reverse=True)
    wrs = sorted([p for p in lineup if p["pos"] == "WR"], key=lambda x: x["salary"], reverse=True)
    tes = sorted([p for p in lineup if p["pos"] == "TE"], key=lambda x: x["salary"], reverse=True)
    dst = [p for p in lineup if p["pos"] == "DST"][0]
    
    # Determine FLEX (highest salary remaining player)
    remaining = []
    if len(rbs) > 2:
        remaining.extend(rbs[2:])
    if len(wrs) > 3:
        remaining.extend(wrs[3:])
    if len(tes) > 1:
        remaining.extend(tes[1:])
    
    flex = max(remaining, key=lambda x: x["salary"]) if remaining else None
    
    return {
        "QB": qb,
        "RB1": rbs[0] if len(rbs) > 0 else None,
        "RB2": rbs[1] if len(rbs) > 1 else None,
        "WR1": wrs[0] if len(wrs) > 0 else None,
        "WR2": wrs[1] if len(wrs) > 1 else None,
        "WR3": wrs[2] if len(wrs) > 2 else None,
        "TE1": tes[0] if len(tes) > 0 else None,
        "FLEX": flex,
        "DST": dst
    }

def format_lineup_for_draftkings(lineup, lineup_num):
    """Format lineup for DraftKings CSV upload"""
    # Sort players by position priority
    qb = [p for p in lineup if p["pos"] == "QB"][0]
    rbs = sorted([p for p in lineup if p["pos"] == "RB"], key=lambda x: x["salary"], reverse=True)
    wrs = sorted([p for p in lineup if p["pos"] == "WR"], key=lambda x: x["salary"], reverse=True)
    tes = sorted([p for p in lineup if p["pos"] == "TE"], key=lambda x: x["salary"], reverse=True)
    dst = [p for p in lineup if p["pos"] == "DST"][0]
    
    # Determine FLEX (highest salary remaining player)
    remaining = []
    if len(rbs) > 2:
        remaining.extend(rbs[2:])
    if len(wrs) > 3:
        remaining.extend(wrs[3:])
    if len(tes) > 1:
        remaining.extend(tes[1:])
    
    flex = max(remaining, key=lambda x: x["salary"]) if remaining else None
    
    # Create DraftKings format rows
    rows = []
    
    # QB
    rows.append({
        "Position": "QB",
        "Name + ID": f"{qb['name']} ({qb.get('id', '')})",
        "Name": qb['name'],
        "ID": qb.get('id', ''),
        "Roster Position": "QB",
        "Salary": qb['salary'],
        "Game Info": "",
        "TeamAbbrev": qb['team'],
        "AvgPointsPerGame": qb.get('proj', 0)
    })
    
    # RB1
    if len(rbs) > 0:
        rows.append({
            "Position": "RB",
            "Name + ID": f"{rbs[0]['name']} ({rbs[0].get('id', '')})",
            "Name": rbs[0]['name'],
            "ID": rbs[0].get('id', ''),
            "Roster Position": "RB",
            "Salary": rbs[0]['salary'],
            "Game Info": "",
            "TeamAbbrev": rbs[0]['team'],
            "AvgPointsPerGame": rbs[0].get('proj', 0)
        })
    
    # RB2
    if len(rbs) > 1:
        rows.append({
            "Position": "RB",
            "Name + ID": f"{rbs[1]['name']} ({rbs[1].get('id', '')})",
            "Name": rbs[1]['name'],
            "ID": rbs[1].get('id', ''),
            "Roster Position": "RB",
            "Salary": rbs[1]['salary'],
            "Game Info": "",
            "TeamAbbrev": rbs[1]['team'],
            "AvgPointsPerGame": rbs[1].get('proj', 0)
        })
    
    # WR1
    if len(wrs) > 0:
        rows.append({
            "Position": "WR",
            "Name + ID": f"{wrs[0]['name']} ({wrs[0].get('id', '')})",
            "Name": wrs[0]['name'],
            "ID": wrs[0].get('id', ''),
            "Roster Position": "WR",
            "Salary": wrs[0]['salary'],
            "Game Info": "",
            "TeamAbbrev": wrs[0]['team'],
            "AvgPointsPerGame": wrs[0].get('proj', 0)
        })
    
    # WR2
    if len(wrs) > 1:
        rows.append({
            "Position": "WR",
            "Name + ID": f"{wrs[1]['name']} ({wrs[1].get('id', '')})",
            "Name": wrs[1]['name'],
            "ID": wrs[1].get('id', ''),
            "Roster Position": "WR",
            "Salary": wrs[1]['salary'],
            "Game Info": "",
            "TeamAbbrev": wrs[1]['team'],
            "AvgPointsPerGame": wrs[1].get('proj', 0)
        })
    
    # WR3
    if len(wrs) > 2:
        rows.append({
            "Position": "WR",
            "Name + ID": f"{wrs[2]['name']} ({wrs[2].get('id', '')})",
            "Name": wrs[2]['name'],
            "ID": wrs[2].get('id', ''),
            "Roster Position": "WR",
            "Salary": wrs[2]['salary'],
            "Game Info": "",
            "TeamAbbrev": wrs[2]['team'],
            "AvgPointsPerGame": wrs[2].get('proj', 0)
        })
    
    # TE1
    if len(tes) > 0:
        rows.append({
            "Position": "TE",
            "Name + ID": f"{tes[0]['name']} ({tes[0].get('id', '')})",
            "Name": tes[0]['name'],
            "ID": tes[0].get('id', ''),
            "Roster Position": "TE",
            "Salary": tes[0]['salary'],
            "Game Info": "",
            "TeamAbbrev": tes[0]['team'],
            "AvgPointsPerGame": tes[0].get('proj', 0)
        })
    
    # FLEX
    if flex:
        flex_pos = flex['pos']
        rows.append({
            "Position": flex_pos,
            "Name + ID": f"{flex['name']} ({flex.get('id', '')})",
            "Name": flex['name'],
            "ID": flex.get('id', ''),
            "Roster Position": "FLEX",
            "Salary": flex['salary'],
            "Game Info": "",
            "TeamAbbrev": flex['team'],
            "AvgPointsPerGame": flex.get('proj', 0)
        })
    
    # DST
    rows.append({
        "Position": "DST",
        "Name + ID": f"{dst['name']} ({dst.get('id', '')})",
        "Name": dst['name'],
        "ID": dst.get('id', ''),
        "Roster Position": "DST",
        "Salary": dst['salary'],
        "Game Info": "",
        "TeamAbbrev": dst['team'],
        "AvgPointsPerGame": dst.get('proj', 0)
    })
    
    return rows

def pos_ok(lineup, to_add_pos):
    counts = collections.Counter([p["pos"] for p in lineup])
    
    # During building, be very flexible to allow reaching 9 players
    if len(lineup) < 9:
        # Allow maximum flexibility during building
        limits = {"QB":1,"RB":5,"WR":6,"TE":4,"DST":1}
    else:
        # Strict limits for final validation
        limits = {"QB":1,"RB":3,"WR":4,"TE":2,"DST":1}
    
    return counts[to_add_pos] < limits.get(to_add_pos, 0)

def finalize_positions(lineup):
    # Validate exactly: QB1, RB2, WR3, TE1, DST1, FLEX1 among RB/WR/TE
    counts = collections.Counter([p["pos"] for p in lineup])
    if counts["QB"] != 1: return False
    if counts["DST"] != 1: return False
    # RB/WR/TE totals: should be 7 with at least RB2/WR3/TE1
    r = counts["RB"]; w = counts["WR"]; t = counts["TE"]
    if r + w + t != 7: return False
    if r < 2 or w < 3 or t < 1: return False
    # ok
    return True

def ok_ownership(lineup, cfg):
    own = sum(p["own"] for p in lineup)
    low = sum(1 for p in lineup if p["own"] < cfg["low_owned_threshold_pct"])
    sub10 = sum(1 for p in lineup if p["own"] < 10)
    if own > cfg["cum_own_cap_pct"]: return False
    if low < cfg["min_low_owned_per_lu"]: return False
    if sub10 < cfg["min_sub10_owned_per_lu"]: return False
    return True

def has_proper_stack(lineup, schedule_df):
    """Check if lineup has proper double stack + bring-back"""
    if len(lineup) < 9:
        return False
    
    # Find QB
    qb = next((p for p in lineup if p["pos"] == "QB"), None)
    if not qb:
        return False
    
    qb_team = qb["team"]
    
    # Find players on same team as QB (stack should be exactly 3 players: QB + 2 pass catchers)
    same_team_players = [p for p in lineup if p["team"] == qb_team and p["pos"] in ["WR", "TE"]]
    
    # Need exactly 2 pass catchers from QB's team (no RBs in stack)
    has_double_stack = len(same_team_players) == 2
    
    # Find bring-back (1 offensive player from the correct opponent team - no DST)
    opponent_team = get_opponent_team(qb_team, schedule_df)
    if not opponent_team:
        return False
    
    opponent_players = [p for p in lineup if p["team"] == opponent_team and p["pos"] in ["RB", "WR", "TE"]]
    has_bringback = len(opponent_players) >= 1
    
    return has_double_stack and has_bringback

def main():
    # Load configuration
    cfg = read_weights("config/weights.yaml")
    
    # Adjust salary constraints for this approach
    cfg["min_salary"] = 49600  # Minimum salary requirement
    print(f"Config: {cfg}")
    
    # Load data
    dk_df = load_dk("DKSalaries.csv")
    proj_df = projection_proxy(dk_df)
    own_df = ownership_proxy(dk_df)
    
    # Load schedule to get correct opponent teams
    schedule_df = pd.read_csv("out/week01/weekly_inputs.csv")
    
    # Load injury report to filter out injured players
    injury_df = pd.read_csv("nfl-injury-report.csv")
    injured_players = set()
    for _, row in injury_df.iterrows():
        if row['Status'] in ['Out', 'IR', 'IR-R', 'NFI-R', 'PUP-R', 'Reserve-CEL', 'Reserve-Ex', 'Reserve-Ret', 'Reserve-Sus']:
            injured_players.add(row['Player'])
    
    print(f"Filtering out {len(injured_players)} injured players")
    
    # Build player rows (filtering out injured players)
    players = []
    for _, row in dk_df.iterrows():
        # Skip injured players
        if row["name"] in injured_players:
            continue
            
        proj_row = proj_df[proj_df["name"] == row["name"]].iloc[0] if len(proj_df[proj_df["name"] == row["name"]]) > 0 else None
        own_row = own_df[own_df["name"] == row["name"]].iloc[0] if len(own_df[own_df["name"] == row["name"]]) > 0 else None
        
        players.append({
            "name": row["name"], "team": row["team"], "pos": row["pos"], "salary": int(row["salary"]),
            "id": row.get("id", ""),  # Add player ID for DraftKings format
            "proj": float(proj_row["proj"]) if proj_row is not None else 0.0,
            "p90": float(proj_row["p90"]) if proj_row is not None else 0.0,
            "own": float(own_row["own"]) if own_row is not None else 5.0
        })
    
    print(f"Loaded {len(players)} players")
    
    # Apply positional minimum salary filters to avoid low-salary players who might not play much
    original_count = len(players)
    players = [p for p in players if (
        (p["pos"] == "QB" and p["salary"] >= 4800) or
        (p["pos"] == "RB" and p["salary"] >= 4100) or
        (p["pos"] == "WR" and p["salary"] >= 3100) or
        (p["pos"] == "TE" and p["salary"] >= 2600) or
        (p["pos"] == "DST")
    )]
    print(f"After positional minimums: {len(players)} players (filtered out {original_count - len(players)} low-salary players)")
    
    # Sort players by score
    for p in players:
        p["score"] = p["proj"] + 0.35*(p["p90"]-p["proj"]) - 0.03*p["own"]
    
    players.sort(key=lambda x: x["score"], reverse=True)
    
    # Generate 150 lineups with proper stacking
    lineups = []
    seen_five_sets = set()
    rng = random.Random(42)
    
    attempts = 0
    max_attempts = 20000
    
    while len(lineups) < 150 and attempts < max_attempts:
        attempts += 1
        
        if attempts % 1000 == 0:
            print(f"Attempt {attempts}, lineups: {len(lineups)}")
        
        try:
            # Start with a random QB (prefer higher salary)
            qb_pool = [p for p in players if p["pos"] == "QB"]
            if not qb_pool:
                continue
            
            # Sort by salary and pick from top 50%
            qb_pool.sort(key=lambda x: x["salary"], reverse=True)
            qb = random.choice(qb_pool[:len(qb_pool)//2])
            lu = [qb]
            qb_team = qb["team"]
            
            # Find opponent team (for bring-back) using actual schedule
            opponent_team = get_opponent_team(qb_team, schedule_df)
            if not opponent_team:
                continue
            
            # Check if opponent team has available offensive players (no DST for bring-back)
            opponent_players = [p for p in players if p["team"] == opponent_team and p["pos"] in ["RB", "WR", "TE"]]
            if not opponent_players:
                continue
            
            # Add 2 pass catchers from QB's team (double stack) - ONLY 2, no more
            # Prioritize higher-salary players for stacking
            same_team_pass_catchers = [p for p in players if p["team"] == qb_team and p["pos"] in ["WR", "TE"] and p["name"] != qb["name"]]
            if len(same_team_pass_catchers) < 2:
                continue
            
            # Sort by salary (higher first) and pick top 2
            same_team_pass_catchers.sort(key=lambda x: x["salary"], reverse=True)
            selected_pass_catchers = random.sample(same_team_pass_catchers[:min(8, len(same_team_pass_catchers))], 2)
            lu.extend(selected_pass_catchers)
            
            # NO additional players from QB's team - stack is complete with 3 players total
            
            # Add 1 bring-back (player from opponent team)
            opponent_players = [p for p in players if p["team"] == opponent_team and p["pos"] in ["RB", "WR", "TE"] and p["name"] not in [x["name"] for x in lu]]
            if not opponent_players:
                continue
            
            opponent_players.sort(key=lambda x: x["salary"], reverse=True)
            lu.append(random.choice(opponent_players[:min(10, len(opponent_players))]))
            
            # Now fill remaining positions with players from OTHER teams (not QB's team, not opponent team)
            # This ensures we have: QB + 2 stack players + 1 bring-back + 5 other players
            
            # Fill remaining positions to reach 9 players with proper position targeting
            available_players = [p for p in players if p["name"] not in [x["name"] for x in lu] and p["team"] != qb["team"] and p["team"] != opponent_team]
            
            while len(lu) < 9:
                # Determine what positions we still need
                counts = collections.Counter([p["pos"] for p in lu])
                needed_positions = []
                
                # Need exactly 1 QB, 2-3 RB, 3-4 WR, 1-2 TE, 1 DST
                if counts["QB"] < 1:
                    needed_positions.append("QB")
                if counts["RB"] < 2:
                    needed_positions.append("RB")
                if counts["WR"] < 3:
                    needed_positions.append("WR")
                if counts["TE"] < 1:
                    needed_positions.append("TE")
                if counts["DST"] < 1:
                    needed_positions.append("DST")
                
                # If no specific positions needed, add best available
                if not needed_positions:
                    needed_positions = ["RB", "WR", "TE", "DST"]
                
                # Find valid players for needed positions
                valid_players = []
                for pos in needed_positions:
                    pos_players = [p for p in available_players if p["pos"] == pos and pos_ok(lu, p["pos"])]
                    if pos_players:
                        valid_players.extend(pos_players)
                
                if not valid_players:
                    # Fallback: any valid position
                    valid_players = [p for p in available_players if pos_ok(lu, p["pos"])]
                
                if not valid_players:
                    break
                
                # Sort by salary (higher first) to allow more salary variation
                valid_players.sort(key=lambda x: x["salary"], reverse=True)
                # Pick from top 20 players to allow more variation
                selected = random.choice(valid_players[:min(20, len(valid_players))])
                lu.append(selected)
                available_players.remove(selected)
            
            # Debug: print first lineup attempt
            if attempts == 1:
                print(f"First lineup attempt: {len(lu)} players")
                for p in lu:
                    print(f"  {p['pos']}: {p['name']} ({p['team']}) - ${p['salary']}")
                print(f"Salary total: {sum(p['salary'] for p in lu)}")
                print(f"Position validation: {finalize_positions(lu)}")
                print(f"Salary validation: {cfg['min_salary']} <= {sum(p['salary'] for p in lu)} <= {cfg['max_salary']}")
                print(f"Ownership validation: {ok_ownership(lu, cfg)}")
                print(f"Stack validation: {has_proper_stack(lu, schedule_df)}")
            
            # Validate lineup
            if len(lu) != 9:
                continue
                
            if not finalize_positions(lu):
                continue
                
            if not has_proper_stack(lu, schedule_df):
                continue
                
            ssum = sum(p["salary"] for p in lu)
            if not (cfg["min_salary"] <= ssum <= cfg["max_salary"]):
                continue
                
            if not ok_ownership(lu, cfg):
                continue
                
            # Check uniqueness
            five = tuple(sorted([p["name"] for p in lu[:5]]))
            if attempts <= 5:  # Debug first few attempts
                print(f"  Uniqueness check: {five}")
                print(f"  Already seen: {five in seen_five_sets}")
                print(f"  seen_five_sets size: {len(seen_five_sets)}")
            
            if five in seen_five_sets:
                print(f"  DUPLICATE: Skipping lineup")
                continue
                
            seen_five_sets.add(five)
            
            # Add lineup
            score = lineup_score(lu, 0.35, 0.03)
            lineups.append((score, lu))
            print(f"  SUCCESS: Added lineup {len(lineups)}")
            
            if len(lineups) % 10 == 0:
                print(f"Generated {len(lineups)} lineups...")
                
        except Exception as e:
            print(f"Error on attempt {attempts}: {e}")
            continue
    
    print(f"Generated {len(lineups)} lineups total")
    
    # Sort by score and take top 150
    lineups.sort(key=lambda x: x[0], reverse=True)
    lineups = lineups[:150]
    
    # Export lineups in standard format
    rows = []
    for i, (score, lu) in enumerate(lineups):
        for j, p in enumerate(lu):
            rows.append({
                "Lineup": i + 1,
                "Position": j + 1,
                "Name": p["name"],
                "Position_Type": p["pos"],
                "Team": p["team"],
                "Salary": p["salary"],
                "Projection": p["proj"],
                "Ownership": p["own"],
                "Score": score
            })
    
    df = pd.DataFrame(rows)
    df.to_csv("out/week01/lineups_150_proper_stacks.csv", index=False)
    print(f"Exported {len(lineups)} lineups to out/week01/lineups_150_proper_stacks.csv")
    
    # Export lineups in DraftKings upload format
    all_dk_rows = []
    for i, (score, lu) in enumerate(lineups):
        dk_rows = format_lineup_for_draftkings(lu, i + 1)
        all_dk_rows.extend(dk_rows)
    
    dk_df = pd.DataFrame(all_dk_rows)
    dk_df.to_csv("out/week01/lineups_150_draftkings_upload.csv", index=False)
    print(f"Exported {len(lineups)} lineups to out/week01/lineups_150_draftkings_upload.csv")

if __name__ == "__main__":
    main()
