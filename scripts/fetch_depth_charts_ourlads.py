
import argparse, pandas as pd

# Create depth chart roles based on DK data and common knowledge
# This is a simplified version - in production you'd want to scrape actual depth charts
DEPTH_CHART_2025 = {
    "ARI": {"QB1": "Kyler Murray", "RB1": "James Conner", "WR1": "Marvin Harrison Jr.", "WR2": "Michael Wilson", "TE1": "Trey McBride"},
    "ATL": {"QB1": "Michael Penix Jr.", "RB1": "Bijan Robinson", "WR1": "Drake London", "WR2": "Darnell Mooney", "TE1": "Kyle Pitts"},
    "BAL": {"QB1": "Lamar Jackson", "RB1": "Derrick Henry", "WR1": "Zay Flowers", "WR2": "Rashod Bateman", "TE1": "Mark Andrews"},
    "BUF": {"QB1": "Josh Allen", "RB1": "James Cook", "WR1": "Stefon Diggs", "WR2": "Khalil Shakir", "TE1": "Dalton Kincaid"},
    "CAR": {"QB1": "Bryce Young", "RB1": "Chuba Hubbard", "WR1": "Adam Thielen", "WR2": "Diontae Johnson", "TE1": "Tommy Tremble"},
    "CHI": {"QB1": "Caleb Williams", "RB1": "D'Andre Swift", "WR1": "DJ Moore", "WR2": "Rome Odunze", "TE1": "Cole Kmet"},
    "CIN": {"QB1": "Joe Burrow", "RB1": "Chase Brown", "WR1": "Ja'Marr Chase", "WR2": "Tee Higgins", "TE1": "Mike Gesicki"},
    "CLE": {"QB1": "Deshaun Watson", "RB1": "Nick Chubb", "WR1": "Amari Cooper", "WR2": "Jerry Jeudy", "TE1": "David Njoku"},
    "DAL": {"QB1": "Dak Prescott", "RB1": "Ezekiel Elliott", "WR1": "CeeDee Lamb", "WR2": "Brandin Cooks", "TE1": "Jake Ferguson"},
    "DEN": {"QB1": "Bo Nix", "RB1": "Javonte Williams", "WR1": "Courtland Sutton", "WR2": "Marvin Mims", "TE1": "Greg Dulcich"},
    "DET": {"QB1": "Jared Goff", "RB1": "Jahmyr Gibbs", "WR1": "Amon-Ra St. Brown", "WR2": "Jameson Williams", "TE1": "Sam LaPorta"},
    "GB": {"QB1": "Jordan Love", "RB1": "Josh Jacobs", "WR1": "Christian Watson", "WR2": "Jayden Reed", "TE1": "Luke Musgrave"},
    "HOU": {"QB1": "C.J. Stroud", "RB1": "Joe Mixon", "WR1": "Nico Collins", "WR2": "Tank Dell", "TE1": "Dalton Schultz"},
    "IND": {"QB1": "Anthony Richardson", "RB1": "Jonathan Taylor", "WR1": "Michael Pittman Jr.", "WR2": "Adonai Mitchell", "TE1": "Jelani Woods"},
    "JAX": {"QB1": "Trevor Lawrence", "RB1": "Travis Etienne Jr.", "WR1": "Brian Thomas Jr.", "WR2": "Christian Kirk", "TE1": "Evan Engram"},
    "KC": {"QB1": "Patrick Mahomes", "RB1": "Isiah Pacheco", "WR1": "Rashee Rice", "WR2": "Marquise Brown", "TE1": "Travis Kelce"},
    "LAC": {"QB1": "Justin Herbert", "RB1": "Gus Edwards", "WR1": "Keenan Allen", "WR2": "Joshua Palmer", "TE1": "Gerald Everett"},
    "LAR": {"QB1": "Matthew Stafford", "RB1": "Kyren Williams", "WR1": "Puka Nacua", "WR2": "Cooper Kupp", "TE1": "Tyler Higbee"},
    "LV": {"QB1": "Aidan O'Connell", "RB1": "Zamir White", "WR1": "Davante Adams", "WR2": "Jakobi Meyers", "TE1": "Brock Bowers"},
    "MIA": {"QB1": "Tua Tagovailoa", "RB1": "De'Von Achane", "WR1": "Tyreek Hill", "WR2": "Jaylen Waddle", "TE1": "Durham Smythe"},
    "MIN": {"QB1": "Sam Darnold", "RB1": "Aaron Jones", "WR1": "Justin Jefferson", "WR2": "Jordan Addison", "TE1": "T.J. Hockenson"},
    "NE": {"QB1": "Drake Maye", "RB1": "Rhamondre Stevenson", "WR1": "Kendrick Bourne", "WR2": "DeMario Douglas", "TE1": "Hunter Henry"},
    "NO": {"QB1": "Derek Carr", "RB1": "Alvin Kamara", "WR1": "Chris Olave", "WR2": "Rashid Shaheed", "TE1": "Juwan Johnson"},
    "NYG": {"QB1": "Daniel Jones", "RB1": "Devon Singletary", "WR1": "Malik Nabers", "WR2": "Jalin Hyatt", "TE1": "Daniel Bellinger"},
    "NYJ": {"QB1": "Aaron Rodgers", "RB1": "Breece Hall", "WR1": "Garrett Wilson", "WR2": "Mike Williams", "TE1": "Tyler Conklin"},
    "PHI": {"QB1": "Jalen Hurts", "RB1": "Saquon Barkley", "WR1": "A.J. Brown", "WR2": "DeVonta Smith", "TE1": "Dallas Goedert"},
    "PIT": {"QB1": "Russell Wilson", "RB1": "Najee Harris", "WR1": "George Pickens", "WR2": "Roman Wilson", "TE1": "Pat Freiermuth"},
    "SF": {"QB1": "Brock Purdy", "RB1": "Christian McCaffrey", "WR1": "Brandon Aiyuk", "WR2": "Deebo Samuel", "TE1": "George Kittle"},
    "SEA": {"QB1": "Geno Smith", "RB1": "Kenneth Walker III", "WR1": "DK Metcalf", "WR2": "Tyler Lockett", "TE1": "Noah Fant"},
    "TB": {"QB1": "Baker Mayfield", "RB1": "Rachaad White", "WR1": "Mike Evans", "WR2": "Chris Godwin", "TE1": "Cade Otton"},
    "TEN": {"QB1": "Will Levis", "RB1": "Tony Pollard", "WR1": "Calvin Ridley", "WR2": "Treylon Burks", "TE1": "Chigoziem Okonkwo"},
    "WAS": {"QB1": "Jayden Daniels", "RB1": "Austin Ekeler", "WR1": "Terry McLaurin", "WR2": "Jahan Dotson", "TE1": "Zach Ertz"}
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    
    rows = []
    for team, roles in DEPTH_CHART_2025.items():
        row = {"team": team}
        row.update(roles)
        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv(args.out, index=False)
    print(f"Wrote depth chart roles for {len(df)} teams to {args.out}")

if __name__ == "__main__":
    main()
