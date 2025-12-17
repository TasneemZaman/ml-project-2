"""
Test script to verify TMDB API connection and fetch real movie data
"""

from data_collection import DataCollector
import pandas as pd

def test_tmdb_connection():
    """Test TMDB API connection"""
    print("="*70)
    print("TESTING TMDB API CONNECTION")
    print("="*70)
    
    collector = DataCollector()
    
    # Test 1: Search for a movie
    print("\n1. Testing movie search...")
    avatar = collector.search_tmdb_movie("Avatar", year=2009)
    if avatar:
        print(f"   ✓ Found: {avatar.get('title')} ({avatar.get('release_date')})")
        print(f"   Rating: {avatar.get('vote_average')}/10")
        print(f"   Popularity: {avatar.get('popularity')}")
    else:
        print("   ✗ Search failed")
    
    # Test 2: Get movie details
    print("\n2. Testing movie details fetch...")
    if avatar:
        movie_id = avatar.get('id')
        details = collector.fetch_tmdb_movie(movie_id)
        if details:
            print(f"   ✓ Retrieved details for: {details.get('title')}")
            print(f"   Budget: ${details.get('budget', 0):,}")
            print(f"   Revenue: ${details.get('revenue', 0):,}")
            print(f"   Runtime: {details.get('runtime')} minutes")
        else:
            print("   ✗ Details fetch failed")
    
    # Test 3: Get movie credits
    print("\n3. Testing credits fetch...")
    if avatar:
        credits = collector.get_movie_credits(movie_id)
        if credits and 'crew' in credits:
            directors = [c['name'] for c in credits['crew'] if c['job'] == 'Director']
            print(f"   ✓ Director(s): {', '.join(directors)}")
        else:
            print("   ✗ Credits fetch failed")
    
    # Test 4: Get popular movies
    print("\n4. Testing popular movies fetch...")
    popular = collector.get_popular_movies(page=1)
    if popular:
        print(f"   ✓ Retrieved {len(popular)} popular movies")
        print(f"   Top 3: {', '.join([m['title'] for m in popular[:3]])}")
    else:
        print("   ✗ Popular movies fetch failed")
    
    # Test 5: Collect full dataset
    print("\n5. Testing full dataset collection...")
    print("   (This will fetch multiple movies - may take a minute)")
    try:
        df = collector.collect_historical_boxoffice_data(use_real_data=True)
        print(f"\n   ✓ Successfully collected {len(df)} movies!")
        print(f"\n   Dataset preview:")
        print(df[['movie_title', 'budget', 'first_week', 'imdb_rating']].head())
        
        # Save to CSV
        output_path = "data/raw/tmdb_movies.csv"
        df.to_csv(output_path, index=False)
        print(f"\n   ✓ Saved to: {output_path}")
        
    except Exception as e:
        print(f"   ✗ Dataset collection failed: {e}")
    
    print("\n" + "="*70)
    print("TMDB API TEST COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    test_tmdb_connection()
