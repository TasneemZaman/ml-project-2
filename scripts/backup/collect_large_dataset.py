"""
Enhanced TMDB Data Collection - Collect 5000+ movies from 1990 onwards
"""

import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
from typing import List, Dict
import json

# TMDB API Configuration
TMDB_API_KEY = 'd429e3e7a57fe68708d1380b99dbdf43'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'


class LargeScaleDataCollector:
    """Collects large dataset of movies from TMDB"""
    
    def __init__(self):
        self.api_key = TMDB_API_KEY
        self.base_url = TMDB_BASE_URL
        self.collected_movies = []
        
    def get_movies_by_year(self, year: int, page: int = 1) -> Dict:
        """Get movies released in a specific year"""
        try:
            url = f"{self.base_url}/discover/movie"
            params = {
                'api_key': self.api_key,
                'primary_release_year': year,
                'sort_by': 'popularity.desc',
                'page': page,
                'vote_count.gte': 10,  # At least 10 votes
                'include_adult': 'false'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching movies for year {year}, page {page}: {e}")
            return {}
    
    def get_movie_details(self, movie_id: int) -> Dict:
        """Get detailed movie information"""
        try:
            url = f"{self.base_url}/movie/{movie_id}"
            params = {'api_key': self.api_key}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {}
    
    def get_movie_credits(self, movie_id: int) -> Dict:
        """Get movie credits (cast and crew)"""
        try:
            url = f"{self.base_url}/movie/{movie_id}/credits"
            params = {'api_key': self.api_key}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {}
    
    def process_movie(self, movie_basic: Dict) -> Dict:
        """Process a movie and get all its details"""
        movie_id = movie_basic.get('id')
        
        # Get detailed info
        details = self.get_movie_details(movie_id)
        if not details:
            return None
        
        # Get credits
        credits = self.get_movie_credits(movie_id)
        director = 'Unknown'
        if credits and 'crew' in credits:
            directors = [c['name'] for c in credits['crew'] if c['job'] == 'Director']
            if directors:
                director = directors[0]
        
        # Extract and structure data
        movie_data = {
            'movie_title': details.get('title', 'Unknown'),
            'release_date': details.get('release_date', '1990-01-01'),
            'budget': details.get('budget', 0),
            'revenue': details.get('revenue', 0),
            'runtime': details.get('runtime', 90),
            'imdb_rating': details.get('vote_average', 6.0),
            'imdb_votes': details.get('vote_count', 100),
            'popularity': details.get('popularity', 10.0),
            'genre': '|'.join([g['name'] for g in details.get('genres', [])]),
            'director': director,
            'original_language': details.get('original_language', 'en'),
        }
        
        # Calculate first week and opening weekend estimates
        revenue = movie_data['revenue']
        budget = movie_data['budget']
        
        if revenue > 0:
            # Estimate first week as percentage of total revenue
            # Blockbusters typically make 25-45% in first week
            first_week_ratio = np.random.uniform(0.25, 0.45) if revenue > 100000000 else np.random.uniform(0.15, 0.35)
            movie_data['first_week'] = revenue * first_week_ratio
            movie_data['opening_weekend'] = movie_data['first_week'] * np.random.uniform(0.40, 0.60)
        elif budget > 0:
            # Estimate based on budget if no revenue data
            movie_data['first_week'] = budget * np.random.uniform(0.2, 0.7)
            movie_data['opening_weekend'] = movie_data['first_week'] * 0.5
        else:
            # Default estimates for unknown budget/revenue
            movie_data['first_week'] = np.random.uniform(1000000, 50000000)
            movie_data['opening_weekend'] = movie_data['first_week'] * 0.5
        
        # Add synthetic features
        movie_data.update(self._add_synthetic_features(movie_data))
        
        return movie_data
    
    def _add_synthetic_features(self, movie_info: Dict) -> Dict:
        """Add synthetic features for theater counts and social media"""
        # Theater counts based on budget/popularity
        budget = movie_info.get('budget', 0)
        popularity = movie_info.get('popularity', 10)
        
        if budget > 100000000:  # Big budget
            num_theaters = np.random.randint(3500, 4700)
            avg_per_theater = np.random.randint(40000, 90000)
        elif budget > 50000000:  # Medium budget
            num_theaters = np.random.randint(2500, 3500)
            avg_per_theater = np.random.randint(20000, 50000)
        else:  # Lower budget
            num_theaters = np.random.randint(1000, 2500)
            avg_per_theater = np.random.randint(5000, 25000)
        
        features = {
            'num_theaters': num_theaters,
            'average_per_theater': avg_per_theater,
            'metascore': int(movie_info.get('imdb_rating', 6.0) * 10 + np.random.randint(-8, 8)),
            'num_reviews': np.random.randint(100, 2500),
            'num_critic_reviews': np.random.randint(20, 250),
            
            # T-7 social media data (scaled by popularity)
            'twitter_mentions': int(popularity * np.random.uniform(1000, 5000)),
            'twitter_sentiment': np.random.uniform(0.5, 0.95),
            'google_trends_score': min(100, popularity * np.random.uniform(0.8, 1.5)),
            'youtube_trailer_views': int(popularity * np.random.uniform(50000, 500000)),
            'youtube_trailer_likes': int(popularity * np.random.uniform(5000, 50000)),
            'instagram_hashtag_count': int(popularity * np.random.uniform(2000, 20000)),
            'facebook_page_likes': int(popularity * np.random.uniform(20000, 200000)),
            'reddit_mentions': np.random.randint(100, 10000),
            'search_volume_index': min(100, popularity * np.random.uniform(0.5, 1.2)),
            'ticket_presales': int(movie_info.get('first_week', 1000000) * np.random.uniform(0.05, 0.15)),
            
            # Temporal features
            'release_month': int(movie_info.get('release_date', '1990-01-01').split('-')[1]),
            'release_day_of_week': np.random.randint(0, 7),
            'is_holiday_season': 1 if int(movie_info.get('release_date', '1990-01-01').split('-')[1]) in [11, 12, 1] else 0,
            'is_summer': 1 if int(movie_info.get('release_date', '1990-01-01').split('-')[1]) in [5, 6, 7, 8] else 0,
            'competing_releases_same_week': np.random.randint(0, 5),
            
            # Franchise features (estimated)
            'is_sequel': 1 if any(word in movie_info.get('movie_title', '').lower() for word in ['2', 'ii', '3', 'iii', 'returns', 'rises']) else 0,
            'franchise_previous_avg_gross': np.random.uniform(100000000, 800000000) if np.random.random() > 0.7 else 0,
            'years_since_last_release': np.random.randint(1, 6) if np.random.random() > 0.7 else 0,
            
            'studio': 'Unknown',
            'total_gross': movie_info.get('revenue', 0)
        }
        
        return features
    
    def collect_movies_from_year_range(self, start_year: int, end_year: int, 
                                       target_movies: int = 5000) -> pd.DataFrame:
        """Collect movies from a range of years"""
        print("="*80)
        print(f"COLLECTING {target_movies}+ MOVIES FROM {start_year} TO {end_year}")
        print("="*80)
        
        all_movies = []
        movies_collected = 0
        years = list(range(start_year, end_year + 1))
        
        for year in years:
            if movies_collected >= target_movies:
                break
            
            print(f"\n📅 Processing year: {year}")
            page = 1
            year_movies = 0
            
            while movies_collected < target_movies:
                # Get movies for this year and page
                result = self.get_movies_by_year(year, page)
                
                if not result or 'results' not in result:
                    break
                
                movies = result['results']
                if not movies:
                    break
                
                total_pages = min(result.get('total_pages', 1), 500)  # TMDB limit
                
                # Process each movie
                for movie_basic in movies:
                    if movies_collected >= target_movies:
                        break
                    
                    movie_data = self.process_movie(movie_basic)
                    if movie_data:
                        all_movies.append(movie_data)
                        movies_collected += 1
                        year_movies += 1
                        
                        if movies_collected % 100 == 0:
                            print(f"  ✓ Collected {movies_collected} movies...")
                    
                    time.sleep(0.25)  # Rate limiting (4 requests per second)
                
                # Move to next page
                page += 1
                if page > total_pages or page > 20:  # Limit pages per year
                    break
            
            print(f"  ✓ Year {year}: {year_movies} movies collected")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_movies)
        
        print("\n" + "="*80)
        print(f"✅ COLLECTION COMPLETE!")
        print(f"Total movies collected: {len(df)}")
        print(f"Date range: {df['release_date'].min()} to {df['release_date'].max()}")
        print("="*80)
        
        return df


def main():
    """Main execution function"""
    collector = LargeScaleDataCollector()
    
    # Collect 5000+ movies from 1990 to present
    start_year = 1990
    end_year = 2024
    target_movies = 5000
    
    print(f"\n🎬 Starting large-scale data collection...")
    print(f"Target: {target_movies}+ movies from {start_year}-{end_year}")
    print(f"This will take approximately {target_movies * 0.25 / 60:.1f} minutes")
    print(f"(Rate limited to 4 requests per second)\n")
    
    # Collect data
    df = collector.collect_movies_from_year_range(start_year, end_year, target_movies)
    
    # Save to CSV
    output_file = 'data/raw/tmdb_movies_large.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✅ Data saved to: {output_file}")
    
    # Print statistics
    print("\n" + "="*80)
    print("DATASET STATISTICS")
    print("="*80)
    print(f"Total movies: {len(df)}")
    print(f"Date range: {df['release_date'].min()} to {df['release_date'].max()}")
    print(f"Unique genres: {df['genre'].nunique()}")
    print(f"Unique directors: {df['director'].nunique()}")
    print(f"\nBudget statistics:")
    print(f"  Average: ${df['budget'].mean():,.0f}")
    print(f"  Median: ${df['budget'].median():,.0f}")
    print(f"  Max: ${df['budget'].max():,.0f}")
    print(f"\nRevenue statistics:")
    print(f"  Average: ${df['revenue'].mean():,.0f}")
    print(f"  Median: ${df['revenue'].median():,.0f}")
    print(f"  Max: ${df['revenue'].max():,.0f}")
    print(f"\nFirst week income statistics:")
    print(f"  Average: ${df['first_week'].mean():,.0f}")
    print(f"  Median: ${df['first_week'].median():,.0f}")
    print(f"  Max: ${df['first_week'].max():,.0f}")
    print("\n" + "="*80)
    
    # Show sample
    print("\nSample of collected movies:")
    print(df[['movie_title', 'release_date', 'budget', 'revenue', 'imdb_rating']].head(10))
    
    return df


if __name__ == "__main__":
    df = main()
