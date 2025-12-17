# Updating Data to Include 2025 Box Office

## Current Situation
- Your dataset: **4,901 movies** (1990 - Dec 25, 2024)
- Box Office data: **3,842 movies** have it
- Missing BOM data: **1,059 movies**
- 2024+ movies: **141 movies** (108 have BOM data)

## Options to Get Data Up to Dec 12, 2025

### Option 1: Collect New 2025 Movies (RECOMMENDED)
Collect movies released between Dec 25, 2024 and Dec 12, 2025.

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the collection script
python update_2025_data.py
```

**What it does:**
1. Fetches new movies from TMDB (2025 releases)
2. Enriches with Box Office Mojo data
3. Adds YouTube trailer stats
4. Merges with your existing dataset

**Time:** ~1-2 hours (depends on how many movies)

---

### Option 2: Update Existing Movies' Box Office Data
Update movies that are already in your dataset but missing BOM data.

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the update script
python update_bom_data.py
```

**Interactive options:**
1. **Update only recent missing data** (2024+ movies without BOM) - ~15 minutes
2. **Update all missing data** (1,059 movies) - ~4-5 hours
3. **Refresh all BOM data** (all 4,901 movies) - ~14-16 hours

**What it does:**
- Scrapes Box Office Mojo for movies you select
- Updates: opening weekend, domestic total, worldwide total, international total
- Creates backup before updating
- Rate-limited to avoid blocking (3-5 seconds per movie)

---

### Option 3: Quick Manual Check
Just want to see what 2025 data is available?

```python
import pandas as pd
from collectors import TMDBCollector

# Get TMDB data for 2025
tmdb = TMDBCollector()
# (Check TMDB API manually)
```

---

## Recommended Workflow

### Step 1: Update Missing Recent Data (Quick)
```bash
python update_bom_data.py
# Choose option 1: Update only missing BOM data (recent movies)
```
This updates ~33 movies from 2024 that don't have BOM data yet.

### Step 2: Collect New 2025 Movies
```bash
python update_2025_data.py
```
This adds movies released in 2025 up to Dec 12.

### Step 3: Update Your Notebook
Once data is updated, re-run your notebook cells starting from cell 5 (data loading):
- The duplicate column drop is already handled
- Missing value imputation will adjust automatically
- All downstream analysis will use the updated data

---

## Important Notes

### Rate Limiting
- **Box Office Mojo**: 3-5 seconds per movie (they block aggressive scraping)
- **TMDB API**: 0.25-0.3 seconds per request (has rate limits)
- **YouTube API**: 1 second per request (has daily quota)

### Data Backup
Both scripts automatically create backups before modifying your data:
- Format: `movies_with_youtube_backup_YYYYMMDD_HHMMSS.csv`
- Location: `data/raw/`

### If Something Goes Wrong
All backups are kept, so you can always restore:
```bash
cp data/raw/movies_with_youtube_backup_XXXXXX.csv data/raw/movies_with_youtube.csv
```

---

## Quick Status Check

To see what data you have:
```bash
python check_status.py
```

Or in Python:
```python
import pandas as pd
df = pd.read_csv('data/raw/movies_with_youtube.csv')
df['release_date'] = pd.to_datetime(df['release_date'])

print(f"Date range: {df['release_date'].min()} to {df['release_date'].max()}")
print(f"Total: {len(df)} movies")
print(f"With BOM: {df['bom_opening_weekend'].notna().sum()}")
print(f"Missing BOM: {df['bom_opening_weekend'].isna().sum()}")
```

---

## Alternative: Manual Box Office Mojo Integration

If the scrapers aren't working well, you can:

1. **Download CSV from Box Office Mojo directly** (if available)
2. **Use their API** (if they offer one - they don't currently)
3. **Manual entry** for critical movies only
4. **Alternative data source**: The Numbers (thenumbers.com) or IMDb Box Office

Let me know which approach you'd like to take!
