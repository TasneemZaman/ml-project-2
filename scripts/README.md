# Scripts Organization

## 📁 Folder Structure

```
scripts/
├── data_collection/        # Raw data collection from external sources
│   ├── collect_all_years.py
│   ├── collect_year_batch.py
│   ├── collect_first_week_targets.py
│   ├── collectors.py
│   └── README.md
│
├── enrichment/            # Dataset enrichment with additional features
│   ├── update_2025_data.py
│   ├── update_bom_data.py
│   ├── enrich_with_daily_bom.py
│   ├── run_bom_enrichment.py
│   ├── scrape_individual_movies.py
│   └── README.md
│
├── utils/                 # Configuration and pipeline management
│   ├── config.py
│   ├── data_pipeline.py
│   ├── check_status.py
│   └── README.md
│
├── archive/               # Deprecated/old scripts (formerly old_scripts/)
│   └── [legacy scripts]
│
├── backup/                # Backup scripts (formerly backup_scripts/)
│   └── [backup versions]
│
└── README.md             # This file
```

---

## 🚀 Quick Start

### 1. Data Collection (First Time)
```bash
# Collect Box Office Mojo data for all years
cd scripts/data_collection
python collect_all_years.py weekly

# Aggregate to first week targets
python collect_first_week_targets.py
```

### 2. Regular Updates
```bash
# Update with latest 2025 releases
cd scripts/enrichment
python update_2025_data.py
```

### 3. Check Status
```bash
# Monitor progress
cd scripts/utils
python check_status.py
```

---

## 📂 Folder Descriptions

### `data_collection/`
**Purpose:** Collect raw data from external sources  
**Key Scripts:**
- `collect_all_years.py` - Multi-year batch collection
- `collect_year_batch.py` - Batch by date strategy
- `collectors.py` - Core collection functions

**Output:** Daily box office records → aggregated features

### `enrichment/`
**Purpose:** Enrich dataset with additional metrics  
**Key Scripts:**
- `update_2025_data.py` - Latest releases
- `enrich_with_daily_bom.py` - Daily BOM metrics
- `run_bom_enrichment.py` - Easy enrichment runner

**Output:** Enhanced dataset with 27+ daily features

### `utils/`
**Purpose:** Configuration and monitoring  
**Key Scripts:**
- `config.py` - Central configuration
- `data_pipeline.py` - End-to-end processing
- `check_status.py` - Progress monitoring

**Output:** Status reports, processed datasets

### `archive/`
**Purpose:** Legacy scripts (not actively maintained)  
**Contents:** Old collection methods, deprecated APIs

### `backup/`
**Purpose:** Backup versions of scripts  
**Contents:** Previous implementations, alternative approaches

---

## 📊 Data Flow

```
External APIs (TMDB, BOM, YouTube)
           ↓
    data_collection/
           ↓
Raw datasets (daily records)
           ↓
     enrichment/
           ↓
Enriched dataset (features)
           ↓
      utils/ (pipeline)
           ↓
Final clean dataset
           ↓
  ML Pipeline (notebook)
```

---

## 📝 Detailed Documentation

Each folder contains a detailed `README.md` with:
- Script descriptions
- Usage examples
- Input/output specifications
- Common workflows

**See individual folder READMEs for more details.**

---

## ⚙️ Configuration

Edit `scripts/utils/config.py` to set:
- API keys (TMDB, YouTube)
- File paths
- Scraping delays
- Feature definitions

---

## 🔍 Finding Scripts

### By Task:
- **Collect new data** → `data_collection/`
- **Update existing data** → `enrichment/`
- **Check progress** → `utils/check_status.py`
- **Run full pipeline** → `utils/data_pipeline.py`

### By Data Source:
- **Box Office Mojo** → `data_collection/collect_year_batch.py`
- **TMDB** → `enrichment/update_2025_data.py`
- **YouTube** → `collectors.py`

### By Output:
- **First week gross** → `data_collection/collect_first_week_targets.py`
- **Daily metrics** → `enrichment/enrich_with_daily_bom.py`
- **Clean dataset** → `utils/data_pipeline.py`

---

**Last Updated:** December 22, 2025  
**Total Scripts:** 12 active + archive + backup
