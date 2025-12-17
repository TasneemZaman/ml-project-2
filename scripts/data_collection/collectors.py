"""
Consolidated Data Collectors
All data collection logic in one place: TMDB, YouTube, Box Office
Note: Google Trends removed - too unreliable. Use YouTube views instead.
"""
import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from config import TMDB_API_KEY

# Try to import YOUTUBE_API_KEYS, use default if not available
try:
    from config import YOUTUBE_API_KEYS
except ImportError:
    YOUTUBE_API_KEYS = [os.getenv('YOUTUBE_API_KEY', '')]

# ============================================================================
# TMDB COLLECTOR
# ============================================================================

class TMDBCollector:
    """Collect movie data from The Movie Database (TMDB)."""
    
    def __init__(self, api_key=TMDB_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
    
    def get_popular_movies(self, min_year=2000, max_year=2024, min_vote_count=100, total_movies=5000):
        """
        Collect popular movies from TMDB.
        
        Args:
            min_year: Minimum release year
            max_year: Maximum release year
            min_vote_count: Minimum number of votes
            total_movies: Target number of movies to collect
        
        Returns:
            DataFrame with movie data
        """
        movies = []
        page = 1
        
        print(f"Collecting {total_movies} movies from TMDB...")
        print(f"Criteria: {min_year}-{max_year}, min {min_vote_count} votes\n")
        
        while len(movies) < total_movies:
            try:
                url = f"{self.base_url}/discover/movie"
                params = {
                    'api_key': self.api_key,
                    'language': 'en-US',
                    'sort_by': 'popularity.desc',
                    'page': page,
                    'vote_count.gte': min_vote_count,
                    'primary_release_date.gte': f'{min_year}-01-01',
                    'primary_release_date.lte': f'{max_year}-12-31'
                }
                
                response = requests.get(url, params=params)
                data = response.json()
                
                if 'results' not in data or not data['results']:
                    print(f"No more results at page {page}")
                    break
                
                for movie in data['results']:
                    if len(movies) >= total_movies:
                        break
                    
                    movies.append({
                        'tmdb_id': movie['id'],
                        'title': movie['title'],
                        'release_date': movie.get('release_date', ''),
                        'popularity': movie.get('popularity', 0),
                        'vote_average': movie.get('vote_average', 0),
                        'vote_count': movie.get('vote_count', 0),
                        'overview': movie.get('overview', ''),
                        'original_language': movie.get('original_language', '')
                    })
                
                print(f"Page {page}: Collected {len(movies)}/{total_movies} movies", end='\r')
                page += 1
                time.sleep(0.25)  # Rate limiting
                
            except Exception as e:
                print(f"\nError on page {page}: {e}")
                time.sleep(5)
                continue
        
        print(f"\n✅ Collected {len(movies)} movies from TMDB")
        return pd.DataFrame(movies)
    
    def get_movie_details(self, tmdb_id):
        """Get detailed information for a specific movie."""
        try:
            url = f"{self.base_url}/movie/{tmdb_id}"
            params = {'api_key': self.api_key, 'language': 'en-US'}
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching details for TMDB ID {tmdb_id}: {e}")
        
        return None


# ============================================================================
# YOUTUBE COLLECTOR
# ============================================================================

class YouTubeCollector:
    """Collect YouTube statistics for movies."""
    
    def __init__(self, api_keys=YOUTUBE_API_KEYS):
        self.api_keys = api_keys if isinstance(api_keys, list) else [api_keys]
        self.current_key_index = 0
        self.youtube = self._build_service()
    
    def _build_service(self):
        """Build YouTube API service."""
        return build('youtube', 'v3', developerKey=self.api_keys[self.current_key_index])
    
    def _rotate_key(self):
        """Rotate to next API key when quota exceeded."""
        if len(self.api_keys) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            self.youtube = self._build_service()
            print(f"🔄 Rotated to API key {self.current_key_index + 1}")
            return True
        return False
    
    def search_movie_trailer(self, movie_title, release_year):
        """Search for official movie trailer on YouTube."""
        try:
            search_query = f"{movie_title} {release_year} official trailer"
            
            request = self.youtube.search().list(
                part='snippet',
                q=search_query,
                type='video',
                maxResults=5,
                videoDuration='medium',
                relevanceLanguage='en'
            )
            
            response = request.execute()
            
            # Find official trailer
            for item in response.get('items', []):
                title = item['snippet']['title'].lower()
                if 'trailer' in title and 'official' in title:
                    return item['id']['videoId']
            
            # If no official trailer, return first result
            if response.get('items'):
                return response['items'][0]['id']['videoId']
            
        except Exception as e:
            error_msg = str(e)
            if 'quotaExceeded' in error_msg:
                if self._rotate_key():
                    return self.search_movie_trailer(movie_title, release_year)
                print("⚠️  All YouTube API keys exhausted")
            else:
                print(f"Error searching for {movie_title}: {e}")
        
        return None
    
    def get_video_stats(self, video_id):
        """Get statistics for a YouTube video."""
        try:
            request = self.youtube.videos().list(
                part='statistics',
                id=video_id
            )
            
            response = request.execute()
            
            if response.get('items'):
                stats = response['items'][0]['statistics']
                return {
                    'youtube_video_id': video_id,
                    'youtube_views': int(stats.get('viewCount', 0)),
                    'youtube_likes': int(stats.get('likeCount', 0)),
                    'youtube_comments': int(stats.get('commentCount', 0))
                }
        
        except Exception as e:
            error_msg = str(e)
            if 'quotaExceeded' in error_msg:
                if self._rotate_key():
                    return self.get_video_stats(video_id)
            print(f"Error getting stats for video {video_id}: {e}")
        
        return {
            'youtube_video_id': None,
            'youtube_views': None,
            'youtube_likes': None,
            'youtube_comments': None
        }
    
    def get_movie_youtube_data(self, movie_title, release_date):
        """Get YouTube data for a movie (trailer stats)."""
        try:
            release_year = pd.to_datetime(release_date).year
            video_id = self.search_movie_trailer(movie_title, release_year)
            
            if video_id:
                return self.get_video_stats(video_id)
        
        except Exception as e:
            print(f"Error processing {movie_title}: {e}")
        
        return {
            'youtube_video_id': None,
            'youtube_views': None,
            'youtube_likes': None,
            'youtube_comments': None
        }


# ============================================================================
# BOX OFFICE MOJO COLLECTOR
# ============================================================================

class BoxOfficeMojoCollector:
    """Scrape box office data from Box Office Mojo."""
    
    def __init__(self):
        self.base_url = "https://www.boxofficemojo.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def search_movie(self, movie_title, release_year):
        """Search for a movie on Box Office Mojo."""
        try:
            search_url = f"{self.base_url}/search/"
            params = {'q': f"{movie_title} {release_year}"}
            
            response = requests.get(search_url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find first movie result link
                results = soup.find_all('a', href=True)
                for link in results:
                    href = link['href']
                    if '/release/' in href:
                        return self.base_url + href
            
            time.sleep(2)  # Rate limiting
        
        except Exception as e:
            print(f"Error searching BOM for {movie_title}: {e}")
        
        return None
    
    def get_box_office_data(self, movie_url):
        """Scrape box office data from movie page."""
        try:
            response = requests.get(movie_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                data = {
                    'domestic_gross': None,
                    'international_gross': None,
                    'worldwide_gross': None,
                    'opening_weekend': None
                }
                
                # Parse box office figures (simplified - actual parsing is more complex)
                money_divs = soup.find_all('span', class_='money')
                if len(money_divs) >= 1:
                    domestic_text = money_divs[0].text.strip()
                    data['domestic_gross'] = self._parse_money(domestic_text)
                
                return data
            
            time.sleep(2)  # Rate limiting
        
        except Exception as e:
            print(f"Error scraping {movie_url}: {e}")
        
        return None
    
    def _parse_money(self, money_str):
        """Convert money string to integer."""
        try:
            money_str = money_str.replace('$', '').replace(',', '')
            if 'M' in money_str:
                return int(float(money_str.replace('M', '')) * 1_000_000)
            elif 'B' in money_str:
                return int(float(money_str.replace('B', '')) * 1_000_000_000)
            elif 'K' in money_str:
                return int(float(money_str.replace('K', '')) * 1_000)
            return int(float(money_str))
        except:
            return None

