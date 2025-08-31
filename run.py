
import argparse, sys
from pathlib import Path
from edge_scores import main as edge_main
from stacks import main as stacks_main
from optimize import main as opt_main
from utils import read_weights

def run(weekly, roles, dk, weights, out_dir, projections=None, ownership=None):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    edge_csv = out/"edge_scores.csv"
    stacks_csv = out/"core_stacks.csv"

    edge_df = edge_main(weekly, weights, str(edge_csv))
    stacks_df = stacks_main(str(edge_csv), roles, weekly, str(stacks_csv))
    lu_csv = opt_main(weekly, str(edge_csv), str(stacks_csv), roles, dk, out_dir, projections, ownership, weights)
    print("Generated:", lu_csv)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--weekly", required=True)
    ap.add_argument("--roles", required=True)
    ap.add_argument("--dk", required=True)
    ap.add_argument("--weights", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--projections", default=None)
    ap.add_argument("--ownership", default=None)
    args = ap.parse_args()
    run(args.weekly, args.roles, args.dk, args.weights, args.out, args.projections, args.ownership)
