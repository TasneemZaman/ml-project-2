# Avatar: Ash & Fire - Box Office Prediction Project

A comprehensive Machine Learning project to predict the first week box office income of "Avatar: Ash & Fire" using T-7 data from IMDB, Box Office Mojo, and social media trends.

## 🎯 Project Overview

This project builds an ensemble of machine learning models to predict box office performance with high accuracy by:
- Collecting historical box office data and movie features
- Engineering advanced features including social media trends (T-7 data)
- Training multiple base models and ensemble methods
- Using stacking and voting ensembles for maximum accuracy
- Providing comprehensive predictions and visualizations

## 📊 Features

### Data Sources
- **IMDB**: Ratings, votes, metascores, popularity metrics
- **Box Office Mojo**: Historical box office performance, theater counts
- **Social Media Trends**: Twitter sentiment, Google Trends, YouTube engagement
- **Temporal Features**: Release timing, seasonality, competition
- **Franchise Features**: Brand value, previous performance

### Models Implemented
1. **Base Models**:
   - Ridge Regression
   - Lasso Regression
   - ElasticNet
   - Random Forest
   - Extra Trees
   - Gradient Boosting
   - XGBoost
   - LightGBM
   - CatBoost
   - SVR
   - K-Nearest Neighbors

2. **Ensemble Methods**:
   - Stacking Ensemble (meta-learner)
   - Voting Ensemble (weighted average)
   - Weighted Average Ensemble

### Feature Engineering
- Interaction features (budget × rating, etc.)
- Polynomial features
- Ratio features
- Social media engagement scores
- Hype index
- Quality scores
- Theater efficiency metrics
- Franchise momentum

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
```

### Installation

1. Clone or download the project:
```bash
cd "untitled folder 2"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Complete Pipeline

Run the entire pipeline (data collection → training → prediction):
```bash
python main.py
```

### Running Individual Steps

**Data Collection:**
```bash
python data_collection.py
```

**Feature Engineering:**
```bash
python feature_engineering.py
```

**Model Training:**
```bash
python model_training.py
```

**Make Predictions:**
```bash
python predict.py
```

**Create Visualizations:**
```bash
python visualization.py
```

## 📁 Project Structure

```
untitled folder 2/
├── config.py                  # Configuration and parameters
├── data_collection.py         # Data collection from multiple sources
├── feature_engineering.py     # Advanced feature engineering
├── model_training.py          # Model training and ensembles
├── predict.py                 # Prediction module
├── visualization.py           # Visualization and reporting
├── main.py                    # Complete pipeline
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── data/
│   ├── raw/                   # Raw collected data
│   └── processed/             # Engineered features
│
├── models/                    # Trained model files (.pkl)
│
└── results/                   # Predictions and visualizations
    ├── model_results.csv
    ├── all_predictions.csv
    ├── prediction_report.txt
    ├── model_comparison.png
    ├── predictions_by_model.html
    ├── prediction_distribution.html
    └── dashboard.html
```

## 🎬 Movie Configuration

Update the movie information in `config.py`:

```python
MOVIE_INFO = {
    'title': 'Avatar: Ash & Fire',
    'expected_release_date': '2025-12-18',
    'franchise': 'Avatar',
    'genre': ['Action', 'Adventure', 'Sci-Fi'],
    'production_budget': 400000000,
    'director': 'James Cameron',
    'studio': '20th Century Studios'
}
```

## 📈 Model Performance

The models are evaluated using:
- **RMSE** (Root Mean Squared Error): Lower is better
- **MAE** (Mean Absolute Error): Prediction accuracy
- **R² Score**: Variance explained (0-1, higher is better)
- **Cross-Validation**: 5-fold CV for robust evaluation

## 🔍 Key Features

### T-7 Data (7 Days Before Release)
- Twitter mentions and sentiment
- Google Trends scores
- YouTube trailer engagement
- Instagram hashtag counts
- Ticket pre-sales
- Search volume index

### Advanced Ensembling
- **Stacking**: Uses predictions from base models as features for meta-learner
- **Voting**: Weighted average with optimized weights
- **Weighted Average**: Inverse RMSE weighting of top 5 models

## 📊 Results and Outputs

After running the pipeline, you'll find:

1. **model_results.csv**: Performance metrics for all models
2. **all_predictions.csv**: Predictions from each model
3. **prediction_report.txt**: Detailed text report
4. **Visualizations**:
   - Model comparison charts
   - Prediction distribution plots
   - Interactive dashboard
   - Feature importance plots

## 🛠️ Customization

### Adding New Data Sources
Edit `data_collection.py` to add new data collectors:
```python
def collect_custom_features(self):
    # Your custom data collection logic
    pass
```

### Adding New Models
Edit `model_training.py` in `get_base_models()`:
```python
'YourModel': YourModelClass(parameters)
```

### Modifying Features
Edit `feature_engineering.py` to add new feature transformations

## 📝 Notes

- **Sample Data**: The current implementation uses simulated data for demonstration
- **Real Data**: To use real data, implement actual API calls or web scraping in `data_collection.py`
- **API Keys**: Set API keys in a `.env` file for TMDB, OMDB, etc.
- **Training Time**: Ensemble training may take 10-30 minutes depending on your hardware

## 🎯 Accuracy Optimization

The project maximizes accuracy through:
1. **Extensive Feature Engineering**: 50+ features from raw data
2. **Multiple Model Types**: Linear, tree-based, and boosting algorithms
3. **Hyperparameter Tuning**: Optimized parameters for each model
4. **Ensemble Methods**: Combining predictions for robustness
5. **Cross-Validation**: Preventing overfitting
6. **Data Scaling**: Robust scaling for feature normalization

## 🤝 Contributing

Feel free to enhance the project by:
- Adding real data sources
- Implementing hyperparameter optimization (GridSearch/Optuna)
- Adding deep learning models
- Improving feature engineering
- Adding more visualization options

## 📄 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- Data sources: IMDB, Box Office Mojo, The Numbers
- ML libraries: scikit-learn, XGBoost, LightGBM, CatBoost
- Visualization: matplotlib, seaborn, plotly

---

**Good luck with your box office predictions! 🎬📈**
