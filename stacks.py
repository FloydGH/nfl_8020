
import pandas as pd, numpy as np, math, random
from utils import read_weights, load_weekly_inputs, load_roles

def pick_games(edge_df, weights):
    # Allocate by tiers using config shares
    tierA = edge_df[edge_df["tier"]=="A"].copy().sort_values("edge_score", ascending=False)
    tierB = edge_df[edge_df["tier"]=="B"].copy().sort_values("edge_score", ascending=False)
    tierC = edge_df[edge_df["tier"]=="C"].copy().sort_values("edge_score", ascending=False)
    
    print(f"DEBUG: Tier A games: {len(tierA)}")
    print(f"DEBUG: Tier B games: {len(tierB)}")
    print(f"DEBUG: Tier C games: {len(tierC)}")
    
    # Keep top few
    sel = pd.concat([tierA.head(3), tierB.head(2), tierC.head(1)], ignore_index=True)
    print(f"DEBUG: Selected {len(sel)} games:")
    print(sel[["home_team", "away_team", "tier", "edge_score"]])
    
    return sel

def build_core_stacks(selected_games, roles_df, weekly_df, weights):
    # For each game, create stack blueprints: 3v1 default; allow other shells conditionally
    shells = []
    
    print(f"DEBUG: Building stacks for {len(selected_games)} selected games")
    
    for _, g in selected_games.iterrows():
        home, away = g["home_team"], g["away_team"]
        print(f"DEBUG: Processing game {home} vs {away}")
        
        # Get role players
        rh = roles_df[roles_df["team"]==home].iloc[0].to_dict() if (roles_df["team"]==home).any() else None
        ra = roles_df[roles_df["team"]==away].iloc[0].to_dict() if (roles_df["team"]==away).any() else None
        
        if not (rh and ra and rh.get("QB1") and ra.get("QB1")):
            print(f"DEBUG: Missing role data for {home} vs {away}")
            print(f"  rh: {rh is not None}, ra: {ra is not None}")
            if rh: print(f"  rh QB1: {rh.get('QB1')}")
            if ra: print(f"  ra QB1: {ra.get('QB1')}")
            continue
            
        print(f"DEBUG: Found roles for {home} vs {away}")
        print(f"  {home} QB1: {rh.get('QB1')}, WR1: {rh.get('WR1')}, WR2: {rh.get('WR2')}")
        print(f"  {away} QB1: {ra.get('QB1')}, WR1: {ra.get('WR1')}, WR2: {ra.get('WR2')}")
        
        # WR/TE candidates - handle missing slot_wr column
        def pcands(r):
            out = [r.get("WR1"), r.get("WR2"), r.get("TE1")]
            # Add slot_wr if it exists, otherwise use WR2
            if "slot_wr" in r:
                out.append(r.get("slot_wr"))
            return [x for x in out if x and isinstance(x, str)]
        Hpcs = pcands(rh)
        Apcs = pcands(ra)
        
        print(f"  {home} pass-catchers: {Hpcs}")
        print(f"  {away} pass-catchers: {Apcs}")
        
        # build 3v1 for both teams
        for (qb_team, qb, mates, opp_mates, opp_team) in [
            (home, rh["QB1"], Hpcs, Apcs, away),
            (away, ra["QB1"], Apcs, Hpcs, home),
        ]:
            # choose pairs of 2 teammates
            pairs = []
            for i in range(len(mates)):
                for j in range(i+1, len(mates)):
                    pairs.append((mates[i], mates[j]))
            if not pairs: 
                print(f"  No pairs found for {qb_team}")
                continue
                
            print(f"  {qb_team} pairs: {pairs}")
                
            # bring-backs (top two options)
            bringbacks = opp_mates[:2] if len(opp_mates)>=1 else []
            if not bringbacks: 
                print(f"  No bringbacks found for {qb_team}")
                continue
                
            print(f"  {qb_team} bringbacks: {bringbacks}")
                
            # create few combos
            for p in pairs[:3]:
                for b in bringbacks[:2]:
                    shells.append({
                        "game_id": g["game_id"],
                        "tier": g["tier"],
                        "qb": qb,
                        "team_qb": qb_team,
                        "stack": [p[0], p[1]],
                        "bringback": b,
                        "opp_team": opp_team
                    })
                    print(f"  Created stack: {qb} + {p[0]}/{p[1]} + {b}")
    
    print(f"DEBUG: Created {len(shells)} total stacks")
    return pd.DataFrame(shells)

def main(edge_path, roles_path, weekly_path, out_path):
    weights = {} # not used directly here
    edge = pd.read_csv(edge_path)
    roles = load_roles(roles_path)
    weekly = load_weekly_inputs(weekly_path)
    sel = pick_games(edge, weights)
    stacks = build_core_stacks(sel, roles, weekly, weights)
    stacks.to_csv(out_path, index=False)
    return stacks

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--edge", required=True)
    ap.add_argument("--roles", required=True)
    ap.add_argument("--weekly", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    main(args.edge, args.roles, args.weekly, args.out)
