
import argparse, os, pandas as pd, numpy as np, json, yaml

def minmax(series):
    if series.isna().all(): 
        return series.fillna(0.0)
    lo, hi = series.min(), series.max()
    if hi - lo < 1e-9:
        return pd.Series(50.0, index=series.index)
    return (series - lo) / (hi - lo) * 100.0

def main(indir:str, weights:str, out_csv:str):
    sched = pd.read_csv(os.path.join(indir, "schedule.csv"))
    odds = pd.read_csv(os.path.join(indir, "odds.csv"))
    wx = pd.read_csv(os.path.join(indir, "weather.csv"))
    proe = pd.read_csv(os.path.join(indir, "proe_pace.csv"))
    conc = pd.read_csv(os.path.join(indir, "concentration.csv"))
    with open(weights,"r") as f:
        W = yaml.safe_load(f)

    # Simple joins:
    df = sched.merge(wx, on=["game_id","home_team","away_team"], how="left")

    # Merge odds by naive string contains (book names use full team names). Leave blank if unmatched.
    def resolve_ou(row):
        # try to match by team abbreviation occurring in name columns
        # this placeholder can be improved using a mapping file
        return np.nan
    # Build team-level features by aligning home/away to proe & concentration
    proe = proe.rename(columns={"team":"team_abbr","proe":"proe_pct","sec_per_play_neutral":"sec_per_play"})
    conc = conc.rename(columns={"team":"team_abbr"})

    df = df.merge(proe.add_suffix("_home").rename(columns={"team_abbr_home":"home_team"}), left_on="home_team", right_on="home_team", how="left")
    df = df.merge(proe.add_suffix("_away").rename(columns={"team_abbr_away":"away_team"}), left_on="away_team", right_on="away_team", how="left")
    df = df.merge(conc.add_suffix("_home").rename(columns={"team_abbr_home":"home_team"}), on="home_team", how="left")
    df = df.merge(conc.add_suffix("_away").rename(columns={"team_abbr_away":"away_team"}), on="away_team", how="left")

    # Combined metrics
    df["combined_proe"] = (df["proe_pct_home"] + df["proe_pct_away"]) / 2.0
    df["combined_pace_sp"] = (df["sec_per_play_home"] + df["sec_per_play_away"]) / 2.0
    df["combined_concentration"] = (df["top2_tgt_share_avg_home"] + df["top2_tgt_share_avg_away"]) / 2.0
    # Venue score (dome/fixed best; retractable mid; outdoor penalized by wind)
    roof = df["venue_roof"].fillna("outdoor").str.lower()
    venue_score = np.where(roof.isin(["dome","fixed"]), 100.0,
                    np.where(roof.eq("retractable"), 80.0, 60.0))
    wind = df["wind_mph"].fillna(0.0)
    venue_score = venue_score - np.clip(wind, 0, 25)  # subtract 1 per mph up to 25
    df["venue_score"] = venue_score

    # Normalize components
    df["z_ou"] = minmax(df.get("ou_consensus", pd.Series(np.nan, index=df.index)).fillna(df.get("spread_home_consensus",0)*0))
    df["z_proe"] = minmax(df["combined_proe"])
    df["z_pace"] = 100 - minmax(df["combined_pace_sp"])  # faster (lower sec/play) -> higher score
    df["z_venue"] = minmax(df["venue_score"])
    df["z_conc"] = minmax(df["combined_concentration"])
    # Ownership leverage placeholder (0 if not provided)
    if "stack_cum_own" in df.columns:
        df["z_lev"] = 100 - minmax(df["stack_cum_own"])  # lower ownership -> higher score
    else:
        df["z_lev"] = 50.0

    # Weighted score
    df["edge_score"] = (
        W["w_ou"]*df["z_ou"] +
        W["w_proe"]*df["z_proe"] +
        W["w_pace"]*df["z_pace"] +
        W["w_venue"]*df["z_venue"] +
        W["w_concentration"]*df["z_conc"] +
        W["w_leverage"]*df["z_lev"]
    )
    df = df.sort_values("edge_score", ascending=False)
    df.to_csv(out_csv, index=False)
    print(f"Wrote {out_csv}")

if __name__=="__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", required=True)
    ap.add_argument("--weights", default=os.path.join(os.path.dirname(__file__), "..","config","weights.yaml"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    main(args.indir, args.weights, args.out)
