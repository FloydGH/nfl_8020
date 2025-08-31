
import pandas as pd, numpy as np
from utils import read_weights, normalize_0_100, tier_label, load_weekly_inputs

def calc_edge_scores(weekly_df, weights):
    rows = []
    for _,r in weekly_df.iterrows():
        # Over/Under scoring
        ou_score = 0
        if pd.notna(r["ou"]) and r["ou"] > 0:
            if r["ou"] < 44: ou_score = 0
            elif r["ou"] <= 46.5: ou_score = 50
            elif r["ou"] <= 49: ou_score = 75
            else: ou_score = 100
        
        # Spread scoring
        spread = abs(r["spread_home"]) if pd.notna(r["spread_home"]) and r["spread_home"] != 0 else 99
        spread_score = 100 if spread <= 3 else 70 if spread <= 6 else 40 if spread <= 9.5 else 10
        
        # PROE scoring (Pass Rate Over Expected)
        proe_home = r.get("proe_home", 0) or 0
        proe_away = r.get("proe_away", 0) or 0
        combined_proe = proe_home + proe_away
        # Normalize combined PROE roughly -10..+10 to 0..100
        proe_norm = normalize_0_100(combined_proe, -10, 10)

        # Pace scoring (lower seconds per play = faster pace = higher score)
        pace_home = r.get("pace_rank_home", 16) or 16
        pace_away = r.get("pace_rank_away", 16) or 16
        # convert rank to score: rank 1 -> 100, rank 32 -> 0
        pace_score = ((32 - pace_home) / 31 * 100 + (32 - pace_away) / 31 * 100) / 2.0

        # Combined PROE and pace score
        proe_pace = (proe_norm * 0.6 + pace_score * 0.4)

        # Venue and weather scoring
        venue = (r.get("venue_roof","") or "").lower()
        wind = r.get("wind_mph", 0) or 0
        venue_score = 100 if "dome" in venue or "fixed" in venue else 70
        if wind >= 15: venue_score = 20

        # Concentration scoring: use WR1/WR2 target share and TE/RB route participation
        conc_home = np.nanmean([
            r.get("wr1_tgt_share_home", 0.28), 
            r.get("wr2_tgt_share_home", 0.18), 
            r.get("te_route_share_home", 0.18), 
            r.get("rb_route_share_home", 0.16)
        ])
        conc_away = np.nanmean([
            r.get("wr1_tgt_share_away", 0.28), 
            r.get("wr2_tgt_share_away", 0.18), 
            r.get("te_route_share_away", 0.18), 
            r.get("rb_route_share_away", 0.16)
        ])
        conc_score = normalize_0_100((conc_home + conc_away) / 2.0, 0.10, 0.35)

        # Ownership penalty (placeholder for now)
        own_penalty = min(max(r.get("stack_cum_own_est", 0), 0), 120) / 120.0 * 100.0

        # Calculate final edge score
        edge = (
            weights["w_ou"] * ou_score +
            weights["w_spread"] * spread_score +
            weights["w_proe_pace"] * proe_pace +
            weights["w_venue_weather"] * venue_score +
            weights["w_concentration"] * conc_score -
            weights["w_ownership_penalty"] * own_penalty
        )
        
        rows.append({
            "game_id": r["game_id"],
            "home_team": r["home_team"],
            "away_team": r["away_team"],
            "ou": r["ou"],
            "spread_home": r["spread_home"],
            "edge_score": round(edge, 2),
            "tier": tier_label(edge)
        })
    
    out = pd.DataFrame(rows).sort_values(["tier","edge_score"], ascending=[True, False]).reset_index(drop=True)
    return out

def main(weekly_path, weights_path, out_path):
    weekly = load_weekly_inputs(weekly_path)
    weights = read_weights(weights_path)
    edge = calc_edge_scores(weekly, weights)
    edge.to_csv(out_path, index=False)
    return edge

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--weekly", required=True)
    ap.add_argument("--weights", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    main(args.weekly, args.weights, args.out)
