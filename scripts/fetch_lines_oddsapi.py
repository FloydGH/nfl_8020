
import requests, pandas as pd, argparse, os

# Updated team name mapping for 2025 season
TEAM_NAME_TO_ABBR = {
    "Arizona Cardinals": "ARI",
    "Atlanta Falcons": "ATL", 
    "Baltimore Ravens": "BAL",
    "Buffalo Bills": "BUF",
    "Carolina Panthers": "CAR",
    "Chicago Bears": "CHI",
    "Cincinnati Bengals": "CIN",
    "Cleveland Browns": "CLE",
    "Dallas Cowboys": "DAL",
    "Denver Broncos": "DEN",
    "Detroit Lions": "DET",
    "Green Bay Packers": "GB",
    "Houston Texans": "HOU",
    "Indianapolis Colts": "IND",
    "Jacksonville Jaguars": "JAX",
    "Kansas City Chiefs": "KC",
    "Las Vegas Raiders": "LV",
    "Los Angeles Chargers": "LAC",
    "Los Angeles Rams": "LAR",
    "Miami Dolphins": "MIA",
    "Minnesota Vikings": "MIN",
    "New England Patriots": "NE",
    "New Orleans Saints": "NO",
    "New York Giants": "NYG",
    "New York Jets": "NYJ",
    "Philadelphia Eagles": "PHI",
    "Pittsburgh Steelers": "PIT",
    "San Francisco 49ers": "SF",
    "Seattle Seahawks": "SEA",
    "Tampa Bay Buccaneers": "TB",
    "Tennessee Titans": "TEN",
    "Washington Commanders": "WAS"
}

def fetch_odds(api_key, sport="americanfootball_nfl"):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": api_key,
        "regions": "us",
        "markets": "spreads,totals",
        "oddsFormat": "american"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching odds: {e}")
        return []

def parse_odds_data(odds_data):
    rows = []
    for game in odds_data:
        home_team = game.get("home_team", "")
        away_team = game.get("away_team", "")
        
        # Get spreads and totals
        spreads = [book for book in game.get("bookmakers", []) if book.get("key") == "draftkings"]
        totals = [book for book in game.get("bookmakers", []) if book.get("key") == "draftkings"]
        
        spread_home = None
        ou = None
        
        if spreads:
            spread_markets = [m for m in spreads[0].get("markets", []) if m.get("key") == "spreads"]
            if spread_markets:
                spread_home = spread_markets[0].get("outcomes", [{}])[0].get("point", None)
        
        if totals:
            total_markets = [m for m in totals[0].get("markets", []) if m.get("key") == "totals"]
            if total_markets:
                ou = total_markets[0].get("outcomes", [{}])[0].get("point", None)
        
        rows.append({
            "home_team_name": home_team,
            "away_team_name": away_team,
            "ou_consensus": ou,
            "spread_home_consensus": spread_home
        })
    
    return pd.DataFrame(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--api_key", default=os.getenv("ODDS_API_KEY"))
    args = ap.parse_args()
    
    if not args.api_key:
        print("Error: No API key provided. Set ODDS_API_KEY environment variable or use --api_key")
        return
    
    odds_data = fetch_odds(args.api_key)
    if len(odds_data) == 0:  # Fixed: check length instead of truthiness
        print("No odds data received")
        return
    
    df = parse_odds_data(odds_data)
    
    # Add team abbreviations
    df["home_abbr"] = df["home_team_name"].map(TEAM_NAME_TO_ABBR)
    df["away_abbr"] = df["away_team_name"].map(TEAM_NAME_TO_ABBR)
    
    # Filter to only include teams we have data for
    df = df.dropna(subset=["home_abbr", "away_abbr"])
    
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} games to {args.out}")

if __name__ == "__main__":
    main()
