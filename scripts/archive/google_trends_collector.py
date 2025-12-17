"""
Collect real Google Trends data for movies.
Shows search interest over time (no API key required).
"""
from pytrends.request import TrendReq
import pandas as pd
import time
from datetime import datetime, timedelta

def get_movie_trends(movie_title, release_date):
    """
    Get Google Trends data for a movie around its release date.
    Returns average search interest score (0-100).
    """
    try:
        # Initialize pytrends
        pytrends = TrendReq(hl='en-US', tz=360)
        
        # Parse release date
        release = pd.to_datetime(release_date)
        
        # Get trends for 3 months around release (1 month before, 2 months after)
        start_date = (release - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = (release + timedelta(days=60)).strftime('%Y-%m-%d')
        
        # Build timeframe
        timeframe = f'{start_date} {end_date}'
        
        # Search for movie
        pytrends.build_payload([movie_title], timeframe=timeframe, geo='US')
        
        # Get interest over time
        data = pytrends.interest_over_time()
        
        if not data.empty and movie_title in data.columns:
            # Return average search interest
            avg_interest = data[movie_title].mean()
            max_interest = data[movie_title].max()
            return {
                'trends_avg_interest': int(avg_interest),
                'trends_peak_interest': int(max_interest),
                'trends_timeframe': timeframe
            }
    
    except Exception as e:
        # Common issues: too many requests (429), movie not found, rate limiting
        error_msg = str(e)
        if '429' in error_msg or 'TooManyRequests' in error_msg:
            print(f"⚠️  Rate limited by Google Trends for '{movie_title}'")
        elif 'timeout' in error_msg.lower():
            print(f"⚠️  Timeout for '{movie_title}'")
        else:
            print(f"❌ Error for '{movie_title}': {type(e).__name__}")
    
    return {'trends_avg_interest': None, 'trends_peak_interest': None, 'trends_timeframe': None}

def test_google_trends():
    """Test Google Trends with sample movies."""
    test_movies = [
        ("Avatar", "2009-12-18"),
        ("Avengers Endgame", "2019-04-26"),
        ("Inside Out 2", "2024-06-14")
    ]
    
    print("=" * 100)
    print("TESTING GOOGLE TRENDS")
    print("=" * 100)
    print("⚠️  Note: Google Trends rate limits apply. This may be slow.\n")
    
    for title, date in test_movies:
        print(f"🔍 Searching trends for: {title} ({date})")
        trends = get_movie_trends(title, date)
        
        if trends['trends_avg_interest']:
            print(f"   ✅ Average interest: {trends['trends_avg_interest']}/100")
            print(f"   📈 Peak interest: {trends['trends_peak_interest']}/100")
            print(f"   📅 Timeframe: {trends['trends_timeframe']}")
        else:
            print(f"   ❌ No trends data available")
        
        print()
        time.sleep(5)  # Important: avoid rate limiting
    
    print("=" * 100)
    print("✅ Google Trends test complete!")
    print("=" * 100)
    print("\n⚠️  IMPORTANT NOTES:")
    print("   - Google Trends has strict rate limits")
    print("   - For 4,901 movies, this would take ~7 hours (5 sec per movie)")
    print("   - Consider running overnight or in smaller batches")
    print("   - Alternative: Use YouTube data as primary engagement metric")

if __name__ == '__main__':
    test_google_trends()
