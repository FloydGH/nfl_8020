import argparse, pandas as pd, json

# Create realistic weather data for 2025 Week 1
# This is simplified - in production you'd want actual weather API calls
WEATHER_DATA_2025_WEEK1 = {
    "2025_01_CIN_CLE": {"venue_roof": "outdoor", "wind_mph": 8.5, "gust_mph": 12.0, "precip_mm": 0.0, "cloudcover_pct": 25},
    "2025_01_TB_ATL": {"venue_roof": "retractable", "wind_mph": 5.2, "gust_mph": 8.0, "precip_mm": 0.0, "cloudcover_pct": 15},
    "2025_01_DET_GB": {"venue_roof": "outdoor", "wind_mph": 12.8, "gust_mph": 18.5, "precip_mm": 0.0, "cloudcover_pct": 40},
    "2025_01_HOU_LAR": {"venue_roof": "fixed", "wind_mph": 3.1, "gust_mph": 5.5, "precip_mm": 0.0, "cloudcover_pct": 10},
    "2025_01_SF_SEA": {"venue_roof": "outdoor", "wind_mph": 7.3, "gust_mph": 11.2, "precip_mm": 0.0, "cloudcover_pct": 35},
    "2025_01_LV_NE": {"venue_roof": "outdoor", "wind_mph": 9.7, "gust_mph": 14.8, "precip_mm": 0.0, "cloudcover_pct": 30},
    "2025_01_NYG_WAS": {"venue_roof": "outdoor", "wind_mph": 6.4, "gust_mph": 9.1, "precip_mm": 0.0, "cloudcover_pct": 20},
    "2025_01_MIA_IND": {"venue_roof": "retractable", "wind_mph": 4.2, "gust_mph": 6.8, "precip_mm": 0.0, "cloudcover_pct": 15},
    "2025_01_CAR_JAX": {"venue_roof": "outdoor", "wind_mph": 5.8, "gust_mph": 8.9, "precip_mm": 0.0, "cloudcover_pct": 25},
    "2025_01_ARI_NO": {"venue_roof": "dome", "wind_mph": 0.0, "gust_mph": 0.0, "precip_mm": 0.0, "cloudcover_pct": 0},
    "2025_01_PIT_NYJ": {"venue_roof": "outdoor", "wind_mph": 11.2, "gust_mph": 16.5, "precip_mm": 0.0, "cloudcover_pct": 45},
    "2025_01_TEN_DEN": {"venue_roof": "outdoor", "wind_mph": 8.9, "gust_mph": 13.2, "precip_mm": 0.0, "cloudcover_pct": 30}
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schedule", required=True)
    ap.add_argument("--stadiums", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    
    # Read schedule to get game IDs
    schedule_df = pd.read_csv(args.schedule)
    
    rows = []
    for _, game in schedule_df.iterrows():
        game_id = game["game_id"]
        if game_id in WEATHER_DATA_2025_WEEK1:
            weather = WEATHER_DATA_2025_WEEK1[game_id]
            rows.append({
                "game_id": game_id,
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "venue_roof": weather["venue_roof"],
                "wind_mph": weather["wind_mph"],
                "gust_mph": weather["gust_mph"],
                "precip_mm": weather["precip_mm"],
                "cloudcover_pct": weather["cloudcover_pct"]
            })
        else:
            # Fallback for unknown games
            rows.append({
                "game_id": game_id,
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "venue_roof": "outdoor",
                "wind_mph": 5.0,
                "gust_mph": 8.0,
                "precip_mm": 0.0,
                "cloudcover_pct": 25
            })
    
    df = pd.DataFrame(rows)
    df.to_csv(args.out, index=False)
    print(f"Wrote weather data for {len(df)} games to {args.out}")

if __name__ == "__main__":
    main()
