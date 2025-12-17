# Optimal Data Collection Strategy for First Week Revenue Prediction

## 🎯 Your Goal: Predict First Week Revenue

Since your target is **first week revenue**, here's the optimal collection strategy:

---

## 📊 What Data Do We Need?

### For First Week Prediction, You Need:
1. **Friday (Opening Day)** - Day 1
2. **Saturday** - Day 2  
3. **Sunday** - Day 3
4. **Monday-Thursday** - Days 4-7

**Total: 7 days of data per movie**

---

## 🔄 Current Collection (What We're Doing Now)

### Current Approach:
```
Collect ALL movies on date pages for last 30 days
→ 30 days × 40 movies/day = 1,200 records
→ Result: Most movies tracked 14-29 days
```

### What We Actually Use:
```python
# We aggregate ENTIRE RUN into features like:
- daily_opening_3day_gross      # ← Only first 3 days matter!
- daily_week1_avg_gross         # ← Only first 7 days matter!
- daily_week2_avg_gross         # ← NOT RELEVANT for week 1 prediction!
- daily_opening_to_total_ratio  # ← NOT RELEVANT (need final total)
```

### Problems:
- ❌ Collecting too much data (weeks 2-4) we don't need
- ❌ Computing features that require full theatrical run
- ❌ Missing historical movies (only got last 30 days)

---

## ✅ Optimal Strategy for First Week Prediction

### Strategy 1: **"First 7 Days Only"** (RECOMMENDED)

```python
# For each movie, collect ONLY first 7 days after release
# Example for movie released on 2024-11-22:

Release Date: 2024-11-22
Collect: 2024-11-22 to 2024-11-28 (7 days)

Data collected:
Day 1 (Fri):  Theaters, Daily Gross, Per-Theater Avg
Day 2 (Sat):  Theaters, Daily Gross, YD% change
Day 3 (Sun):  Theaters, Daily Gross, YD% change  
Day 4 (Mon):  Theaters, Daily Gross, YD% change
Day 5 (Tue):  Theaters, Daily Gross, YD% change
Day 6 (Wed):  Theaters, Daily Gross, YD% change
Day 7 (Thu):  Theaters, Daily Gross, YD% change

STOP HERE - We have what we need!
```

### Why This Works:
✅ **First week IS our target** - no need for week 2+ data  
✅ **Much less scraping** - 7 days per movie vs 20-30 days  
✅ **Historical data works** - can collect ANY movie's first week  
✅ **Features are predictive** - opening momentum predicts week 1 total

---

## 📈 Key Features for First Week Prediction

### **Most Important (Must Have)**:

1. **Opening Day Metrics** (Day 1 - Friday)
   ```
   - opening_day_theaters        # How wide is release?
   - opening_day_gross           # How strong is day 1?
   - opening_day_per_theater     # Sold out or weak?
   ```

2. **Opening Weekend** (Days 1-3 - Fri-Sun)
   ```
   - opening_weekend_3day_gross  # The classic metric!
   - opening_weekend_theaters    # Any expansion?
   - opening_weekend_per_theater # Sustained demand?
   ```

3. **Weekday Momentum** (Days 4-7 - Mon-Thu)
   ```
   - weekday_avg_gross           # How are weekdays?
   - weekday_yd_changes          # Growing or dropping?
   - friday_to_monday_drop       # Weekend → weekday cliff
   ```

4. **Week 1 Total** (Days 1-7)
   ```
   - week1_total_gross           # Our TARGET!
   - week1_avg_daily             # Consistency metric
   - week1_peak_day              # Best single day
   ```

### **Less Important (Skip)**:
- ❌ Week 2 data (we're predicting week 1!)
- ❌ Final total ratio (need to wait months)
- ❌ Long-term trends (not relevant for week 1)

---

## 🎯 Optimal Collection Strategy

### Option A: "4-Day Interval" (Your Suggestion)

**Collect every 4 days to ensure we capture first week:**

```python
# For movies released in 2024:
dates_to_scrape = [
    '2024-01-01', '2024-01-05', '2024-01-09',  # Jan
    '2024-02-01', '2024-02-05', '2024-02-09',  # Feb
    # ... etc
]

# Why 4 days?
# - Most movies release on Friday
# - Day 1 (Fri), Day 5 (Tue), Day 9 (Sat next week)
# - Captures opening weekend + weekdays
```

**Pros:**
- ✅ Covers all major release days
- ✅ Gets opening weekend data
- ✅ Less scraping than daily

**Cons:**
- ⚠️ Miss some days (might get Day 1, 5, 9 but not 2-4, 6-8)
- ⚠️ Harder to compute exact 7-day total

### Option B: "First Week Only" (BEST)

**Target each movie's first 7 days specifically:**

```python
# For each movie in dataset:
movie_release_date = '2024-11-22'

# Scrape exactly 7 days after release:
scrape_dates = [
    '2024-11-22', '2024-11-23', '2024-11-24',  # Fri-Sun (opening weekend)
    '2024-11-25', '2024-11-26', '2024-11-27', '2024-11-28'  # Mon-Thu
]

# Sum up: WEEK 1 REVENUE = sum of all 7 days
```

**Pros:**
- ✅ **Most accurate** - exact 7-day window
- ✅ **All relevant data** - complete first week
- ✅ **Historical works** - can get any movie's first week
- ✅ **Efficient** - only 7 days per movie

**Cons:**
- ⚠️ Need release dates for each movie (you have this!)

### Option C: "Opening Weekend + Weekday Sample"

**Minimal data collection:**

```python
# Just get these key days:
Day 1 (Fri):  Opening day metrics
Day 2 (Sat):  Weekend trajectory  
Day 3 (Sun):  Weekend total
Day 5 (Tue):  Weekday sample

# Then ESTIMATE week 1 total using patterns:
estimated_week1 = opening_weekend * 1.4  # Historical multiplier
```

**Pros:**
- ✅ Very fast - only 4 days per movie
- ✅ Opening weekend is 70% of week 1

**Cons:**
- ⚠️ Less accurate - estimation based
- ⚠️ Miss Monday's boost (post-weekend word-of-mouth)

---

## 📊 Recommended Approach: "First Week Only"

### Implementation:

```python
def collect_first_week_data(movie_title, release_date):
    """
    Collect exactly 7 days after release for accurate week 1 prediction.
    """
    release = pd.to_datetime(release_date)
    
    # Scrape days 0-6 after release
    daily_data = []
    for day in range(7):
        date = release + timedelta(days=day)
        date_str = date.strftime('%Y-%m-%d')
        
        # Scrape BOM date page for this date
        data = scrape_daily_data(date_str)
        
        # Find this movie in the data
        movie_data = data[data['release'] == movie_title]
        if len(movie_data) > 0:
            daily_data.append(movie_data)
    
    # Aggregate into features
    features = {
        'opening_day_gross': daily_data[0]['daily_gross'],
        'opening_weekend_gross': sum([d['daily_gross'] for d in daily_data[:3]]),
        'week1_total_gross': sum([d['daily_gross'] for d in daily_data]),
        'opening_theaters': daily_data[0]['theaters'],
        # ... etc
    }
    
    return features
```

### Data Required:
```
For 4,901 movies × 7 days = 34,307 date pages
BUT: Many movies share dates, so actually ~2,000 unique dates
At 2 sec/page = ~4,000 seconds = 67 minutes

More realistic: Top 1,000 recent movies × 7 days = 1,000 unique dates
At 2 sec/page = 33 minutes
```

---

## 🎯 What Features to Create

### For First Week Revenue Prediction:

```python
features = {
    # Opening Day (Day 1 - Friday)
    'day1_theaters': ...,
    'day1_gross': ...,
    'day1_per_theater': ...,
    
    # Opening Weekend (Days 1-3 - Fri-Sun)
    'opening_weekend_gross': day1 + day2 + day3,
    'opening_weekend_per_theater': sum / avg_theaters,
    'saturday_bump': (day2 - day1) / day1,  # Usually positive
    'sunday_drop': (day3 - day2) / day2,    # Usually negative
    
    # Weekday Performance (Days 4-7 - Mon-Thu)  
    'weekday_avg_gross': mean(day4, day5, day6, day7),
    'monday_drop': (day4 - day3) / day3,    # Big drop from weekend
    'weekday_stability': std(day4-day7),    # Are weekdays consistent?
    
    # Full Week 1
    'week1_total_gross': sum(day1-day7),    # ← YOUR TARGET!
    'week1_daily_avg': mean(day1-day7),
    'weekend_to_week1_ratio': weekend / week1,  # Usually 0.65-0.75
    
    # Momentum Indicators
    'yd_avg_change': mean of all day-to-day % changes,
    'trending_up': boolean (are days 4-7 > days 1-3?),
}
```

---

## 📅 Recommended Data Collection Plan

### Phase 1: Recent Movies (Test)
```bash
# Collect first week for movies released in last 3 months
# ~90 days / 7 days per week = ~13 weeks × 5 movies = ~65 movies
# Time: ~30 minutes

python3 collect_first_week.py --start-date 2024-09-21 --end-date 2024-12-21
```

### Phase 2: 2024 Movies (Production)
```bash
# Collect all 2024 theatrical releases
# ~300 movies × 7 days = target data
# Time: ~2 hours

python3 collect_first_week.py --year 2024
```

### Phase 3: Historical (Optional)
```bash
# Collect 2020-2023 for training data
# Time: ~6-8 hours

python3 collect_first_week.py --start-year 2020 --end-year 2023
```

---

## 🎯 Summary

### **For First Week Revenue Prediction:**

| Approach | Data Needed | Scraping Time | Accuracy | Recommended |
|----------|-------------|---------------|----------|-------------|
| **First 7 Days** | Days 0-6 after release | ~67 min (all movies) | ⭐⭐⭐⭐⭐ | ✅ **YES** |
| **4-Day Interval** | Every 4th day | ~30 min | ⭐⭐⭐ | ⚠️ Maybe |
| **Opening Weekend Only** | Days 0-2 only | ~15 min | ⭐⭐⭐⭐ | ✅ Good start |
| **Current (30 days)** | Days 0-30 | ~2 hours | ⭐⭐ | ❌ Overkill |

### **Best Strategy:**
1. ✅ Collect **exactly 7 days** after each movie's release
2. ✅ Focus on **2024 releases** first (most relevant)
3. ✅ Use features based on **opening weekend + first weekdays**
4. ✅ Your target is literally in the data: `sum(day1-day7)` = first week gross

### **Key Features (Most Predictive):**
1. Opening day theaters (distribution scale)
2. Opening weekend gross (momentum)
3. Per-theater averages (demand intensity)
4. Saturday bump % (word-of-mouth)
5. Weekday average (staying power)

---

Would you like me to create a modified scraper that collects **only the first 7 days** for each movie? This would be much more efficient and directly aligned with your first-week prediction goal! 🎯
