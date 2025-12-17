# Production ML Pipeline - Pre-Flight Checklist

## ✅ Verification Before Running

### 1. Data Files Present
- [ ] `data/processed/movie_dataset.csv` exists (4,909 movies)
- [ ] Dataset has `first_week_gross` column
- [ ] Dataset has `is_complete` flag
- [ ] Clean dataset has 46 organized columns

### 2. Required Python Packages
```bash
# Check if installed:
pip list | grep -E "pandas|numpy|scikit-learn|xgboost|lightgbm|catboost|matplotlib|seaborn"
```

Required packages:
- [ ] pandas >= 1.3.0
- [ ] numpy >= 1.21.0
- [ ] scikit-learn >= 1.0.0
- [ ] xgboost >= 1.5.0
- [ ] lightgbm >= 3.3.0
- [ ] catboost >= 1.0.0
- [ ] matplotlib >= 3.4.0
- [ ] seaborn >= 0.11.0

### 3. Directory Structure
```
untitled folder 2/
├── data/
│   ├── processed/
│   │   └── movie_dataset.csv  ← Must exist
│   └── raw/
│       └── movies_with_youtube.csv
├── models/  ← Will be created automatically
├── complete_ml_pipeline.ipynb  ← Updated
└── PRODUCTION_ML_UPDATES.md  ← Documentation
```

### 4. Notebook Cells to Run (in order)

#### Section 1: Setup & Data Loading
- [ ] Cell 1: Imports
- [ ] Cell 2: Load movie_dataset.csv
- [ ] Cell 3: Check dataset completeness
- [ ] Cell 4: Statistical summary
- [ ] Cell 5: Filter training set (train_df = df[df['is_complete'] == True])

#### Section 2: Exploratory Data Analysis
- [ ] Correlation analysis (first_week_gross)
- [ ] Feature distributions
- [ ] Visualizations

#### Section 3: Feature Engineering
- [ ] Cell: Date features (if needed)
- [ ] Cell: Budget features
- [ ] Cell: Genres, cast, production features
- [ ] Cell: YouTube engagement features
- [ ] Cell: Holiday timing features
- [ ] Cell: Interaction features

#### Section 4: Data Preprocessing
- [ ] Cell: Feature selection (60+ pre-release features)
- [ ] Cell: Data quality validation
- [ ] Cell: Train-test split (stratified)
- [ ] Cell: Feature scaling (RobustScaler)

#### Section 5: Model Training
- [ ] Cell: Define train_and_evaluate function
- [ ] Cell: Train 11 models with optimized hyperparameters
- [ ] Cell: Model comparison table & visualization
- [ ] Cell: Cross-validation (top 3 models)
- [ ] Cell: Feature importance analysis

#### Section 6: Model Persistence
- [ ] Cell: Save models, scaler, feature names, metadata

#### Section 7: Production Pipeline
- [ ] Cell: Define predict_first_week_gross() function

#### Section 8: Avatar Prediction
- [ ] Cell: Avatar movie details
- [ ] Cell: Make prediction with confidence interval

---

## 🚀 Execution Checklist

### Pre-Execution
- [ ] Kernel restarted (fresh state)
- [ ] All imports working
- [ ] Dataset loads successfully
- [ ] Training set filtered (1,227 movies)

### During Execution
- [ ] Feature engineering completes without errors
- [ ] All 60+ features created
- [ ] Train-test split: 982 / 245 samples
- [ ] Scaler fitted on training data only
- [ ] All 11 models train successfully
- [ ] No warnings about data leakage

### Post-Execution Validation
- [ ] Best model identified (likely XGBoost or LightGBM)
- [ ] Test R² > 0.70 (target: 0.75-0.85)
- [ ] RMSE < $6M (target: $3.5M-$5.5M)
- [ ] Cross-validation scores consistent
- [ ] Feature importance saved
- [ ] Models saved to models/ directory
- [ ] Avatar prediction generates result

---

## 📊 Expected Results Checklist

### Model Performance
```
✓ Best Model R²: 0.75 - 0.85
✓ RMSE: $3.5M - $5.5M  
✓ MAE: $2.5M - $4.0M
✓ Cross-validation stable (CV std < 0.05)
✓ Low overfitting (Train R² - Test R² < 0.10)
```

### Feature Importance (Expected Top Features)
1. ✓ budget or budget_log
2. ✓ youtube_views_log
3. ✓ tmdb_popularity or tmdb_popularity_log
4. ✓ budget_youtube_interaction
5. ✓ is_holiday_release or is_christmas_release
6. ✓ youtube_engagement_score
7. ✓ tmdb_vote_count_log
8. ✓ genre_action or genre_adventure
9. ✓ is_major_studio
10. ✓ runtime_log

### Files Created
- [ ] `models/best_model_{timestamp}.pkl`
- [ ] `models/scaler_{timestamp}.pkl`
- [ ] `models/feature_names_{timestamp}.json`
- [ ] `models/metadata_{timestamp}.json`
- [ ] `data/processed/feature_importance.csv`
- [ ] Top 3 model backups in models/

### Avatar Prediction Output
```
Expected format:
🎬 Avatar: Fire & Ash - First Week Box Office Prediction:

   Point Estimate:  $XXX.XXM

   95% Confidence Interval:
      Lower Bound:  $XXX.XXM
      Upper Bound:  $XXX.XXM

📊 Franchise Comparison: [Avatar 1 vs Avatar 2 vs Avatar 3]
💡 Interpretation: [Blockbuster/Strong/Moderate classification]
```

---

## 🐛 Common Issues & Solutions

### Issue 1: ModuleNotFoundError
```python
# Solution: Install missing packages
pip install pandas numpy scikit-learn xgboost lightgbm catboost matplotlib seaborn
```

### Issue 2: Dataset not found
```python
# Solution: Check path
import os
print(os.path.exists('data/processed/movie_dataset.csv'))
# If False, verify dataset was created in previous steps
```

### Issue 3: No training data (train_df empty)
```python
# Solution: Check is_complete flag
print(df['is_complete'].sum())
# Should show 1,227 movies
```

### Issue 4: NameError (best_model not defined)
```python
# Solution: Make sure model training cell ran successfully
# Check: trained_models dictionary should contain all models
print(list(trained_models.keys()))
```

### Issue 5: ValueError (feature mismatch)
```python
# Solution: Ensure feature engineering ran completely
# Check: X_clean should have ~60 features
print(f"Features: {X_clean.shape[1]}")
```

### Issue 6: Prediction fails for Avatar
```python
# Solution: Check that these exist:
# - best_model (from training)
# - scaler (from preprocessing)
# - feature_names (list of feature names)
# - predict_first_week_gross() function defined
```

---

## 🎯 Success Criteria

### ✅ Pipeline is successful if:

1. **Data Loading**
   - [x] 1,227 complete training movies loaded
   - [x] first_week_gross range: $1K - $122M

2. **Feature Engineering**
   - [x] ~60 pre-release features created
   - [x] No post-release features included
   - [x] All transformations applied successfully

3. **Model Training**
   - [x] 11 models trained successfully
   - [x] Best model R² > 0.70
   - [x] RMSE < $6M
   - [x] Cross-validation stable

4. **Model Persistence**
   - [x] All files saved to models/
   - [x] Metadata includes all metrics
   - [x] Feature names stored correctly

5. **Avatar Prediction**
   - [x] Prediction generates without errors
   - [x] Result in range $80M - $200M
   - [x] Confidence interval calculated
   - [x] Interpretation provided

---

## 📝 Post-Execution Tasks

### After successful run:

1. **Document Results**
   - [ ] Note best model name
   - [ ] Record test R², RMSE, MAE
   - [ ] Save Avatar prediction
   - [ ] Screenshot feature importance

2. **Validate Predictions**
   - [ ] Check if Avatar prediction is reasonable
   - [ ] Compare with franchise history
   - [ ] Verify confidence interval width

3. **Backup Models**
   - [ ] Copy models/ directory to safe location
   - [ ] Note timestamp of production models
   - [ ] Keep metadata.json for reference

4. **Prepare for Deployment**
   - [ ] Test predict_first_week_gross() function separately
   - [ ] Verify loading saved models works
   - [ ] Document prediction process

---

## 🎊 Completion

When all checkboxes are complete, your production ML pipeline is:
- ✅ Fully functional
- ✅ Production-ready
- ✅ Properly documented
- ✅ Ready for Avatar: Fire & Ash prediction

**Next:** Run the notebook and make your prediction! 🚀🎬

---

**Last Updated:** December 22, 2025
**Pipeline Version:** 2.0
**Status:** Ready for Execution ✅
