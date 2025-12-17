"""
Append Movie Data - Add new movies to existing dataset
Collects data from 1990 onwards with T-7 trend data
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# TMDB API Configuration
TMDB_API_KEY = 'd429e3e7a57fe68708d1380b99dbdf43'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'


class MovieDataAppender:
    """Append new movies to existing dataset"""
    
    def __init__(self, existing_file: str = 'data/raw/imdb_movies_large.csv'):
        self.api_key = TMDB_API_KEY
        self.base_url = TMDB_BASE_URL
        self.existing_file = existing_file
        
        # Load existing data
        try:
            self.existing_df = pd.read_csv(existing_file)
            self.existing_titles = set(self.existing_df['movie_title'].str.lower())
            print(f"✓ Loaded {len(self.existing_df)} existing movies")
        except FileNotFoundError:
            self.existing_df = pd.DataFrame()
            self.existing_titles = set()
            print("No existing file found. Will create new dataset.")
    
    def get_movies_by_year(self, year: int, page: int = 1) -> Dict:
        """Get movies released in a specific year"""
        try:
            url = f"{self.base_url}/discover/movie"
            params = {
                'api_key': self.api_key,
                'primary_release_year': year,
                'sort_by': 'vote_count.desc',  # Sort by popularity
                'page': page,
                'vote_count.gte': 100,  # At least 100 votes for relevance
                'include_adult': 'false'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching movies for year {year}, page {page}: {e}")
            return {}
    
    def get_movie_details(self, movie_id: int) -> Dict:
        """Get detailed movie information"""
        try:
            url = f"{self.base_url}/movie/{movie_id}"
            params = {
                'api_key': self.api_key,
                'append_to_response': 'credits,keywords,release_dates'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching details for movie {movie_id}: {e}")
            return {}
    
    def generate_t7_trend_data(self, movie_data: Dict) -> Dict:
        """Generate synthetic T-7 trend data based on movie popularity and budget"""
        popularity = movie_data.get('popularity', 50)
        vote_average = movie_data.get('vote_average', 7.0)
        vote_count = movie_data.get('vote_count', 1000)
        budget = movie_data.get('budget', 50000000)
        
        # Base multiplier on movie metrics
        multiplier = min(popularity / 100, 3.0) * (vote_average / 10) * np.log1p(vote_count / 1000)
        
        # Generate T-7 metrics with some randomness
        t7_data = {
            'twitter_mentions': int(np.random.uniform(10000, 200000) * multiplier),
            'twitter_sentiment': np.random.uniform(0.5, 0.95),
            'google_trends_score': min(100, popularity * np.random.uniform(0.8, 1.2)),
            'youtube_trailer_views': int(np.random.uniform(1000000, 50000000) * multiplier),
            'youtube_trailer_likes': int(np.random.uniform(50000, 2000000) * multiplier),
            'instagram_hashtag_count': int(np.random.uniform(20000, 500000) * multiplier),
            'facebook_page_likes': int(np.random.uniform(100000, 5000000) * multiplier),
            'reddit_mentions': int(np.random.uniform(500, 12000) * multiplier),
            'search_volume_index': min(100, popularity * np.random.uniform(0.7, 1.1)),
            'ticket_presales': int(np.random.uniform(1000000, 20000000) * (budget / 100000000))
        }
        
        return t7_data
    
    def generate_box_office_data(self, movie_data: Dict) -> Dict:
        """Generate box office estimates based on revenue and popularity"""
        revenue = movie_data.get('revenue', 0)
        popularity = movie_data.get('popularity', 50)
        vote_average = movie_data.get('vote_average', 7.0)
        budget = movie_data.get('budget', 50000000)
        
        # Estimate box office metrics
        if revenue > 0:
            # First week typically 35-45% of total revenue
            first_week = revenue * np.random.uniform(0.35, 0.45)
            # Opening weekend typically 25-35% of first week
            opening_weekend = first_week * np.random.uniform(0.55, 0.75)
        else:
            # Estimate based on budget and popularity
            first_week = budget * np.random.uniform(0.3, 2.5) * (popularity / 50)
            opening_weekend = first_week * np.random.uniform(0.55, 0.75)
        
        # Theater count based on budget and popularity
        if budget > 100000000:
            num_theaters = np.random.randint(3500, 4500)
        elif budget > 50000000:
            num_theaters = np.random.randint(2500, 3800)
        else:
            num_theaters = np.random.randint(1500, 3000)
        
        average_per_theater = opening_weekend / num_theaters if num_theaters > 0 else 0
        total_gross = revenue if revenue > 0 else first_week * np.random.uniform(2.0, 3.5)
        
        return {
            'first_week': int(first_week),
            'opening_weekend': int(opening_weekend),
            'num_theaters': num_theaters,
            'average_per_theater': int(average_per_theater),
            'total_gross': int(total_gross)
        }
    
    def process_movie(self, movie_basic: Dict) -> Optional[Dict]:
        """Process a single movie and extract all features"""
        try:
            movie_id = movie_basic['id']
            title = movie_basic.get('title', 'Unknown')
            
            # Skip if already exists
            if title.lower() in self.existing_titles:
                return None
            
            # Get detailed info
            movie_details = self.get_movie_details(movie_id)
            if not movie_details:
                return None
            
            # Extract release date
            release_date = movie_details.get('release_date', '')
            if not release_date:
                return None
            
            # Parse release date for temporal features
            try:
                release_dt = datetime.strptime(release_date, '%Y-%m-%d')
                release_month = release_dt.month
                release_day_of_week = release_dt.weekday()
                is_summer = 1 if release_month in [6, 7, 8] else 0
                is_holiday_season = 1 if release_month in [11, 12] else 0
            except:
                release_month = 1
                release_day_of_week = 0
                is_summer = 0
                is_holiday_season = 0
            
            # Get director
            director = 'Unknown'
            credits = movie_details.get('credits', {})
            crew = credits.get('crew', [])
            for person in crew:
                if person.get('job') == 'Director':
                    director = person.get('name', 'Unknown')
                    break
            
            # Get genre
            genres = movie_details.get('genres', [])
            genre = '|'.join([g['name'] for g in genres[:3]]) if genres else 'Unknown'
            
            # Get studio (production company)
            production_companies = movie_details.get('production_companies', [])
            studio = production_companies[0]['name'] if production_companies else 'Unknown'
            
            # Basic movie data
            budget = movie_details.get('budget', 0)
            revenue = movie_details.get('revenue', 0)
            runtime = movie_details.get('runtime', 120)
            vote_average = movie_details.get('vote_average', 7.0)
            vote_count = movie_details.get('vote_count', 1000)
            popularity = movie_details.get('popularity', 50)
            original_language = movie_details.get('original_language', 'en')
            
            # Generate synthetic data
            metascore = int(vote_average * 10 * np.random.uniform(0.9, 1.1))
            num_reviews = int(vote_count * np.random.uniform(0.05, 0.15))
            num_critic_reviews = int(num_reviews * np.random.uniform(0.05, 0.12))
            competing_releases_same_week = np.random.randint(0, 4)
            
            # Franchise detection (simple heuristic)
            title_lower = title.lower()
            is_sequel = 1 if any(word in title_lower for word in ['2', '3', '4', 'ii', 'iii', 'iv', 'part', 'vol', 'chapter', 'returns', 'rises', 'awakens']) else 0
            franchise_previous_avg_gross = revenue * np.random.uniform(0.7, 1.3) if is_sequel else 0
            years_since_last_release = np.random.randint(2, 5) if is_sequel else 0
            
            # Generate T-7 trend data
            t7_data = self.generate_t7_trend_data(movie_details)
            
            # Generate box office data
            box_office = self.generate_box_office_data(movie_details)
            
            # Compile all data
            movie_row = {
                'movie_title': title,
                'release_date': release_date,
                'budget': budget,
                'revenue': revenue,
                'runtime': runtime,
                'imdb_rating': vote_average,
                'imdb_votes': vote_count,
                'popularity': popularity,
                'genre': genre,
                'director': director,
                'first_week': box_office['first_week'],
                'opening_weekend': box_office['opening_weekend'],
                'num_theaters': box_office['num_theaters'],
                'average_per_theater': box_office['average_per_theater'],
                'metascore': metascore,
                'num_reviews': num_reviews,
                'num_critic_reviews': num_critic_reviews,
                'twitter_mentions': t7_data['twitter_mentions'],
                'twitter_sentiment': t7_data['twitter_sentiment'],
                'google_trends_score': t7_data['google_trends_score'],
                'youtube_trailer_views': t7_data['youtube_trailer_views'],
                'youtube_trailer_likes': t7_data['youtube_trailer_likes'],
                'instagram_hashtag_count': t7_data['instagram_hashtag_count'],
                'facebook_page_likes': t7_data['facebook_page_likes'],
                'reddit_mentions': t7_data['reddit_mentions'],
                'search_volume_index': t7_data['search_volume_index'],
                'ticket_presales': t7_data['ticket_presales'],
                'release_month': release_month,
                'release_day_of_week': release_day_of_week,
                'is_holiday_season': is_holiday_season,
                'is_summer': is_summer,
                'competing_releases_same_week': competing_releases_same_week,
                'is_sequel': is_sequel,
                'franchise_previous_avg_gross': franchise_previous_avg_gross,
                'years_since_last_release': years_since_last_release,
                'studio': studio,
                'total_gross': box_office['total_gross'],
                'original_language': original_language
            }
            
            return movie_row
            
        except Exception as e:
            print(f"Error processing movie {movie_basic.get('title', 'Unknown')}: {e}")
            return None
    
    def collect_movies(self, start_year: int = 1990, end_year: int = 2024, 
                      movies_per_year: int = 50, max_pages: int = 3):
        """Collect movies from multiple years"""
        new_movies = []
        
        print(f"\n{'='*70}")
        print(f"COLLECTING MOVIES FROM {start_year} TO {end_year}")
        print(f"{'='*70}\n")
        
        for year in range(start_year, end_year + 1):
            print(f"\n📅 Processing year {year}...")
            year_count = 0
            
            for page in range(1, max_pages + 1):
                # Get movies for this year/page
                result = self.get_movies_by_year(year, page)
                movies = result.get('results', [])
                
                if not movies:
                    break
                
                for movie_basic in movies:
                    if year_count >= movies_per_year:
                        break
                    
                    # Process movie
                    movie_data = self.process_movie(movie_basic)
                    if movie_data:
                        new_movies.append(movie_data)
                        year_count += 1
                        print(f"  ✓ Added: {movie_data['movie_title']} ({len(new_movies)} total)")
                    
                    # Rate limiting
                    time.sleep(0.1)
                
                if year_count >= movies_per_year:
                    break
                
                # Rate limiting between pages
                time.sleep(0.5)
            
            print(f"  Year {year} complete: {year_count} movies added")
        
        return new_movies
    
    def append_and_save(self, new_movies: List[Dict], output_file: Optional[str] = None):
        """Append new movies to existing dataset and save"""
        if not new_movies:
            print("\n⚠️ No new movies to append!")
            return
        
        # Create DataFrame from new movies
        new_df = pd.DataFrame(new_movies)
        
        # Combine with existing data
        if not self.existing_df.empty:
            combined_df = pd.concat([self.existing_df, new_df], ignore_index=True)
        else:
            combined_df = new_df
        
        # Remove duplicates based on title
        combined_df = combined_df.drop_duplicates(subset=['movie_title'], keep='first')
        
        # Sort by release date
        combined_df = combined_df.sort_values('release_date', ascending=False)
        
        # Save to file
        output_file = output_file or self.existing_file
        combined_df.to_csv(output_file, index=False)
        
        print(f"\n{'='*70}")
        print(f"✅ DATASET UPDATED SUCCESSFULLY!")
        print(f"{'='*70}")
        print(f"\nPrevious count: {len(self.existing_df)}")
        print(f"New movies added: {len(new_movies)}")
        print(f"Total movies: {len(combined_df)}")
        print(f"Saved to: {output_file}")
        print(f"\n{'='*70}\n")
        
        return combined_df


def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("MOVIE DATA COLLECTION & APPEND SCRIPT")
    print("="*70 + "\n")
    
    # Initialize collector
    collector = MovieDataAppender('data/raw/imdb_movies_large.csv')
    
    # Configuration
    START_YEAR = 1990
    END_YEAR = 2024
    MOVIES_PER_YEAR = 30  # Adjust based on how many you want
    MAX_PAGES = 2  # Pages to fetch per year
    
    print(f"Configuration:")
    print(f"  Start Year: {START_YEAR}")
    print(f"  End Year: {END_YEAR}")
    print(f"  Target per Year: {MOVIES_PER_YEAR}")
    print(f"  Max Pages per Year: {MAX_PAGES}")
    print(f"  Estimated new movies: ~{(END_YEAR - START_YEAR + 1) * MOVIES_PER_YEAR}")
    
    # Collect new movies
    print("\n⏳ Starting data collection...")
    new_movies = collector.collect_movies(
        start_year=START_YEAR,
        end_year=END_YEAR,
        movies_per_year=MOVIES_PER_YEAR,
        max_pages=MAX_PAGES
    )
    
    # Append and save
    if new_movies:
        final_df = collector.append_and_save(new_movies)
        
        # Show sample of new data
        print("\nSample of newly added movies:")
        print(final_df.head(10)[['movie_title', 'release_date', 'budget', 'first_week', 'imdb_rating']])
    else:
        print("\n⚠️ No new movies collected. Dataset unchanged.")


if __name__ == "__main__":
    main()
