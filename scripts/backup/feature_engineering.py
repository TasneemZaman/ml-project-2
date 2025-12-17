"""
Feature Engineering Module
Creates advanced features for box office prediction
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, RobustScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """Creates and transforms features for modeling"""
    
    def __init__(self):
        self.scaler = RobustScaler()
        self.label_encoders = {}
        
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features between important variables"""
        print("Creating interaction features...")
        
        df = df.copy()
        
        # Budget-related interactions
        if 'budget' in df.columns and 'imdb_rating' in df.columns:
            df['budget_rating_interaction'] = df['budget'] * df['imdb_rating']
        
        if 'budget' in df.columns and 'num_theaters' in df.columns:
            df['budget_per_theater'] = df['budget'] / (df['num_theaters'] + 1)
        
        # Social media engagement score
        social_cols = ['twitter_mentions', 'youtube_trailer_views', 'instagram_hashtag_count']
        if all(col in df.columns for col in social_cols):
            df['social_engagement_score'] = (
                df['twitter_mentions'] * 0.3 +
                df['youtube_trailer_views'] * 0.5 +
                df['instagram_hashtag_count'] * 0.2
            )
        
        # Hype index (combining multiple trend indicators)
        hype_cols = ['google_trends_score', 'twitter_sentiment', 'ticket_presales']
        if all(col in df.columns for col in hype_cols):
            df['hype_index'] = (
                df['google_trends_score'] * 0.4 +
                df['twitter_sentiment'] * 100 * 0.3 +
                (df['ticket_presales'] / df['ticket_presales'].max() * 100) * 0.3
            )
        
        # Quality score
        quality_cols = ['imdb_rating', 'metascore']
        if all(col in df.columns for col in quality_cols):
            df['quality_score'] = (
                df['imdb_rating'] * 10 * 0.6 +
                df['metascore'] * 0.4
            )
        
        # Theater metrics
        if 'num_theaters' in df.columns and 'average_per_theater' in df.columns:
            df['theater_efficiency'] = df['average_per_theater'] / (df['num_theaters'] + 1)
        
        # Franchise momentum
        franchise_cols = ['franchise_previous_avg_gross', 'years_since_last_release']
        if all(col in df.columns for col in franchise_cols):
            df['franchise_momentum'] = (
                df['franchise_previous_avg_gross'] / 
                (df['years_since_last_release'] + 1)
            )
        
        return df
    
    def create_polynomial_features(self, df: pd.DataFrame, 
                                   columns: list, degree: int = 2) -> pd.DataFrame:
        """Create polynomial features for specified columns"""
        print(f"Creating polynomial features (degree={degree})...")
        
        df = df.copy()
        
        for col in columns:
            if col in df.columns:
                for d in range(2, degree + 1):
                    df[f'{col}_pow{d}'] = df[col] ** d
                
                # Log transform for skewed features
                if (df[col] > 0).all():
                    df[f'{col}_log'] = np.log1p(df[col])
                
                # Square root transform
                if (df[col] >= 0).all():
                    df[f'{col}_sqrt'] = np.sqrt(df[col])
        
        return df
    
    def create_ratio_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create ratio-based features"""
        print("Creating ratio features...")
        
        df = df.copy()
        
        # Budget efficiency ratios
        if 'budget' in df.columns:
            if 'imdb_votes' in df.columns:
                df['budget_per_vote'] = df['budget'] / (df['imdb_votes'] + 1)
            
            if 'social_engagement_score' in df.columns:
                df['budget_social_ratio'] = df['budget'] / (df['social_engagement_score'] + 1)
        
        # Engagement ratios
        if 'youtube_trailer_views' in df.columns and 'youtube_trailer_likes' in df.columns:
            df['youtube_engagement_rate'] = (
                df['youtube_trailer_likes'] / (df['youtube_trailer_views'] + 1)
            )
        
        # Market competition ratio
        if 'ticket_presales' in df.columns and 'competing_releases_same_week' in df.columns:
            df['presales_competition_ratio'] = (
                df['ticket_presales'] / (df['competing_releases_same_week'] + 1)
            )
        
        return df
    
    def encode_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features"""
        print("Encoding categorical features...")
        
        df = df.copy()
        
        # Genre encoding (multi-label)
        if 'genre' in df.columns:
            # Split genres and create binary features
            genres = ['Action', 'Adventure', 'Sci-Fi', 'Drama', 'Comedy', 
                     'Thriller', 'Horror', 'Romance']
            for genre in genres:
                df[f'genre_{genre.lower()}'] = df['genre'].str.contains(
                    genre, case=False, na=False
                ).astype(int)
        
        # Studio encoding
        if 'studio' in df.columns:
            if 'studio' not in self.label_encoders:
                self.label_encoders['studio'] = LabelEncoder()
                df['studio_encoded'] = self.label_encoders['studio'].fit_transform(
                    df['studio'].fillna('Unknown')
                )
            else:
                df['studio_encoded'] = self.label_encoders['studio'].transform(
                    df['studio'].fillna('Unknown')
                )
        
        # Director encoding
        if 'director' in df.columns:
            if 'director' not in self.label_encoders:
                self.label_encoders['director'] = LabelEncoder()
                df['director_encoded'] = self.label_encoders['director'].fit_transform(
                    df['director'].fillna('Unknown')
                )
            else:
                df['director_encoded'] = self.label_encoders['director'].transform(
                    df['director'].fillna('Unknown')
                )
        
        return df
    
    def create_time_based_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features"""
        print("Creating time-based features...")
        
        df = df.copy()
        
        if 'release_date' in df.columns:
            df['release_date'] = pd.to_datetime(df['release_date'])
            
            # Cyclical encoding for month and day of week
            if 'release_month' in df.columns:
                df['release_month_sin'] = np.sin(2 * np.pi * df['release_month'] / 12)
                df['release_month_cos'] = np.cos(2 * np.pi * df['release_month'] / 12)
            
            if 'release_day_of_week' in df.columns:
                df['release_day_sin'] = np.sin(2 * np.pi * df['release_day_of_week'] / 7)
                df['release_day_cos'] = np.cos(2 * np.pi * df['release_day_of_week'] / 7)
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values intelligently"""
        print("Handling missing values...")
        
        df = df.copy()
        
        # Numeric columns - fill with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)
        
        # Categorical columns - fill with mode or 'Unknown'
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].isnull().any():
                df[col].fillna('Unknown', inplace=True)
        
        return df
    
    def remove_outliers(self, df: pd.DataFrame, columns: list, 
                       n_std: float = 3) -> pd.DataFrame:
        """Remove outliers using z-score method"""
        print(f"Removing outliers (>{n_std} std dev)...")
        
        df = df.copy()
        initial_rows = len(df)
        
        for col in columns:
            if col in df.columns:
                mean = df[col].mean()
                std = df[col].std()
                df = df[np.abs(df[col] - mean) <= (n_std * std)]
        
        print(f"Removed {initial_rows - len(df)} outlier rows")
        return df
    
    def engineer_all_features(self, df: pd.DataFrame, 
                             is_training: bool = True) -> pd.DataFrame:
        """Apply all feature engineering steps"""
        print("\n" + "="*50)
        print("FEATURE ENGINEERING PIPELINE")
        print("="*50 + "\n")
        
        # Handle missing values first
        df = self.handle_missing_values(df)
        
        # Encode categorical features
        df = self.encode_categorical_features(df)
        
        # Create interaction features
        df = self.create_interaction_features(df)
        
        # Create ratio features
        df = self.create_ratio_features(df)
        
        # Create time-based features
        df = self.create_time_based_features(df)
        
        # Create polynomial features for key numeric columns
        poly_columns = ['budget', 'imdb_rating', 'num_theaters', 'twitter_mentions']
        df = self.create_polynomial_features(df, poly_columns, degree=2)
        
        # Remove outliers (only on training data)
        if is_training:
            outlier_columns = ['budget', 'first_week', 'opening_weekend']
            df = self.remove_outliers(df, outlier_columns, n_std=3)
        
        print(f"\nFinal feature count: {len(df.columns)}")
        print(f"Final sample count: {len(df)}")
        
        return df


if __name__ == "__main__":
    from config import RAW_DATA_DIR, PROCESSED_DATA_DIR
    
    # Load data
    df = pd.read_csv(RAW_DATA_DIR / "historical_movies.csv")
    print(f"Loaded data shape: {df.shape}")
    
    # Engineer features
    engineer = FeatureEngineer()
    df_engineered = engineer.engineer_all_features(df, is_training=True)
    
    # Save processed data
    df_engineered.to_csv(PROCESSED_DATA_DIR / "engineered_features.csv", index=False)
    print(f"\nSaved engineered features to {PROCESSED_DATA_DIR / 'engineered_features.csv'}")
