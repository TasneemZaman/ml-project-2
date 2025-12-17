"""
Main Prediction Module for Avatar: Ash & Fire
Makes predictions using trained models
"""

import pandas as pd
import numpy as np
import joblib
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

from data_collection import DataCollector
from feature_engineering import FeatureEngineer
from config import MODELS_DIR, RESULTS_DIR, MOVIE_INFO


class BoxOfficePredictor:
    """Predicts first week box office income"""
    
    def __init__(self, model_name: str = 'StackingEnsemble'):
        self.model_name = model_name
        self.model = None
        self.scaler = None
        self.feature_engineer = FeatureEngineer()
        
    def load_model(self):
        """Load trained model and scaler"""
        print(f"Loading {self.model_name}...")
        
        model_path = MODELS_DIR / f"{self.model_name}.pkl"
        scaler_path = MODELS_DIR / "scaler.pkl"
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        
        print("Model loaded successfully!")
    
    def collect_movie_data(self, movie_info: Dict) -> pd.DataFrame:
        """Collect data for the target movie"""
        print(f"\nCollecting data for {movie_info['title']}...")
        
        collector = DataCollector()
        
        # Collect all features
        data = {
            'movie_title': movie_info['title'],
            'release_date': movie_info['expected_release_date'],
            'genre': '|'.join(movie_info['genre']),
            'studio': movie_info['studio'],
            'director': movie_info['director'],
            'budget': movie_info.get('production_budget', 400000000),  # Estimate
        }
        
        # Add IMDB features
        imdb_features = collector.collect_imdb_features(movie_info['title'])
        data.update(imdb_features)
        
        # Add T-7 trend data
        trend_features = collector.collect_social_media_trends(movie_info['title'], days_before=7)
        data.update(trend_features)
        
        # Add temporal features
        temporal_features = collector.collect_temporal_features(movie_info['expected_release_date'])
        data.update(temporal_features)
        
        # Add franchise features
        franchise_features = collector.collect_franchise_features(movie_info['franchise'])
        data.update(franchise_features)
        
        # Add theater information (estimates)
        data.update({
            'num_theaters': 4500,  # Expected wide release
            'average_per_theater': 55000,  # Estimate
            'opening_weekend': 200000000,  # Initial estimate
            'total_gross': 0,  # Unknown
            'runtime': 180,  # Estimate
        })
        
        # Create DataFrame
        df = pd.DataFrame([data])
        
        return df
    
    def prepare_features(self, df: pd.DataFrame, feature_names: List[str]) -> np.ndarray:
        """Prepare features for prediction"""
        print("Engineering features...")
        
        # Apply feature engineering
        df_engineered = self.feature_engineer.engineer_all_features(df, is_training=False)
        
        # Select only the features the model was trained on
        # This is crucial for production
        X = df_engineered[feature_names]
        
        # Handle missing columns
        for col in feature_names:
            if col not in X.columns:
                X[col] = 0
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        return X_scaled
    
    def predict(self, movie_info: Dict) -> Dict:
        """Make prediction for a movie"""
        print("\n" + "="*70)
        print(f"PREDICTING FIRST WEEK INCOME FOR: {movie_info['title']}")
        print("="*70)
        
        # Load model if not already loaded
        if self.model is None:
            self.load_model()
        
        # Collect movie data
        df = self.collect_movie_data(movie_info)
        
        # For demo purposes, we'll use all numeric columns
        # In production, you'd save the exact feature names from training
        X = df.select_dtypes(include=[np.number])
        X = X.fillna(X.median())
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make prediction
        prediction = self.model.predict(X_scaled)[0]
        
        results = {
            'movie_title': movie_info['title'],
            'predicted_first_week_income': prediction,
            'model_used': self.model_name,
            'confidence_interval_lower': prediction * 0.85,  # ±15% range
            'confidence_interval_upper': prediction * 1.15,
        }
        
        return results
    
    def predict_with_all_models(self, movie_info: Dict) -> pd.DataFrame:
        """Make predictions using all available models"""
        print("\n" + "="*70)
        print("PREDICTING WITH ALL MODELS")
        print("="*70)
        
        # Collect movie data once
        df = self.collect_movie_data(movie_info)
        X = df.select_dtypes(include=[np.number])
        X = X.fillna(X.median())
        
        # Load scaler
        if self.scaler is None:
            scaler_path = MODELS_DIR / "scaler.pkl"
            self.scaler = joblib.load(scaler_path)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get all model files
        model_files = list(MODELS_DIR.glob("*.pkl"))
        model_files = [f for f in model_files if f.stem != 'scaler']
        
        predictions = []
        
        for model_file in model_files:
            try:
                model = joblib.load(model_file)
                pred = model.predict(X_scaled)[0]
                
                predictions.append({
                    'model_name': model_file.stem,
                    'predicted_first_week_income': pred
                })
                
                print(f"{model_file.stem:<30} ${pred:>15,.2f}")
            except Exception as e:
                print(f"Error with {model_file.stem}: {e}")
        
        # Calculate ensemble average
        pred_values = [p['predicted_first_week_income'] for p in predictions]
        avg_pred = np.mean(pred_values)
        median_pred = np.median(pred_values)
        
        print(f"\n{'Average Prediction':<30} ${avg_pred:>15,.2f}")
        print(f"{'Median Prediction':<30} ${median_pred:>15,.2f}")
        
        predictions_df = pd.DataFrame(predictions)
        predictions_df = predictions_df.sort_values('predicted_first_week_income', ascending=False)
        
        return predictions_df
    
    def generate_prediction_report(self, movie_info: Dict, save_path: str = None):
        """Generate comprehensive prediction report"""
        print("\n" + "="*70)
        print("GENERATING PREDICTION REPORT")
        print("="*70)
        
        # Get predictions from all models
        predictions_df = self.predict_with_all_models(movie_info)
        
        # Calculate statistics
        mean_pred = predictions_df['predicted_first_week_income'].mean()
        median_pred = predictions_df['predicted_first_week_income'].median()
        std_pred = predictions_df['predicted_first_week_income'].std()
        min_pred = predictions_df['predicted_first_week_income'].min()
        max_pred = predictions_df['predicted_first_week_income'].max()
        
        report = f"""
{'='*70}
FIRST WEEK BOX OFFICE PREDICTION REPORT
{'='*70}

Movie: {movie_info['title']}
Release Date: {movie_info['expected_release_date']}
Franchise: {movie_info['franchise']}
Director: {movie_info['director']}
Studio: {movie_info['studio']}

{'='*70}
PREDICTION SUMMARY
{'='*70}

Mean Prediction:     ${mean_pred:>15,.2f}
Median Prediction:   ${median_pred:>15,.2f}
Standard Deviation:  ${std_pred:>15,.2f}

Minimum Prediction:  ${min_pred:>15,.2f}
Maximum Prediction:  ${max_pred:>15,.2f}

Confidence Range:    ${mean_pred * 0.85:>15,.2f} - ${mean_pred * 1.15:,.2f}

{'='*70}
INDIVIDUAL MODEL PREDICTIONS
{'='*70}

"""
        for _, row in predictions_df.iterrows():
            report += f"{row['model_name']:<30} ${row['predicted_first_week_income']:>15,.2f}\n"
        
        report += f"\n{'='*70}\n"
        
        print(report)
        
        if save_path:
            with open(save_path, 'w') as f:
                f.write(report)
            print(f"\nReport saved to {save_path}")
        
        return report, predictions_df


def main():
    """Main execution function"""
    
    # Create predictor
    predictor = BoxOfficePredictor(model_name='StackingEnsemble')
    
    # Generate prediction report
    report, predictions = predictor.generate_prediction_report(
        MOVIE_INFO,
        save_path=RESULTS_DIR / "prediction_report.txt"
    )
    
    # Save predictions to CSV
    predictions.to_csv(RESULTS_DIR / "all_predictions.csv", index=False)
    
    print("\n" + "="*70)
    print("PREDICTION COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    main()
