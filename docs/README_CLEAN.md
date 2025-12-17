# Movie Data Collection - Clean Structure

## 🎯 Main Files (Use These!)

### Core Scripts
- **`data_pipeline.py`** - Main script to run data collection
- **`collectors.py`** - All collector classes (TMDB, YouTube, Box Office, Trends)
- **`config.py`** - API keys configuration

### Notebooks
- **`complete_ml_pipeline.ipynb`** - ML modeling and predictions

### Data
- `data/raw/` - Raw collected data
- `data/processed/` - Processed/cleaned data

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Add your API keys to config.py
```

### 2. Collect Data
```bash
# Run the main pipeline
python data_pipeline.py

# Choose option:
# 1 = Full pipeline (TMDB + YouTube + Box Office)
# 2 = Only TMDB base data
# 3 = Enrich with YouTube
# 4 = Enrich with Box Office
# 5 = Show progress
```

### 3. Train Model
Open `complete_ml_pipeline.ipynb` and run the cells.

## 📊 Data Sources

1. **TMDB** (Required) - Base movie data
   - Title, release date, popularity, votes, overview
   - Fast, reliable, no rate limits

2. **YouTube** (Recommended) - Engagement metrics
   - Trailer views, likes, comments
   - Good coverage, reasonable rate limits
   - Uses multiple API keys for rotation
   - **Best engagement metric for predictions!**

3. **Box Office Mojo** (Optional) - Revenue data
   - Domestic/international/worldwide gross
   - Slow (web scraping, ~3 sec per movie)
   - Consider for smaller datasets only

## ⚠️ Important Notes

### Rate Limits
- **TMDB**: 40 requests/10 seconds (handled automatically)
- **YouTube**: 10,000 units/day per key (rotates through multiple keys)
- **Box Office Mojo**: ~2-3 seconds per request (respectful scraping)
- **Google Trends**: Unpredictable, often blocked (NOT RECOMMENDED)

### Recommended Approach
For 5,000 movies:
1. Collect TMDB base data (~10 minutes)
2. Enrich with YouTube (~2 hours with 5 workers)
3. Skip Box Office Mojo unless needed (~4 hours for full dataset)
4. Use YouTube views as your engagement metric (better than Google Trends!)

## 📁 Old Scripts (Archived)

All old/duplicate scripts have been moved to `old_scripts/` folder.
Don't use these - they're kept for reference only.

## 🔧 Troubleshooting

### "No module named 'googleapiclient'"
```bash
pip install google-api-python-client
```

### "YouTube quota exceeded"
Add more API keys to `config.py` in the `YOUTUBE_API_KEYS` list

### "Too many requests (429)" from Google Trends
This is normal - Google Trends blocks automated requests. Skip this data source.

### Box Office Mojo scraping fails
Website structure may have changed. This is a fragile scraping method.

## 📈 Expected Timeline

For 5,000 movies:
- TMDB collection: ~10-15 minutes
- YouTube enrichment: ~2 hours (with 5 workers)
- Box Office enrichment: ~4 hours (skip if not needed)
- Total (TMDB + YouTube): ~2-3 hours

## 💡 Tips

1. Start small - test with 100 movies first
2. Use YouTube data instead of Google Trends
3. Run Box Office collection overnight if needed
4. Save progress frequently (pipeline does this automatically)
5. Monitor progress with option 5 in the menu
