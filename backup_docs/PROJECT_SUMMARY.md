# 🎬 Avatar: Ash & Fire - Box Office Prediction Project

A comprehensive Machine Learning project to predict the first week box office income of "Avatar: Ash & Fire" using historical data, IMDB ratings, Box Office Mojo statistics, and T-7 social media trend data.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Models](#models)
- [Results](#results)

## 🎯 Overview

This project implements a state-of-the-art machine learning pipeline that:
- Collects and processes data from multiple sources (IMDB, Box Office Mojo, Social Media)
- Engineers 50+ advanced features including interactions, polynomials, and ratios
- Trains 13 base models and 2 ensemble models
- Uses **Stacking** and **Voting** ensembles for maximum accuracy
- Provides comprehensive predictions with confidence intervals

## ✨ Features

### Data Sources
- **IMDB**: Ratings, votes, metascores, review counts
- **Box Office Mojo**: Historical performance, budgets, theater counts
- **T-7 Trend Data**: Social media engagement 7 days before release
  - Twitter mentions and sentiment
  - Google Trends scores
  - YouTube trailer engagement
  - Instagram hashtags
  - Ticket pre-sales
- **Temporal Features**: Release timing, seasonality, competition
- **Franchise Features**: Brand value, previous performance

### Models Implemented

#### Base Models (13)
1. Linear Regression
2. Ridge Regression
3. Lasso Regression
4. ElasticNet
5. Decision Tree
6. Random Forest
7. Extra Trees
8. Gradient Boosting
9. **XGBoost** ⭐
10. **LightGBM** ⭐
11. **CatBoost** ⭐
12. SVR
13. K-Nearest Neighbors

#### Ensemble Models (2)
1. **Stacking Ensemble** - Uses predictions from base models as features
2. **Voting Ensemble** - Weighted average of best models

### Feature Engineering
- **Interaction Features**: budget × rating, budget × theaters
- **Polynomial Features**: squared and log transforms
- **Ratio Features**: efficiency metrics
- **Social Engagement Score**: Combined social media metrics
- **Hype Index**: T-7 trend indicator
- **Quality Score**: Combined rating metrics
- **Franchise Momentum**: Brand trajectory indicator

## 📁 Project Structure

```
untitled folder 2/
│
├── 📓 avatar_boxoffice_prediction.ipynb  # Main Jupyter notebook (ALL-IN-ONE)
│
├── 📄 Python Modules:
│   ├── config.py                          # Configuration and settings
│   ├── data_collection.py                 # Data collection functions
│   ├── feature_engineering.py             # Feature engineering pipeline
│   ├── model_training.py                  # Model training and evaluation
│   ├── predict.py                         # Prediction module
│   ├── visualization.py                   # Visualization utilities
│   └── main.py                            # Complete pipeline runner
│
├── 📊 Data:
│   ├── data/raw/                          # Raw collected data
│   └── data/processed/                    # Engineered features
│
├── 🤖 Models:
│   └── models/                            # Trained model files (.pkl)
│
├── 📈 Results:
│   └── results/                           # Predictions and visualizations
│
├── 📋 Configuration:
│   ├── requirements.txt                   # Python dependencies
│   ├── .env.example                       # Environment variables template
│   ├── .gitignore                         # Git ignore file
│   └── README.md                          # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Jupyter Notebook (optional, for interactive notebook)

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd "untitled folder 2"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys if using real data sources
   ```

## 💻 Usage

### Option 1: Jupyter Notebook (Recommended) ⭐

The easiest way to use this project is through the comprehensive Jupyter notebook:

```bash
jupyter notebook avatar_boxoffice_prediction.ipynb
```

The notebook contains:
- ✅ Complete end-to-end pipeline
- ✅ All 13 base models + 2 ensembles
- ✅ Interactive visualizations
- ✅ Detailed explanations
- ✅ Hyperparameter tuning
- ✅ Feature importance analysis
- ✅ Final predictions for Avatar: Ash & Fire

**Just run all cells sequentially!**

### Option 2: Python Scripts

#### Run Complete Pipeline:
```bash
python main.py
```

#### Run Individual Steps:

1. **Data Collection:**
   ```bash
   python data_collection.py
   ```

2. **Feature Engineering:**
   ```bash
   python feature_engineering.py
   ```

3. **Model Training:**
   ```bash
   python model_training.py
   ```

4. **Make Predictions:**
   ```bash
   python predict.py
   ```

5. **Generate Visualizations:**
   ```bash
   python visualization.py
   ```

## 🤖 Models

### Performance Metrics

Models are evaluated using:
- **RMSE** (Root Mean Squared Error) - Lower is better
- **MAE** (Mean Absolute Error) - Prediction accuracy
- **R² Score** - Variance explained (0-1, higher is better)
- **Cross-Validation** - 5-fold CV for robust evaluation

### Best Performers

Typically, the top models are:
1. **Stacking Ensemble** - Combines multiple models intelligently
2. **XGBoost** - Powerful gradient boosting
3. **LightGBM** - Fast and accurate
4. **CatBoost** - Handles categorical features well
5. **Voting Ensemble** - Weighted average approach

## 📊 Results

After running the pipeline or notebook, you'll get:

### Outputs

1. **Model Performance Report**
   - Comparative metrics for all models
   - Cross-validation scores
   - Training times

2. **Predictions for Avatar: Ash & Fire**
   - Individual model predictions
   - Ensemble average
   - Confidence intervals

3. **Visualizations**
   - Model comparison charts
   - Feature importance plots
   - Prediction distributions
   - Interactive dashboards

4. **Feature Importance Analysis**
   - Top contributing features
   - Source breakdown (IMDB, Box Office, Trends)

### Sample Prediction Output

```
AVATAR: ASH & FIRE - FIRST WEEK BOX OFFICE PREDICTIONS
======================================================================
Model                          Prediction
----------------------------------------------------------------------
Stacking Ensemble              $285,450,000.00
Voting Ensemble                $278,320,000.00
Tuned XGBoost                  $282,150,000.00
LightGBM                       $275,880,000.00
CatBoost                       $280,650,000.00

ENSEMBLE STATISTICS
======================================================================
Mean Prediction:               $280,490,000.00
Median Prediction:             $280,650,000.00
Confidence Range:              $238,416,500 - $322,563,500
======================================================================
```

## 🔍 Key Insights

1. **T-7 Data is Highly Predictive** - Social media engagement 7 days before release strongly correlates with box office performance

2. **Ensemble Methods Excel** - Stacking and voting ensembles consistently outperform individual models

3. **Budget Matters** - Production budget remains a strong indicator, especially when combined with theater count

4. **Franchise Power** - Previous franchise performance and brand momentum significantly impact predictions

5. **Pre-sales Signal** - Ticket pre-sales provide early indication of opening week performance

## 🛠️ Customization

### Modify Movie Information

Edit `config.py` to change target movie details:

```python
MOVIE_INFO = {
    'title': 'Your Movie Title',
    'expected_release_date': '2025-12-18',
    'budget': 400000000,
    'director': 'Director Name',
    # ... other details
}
```

### Add New Models

Edit `model_training.py` or add to the notebook:

```python
'YourModel': YourModelClass(parameters)
```

### Customize Features

Edit `feature_engineering.py` to add new feature transformations:

```python
def create_custom_features(df):
    df['new_feature'] = # your logic
    return df
```

## 📈 Accuracy Optimization

The project maximizes accuracy through:

1. **Extensive Feature Engineering** - 50+ features from raw data
2. **Multiple Model Types** - Linear, tree-based, and boosting algorithms
3. **Hyperparameter Tuning** - GridSearchCV optimization
4. **Ensemble Methods** - Combining predictions for robustness
5. **Cross-Validation** - Preventing overfitting
6. **Robust Scaling** - Feature normalization

## 🤝 Contributing

Enhancements welcome:
- Real data source integration
- Additional models (Neural Networks, etc.)
- Advanced hyperparameter optimization (Optuna, Bayesian)
- More visualization options
- API for predictions

## 📝 Notes

- **Sample Data**: Current implementation uses simulated data for demonstration
- **Real Data**: To use real data, implement actual API calls in `data_collection.py`
- **API Keys**: Store sensitive keys in `.env` file
- **Training Time**: Ensemble training may take 10-30 minutes depending on hardware

## 📚 References

- Box Office data sources: Box Office Mojo, The Numbers
- Movie data: IMDB, TMDB
- ML Libraries: scikit-learn, XGBoost, LightGBM, CatBoost
- Visualization: matplotlib, seaborn, plotly

## 📄 License

This project is open source and available for educational purposes.

---

**Built with ❤️ for accurate box office predictions! 🎬📈**

**Questions? Run the Jupyter notebook - it has everything you need!** 📓✨
