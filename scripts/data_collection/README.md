# Data Collection Scripts

Scripts for collecting raw box office data from various sources.

---

## 📝 Scripts

### `collect_all_years.py`
**Purpose:** Orchestrate multi-year batch collection of Box Office Mojo data  
**Usage:** 
```bash
python collect_all_years.py [strategy]
# strategy: 'biweekly' (27 dates/year) or 'weekly' (52 dates/year)
```
**Output:** `data/processed/bom_all_years_batch.csv`

### `collect_year_batch.py`
**Purpose:** Batch collection by date (scrape one date → get all movies)  
**Functions:**
- `collect_year_batch(year, strategy)` - Collect data for one year
- `scrape_daily_data(date)` - Scrape Box Office Mojo daily page
**Strategies:** biweekly (27/year), weekly (52/year), smart (holidays)

### `collect_first_week_targets.py`
**Purpose:** Aggregate daily records into first week totals  
**Input:** `data/processed/bom_all_years_batch.csv` (daily records)  
**Output:** `data/processed/first_week_features_all_years.csv` (per movie)  
**Features:** first_week_gross, opening_theaters, momentum indicators

### `collectors.py`
**Purpose:** Core collection functions for TMDB, BOM, YouTube  
**Functions:**
- `collect_tmdb_data()` - Fetch movie metadata from TMDB
- `collect_bom_data()` - Scrape Box Office Mojo
- `collect_youtube_stats()` - Get trailer statistics
**Used by:** Multiple enrichment scripts

---

## 🔄 Typical Workflow

1. **Batch collect daily data:**
   ```bash
   python collect_all_years.py weekly
   ```

2. **Aggregate to first week:**
   ```bash
   python collect_first_week_targets.py
   ```

3. **Result:** Movies with first_week_gross feature ready for ML

---

## 📊 Data Flow

```
Box Office Mojo Daily Pages
           ↓
   collect_year_batch.py
           ↓
bom_all_years_batch.csv (daily records)
           ↓
collect_first_week_targets.py
           ↓
first_week_features_all_years.csv (per movie)
```
