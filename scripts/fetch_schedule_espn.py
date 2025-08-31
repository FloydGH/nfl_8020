import argparse, pandas as pd

# 2025 Week 1 schedule based on DraftKings slate
WEEK1_2025_SCHEDULE = [
    {"game_id": "2025_01_CIN_CLE", "away_team": "CIN", "home_team": "CLE", "start_time": "2025-09-07 13:00", "venue": "FirstEnergy Stadium"},
    {"game_id": "2025_01_TB_ATL", "away_team": "TB", "home_team": "ATL", "start_time": "2025-09-07 13:00", "venue": "Mercedes-Benz Stadium"},
    {"game_id": "2025_01_DET_GB", "away_team": "DET", "home_team": "GB", "start_time": "2025-09-07 16:25", "venue": "Lambeau Field"},
    {"game_id": "2025_01_HOU_LAR", "away_team": "HOU", "home_team": "LAR", "start_time": "2025-09-07 16:25", "venue": "SoFi Stadium"},
    {"game_id": "2025_01_SF_SEA", "away_team": "SF", "home_team": "SEA", "start_time": "2025-09-07 16:05", "venue": "Lumen Field"},
    {"game_id": "2025_01_LV_NE", "away_team": "LV", "home_team": "NE", "start_time": "2025-09-07 13:00", "venue": "Gillette Stadium"},
    {"game_id": "2025_01_NYG_WAS", "away_team": "NYG", "home_team": "WAS", "start_time": "2025-09-07 13:00", "venue": "FedExField"},
    {"game_id": "2025_01_MIA_IND", "away_team": "MIA", "home_team": "IND", "start_time": "2025-09-07 13:00", "venue": "Lucas Oil Stadium"},
    {"game_id": "2025_01_CAR_JAX", "away_team": "CAR", "home_team": "JAX", "start_time": "2025-09-07 13:00", "venue": "EverBank Stadium"},
    {"game_id": "2025_01_ARI_NO", "away_team": "ARI", "home_team": "NO", "start_time": "2025-09-07 13:00", "venue": "Caesars Superdome"},
    {"game_id": "2025_01_PIT_NYJ", "away_team": "PIT", "home_team": "NYJ", "start_time": "2025-09-07 13:00", "venue": "MetLife Stadium"},
    {"game_id": "2025_01_TEN_DEN", "away_team": "TEN", "home_team": "DEN", "start_time": "2025-09-07 16:05", "venue": "Empower Field at Mile High"}
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", type=int, required=True)
    ap.add_argument("--week", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    
    # For now, just use the hardcoded schedule for 2025 Week 1
    if args.season == 2025 and args.week == 1:
        df = pd.DataFrame(WEEK1_2025_SCHEDULE)
    else:
        # Fallback to empty schedule for other weeks
        df = pd.DataFrame(columns=["game_id", "away_team", "home_team", "start_time", "venue"])
    
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} games to {args.out}")

if __name__ == "__main__":
    main()
