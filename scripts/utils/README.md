# Utility Scripts

Configuration, pipeline management, and status monitoring scripts.

---

## 📝 Scripts

### `config.py`
**Purpose:** Central configuration for all scripts  
**Contains:**
- API keys (TMDB, YouTube)
- File paths
- Scraping settings (delays, retries)
- Feature definitions

**Usage:** Import in other scripts
```python
from config import TMDB_API_KEY, DATA_PATH
```

### `data_pipeline.py`
**Purpose:** End-to-end data processing pipeline  
**Functions:**
- `load_raw_data()` - Load from multiple sources
- `clean_data()` - Handle missing values, outliers
- `merge_datasets()` - Combine TMDB, BOM, YouTube
- `save_processed()` - Save final dataset

**Usage:**
```bash
python data_pipeline.py
```

### `check_status.py`
**Purpose:** Monitor data collection progress and completeness  
**Checks:**
- Dataset size and completeness
- Missing data by source (TMDB, BOM, YouTube)
- Data quality metrics
- Update timestamps

**Usage:**
```bash
python check_status.py
```

**Output:**
```
Dataset Status Report
Total movies: 4,909
Complete movies: 1,227 (25%)
Missing budget: 2,450 (50%)
Missing first_week: 3,605 (73%)
```

---

## 🔧 Configuration Management

### config.py Structure:
```python
# API Configuration
TMDB_API_KEY = "your_key_here"
YOUTUBE_API_KEY = "your_key_here"

# Paths
DATA_PATH = "data/"
RAW_PATH = "data/raw/"
PROCESSED_PATH = "data/processed/"

# Scraping Settings
DELAY_BETWEEN_REQUESTS = 2  # seconds
MAX_RETRIES = 3
TIMEOUT = 10  # seconds

# Feature Settings
FIRST_WEEK_DAYS = 7
MIN_BUDGET = 1000
MIN_YOUTUBE_VIEWS = 100
```

---

## 📊 Status Monitoring

Run `check_status.py` regularly to:
- ✅ Track data collection progress
- ✅ Identify missing data
- ✅ Validate data quality
- ✅ Plan next collection steps

---

## 🔄 Pipeline Execution

### Complete Pipeline:
```bash
# 1. Check current status
python check_status.py

# 2. Run data pipeline (if needed)
python data_pipeline.py

# 3. Verify results
python check_status.py
```

---

## ⚙️ Best Practices

1. **Always check status first** before running collection scripts
2. **Update config.py** with your API keys
3. **Run pipeline after major updates** to ensure data consistency
4. **Monitor logs** for errors or warnings
