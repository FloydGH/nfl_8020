# NFL 80/20 DFS Toolkit

**Goal:** Automate the 80/20 workflow to create 150 correlated, ceiling-focused DK lineups.

## Inputs (minimal)
1. `weekly_inputs.csv` — one row per game. Use the template you downloaded earlier or create one with the same columns.
2. `depth_chart_roles.csv` — map roles to player names for each team (qb1, rb1, wr1, wr2, slot_wr, te1).
3. `DKSalaries.csv` — DraftKings' standard salaries export.
4. Optional:
   - `projections.csv` with columns: `name,team,pos,proj,p90,own`
   - `ownership.csv` with columns: `name,own`
   - If omitted, the toolkit builds a **proxy** projection & ownership from salary and position.

## Outputs
- `out/edge_scores.csv` — ranked game environments with Tier labels
- `out/core_stacks.csv` — the selected stack blueprints
- `out/lineups_150.csv` — 150 lineups with constraints applied

## Quickstart
```
python run.py   --weekly weekly_inputs.csv   --roles depth_chart_roles.csv   --dk DKSalaries.csv   --weights config/weights.yaml   --out out
```

The script will:
1) Compute Edge Scores and pick Tier A/B/C games (Pareto filter)
2) Build core stacks (3v1 default + controlled variety)
3) Auto-generate 150 lineups with:
   - Double stacks + bring-backs
   - WR in FLEX bias
   - Ownership gates & salary bands
   - No offensive players vs your DST
   - Basic exposure smoothing

### Notes
- Ownership is best from paid sources; if not provided, we create a proxy from salary rank and O/U context.
- Projections: if none provided, we derive proxies from salary (and position) and add a ceiling uplift; **replace with your model** as soon as it's ready.
- Weather, PROE, and pace should be in `weekly_inputs.csv`. You can script those pulls separately or paste quickly each week.

## Files
- `run.py` — one-button orchestrator
- `edge_scores.py` — Edge Score & Tiering
- `stacks.py` — build stack blueprints per game
- `optimize.py` — greedy optimizer that respects constraints & uniqueness
- `utils.py` — helpers (ownership proxy, projection proxy, parsing, scoring)

This is intentionally lightweight so you can drop it into Cursor and iterate.
