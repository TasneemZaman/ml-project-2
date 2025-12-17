# Data Enrichment Scripts

Scripts for enriching the main dataset with additional features and metrics.

---

## 📝 Scripts

### `update_2025_data.py`
**Purpose:** Update dataset with latest 2025 movie releases  
**Usage:** 
```bash
python update_2025_data.py
```
**Updates:** TMDB data, BOM data, YouTube stats for 2025 movies

### `update_bom_data.py`
**Purpose:** Update Box Office Mojo data for existing movies  
**Usage:**
```bash
python update_bom_data.py
```
**Features:** opening_weekend, domestic_total, worldwide_total

### `enrich_with_daily_bom.py`
**Purpose:** Add daily box office metrics (theaters, YD%, LW%)  
**Usage:**
```bash
python enrich_with_daily_bom.py [mode]
# mode: 'test', 'range START END', or full dataset
```
**Features:** 27 daily BOM features per movie

### `run_bom_enrichment.py`
**Purpose:** Easy-to-use runner for BOM enrichment  
**Usage:**
```bash
python run_bom_enrichment.py [mode]
# mode: 'test', 'recent', 'full'
```
**Convenience:** User-friendly wrapper for enrich_with_daily_bom.py

### `scrape_individual_movies.py`
**Purpose:** Scrape individual movie pages for daily data  
**Usage:**
```bash
python scrape_individual_movies.py
```
**Note:** Slower than batch collection, use for specific movies only

---

## 🔄 Typical Workflow

### For Regular Updates:
```bash
# Update with latest 2025 releases
python update_2025_data.py

# Refresh Box Office Mojo data
python update_bom_data.py
```

### For Daily Metrics:
```bash
# Quick test (last 7 days)
python run_bom_enrichment.py test

# Recent movies (last 6 months)
python run_bom_enrichment.py recent

# Full enrichment (all movies)
python run_bom_enrichment.py full
```

---

## 📊 Features Added

### Daily BOM Features (27 total):
- **Theater metrics** (6): opening, peak, avg, expansion ratio
- **Revenue metrics** (4): opening day, peak, avg daily
- **Per-theater** (5): opening, peak, avg per-theater
- **Momentum** (5): YD%, LW% changes, volatility
- **Opening weekend** (2): 3-day gross, per-theater
- **Weekly trends** (4): week 1/2 averages, ratios
- **Other** (1): opening to total ratio

---

## ⚠️ Important Notes

- **Rate Limiting:** All scripts include 2-second delays between requests
- **Data Source:** Box Office Mojo (reliable but requires scraping)
- **Update Frequency:** Run weekly for new releases, monthly for historical updates
