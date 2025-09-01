# NFL DFS Data Requirements - 100% Real Data

## Current Status: ❌ PROXY DATA REMOVED - REAL DATA REQUIRED

All proxy data has been removed from the system. The model now requires 100% real data to function.

## Required Data Files

### 1. **projections.csv** - REAL PROJECTIONS REQUIRED
**Status**: ❌ MISSING
**Format**: CSV with columns: `name,team,pos,proj,p90,own`
**Sources**: 
- FantasyPros
- ESPN Fantasy
- NumberFire
- PFF Fantasy
- Your own projection model

**Example**:
```csv
name,team,pos,proj,p90,own
Josh Allen,BUF,QB,24.5,28.2,12.5
Christian McCaffrey,SF,RB,22.8,26.1,15.2
```

### 2. **ownership.csv** - REAL OWNERSHIP REQUIRED
**Status**: ❌ MISSING
**Format**: CSV with columns: `name,own`
**Sources**:
- DraftKings Contest Data
- FantasyPros Ownership
- DFS Ownership Services
- Historical contest data

**Example**:
```csv
name,own
Josh Allen,12.5
Christian McCaffrey,15.2
```

### 3. **weekly_inputs.csv** - ENHANCED WITH MISSING DATA
**Status**: ⚠️ PARTIAL (missing weather, PROE, pace)
**Current Columns**: `game_id,home_team,away_team,start_time,venue,venue_roof,wind_mph,ou,spread_home,home_proe,away_proe,home_pace,away_pace`
**Missing Data**:
- `wind_mph`: Real-time weather data
- `home_proe,away_proe`: Pass Rate Over Expected
- `home_pace,away_pace`: Game pace metrics

**Sources**:
- Weather: OpenWeatherMap API, Weather.com
- PROE: PFF, ESPN Analytics
- Pace: PFF, ESPN Analytics

## Data Collection Plan

### Phase 1: Projections & Ownership (CRITICAL)
1. **Set up projection service integration**
   - FantasyPros API
   - ESPN Fantasy API
   - NumberFire API
   - Or manual weekly updates

2. **Set up ownership data collection**
   - DraftKings contest scraping
   - FantasyPros ownership
   - Historical data analysis

### Phase 2: Weather Data
1. **Weather API integration**
   - OpenWeatherMap API
   - Weather.com API
   - Real-time wind speeds for each game

### Phase 3: Advanced Metrics
1. **PROE Data**
   - PFF subscription
   - ESPN Analytics
   - Team pass rate tendencies

2. **Pace Data**
   - PFF subscription
   - ESPN Analytics
   - Team tempo metrics

## Current Data Completeness: 40%

✅ **Have**:
- DraftKings salaries (real)
- Game schedules (real)
- Team spreads & O/U (real)
- Depth chart roles (real)
- Player injury status (real)

❌ **Missing**:
- Real projections (60% of model weight)
- Real ownership (20% of model weight)
- Weather data (affects scoring)
- PROE data (affects game selection)
- Pace data (affects game selection)

## Next Steps

1. **Immediate**: Set up projection service (FantasyPros/ESPN)
2. **Week 1**: Manual projections entry for testing
3. **Week 2+**: Automated data collection
4. **Ongoing**: Add weather, PROE, pace data

## File Templates

### projections.csv Template
```csv
name,team,pos,proj,p90,own
# Add real projections here
# - proj: Projected fantasy points
# - p90: 90th percentile projection  
# - own: Projected ownership percentage
```

### ownership.csv Template
```csv
name,own
# Add real ownership projections here
# - own: Projected ownership percentage (0-100)
```

### Enhanced weekly_inputs.csv Template
```csv
game_id,home_team,away_team,start_time,venue,venue_roof,wind_mph,ou,spread_home,home_proe,away_proe,home_pace,away_pace
2025_01_WAS_NYG,NYG,WAS,2025-09-07 13:00,MetLife Stadium,outdoor,8,42.0,3.0,0.58,0.62,2.1,2.3
# Add real weather, PROE, and pace data
```
