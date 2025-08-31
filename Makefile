
.PHONY: week

W?=1
SEASON?=2025
OUT?=out/week$(shell printf "%02d" $(W))

week:
	python scripts/build_weekly_inputs.py --season $(SEASON) --week $(W) --outdir $(OUT)
	python scripts/edge_scores.py --indir $(OUT) --out $(OUT)/game_edge_scores.csv
