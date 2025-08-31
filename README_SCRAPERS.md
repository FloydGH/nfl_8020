
# NFL 80/20 Automated Builder (Scrapers Included)

This folder now includes **automated scrapers** so you never hand-fill weekly data.

## 1) Install
```bash
pip install -r /mnt/data/nfl_8020/requirements.txt
```

## 2) Environment
- `ODDS_API_KEY` for [The Odds API](https://the-odds-api.com) (free tier okay).

```bash
export ODDS_API_KEY=YOUR_KEY
```

## 3) One-shot weekly ingest
```bash
python /mnt/data/nfl_8020/scripts/build_weekly_inputs.py --season 2025 --week 1 --outdir /mnt/data/nfl_8020/out/week01
```

Outputs in `/mnt/data/nfl_8020/out/week01/`:
- `schedule.csv` (ESPN events API)  
- `odds.csv` (The Odds API; totals & spreads)  
- `weather.csv` (Open-Meteo at stadium coords; wind mph; domes skipped)  
- `proe_pace.csv` (computed from nfl_data_py / nflfastR xpass)  
- `concentration.csv` (top-2 target share avg last 4 weeks)  
- `roles.csv` (WR1/WR2/TE1/RB1 via OurLads)  
- `weekly_inputs.csv` (base table; ready to merge with edge scoring)

> Note: `weekly_inputs.csv` currently contains schedule + venue/wind columns. Odds and team-level metrics are saved as separate files to keep joins clean. You can merge them into your `edge_scores.py` pipeline by team & game ID reliably.

## Sources

- **Schedule**: ESPN JSON events API (regular season)  
- **Lines/Totals**: The Odds API (consensus across books)  
- **Weather (Wind)**: Open-Meteo (no API key) at stadium lat/lon; domes & fixed roofs skipped  
- **PROE & Pace**: Computed from `nfl_data_py` (`xpass` present in nflfastR pbp), last 4 weeks by default  
- **Concentration**: Weekly `targets` via `nfl_data_py`; average of top-2 target shares by team  
- **Depth Charts**: OurLads team pages parsed for QB1/RB1/WR1/WR2/TE1

## Legal/ToS

- Scrape respectfully: add headers, backoff, and abide by each site's robots/ToS if you extend these.
- For commercial use, review each provider’s terms.

## Next Steps

- Wire `out/weekXX/*.csv` into your existing `edge_scores.py` + optimizer.
- Replace `odds.csv` merge in `build_weekly_inputs.py` with your book priority & team-name resolver.
- Optionally add paid ownership feeds; keep the proxy when absent.
