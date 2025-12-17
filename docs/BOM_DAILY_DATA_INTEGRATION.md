# Box Office Mojo Daily Data Integration Guide

## Overview

This guide explains how to integrate **Box Office Mojo daily data** into your movie revenue prediction pipeline. Daily data includes crucial metrics like theater counts, daily gross, day-to-day changes (YD%), and week-to-week changes (LW%) that can significantly improve prediction accuracy.

## 📊 What Data Gets Collected

From BOM daily pages (e.g., https://www.boxofficemojo.com/date/2025-12-13/):

| Field | Description | Example |
|-------|-------------|---------|
| **Daily** | Daily gross revenue | $2,500,000 |
| **YD %** | Percentage change from yesterday | +15.2% |
| **LW %** | Percentage change from last week | -25.3% |
| **Theaters** | Number of theaters | 3,521 |
| **Avg** | Average per theater | $710 |
| **To Date** | Cumulative revenue | $45,200,000 |
| **Days** | Days in theatrical release | 10 |

## 🎯 Feature Engineering Strategy

### 1. Theater Distribution Features
```python
- daily_opening_theaters          # Opening weekend theater count
- daily_peak_theaters              # Maximum theaters during run
- daily_avg_theaters               # Average theater count
- daily_theater_expansion_ratio    # Peak/Opening ratio
```

**Why Important**: Theater count indicates studio confidence and distribution strategy. Wide releases (3000+ theaters) have different revenue patterns than limited releases (< 1000).

### 2. Revenue Momentum Features
```python
- daily_opening_day_gross          # First day revenue
- daily_opening_3day_gross         # Opening weekend total
- daily_avg_yd_change              # Average day-to-day % change
- daily_avg_lw_change              # Average week-to-week % change
- daily_yd_volatility              # Standard deviation of daily changes
```

**Why Important**: Captures word-of-mouth and staying power. Movies with positive YD% changes on weekdays show strong audience interest.

### 3. Per-Theater Performance
```python
- daily_opening_per_theater        # Opening per-theater average
- daily_peak_per_theater           # Best per-theater day
- daily_avg_per_theater            # Average across run
- daily_per_theater_decline_rate   # Rate of decline
```

**Why Important**: High per-theater averages indicate strong audience demand. Helps distinguish sold-out screenings from empty theaters.

### 4. Weekly Trends
```python
- daily_week1_avg_gross            # First week average
- daily_week2_avg_gross            # Second week average
- daily_week2_week1_ratio          # Week 2/Week 1 ratio
- daily_opening_to_total_ratio     # Opening/Final total ratio
```

**Why Important**: Legs! Movies with high week 2/week 1 ratios have staying power (e.g., "Avatar", "Frozen"). Front-loaded movies drop 60%+ in week 2.

## 🚀 Implementation Steps

### Step 1: Test the Scraper

```bash
python enrich_with_daily_bom.py test
```

This scrapes a single day to verify the scraper works.

### Step 2: Collect Recent Data

```bash
python enrich_with_daily_bom.py range 2024-01-01 2025-12-13
```

This collects daily data for approximately 1 year (~350 days × 50 movies/day = ~17,500 records).

**Estimated time**: 350 days × 2 seconds = ~12 minutes

### Step 3: Enrich Your Dataset

```bash
python enrich_with_daily_bom.py
```

This:
1. Scrapes daily data for specified date range
2. Matches movies in your dataset using BOM URLs
3. Aggregates daily records into features
4. Saves enriched dataset with new columns

### Step 4: Update Your ML Pipeline

In `complete_ml_pipeline.ipynb`:

```python
# Load enriched data
df = pd.read_csv('data/raw/movies_with_youtube.csv')

# Add daily features to feature engineering
daily_features = [
    'daily_opening_theaters',
    'daily_peak_theaters',
    'daily_theater_expansion_ratio',
    'daily_opening_3day_gross',
    'daily_avg_per_theater',
    'daily_avg_yd_change',
    'daily_week2_week1_ratio',
    'daily_opening_to_total_ratio'
]

# Handle missing values (movies without daily data)
for col in daily_features:
    if col in df.columns:
        df[col].fillna(df[col].median(), inplace=True)

# Include in model
X = df[numeric_features + daily_features]
```

## 📈 Expected Performance Improvements

Based on feature importance analysis:

| Feature | Predicted Importance | Impact |
|---------|---------------------|---------|
| `daily_opening_3day_gross` | **Very High** | Direct correlation with final revenue |
| `daily_opening_theaters` | **High** | Indicates distribution scale |
| `daily_avg_per_theater` | **High** | Measures demand intensity |
| `daily_theater_expansion_ratio` | **Medium-High** | Captures hit potential |
| `daily_week2_week1_ratio` | **Medium-High** | Measures staying power |
| `daily_avg_yd_change` | **Medium** | Word-of-mouth indicator |

**Expected Model Improvements**:
- **R² Score**: +10-15% improvement (e.g., 0.75 → 0.85)
- **RMSE**: 20-30% reduction in error
- **MAE**: 15-25% reduction in error

## 🎮 Use Case Scenarios

### Scenario 1: Pre-Release Prediction (No Daily Data Yet)
```python
# Use historical patterns from similar movies
# Features: budget, genres, cast, director, marketing (YouTube views)
# Cannot use daily features - movie hasn't released yet!
```

### Scenario 2: Post-Opening Weekend Prediction
```python
# Now have 3-4 days of data!
# Use: opening_theaters, opening_3day_gross, avg_yd_change
# Accuracy: Much higher! Can predict final with 70-80% accuracy
```

### Scenario 3: Mid-Run Tracking
```python
# Have 2-3 weeks of data
# Use: week2_week1_ratio, theater_expansion_ratio, avg_lw_change
# Can determine if movie is a hit or underperforming
```

### Scenario 4: Historical Analysis
```python
# Analyze completed theatrical runs
# All daily features available
# Perfect for training models and understanding success factors
```

## 🔍 Analysis Insights

After collecting daily data, you can answer questions like:

1. **What opening weekend theater count predicts $100M+ movies?**
   - Typically 3000+ theaters for blockbusters
   - 1500-2500 for mid-tier films
   - <1000 for limited/indie releases

2. **What per-theater average indicates a hit?**
   - $10,000+ per theater on opening day = likely hit
   - $5,000-$10,000 = solid performance
   - <$5,000 = may struggle

3. **What week 2 drop is normal?**
   - 40-50% drop is typical
   - <40% drop = excellent legs
   - >60% drop = front-loaded/bad word-of-mouth

4. **How does theater expansion correlate with success?**
   - Expanding from 500 → 2000 theaters = breakout hit
   - Stable theater count = as expected
   - Rapid theater reduction = underperforming

## ⚙️ Technical Details

### Data Collection Rate Limiting
```python
time.sleep(2)  # 2 seconds between requests
# ~30 requests/minute
# ~1800 requests/hour
# Can collect ~350 days in ~12 minutes
```

### Data Matching Strategy
1. **Primary**: Match by `bom_url` (most reliable)
2. **Fallback**: Match by title (fuzzy matching)
3. **Manual**: Review unmatched movies

### Missing Data Handling
```python
# Some movies won't have daily data because:
# - Released before date range
# - Never tracked by BOM
# - Limited/festival release

# Strategy: Impute with median or create binary flag
df['has_daily_data'] = df['daily_opening_theaters'].notna()
```

## 🎨 Visualization Ideas

After collecting data, create visualizations:

```python
# Theater count trajectory
plt.plot(daily_data[daily_data['release'] == 'Wicked']['theaters'])

# Per-theater performance over time
plt.plot(daily_data[daily_data['release'] == 'Wicked']['per_theater_avg'])

# Week-over-week comparison
sns.barplot(x='week', y='avg_gross', hue='movie_category')
```

## 📝 Files Created

| File | Purpose |
|------|---------|
| `enrich_with_daily_bom.py` | Main script for data collection |
| `data/processed/bom_daily_data.csv` | Raw daily records |
| `data/raw/movies_with_youtube.csv` | Updated with daily features |
| `BOM_DAILY_DATA_INTEGRATION.md` | This guide |

## 🚨 Important Notes

1. **Respect Rate Limits**: Use 2-second delays between requests
2. **Check robots.txt**: Ensure scraping is allowed
3. **Data Rights**: Use collected data for personal/academic purposes
4. **API Alternative**: Consider Box Office Mojo API if available (paid)
5. **Error Handling**: Script handles connection errors gracefully
6. **Incremental Updates**: Can re-run script to update with new dates

## 🎓 Learning Resources

- [Box Office Mojo](https://www.boxofficemojo.com/)
- [Understanding Box Office Legs](https://www.the-numbers.com/market/)
- [Theater Count Strategy](https://stephenfollows.com/hollywood-release-strategies/)

## 💡 Future Enhancements

1. **Real-time tracking**: Daily automated scraping for current releases
2. **International data**: Collect per-country daily grosses
3. **Comparison tools**: Compare similar movies at same point in release
4. **Prediction updates**: Update predictions daily as new data arrives
5. **Alert system**: Notify when movie over/underperforms projections

---

**Ready to get started?** Run:
```bash
python enrich_with_daily_bom.py test
```

Good luck with your predictions! 🎬📊
