"""
Data Collection Module
Collects data from IMDB, Box Office Mojo, and trending data sources
Now includes real TMDB API integration!
"""

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# TMDB API Configuration
TMDB_API_KEY = 'd429e3e7a57fe68708d1380b99dbdf43'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

class DataCollector:
    """Collects movie data from multiple sources including TMDB API"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.tmdb_api_key = TMDB_API_KEY
    
    def fetch_tmdb_movie(self, movie_id: int) -> Dict:
        """Fetch movie details from TMDB API"""
        try:
            url = f"{TMDB_BASE_URL}/movie/{movie_id}"
            params = {'api_key': self.tmdb_api_key}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching TMDB movie {movie_id}: {e}")
            return {}
    
    def search_tmdb_movie(self, title: str, year: Optional[int] = None) -> Dict:
        """Search for a movie on TMDB"""
        try:
            url = f"{TMDB_BASE_URL}/search/movie"
            params = {
                'api_key': self.tmdb_api_key,
                'query': title
            }
            if year:
                params['year'] = year
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['results']:
                return data['results'][0]  # Return first match
            return {}
        except Exception as e:
            print(f"Error searching TMDB for {title}: {e}")
            return {}
    
    def get_movie_credits(self, movie_id: int) -> Dict:
        """Get movie cast and crew from TMDB"""
        try:
            url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits"
            params = {'api_key': self.tmdb_api_key}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching credits for movie {movie_id}: {e}")
            return {}
    
    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        """Get popular movies from TMDB"""
        try:
            url = f"{TMDB_BASE_URL}/movie/popular"
            params = {
                'api_key': self.tmdb_api_key,
                'page': page
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            print(f"Error fetching popular movies: {e}")
            return []
    
    def get_top_rated_movies(self, page: int = 1) -> List[Dict]:
        """Get top rated movies from TMDB"""
        try:
            url = f"{TMDB_BASE_URL}/movie/top_rated"
            params = {
                'api_key': self.tmdb_api_key,
                'page': page
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            print(f"Error fetching top rated movies: {e}")
            return []
    
    def collect_historical_boxoffice_data(self, use_real_data: bool = True) -> pd.DataFrame:
        """
        Collect historical box office data
        If use_real_data=True, fetches from TMDB API
        Otherwise uses synthetic data
        """
        print("Collecting historical box office data...")
        
        if use_real_data:
            print("Fetching real data from TMDB API...")
            return self._collect_real_tmdb_data()
        else:
            print("Using synthetic data for demonstration...")
            return self._collect_synthetic_data()
    
    def _collect_real_tmdb_data(self) -> pd.DataFrame:
        """Collect real movie data from TMDB API"""
        movies_data = []
        
        # Get blockbuster movies with known box office data
        blockbuster_ids = [
            19995,   # Avatar
            76600,   # Avatar: The Way of Water
            299534,  # Avengers: Endgame
            140607,  # Star Wars: The Force Awakens
            271110,  # Captain America: Civil War
            284053,  # Thor: Ragnarok
            284054,  # Black Panther
            315635,  # Spider-Man: Homecoming
            299536,  # Avengers: Infinity War
            181808,  # Star Wars: The Last Jedi
            335983,  # Rogue One
            157336,  # Interstellar
            118340,  # Guardians of the Galaxy
            122917,  # The Hobbit: The Battle of the Five Armies
            166424,  # Furious 7
            87101,   # Terminator Genisys
            135397,  # Jurassic World
            102382,  # The Amazing Spider-Man 2
            254128,  # San Andreas
            258489,  # The Legend of Tarzan
        ]
        
        for movie_id in blockbuster_ids:
            try:
                # Fetch movie details
                movie_data = self.fetch_tmdb_movie(movie_id)
                if not movie_data:
                    continue
                
                # Fetch credits
                credits = self.get_movie_credits(movie_id)
                director = 'Unknown'
                if credits and 'crew' in credits:
                    directors = [c['name'] for c in credits['crew'] if c['job'] == 'Director']
                    if directors:
                        director = directors[0]
                
                # Extract relevant information
                movie_info = {
                    'movie_title': movie_data.get('title', 'Unknown'),
                    'release_date': movie_data.get('release_date', '2020-01-01'),
                    'budget': movie_data.get('budget', 0),
                    'revenue': movie_data.get('revenue', 0),
                    'runtime': movie_data.get('runtime', 120),
                    'imdb_rating': movie_data.get('vote_average', 7.0),
                    'imdb_votes': movie_data.get('vote_count', 1000),
                    'popularity': movie_data.get('popularity', 50.0),
                    'genre': '|'.join([g['name'] for g in movie_data.get('genres', [])]),
                    'director': director,
                    'original_language': movie_data.get('original_language', 'en'),
                }
                
                # Estimate additional fields (since TMDB doesn't have all box office details)
                if movie_info['revenue'] > 0:
                    # Estimate first week as ~30-40% of total for blockbusters
                    movie_info['first_week'] = movie_info['revenue'] * np.random.uniform(0.25, 0.45)
                    movie_info['opening_weekend'] = movie_info['first_week'] * np.random.uniform(0.40, 0.60)
                else:
                    # Use budget-based estimates
                    movie_info['first_week'] = movie_info['budget'] * np.random.uniform(0.3, 0.8)
                    movie_info['opening_weekend'] = movie_info['first_week'] * 0.5
                
                # Add synthetic theater and social media data
                movie_info.update(self._add_synthetic_features(movie_info))
                
                movies_data.append(movie_info)
                print(f"  ✓ Collected: {movie_info['movie_title']}")
                time.sleep(0.25)  # Rate limiting
                
            except Exception as e:
                print(f"  ✗ Error with movie ID {movie_id}: {e}")
                continue
        
        df = pd.DataFrame(movies_data)
        print(f"\n✓ Collected {len(df)} real movies from TMDB")
        return df
    
    def _collect_synthetic_data(self) -> pd.DataFrame:
        """Collect synthetic data for demonstration"""
    def _collect_synthetic_data(self) -> pd.DataFrame:
        """Collect synthetic data for demonstration"""
        
        # Sample structure - replace with actual scraping/API calls
        historical_data = {
            'movie_title': [],
            'release_date': [],
            'opening_weekend': [],
            'first_week': [],
            'total_gross': [],
            'budget': [],
            'genre': [],
            'rating': [],
            'runtime': [],
            'studio': [],
            'director': [],
            'num_theaters': [],
            'average_per_theater': []
        }
        
        # Example movies for training (Avatar franchise + similar blockbusters)
        example_movies = [
            {'movie_title': 'Avatar', 'release_date': '2009-12-18', 'opening_weekend': 77025481,
             'first_week': 150000000, 'total_gross': 760507625, 'budget': 237000000,
             'genre': 'Action|Adventure|Sci-Fi', 'rating': 7.9, 'runtime': 162,
             'studio': '20th Century Fox', 'director': 'James Cameron', 
             'num_theaters': 3452, 'average_per_theater': 22312},
            
            {'movie_title': 'Avatar: The Way of Water', 'release_date': '2022-12-16', 
             'opening_weekend': 134100226, 'first_week': 250000000, 'total_gross': 684075767,
             'budget': 350000000, 'genre': 'Action|Adventure|Sci-Fi', 'rating': 7.6,
             'runtime': 192, 'studio': '20th Century Studios', 'director': 'James Cameron',
             'num_theaters': 4202, 'average_per_theater': 31925},
            
            {'movie_title': 'Avengers: Endgame', 'release_date': '2019-04-26',
             'opening_weekend': 357115007, 'first_week': 600000000, 'total_gross': 858373000,
             'budget': 356000000, 'genre': 'Action|Adventure|Drama', 'rating': 8.4,
             'runtime': 181, 'studio': 'Marvel Studios', 'director': 'Russo Brothers',
             'num_theaters': 4662, 'average_per_theater': 76601},
            
            {'movie_title': 'Star Wars: The Force Awakens', 'release_date': '2015-12-18',
             'opening_weekend': 247966675, 'first_week': 390000000, 'total_gross': 936662225,
             'budget': 245000000, 'genre': 'Action|Adventure|Sci-Fi', 'rating': 7.8,
             'runtime': 138, 'studio': 'Lucasfilm', 'director': 'J.J. Abrams',
             'num_theaters': 4134, 'average_per_theater': 59984},
        ]
        
        for movie in example_movies:
            for key in historical_data.keys():
                historical_data[key].append(movie.get(key, None))
        
        df = pd.DataFrame(historical_data)
        print(f"Collected {len(df)} historical movies")
        return df
    
    def _add_synthetic_features(self, movie_info: Dict) -> Dict:
        """Add synthetic features for social media and theater data"""
        features = {
            'num_theaters': np.random.randint(3000, 4700),
            'average_per_theater': np.random.randint(15000, 85000),
            'metascore': int(movie_info.get('imdb_rating', 7.0) * 10 + np.random.randint(-5, 5)),
            'num_reviews': np.random.randint(300, 2500),
            'num_critic_reviews': np.random.randint(30, 250),
            'twitter_mentions': np.random.randint(30000, 250000),
            'twitter_sentiment': np.random.uniform(0.5, 0.95),
            'google_trends_score': np.random.uniform(60, 100),
            'youtube_trailer_views': np.random.randint(5000000, 60000000),
            'youtube_trailer_likes': np.random.randint(200000, 2500000),
            'instagram_hashtag_count': np.random.randint(50000, 600000),
            'facebook_page_likes': np.random.randint(500000, 6000000),
            'reddit_mentions': np.random.randint(500, 15000),
            'search_volume_index': np.random.uniform(50, 100),
            'ticket_presales': np.random.randint(3000000, 25000000),
            'release_month': int(movie_info.get('release_date', '2020-01-01').split('-')[1]),
            'release_day_of_week': np.random.randint(0, 7),
            'is_holiday_season': np.random.choice([0, 1], p=[0.7, 0.3]),
            'is_summer': np.random.choice([0, 1], p=[0.6, 0.4]),
            'competing_releases_same_week': np.random.randint(0, 4),
            'is_sequel': np.random.choice([0, 1], p=[0.4, 0.6]),
            'franchise_previous_avg_gross': np.random.uniform(200000000, 800000000),
            'years_since_last_release': np.random.randint(1, 6),
            'studio': 'Unknown',
            'total_gross': movie_info.get('revenue', 0)
        }
        return features
    
    def collect_imdb_features(self, movie_title: str) -> Dict:
        """
        Collect IMDB features for a movie
        Returns ratings, votes, popularity metrics
        """
        print(f"Collecting IMDB data for {movie_title}...")
        
        # Template - replace with actual IMDB scraping or API
        imdb_data = {
            'imdb_rating': np.random.uniform(7.0, 8.5),
            'imdb_votes': np.random.randint(100000, 500000),
            'metascore': np.random.randint(70, 90),
            'num_reviews': np.random.randint(500, 2000),
            'num_critic_reviews': np.random.randint(50, 200),
            'popularity_score': np.random.uniform(80, 100)
        }
        
        return imdb_data
    
    def collect_social_media_trends(self, movie_title: str, days_before: int = 7) -> Dict:
        """
        Collect social media trend data (T-7 data)
        This would ideally pull from Twitter, Google Trends, YouTube, etc.
        """
        print(f"Collecting T-{days_before} trend data for {movie_title}...")
        
        # Template - replace with actual API calls
        trend_data = {
            'twitter_mentions': np.random.randint(50000, 200000),
            'twitter_sentiment': np.random.uniform(0.6, 0.9),
            'google_trends_score': np.random.uniform(75, 100),
            'youtube_trailer_views': np.random.randint(10000000, 50000000),
            'youtube_trailer_likes': np.random.randint(500000, 2000000),
            'instagram_hashtag_count': np.random.randint(100000, 500000),
            'facebook_page_likes': np.random.randint(1000000, 5000000),
            'reddit_mentions': np.random.randint(1000, 10000),
            'search_volume_index': np.random.uniform(80, 100),
            'ticket_presales': np.random.randint(5000000, 20000000)
        }
        
        return trend_data
    
    def collect_temporal_features(self, release_date: str) -> Dict:
        """
        Collect temporal features like season, holidays, competition
        """
        print("Collecting temporal features...")
        
        release_dt = datetime.strptime(release_date, '%Y-%m-%d')
        
        temporal_data = {
            'release_month': release_dt.month,
            'release_day_of_week': release_dt.weekday(),
            'is_holiday_season': int(release_dt.month in [11, 12, 1]),
            'is_summer': int(release_dt.month in [5, 6, 7, 8]),
            'days_since_last_major_release': np.random.randint(7, 30),
            'competing_releases_same_week': np.random.randint(0, 3),
            'competing_releases_same_genre': np.random.randint(0, 2)
        }
        
        return temporal_data
    
    def collect_franchise_features(self, franchise_name: str) -> Dict:
        """
        Collect franchise-specific features
        """
        print(f"Collecting franchise features for {franchise_name}...")
        
        # Template for franchise features
        franchise_data = {
            'is_sequel': 1,
            'franchise_previous_avg_gross': 720000000,
            'franchise_previous_avg_opening': 105000000,
            'years_since_last_release': 3,
            'franchise_total_movies': 3,
            'franchise_avg_rating': 7.75,
            'franchise_brand_value': 95.0  # Score out of 100
        }
        
        return franchise_data
    
    def create_full_dataset(self, save_path: Optional[str] = None) -> pd.DataFrame:
        """
        Create a complete dataset combining all features
        """
        print("Creating full dataset...")
        
        # Collect historical data
        historical_df = self.collect_historical_boxoffice_data()
        
        # Add additional features to each movie
        for idx, row in historical_df.iterrows():
            # IMDB features
            imdb_features = self.collect_imdb_features(row['movie_title'])
            for key, value in imdb_features.items():
                historical_df.at[idx, key] = value
            
            # Temporal features
            temporal_features = self.collect_temporal_features(row['release_date'])
            for key, value in temporal_features.items():
                historical_df.at[idx, key] = value
            
            # Trend data (simulated T-7 data)
            trend_features = self.collect_social_media_trends(row['movie_title'])
            for key, value in trend_features.items():
                historical_df.at[idx, key] = value
            
            time.sleep(0.1)  # Respectful scraping
        
        if save_path:
            historical_df.to_csv(save_path, index=False)
            print(f"Dataset saved to {save_path}")
        
        return historical_df


if __name__ == "__main__":
    from config import RAW_DATA_DIR
    
    collector = DataCollector()
    dataset = collector.create_full_dataset(
        save_path=RAW_DATA_DIR / "historical_movies.csv"
    )
    print(f"\nDataset shape: {dataset.shape}")
    print(f"\nColumns: {list(dataset.columns)}")
    print(f"\nFirst few rows:\n{dataset.head()}")
