
import os, argparse, pandas as pd, json, subprocess, sys, shutil, yaml

here = os.path.dirname(__file__)

def run(cmd:list):
    print("+", " ".join(cmd))
    res = subprocess.run(cmd, check=True)
    return res.returncode

if __name__=="__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", type=int, required=True)
    ap.add_argument("--week", type=int, required=True)
    ap.add_argument("--outdir", type=str, required=True)
    ap.add_argument("--odds_api_key", type=str, default=os.getenv("ODDS_API_KEY"))
    ap.add_argument("--stadiums", type=str, default=os.path.join(os.path.dirname(here),"config","stadiums.json"))
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    schedule_csv = os.path.join(args.outdir, "schedule.csv")
    odds_csv = os.path.join(args.outdir, "odds.csv")
    weather_csv = os.path.join(args.outdir, "weather.csv")
    proe_csv = os.path.join(args.outdir, "proe_pace.csv")
    conc_csv = os.path.join(args.outdir, "concentration.csv")
    roles_csv = os.path.join(args.outdir, "roles.csv")

    # Run all the data fetching scripts
    run([sys.executable, os.path.join(here,"fetch_schedule_espn.py"), "--season", str(args.season), "--week", str(args.week), "--out", schedule_csv])
    run([sys.executable, os.path.join(here,"fetch_lines_oddsapi.py"), "--out", odds_csv] + (["--api_key", args.odds_api_key] if args.odds_api_key else []))
    run([sys.executable, os.path.join(here,"fetch_weather_openmeteo.py"), "--schedule", schedule_csv, "--stadiums", args.stadiums, "--out", weather_csv])
    run([sys.executable, os.path.join(here,"compute_proe_pace.py"), "--season", str(args.season), "--out", proe_csv])
    run([sys.executable, os.path.join(here,"compute_concentration.py"), "--season", str(args.season), "--out", conc_csv])
    run([sys.executable, os.path.join(here,"fetch_depth_charts_ourlads.py"), "--out", roles_csv])

    # Load all the data
    sched = pd.read_csv(schedule_csv)
    odds = pd.read_csv(odds_csv)
    wx = pd.read_csv(weather_csv)
    proe = pd.read_csv(proe_csv)
    conc = pd.read_csv(conc_csv)
    roles = pd.read_csv(roles_csv)

    # Start with schedule and merge weather
    df = sched.merge(wx[["game_id","venue_roof","wind_mph"]], on="game_id", how="left")
    
    # Merge odds data by team abbreviations
    if not odds.empty:
        # Create a mapping for team names to abbreviations
        team_mapping = {
            "Eagles": "PHI", "Cowboys": "DAL", "Falcons": "ATL", "Buccaneers": "TB",
            "Chargers": "LAC", "Chiefs": "KC", "Jaguars": "JAX", "Panthers": "CAR",
            "Commanders": "WAS", "Giants": "NYG", "Saints": "NO", "Cardinals": "ARI",
            "Browns": "CLE", "Bengals": "CIN", "Colts": "IND", "Dolphins": "MIA",
            "Patriots": "NE", "Raiders": "LV", "Jets": "NYJ", "Steelers": "PIT",
            "Broncos": "DEN", "Titans": "TEN", "Seahawks": "SEA", "49ers": "SF",
            "Lions": "DET", "Bears": "CHI", "Packers": "GB", "Vikings": "MIN",
            "Rams": "LAR", "Texans": "HOU", "Bills": "BUF", "Ravens": "BAL"
        }
        
        # Extract team abbreviations from full names
        odds["home_abbr"] = odds["home_team_name"].str.split().str[-1].map(team_mapping)
        odds["away_abbr"] = odds["away_team_name"].str.split().str[-1].map(team_mapping)
        
        # Filter odds to only include our specific games
        game_odds = []
        for _, game in df.iterrows():
            home_team = game["home_team"]
            away_team = game["away_team"]
            
            # Find matching odds
            matching_odds = odds[
                ((odds["home_abbr"] == home_team) & (odds["away_abbr"] == away_team)) |
                ((odds["home_abbr"] == away_team) & (odds["away_abbr"] == home_team))
            ]
            
            if not matching_odds.empty:
                odds_row = matching_odds.iloc[0]
                # Determine if we need to flip the spread
                if odds_row["home_abbr"] == home_team:
                    spread = odds_row["spread_home_consensus"]
                else:
                    spread = -odds_row["spread_home_consensus"] if odds_row["spread_home_consensus"] is not None else None
                
                game_odds.append({
                    "game_id": game["game_id"],
                    "ou": odds_row["ou_consensus"],
                    "spread_home": spread
                })
            else:
                game_odds.append({
                    "game_id": game["game_id"],
                    "ou": None,
                    "spread_home": None
                })
        
        odds_df = pd.DataFrame(game_odds)
        df = df.merge(odds_df, on="game_id", how="left")
    else:
        # Add placeholder columns if no odds data
        df["ou"] = None
        df["spread_home"] = None

    # Merge PROE and pace data
    proe_home = proe.rename(columns={
        "team": "home_team",
        "proe": "proe_home",
        "sec_per_play_neutral": "sec_per_play_home"
    })
    proe_away = proe.rename(columns={
        "team": "away_team", 
        "proe": "proe_away",
        "sec_per_play_neutral": "sec_per_play_away"
    })
    
    df = df.merge(proe_home[["home_team","proe_home","sec_per_play_home"]], on="home_team", how="left")
    df = df.merge(proe_away[["away_team","proe_away","sec_per_play_away"]], on="away_team", how="left")
    
    # Calculate pace ranks
    pace_df = proe[["team","sec_per_play_neutral"]].copy()
    pace_df["pace_rank"] = pace_df["sec_per_play_neutral"].rank(method="min")
    
    pace_home = pace_df.rename(columns={"team": "home_team", "pace_rank": "pace_rank_home"})
    pace_away = pace_df.rename(columns={"team": "away_team", "pace_rank": "pace_rank_away"})
    
    df = df.merge(pace_home[["home_team","pace_rank_home"]], on="home_team", how="left")
    df = df.merge(pace_away[["away_team","pace_rank_away"]], on="away_team", how="left")

    # Merge concentration data
    conc_home = conc.rename(columns={
        "team": "home_team",
        "top2_tgt_share_avg": "top2_tgt_share_home",
        "te_route_share": "te_route_share_home", 
        "rb_route_share": "rb_route_share_home"
    })
    conc_away = conc.rename(columns={
        "team": "away_team",
        "top2_tgt_share_avg": "top2_tgt_share_away",
        "te_route_share": "te_route_share_away",
        "rb_route_share": "rb_route_share_away"
    })
    
    df = df.merge(conc_home[["home_team","top2_tgt_share_home","te_route_share_home","rb_route_share_home"]], on="home_team", how="left")
    df = df.merge(conc_away[["away_team","top2_tgt_share_away","te_route_share_away","rb_route_share_away"]], on="away_team", how="left")
    
    # Create WR1/WR2 target share columns
    for side in ["home", "away"]:
        top2 = df[f"top2_tgt_share_{side}"].fillna(0.45)
        df[f"wr1_tgt_share_{side}"] = (top2 * 0.60).clip(0, 1)
        df[f"wr2_tgt_share_{side}"] = (top2 * 0.40).clip(0, 1)
        
        # Fill missing route shares
        if f"te_route_share_{side}" not in df.columns:
            df[f"te_route_share_{side}"] = 0.18
        if f"rb_route_share_{side}" not in df.columns:
            df[f"rb_route_share_{side}"] = 0.16

    # Add ownership penalty placeholder
    df["stack_cum_own_est"] = 0.0

    # Ensure all required columns exist
    required_columns = [
        "game_id", "home_team", "away_team", "venue_roof", "wind_mph",
        "ou", "spread_home", "proe_home", "proe_away", "pace_rank_home", "pace_rank_away",
        "wr1_tgt_share_home", "wr2_tgt_share_home", "te_route_share_home", "rb_route_share_home",
        "wr1_tgt_share_away", "wr2_tgt_share_away", "te_route_share_away", "rb_route_share_away",
        "stack_cum_own_est"
    ]
    
    for col in required_columns:
        if col not in df.columns:
            if "proe" in col:
                df[col] = 0.0
            elif "pace_rank" in col:
                df[col] = 16.0
            elif "tgt_share" in col or "route_share" in col:
                df[col] = 0.2
            elif col == "stack_cum_own_est":
                df[col] = 0.0
            else:
                df[col] = None

    # Write the final weekly inputs file
    weekly_inputs = os.path.join(args.outdir, "weekly_inputs.csv")
    df[required_columns].to_csv(weekly_inputs, index=False)
    print(f"Wrote complete weekly inputs to {weekly_inputs}")
    print(f"Data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Show sample of odds data
    if "ou" in df.columns and "spread_home" in df.columns:
        print("\nOdds data sample:")
        odds_sample = df[["game_id", "ou", "spread_home"]].head()
        print(odds_sample.to_string(index=False))
