"""
Model Training Module
Trains multiple models including base models, stacking, and ensembles
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.ensemble import (RandomForestRegressor, GradientBoostingRegressor, 
                              ExtraTreesRegressor, AdaBoostRegressor, 
                              StackingRegressor, VotingRegressor)
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
import joblib
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class ModelTrainer:
    """Trains and evaluates multiple ML models"""
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.models = {}
        self.results = {}
        
    def prepare_data(self, df: pd.DataFrame, target_col: str) -> Tuple:
        """Prepare features and target for modeling"""
        print("Preparing data for modeling...")
        
        # Separate features and target
        y = df[target_col]
        
        # Drop non-numeric and target columns
        drop_cols = [target_col, 'movie_title', 'release_date', 'genre', 
                    'studio', 'director']
        X = df.drop(columns=[col for col in drop_cols if col in df.columns])
        
        # Handle any remaining non-numeric columns
        X = X.select_dtypes(include=[np.number])
        
        # Handle infinite values
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median())
        
        print(f"Features shape: {X.shape}")
        print(f"Target shape: {y.shape}")
        
        return X, y
    
    def split_data(self, X: pd.DataFrame, y: pd.Series, 
                   test_size: float = 0.2) -> Tuple:
        """Split data into train and test sets"""
        return train_test_split(X, y, test_size=test_size, 
                               random_state=self.random_state)
    
    def scale_features(self, X_train: pd.DataFrame, 
                      X_test: pd.DataFrame) -> Tuple:
        """Scale features using StandardScaler"""
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled
    
    def get_base_models(self) -> Dict:
        """Define base models for training"""
        print("Initializing base models...")
        
        models = {
            # Linear Models
            'Ridge': Ridge(alpha=10.0, random_state=self.random_state),
            'Lasso': Lasso(alpha=1.0, random_state=self.random_state),
            'ElasticNet': ElasticNet(alpha=1.0, l1_ratio=0.5, 
                                    random_state=self.random_state),
            
            # Tree-based Models
            'RandomForest': RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=self.random_state,
                n_jobs=-1
            ),
            
            'ExtraTrees': ExtraTreesRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=self.random_state,
                n_jobs=-1
            ),
            
            'GradientBoosting': GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=5,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=self.random_state
            ),
            
            # Advanced Boosting Models
            'XGBoost': xgb.XGBRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=6,
                min_child_weight=3,
                subsample=0.8,
                colsample_bytree=0.8,
                gamma=0.1,
                random_state=self.random_state,
                n_jobs=-1
            ),
            
            'LightGBM': lgb.LGBMRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=6,
                num_leaves=31,
                min_child_samples=20,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=self.random_state,
                n_jobs=-1,
                verbose=-1
            ),
            
            'CatBoost': CatBoostRegressor(
                iterations=200,
                learning_rate=0.05,
                depth=6,
                l2_leaf_reg=3,
                random_state=self.random_state,
                verbose=0
            ),
            
            # Other Models
            'SVR': SVR(kernel='rbf', C=100, gamma='auto'),
            
            'KNN': KNeighborsRegressor(n_neighbors=5, weights='distance')
        }
        
        return models
    
    def evaluate_model(self, model, X_train, y_train, X_test, y_test, 
                      model_name: str) -> Dict:
        """Evaluate a single model"""
        print(f"\nTraining {model_name}...")
        
        # Train
        model.fit(X_train, y_train)
        
        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        # Metrics
        results = {
            'model_name': model_name,
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
            'train_mae': mean_absolute_error(y_train, y_train_pred),
            'test_mae': mean_absolute_error(y_test, y_test_pred),
            'train_r2': r2_score(y_train, y_train_pred),
            'test_r2': r2_score(y_test, y_test_pred),
        }
        
        # Cross-validation score
        cv_scores = cross_val_score(model, X_train, y_train, 
                                   cv=5, scoring='neg_mean_squared_error',
                                   n_jobs=-1)
        results['cv_rmse'] = np.sqrt(-cv_scores.mean())
        results['cv_rmse_std'] = np.sqrt(cv_scores.std())
        
        print(f"  Test RMSE: ${results['test_rmse']:,.2f}")
        print(f"  Test R²: {results['test_r2']:.4f}")
        print(f"  CV RMSE: ${results['cv_rmse']:,.2f} (±${results['cv_rmse_std']:,.2f})")
        
        return results, model
    
    def train_all_base_models(self, X_train, y_train, X_test, y_test) -> Dict:
        """Train all base models"""
        print("\n" + "="*70)
        print("TRAINING BASE MODELS")
        print("="*70)
        
        models = self.get_base_models()
        
        for model_name, model in models.items():
            results, trained_model = self.evaluate_model(
                model, X_train, y_train, X_test, y_test, model_name
            )
            self.results[model_name] = results
            self.models[model_name] = trained_model
        
        return self.results
    
    def create_stacking_ensemble(self, X_train, y_train, X_test, y_test) -> Dict:
        """Create and train stacking ensemble"""
        print("\n" + "="*70)
        print("TRAINING STACKING ENSEMBLE")
        print("="*70)
        
        # Define base estimators (best performing models)
        base_estimators = [
            ('rf', RandomForestRegressor(n_estimators=200, max_depth=15, 
                                        random_state=self.random_state, n_jobs=-1)),
            ('xgb', xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, 
                                    max_depth=6, random_state=self.random_state)),
            ('lgb', lgb.LGBMRegressor(n_estimators=200, learning_rate=0.05,
                                     random_state=self.random_state, verbose=-1)),
            ('catboost', CatBoostRegressor(iterations=200, learning_rate=0.05,
                                          random_state=self.random_state, verbose=0)),
            ('et', ExtraTreesRegressor(n_estimators=200, max_depth=15,
                                      random_state=self.random_state, n_jobs=-1))
        ]
        
        # Meta-learner
        meta_learner = Ridge(alpha=10.0)
        
        # Create stacking regressor
        stacking_model = StackingRegressor(
            estimators=base_estimators,
            final_estimator=meta_learner,
            cv=5,
            n_jobs=-1
        )
        
        # Evaluate
        results, trained_model = self.evaluate_model(
            stacking_model, X_train, y_train, X_test, y_test, 
            'StackingEnsemble'
        )
        
        self.results['StackingEnsemble'] = results
        self.models['StackingEnsemble'] = trained_model
        
        return results
    
    def create_voting_ensemble(self, X_train, y_train, X_test, y_test) -> Dict:
        """Create and train voting ensemble"""
        print("\n" + "="*70)
        print("TRAINING VOTING ENSEMBLE")
        print("="*70)
        
        # Define estimators with weights
        estimators = [
            ('rf', RandomForestRegressor(n_estimators=200, max_depth=15,
                                        random_state=self.random_state, n_jobs=-1)),
            ('xgb', xgb.XGBRegressor(n_estimators=200, learning_rate=0.05,
                                    max_depth=6, random_state=self.random_state)),
            ('lgb', lgb.LGBMRegressor(n_estimators=200, learning_rate=0.05,
                                     random_state=self.random_state, verbose=-1)),
            ('catboost', CatBoostRegressor(iterations=200, learning_rate=0.05,
                                          random_state=self.random_state, verbose=0)),
        ]
        
        # Create voting regressor (weighted average)
        voting_model = VotingRegressor(
            estimators=estimators,
            weights=[1, 2, 2, 2],  # Give more weight to boosting models
            n_jobs=-1
        )
        
        # Evaluate
        results, trained_model = self.evaluate_model(
            voting_model, X_train, y_train, X_test, y_test,
            'VotingEnsemble'
        )
        
        self.results['VotingEnsemble'] = results
        self.models['VotingEnsemble'] = trained_model
        
        return results
    
    def create_weighted_average_ensemble(self, X_test, y_test) -> Dict:
        """Create weighted average of top models"""
        print("\n" + "="*70)
        print("TRAINING WEIGHTED AVERAGE ENSEMBLE")
        print("="*70)
        
        # Get top 5 models based on test RMSE
        sorted_models = sorted(self.results.items(), 
                             key=lambda x: x[1]['test_rmse'])[:5]
        
        print(f"\nTop 5 models for weighted ensemble:")
        for model_name, results in sorted_models:
            print(f"  {model_name}: RMSE=${results['test_rmse']:,.2f}")
        
        # Calculate weights (inverse of RMSE)
        weights = []
        for model_name, results in sorted_models:
            weight = 1 / results['test_rmse']
            weights.append(weight)
        
        # Normalize weights
        weights = np.array(weights) / sum(weights)
        
        # Make predictions with weighted average
        predictions = np.zeros(len(X_test))
        for (model_name, _), weight in zip(sorted_models, weights):
            pred = self.models[model_name].predict(X_test)
            predictions += weight * pred
        
        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        results = {
            'model_name': 'WeightedAverageEnsemble',
            'test_rmse': rmse,
            'test_mae': mae,
            'test_r2': r2,
            'weights': {name: w for (name, _), w in zip(sorted_models, weights)}
        }
        
        print(f"\nWeighted Average Ensemble:")
        print(f"  Test RMSE: ${rmse:,.2f}")
        print(f"  Test R²: {r2:.4f}")
        
        self.results['WeightedAverageEnsemble'] = results
        
        return results
    
    def print_results_summary(self):
        """Print summary of all model results"""
        print("\n" + "="*70)
        print("MODEL PERFORMANCE SUMMARY")
        print("="*70)
        
        # Create results dataframe
        results_df = pd.DataFrame(self.results).T
        results_df = results_df.sort_values('test_rmse')
        
        print(f"\n{'Model':<30} {'Test RMSE':<15} {'Test R²':<10} {'CV RMSE':<15}")
        print("-" * 70)
        
        for idx, row in results_df.iterrows():
            cv_rmse = row.get('cv_rmse', 0)
            print(f"{idx:<30} ${row['test_rmse']:>13,.2f} {row['test_r2']:>9.4f} "
                  f"${cv_rmse:>13,.2f}")
        
        return results_df
    
    def save_models(self, save_dir):
        """Save all trained models"""
        print(f"\nSaving models to {save_dir}...")
        
        for model_name, model in self.models.items():
            model_path = save_dir / f"{model_name}.pkl"
            joblib.dump(model, model_path)
        
        # Save scaler
        scaler_path = save_dir / "scaler.pkl"
        joblib.dump(self.scaler, scaler_path)
        
        print(f"Saved {len(self.models)} models")


if __name__ == "__main__":
    from config import PROCESSED_DATA_DIR, MODELS_DIR, RESULTS_DIR, TARGET_VARIABLE
    
    # Load processed data
    df = pd.read_csv(PROCESSED_DATA_DIR / "engineered_features.csv")
    print(f"Loaded data shape: {df.shape}")
    
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
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE!")
    print("="*70)
