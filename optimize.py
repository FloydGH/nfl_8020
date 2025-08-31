
import pandas as pd, numpy as np, math, random, itertools, collections
from pathlib import Path
from utils import read_weights, load_dk, load_optional, ownership_proxy, projection_proxy, lineup_score

def pos_ok(lineup, to_add_pos):
    counts = collections.Counter([p["pos"] for p in lineup])
    
    # During building, be more flexible to allow reaching 9 players
    # Final validation will happen later with finalize_positions
    if len(lineup) < 9:
        # Allow more flexibility during building
        limits = {"QB":1,"RB":4,"WR":5,"TE":3,"DST":1}
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

def build_player_rows(dk_df, proj_df, own_df):
    df = dk_df.merge(proj_df, on=["name","team","pos"], how="left")
    if own_df is not None:
        df = df.merge(own_df[["name","own"]], on="name", how="left")
    df["own"] = df["own"].fillna( df.groupby("pos")["own"].transform(lambda s: s.fillna(s.median())) )
    # some teams may not align (team abbreviations); we keep as-is
    # row dicts
    rows = []
    for _,r in df.iterrows():
        rows.append({
            "name": r["name"], "team": r["team"], "pos": r["pos"], "salary": int(r["salary"]),
            "proj": float(r.get("proj", 0.0)), "p90": float(r.get("p90", r.get("proj",0)*1.6)),
            "own": float(r.get("own", 5.0))
        })
    return rows

def team_opponent_map(edge_df):
    m = {}
    for _,r in edge_df.iterrows():
        m[r["home_team"]] = r["away_team"]
        m[r["away_team"]] = r["home_team"]
    return m

def player_lookup_by_name(players):
    return {p["name"]: p for p in players}

def forbid_offense_vs_dst(lineup, cfg):
    if cfg.get("max_same_dst_opp", 0) != 0:
        return True
    dst_teams = [p["team"] for p in lineup if p["pos"]=="DST"]
    if not dst_teams: return True
    dst_team = dst_teams[0]
    # approximate: offensive players from opponent of dst_team should be forbidden
    # Without explicit schedule, we can't map opponent here; we just ensure no same-team offense vs DST of opponent later.
    return True

def build_lineups_150(dk_df, edge_df, stacks_df, players, cfg):
    print(f"DEBUG: Starting build_lineups_150 with {len(players)} players")
    print(f"DEBUG: Stacks data shape: {stacks_df.shape}")
    print(f"DEBUG: Stacks columns: {stacks_df.columns.tolist()}")
    print(f"DEBUG: First few stacks:")
    print(stacks_df.head())
    
    # index players
    by_name = player_lookup_by_name(players)
    print(f"DEBUG: Player lookup created with {len(by_name)} players")
    
    # choose how many lineups per stack roughly by tier shares
    tier_counts = {"A": int(150*cfg["tier_A_share"]), "B": int(150*cfg["tier_B_share"])}
    tier_counts["C"] = 150 - tier_counts["A"] - tier_counts["B"]
    print(f"DEBUG: Tier counts: {tier_counts}")
    
    # bucket stacks by tier
    stacks_by_tier = {k: stacks_df[stacks_df["tier"]==k].to_dict("records") for k in ["A","B","C"]}
    print(f"DEBUG: Stacks by tier: {[(k, len(v)) for k, v in stacks_by_tier.items()]}")
    
    # Prepare candidate pools by position for speed
    pool_by_pos = collections.defaultdict(list)
    for p in players: pool_by_pos[p["pos"]].append(p)
    for v in pool_by_pos.values(): v.sort(key=lambda x: (x["proj"] + 0.35*(x["p90"]-x["proj"]) - 0.03*x["own"]), reverse=True)
    print(f"DEBUG: Position pools: {[(pos, len(players)) for pos, players in pool_by_pos.items()]}")

    # Ownership thresholds
    low_thr = cfg["low_owned_threshold_pct"]

    # Construct lineups
    lineups = []
    seen_five_sets = set()
    rng = random.Random(42)

    def fits_salary(lu):
        s = sum(p["salary"] for p in lu)
        return cfg["min_salary"] <= s <= cfg["max_salary"]

    def ok_ownership(lu):
        own = sum(p["own"] for p in lu)
        low = sum(1 for p in lu if p["own"] < low_thr)
        sub10 = sum(1 for p in lu if p["own"] < 10)
        if own > cfg["cum_own_cap_pct"]: return False
        if low < cfg["min_low_owned_per_lu"]: return False
        if sub10 < cfg["min_sub10_owned_per_lu"]: return False
        return True

    # Helper to get player object or None
    def P(name):
        return by_name.get(name)

    # compile allowable shells proportions
    shells = [
        ("3v1", cfg["pct_3v1"]),
        ("3v0", cfg["pct_3v0"]),
        ("4v1", cfg["pct_4v1"]),
        ("2v1", cfg["pct_2v1"])
    ]

    def pick_shell(tier, weekly_row):
        # choose shell with conditions
        wind = weekly_row.get("wind_mph", 0) or 0
        spread = abs(weekly_row.get("spread_home", 0) or 0)
        pool = []
        for name,share in shells:
            if name=="3v0":
                if spread >= cfg["allow_3v0_spread_cutoff"] or wind >= cfg["allow_3v0_wind_cutoff"]:
                    pool.append((name,share))
            else:
                pool.append((name,share))
        tot = sum(s for _,s in pool) or 1.0
        x = rng.random()*tot
        acc = 0.0
        for n,s in pool:
            acc += s
            if x <= acc: return n
        return "3v1"

    # weekly lookup
    weekly_map = {}
    for _,r in edge_df.iterrows():
        weekly_map[(r["home_team"], r["away_team"])] = r

    def add_flex_bias(lu):
        # Ensure WR in FLEX at least some share by preferring WR when last slot ambiguous—handled implicitly by pool ordering

        return

    # Build for each tier
    for tier in ["A","B","C"]:
        stacks = stacks_by_tier.get(tier, [])
        if not len(stacks): 
            print(f"DEBUG: No stacks for tier {tier}, skipping")
            continue
        need = tier_counts[tier]
        if need <= 0: 
            print(f"DEBUG: Tier {tier} needs {need} lineups, skipping")
            continue
        print(f"DEBUG: Building {need} lineups for tier {tier} with {len(stacks)} stacks")
        
        # cycle through stacks round-robin
        idx = 0
        attempts = 0
        while need > 0 and attempts < need*20:
            attempts += 1
            s = stacks[idx % len(stacks)]
            idx += 1
            # determine weekly row to choose shell
            wkrow = weekly_map.get((s["home_team"] if "home_team" in s else s.get("team_qb"), s.get("opp_team")), {})
            shell = "3v1"  # simplified; could call pick_shell if we had full weekly row here

            # Pull players
            # Parse stack string (e.g., '["Ja\'Marr Chase", \'Tee Higgins\']')
            stack_str = s["stack"]
            if isinstance(stack_str, str):
                # Remove quotes and brackets, split by comma
                clean_str = stack_str.strip("[]'\"")
                stack_names = [name.strip().strip("'\"") for name in clean_str.split(',')]
            else:
                stack_names = stack_str
            
            qb = P(s["qb"]); pc1 = P(stack_names[0]); pc2 = P(stack_names[1]); br = P(s["bringback"])
            if not all([qb, pc1, pc2, br]): 
                print(f"DEBUG: Missing players for stack {s}: qb={qb is not None}, pc1={pc1 is not None}, pc2={pc2 is not None}, br={br is not None}")
                continue
            # Start lineup with core
            lu = [qb, pc1, pc2, br]

            # Fill remaining with greedy best that respects positions, salary, and correlation avoidances
            # Avoid adding more from the two core teams unless role allows; simple rule: exclude same two teams (except DST or pass-catching RBs if they weren't selected)
            core_teams = {qb["team"], br["team"]}
            
            # Strategic filling: prioritize positions we need
            while len(lu) < 9:
                # Determine what positions we need
                counts = collections.Counter([p["pos"] for p in lu])
                needed_positions = []
                
                if counts["TE"] < 1:
                    needed_positions.append("TE")
                if counts["DST"] < 1:
                    needed_positions.append("DST")
                if counts["RB"] < 2:
                    needed_positions.append("RB")
                if counts["WR"] < 3:
                    needed_positions.append("WR")
                
                # If we have the minimums, add flex positions
                if len(needed_positions) == 0:
                    # We have minimums, add flex (RB/WR/TE)
                    if counts["RB"] < 3:
                        needed_positions.append("RB")
                    if counts["WR"] < 4:
                        needed_positions.append("WR")
                    if counts["TE"] < 2:
                        needed_positions.append("TE")
                
                # Find best player for needed positions
                best_player = None
                best_score = -1
                
                for p in players:
                    if p["name"] in {x["name"] for x in lu}:
                        continue
                    if p["team"] in core_teams and p["pos"] != "DST":
                        continue
                    if p["pos"] not in needed_positions:
                        continue
                    if not pos_ok(lu, p["pos"]):
                        continue
                    if sum(x["salary"] for x in lu) + p["salary"] > 50000:
                        continue
                    
                    # Calculate player score
                    score = p["proj"] + 0.35*(p["p90"]-p["proj"]) - 0.03*p["own"]
                    if score > best_score:
                        best_score = score
                        best_player = p
                
                if best_player is None:
                    print(f"DEBUG: Cannot find player for needed positions {needed_positions}, lineup stuck at {len(lu)} players")
                    break
                
                lu.append(best_player)
                print(f"DEBUG: Added {best_player['pos']} {best_player['name']}, lineup now has {len(lu)} players: {[x['pos'] for x in lu]}")

            # If not enough players, skip
            if len(lu) != 9: 
                print(f"DEBUG: Lineup only has {len(lu)} players, skipping")
                continue
            # Validate positions
            if not finalize_positions(lu):
                print(f"DEBUG: Position validation failed for lineup with {len(lu)} players")
                continue
            # Salary band check
            ssum = sum(p["salary"] for p in lu)
            bands = [(49600,50000,0.85),(49200,49599,0.10),(48800,49199,0.05)]
            # lightweight random accept based on band weights
            band = None
            for b in bands:
                if b[0] <= ssum <= b[1]:
                    band = b; break
            if band is None:
                # allow if above min
                if ssum < 49600: 
                    print(f"DEBUG: Salary {ssum} below minimum 49600, skipping")
                    continue
            # Ownership gates
            if not ok_ownership(lu):
                print(f"DEBUG: Ownership validation failed for lineup")
                continue
            # 5-man uniqueness
            five = tuple(sorted([p["name"] for p in lu[:5]]))
            if five in seen_five_sets:
                continue
            seen_five_sets.add(five)
            # Score (for ordering later)
            score = lineup_score(lu, 0.35, 0.03)
            lineups.append((score, lu))
            need -= 1
            print(f"DEBUG: Successfully built lineup {len(lineups)} for tier {tier}")

    print(f"DEBUG: Built {len(lineups)} total lineups")
    # Sort by score desc and take top 150
    lineups = sorted(lineups, key=lambda x: x[0], reverse=True)[:150]
    return lineups

def export_lineups(lineups, out_csv):
    # Export in a readable CSV (Name,Pos,Team,Salary)
    rows = []
    for rank,(score, lu) in enumerate(lineups, start=1):
        row = {"rank": rank, "score": round(score,2), "salary": sum(p["salary"] for p in lu)}
        # add roster slots in DK-like order
        # We'll simply sort by a slot key: QB, RBx2, WRx3, TEx1, FLEXx1 (RB/WR/TE), DST
        # For export we just list names and positions
        lu_sorted = sorted(lu, key=lambda p: {"QB":0,"RB":1,"WR":2,"TE":3,"DST":5}.get(p["pos"],9))
        for i,p in enumerate(lu_sorted):
            row[f"p{i+1}_name"] = p["name"]; row[f"p{i+1}_pos"] = p["pos"]; row[f"p{i+1}_team"] = p["team"]; row[f"p{i+1}_sal"] = p["salary"]
        rows.append(row)
    pd.DataFrame(rows).to_csv(out_csv, index=False)

def main(weekly_path, edge_path, stacks_path, roles_path, dk_path, out_dir, projections_path=None, ownership_path=None, weights_path=None):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    # Load data
    weekly_df = pd.read_csv(weekly_path)
    edge_df    = pd.read_csv(edge_path)
    stacks_df  = pd.read_csv(stacks_path)
    roles_df   = pd.read_csv(roles_path)
    dk_df      = load_dk(dk_path)
    # Projections & ownership
    proj_df = None
    if projections_path and Path(projections_path).exists():
        proj_df = pd.read_csv(projections_path)
        needed = {"name","team","pos","proj","p90"}
        if not needed.issubset(set(proj_df.columns)):
            raise ValueError("projections.csv needs columns: name,team,pos,proj,p90")
    else:
        proj_df = projection_proxy(dk_df)

    own_df = None
    if ownership_path and Path(ownership_path).exists():
        own_df = pd.read_csv(ownership_path)
        if not {"name","own"}.issubset(set(own_df.columns)):
            raise ValueError("ownership.csv needs columns: name,own")
    else:
        own_df = ownership_proxy(dk_df, weekly_df)

    # Build player rows
    players = build_player_rows(dk_df, proj_df, own_df)

    # Read weights/config
    cfg = read_weights(weights_path) if weights_path else {
        "tier_A_share":0.7,"tier_B_share":0.25,"tier_C_share":0.05,
        "min_salary":49600,"max_salary":50000,"low_owned_threshold_pct":5,
        "min_low_owned_per_lu":1,"min_sub10_owned_per_lu":2,"cum_own_cap_pct":125,
        "allow_3v0_spread_cutoff":7.5,"allow_3v0_wind_cutoff":15,
        "pct_3v1":0.70,"pct_3v0":0.15,"pct_4v1":0.10,"pct_2v1":0.05
    }

    # Build lineups
    lineups = build_lineups_150(dk_df, edge_df, stacks_df, players, cfg)
    out_csv = out_dir/"lineups_150.csv"
    export_lineups(lineups, out_csv)
    return out_csv

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--weekly", required=True)
    ap.add_argument("--edge", required=True)
    ap.add_argument("--stacks", required=True)
    ap.add_argument("--roles", required=True)
    ap.add_argument("--dk", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--projections", default=None)
    ap.add_argument("--ownership", default=None)
    ap.add_argument("--weights", default=None)
    args = ap.parse_args()
    main(args.weekly, args.edge, args.stacks, args.roles, args.dk, args.out, args.projections, args.ownership, args.weights)
