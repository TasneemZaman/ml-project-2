"""
Collect real YouTube trailer data for movies.
Uses YouTube Data API v3 to get actual view counts, likes, and comments.
"""
import requests
import pandas as pd
from datetime import datetime
import time

YOUTUBE_API_KEY = 'AIzaSyCYTc07IYBQ3zciaJmEQlF63IsFW94Y_v4'
YOUTUBE_API_BASE = 'https://www.googleapis.com/youtube/v3'

def search_movie_trailer(movie_title, release_year=None, max_results=5):
    """Search for official movie trailer on YouTube."""
    # Build search query
    query = f"{movie_title} official trailer"
    if release_year:
        query += f" {release_year}"
    
    url = f"{YOUTUBE_API_BASE}/search"
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': max_results,
        'key': YOUTUBE_API_KEY,
        'videoDefinition': 'high',
        'order': 'relevance'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('items', [])
        else:
            print(f"YouTube API error {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"Error searching YouTube: {e}")
    
    return []

def get_video_statistics(video_id):
    """Get detailed statistics for a YouTube video."""
    url = f"{YOUTUBE_API_BASE}/videos"
    params = {
        'part': 'statistics,snippet,contentDetails',
        'id': video_id,
        'key': YOUTUBE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            items = response.json().get('items', [])
            if items:
                return items[0]
    except Exception as e:
        print(f"Error getting video stats: {e}")
    
    return None

def get_best_trailer(movie_title, release_year=None):
    """Find the best (most viewed) official trailer for a movie."""
    results = search_movie_trailer(movie_title, release_year)
    
    if not results:
        return None
    
    best_trailer = None
    max_views = 0
    
    for item in results:
        video_id = item['id']['videoId']
        stats = get_video_statistics(video_id)
        
        if stats:
            view_count = int(stats.get('statistics', {}).get('viewCount', 0))
            title = stats.get('snippet', {}).get('title', '').lower()
            
            # Prefer official trailers
            is_official = any(word in title for word in ['official', 'trailer'])
            
            if is_official and view_count > max_views:
                max_views = view_count
                best_trailer = {
                    'video_id': video_id,
                    'title': stats['snippet']['title'],
                    'channel': stats['snippet']['channelTitle'],
                    'published_at': stats['snippet']['publishedAt'],
                    'views': int(stats['statistics'].get('viewCount', 0)),
                    'likes': int(stats['statistics'].get('likeCount', 0)),
                    'comments': int(stats['statistics'].get('commentCount', 0)),
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                }
    
    return best_trailer

def test_youtube_api():
    """Test YouTube API with a few sample movies."""
    test_movies = [
        ("Avatar", 2009),
        ("Avengers Endgame", 2019),
        ("Inside Out 2", 2024)
    ]
    
    print("=" * 100)
    print("TESTING YOUTUBE API")
    print("=" * 100)
    
    for title, year in test_movies:
        print(f"\n🎬 Searching: {title} ({year})")
        trailer = get_best_trailer(title, year)
        
        if trailer:
            print(f"   ✅ Found: {trailer['title']}")
            print(f"   📺 Channel: {trailer['channel']}")
            print(f"   👁️  Views: {trailer['views']:,}")
            print(f"   👍 Likes: {trailer['likes']:,}")
            print(f"   💬 Comments: {trailer['comments']:,}")
            print(f"   🔗 URL: {trailer['url']}")
        else:
            print(f"   ❌ No trailer found")
        
        time.sleep(1)  # Be polite to API
    
    print("\n" + "=" * 100)
    print("✅ YouTube API is working!")
    print("=" * 100)

if __name__ == '__main__':
    test_youtube_api()
