"""
Main Pipeline Script
Runs the complete ML pipeline from data collection to prediction
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config import (RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, 
                   RESULTS_DIR, MOVIE_INFO, TARGET_VARIABLE)
from data_collection import DataCollector
from feature_engineering import FeatureEngineer
from model_training import ModelTrainer
from predict import BoxOfficePredictor
from visualization import ModelVisualizer
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


def run_data_collection():
    """Step 1: Collect data"""
    print("\n" + "="*70)
    print("STEP 1: DATA COLLECTION")
    print("="*70 + "\n")
    
    collector = DataCollector()
    dataset = collector.create_full_dataset(
        save_path=RAW_DATA_DIR / "historical_movies.csv"
    )
    
    print(f"\n✓ Data collection complete: {dataset.shape}")
    return dataset


def run_feature_engineering():
    """Step 2: Engineer features"""
    print("\n" + "="*70)
    print("STEP 2: FEATURE ENGINEERING")
    print("="*70 + "\n")
    
    # Load raw data
    df = pd.read_csv(RAW_DATA_DIR / "historical_movies.csv")
    
    # Engineer features
    engineer = FeatureEngineer()
    df_engineered = engineer.engineer_all_features(df, is_training=True)
    
    # Save processed data
    df_engineered.to_csv(PROCESSED_DATA_DIR / "engineered_features.csv", index=False)
    
    print(f"\n✓ Feature engineering complete: {df_engineered.shape}")
    return df_engineered


def run_model_training():
    """Step 3: Train models"""
    print("\n" + "="*70)
    print("STEP 3: MODEL TRAINING")
    print("="*70 + "\n")
    
    # Load processed data
    df = pd.read_csv(PROCESSED_DATA_DIR / "engineered_features.csv")
    
    # Initialize trainer
    trainer = ModelTrainer(random_state=42)
    
    # Prepare data
    X, y = trainer.prepare_data(df, TARGET_VARIABLE)
    X_train, X_test, y_train, y_test = trainer.split_data(X, y, test_size=0.2)
    
    # Scale features
    X_train_scaled, X_test_scaled = trainer.scale_features(X_train, X_test)
    
    # Train base models
    trainer.train_all_base_models(X_train_scaled, y_train, X_test_scaled, y_test)
    
    # Train stacking ensemble
    trainer.create_stacking_ensemble(X_train_scaled, y_train, X_test_scaled, y_test)
    
    # Train voting ensemble
    trainer.create_voting_ensemble(X_train_scaled, y_train, X_test_scaled, y_test)
    
    # Train weighted average ensemble
    trainer.create_weighted_average_ensemble(X_test_scaled, y_test)
    
    # Print summary
    results_df = trainer.print_results_summary()
    
    # Save results
    results_df.to_csv(RESULTS_DIR / "model_results.csv")
    
    # Save models
    trainer.save_models(MODELS_DIR)
    
    print("\n✓ Model training complete!")
    return results_df


def run_prediction():
    """Step 4: Make predictions"""
    print("\n" + "="*70)
    print("STEP 4: PREDICTION")
    print("="*70 + "\n")
    
    # Create predictor
    predictor = BoxOfficePredictor(model_name='StackingEnsemble')
    
    # Generate prediction report
    report, predictions = predictor.generate_prediction_report(
        MOVIE_INFO,
        save_path=RESULTS_DIR / "prediction_report.txt"
    )
    
    # Save predictions to CSV
    predictions.to_csv(RESULTS_DIR / "all_predictions.csv", index=False)
    
    print("\n✓ Prediction complete!")
    return predictions


def run_visualization():
    """Step 5: Create visualizations"""
    print("\n" + "="*70)
    print("STEP 5: VISUALIZATION")
    print("="*70 + "\n")
    
    # Load results
    results_df = pd.read_csv(RESULTS_DIR / "model_results.csv", index_col=0)
    predictions_df = pd.read_csv(RESULTS_DIR / "all_predictions.csv")
    
    # Create visualizer
    viz = ModelVisualizer(RESULTS_DIR)
    
    # Generate visualizations
    print("Creating model comparison plot...")
    viz.plot_model_comparison(results_df, 
                             save_path=RESULTS_DIR / "model_comparison.png")
    
    print("Creating predictions by model plot...")
    viz.plot_predictions_by_model(predictions_df,
                                 save_path=RESULTS_DIR / "predictions_by_model.html")
    
    print("Creating prediction distribution plot...")
    viz.plot_prediction_distribution(predictions_df,
                                    save_path=RESULTS_DIR / "prediction_distribution.html")
    
    print("Creating dashboard...")
    viz.create_dashboard(results_df, predictions_df,
                        save_path=RESULTS_DIR / "dashboard.html")
    
    print("\n✓ Visualization complete!")


def main():
    """Run complete pipeline"""
    print("\n" + "="*70)
    print("AVATAR: ASH & FIRE BOX OFFICE PREDICTION PIPELINE")
    print("="*70)
    
    try:
        # Step 1: Data Collection
        run_data_collection()
        
        # Step 2: Feature Engineering
        run_feature_engineering()
        
        # Step 3: Model Training
        run_model_training()
        
        # Step 4: Prediction
        run_prediction()
        
        # Step 5: Visualization
        run_visualization()
        
        print("\n" + "="*70)
        print("PIPELINE COMPLETE! ✓")
        print("="*70)
        print(f"\nResults saved to: {RESULTS_DIR}")
        print(f"Models saved to: {MODELS_DIR}")
        print("\nGenerated files:")
        print("  - model_results.csv: Model performance metrics")
        print("  - all_predictions.csv: Predictions from all models")
        print("  - prediction_report.txt: Detailed prediction report")
        print("  - model_comparison.png: Model performance comparison")
        print("  - predictions_by_model.html: Interactive predictions chart")
        print("  - prediction_distribution.html: Prediction distribution")
        print("  - dashboard.html: Complete interactive dashboard")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
