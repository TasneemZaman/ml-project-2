"""
Collect movies from TMDB API (1990-2024) with clean data structure.
Target: ~200 movies per year based on popularity and ratings.
"""
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time

TMDB_API_KEY = 'd429e3e7a57fe68708d1380b99dbdf43'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

def fetch_movies_for_year_page(year, page, session):
    """Fetch one page of movies for a given year."""
    url = f'{TMDB_BASE_URL}/discover/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'primary_release_year': year,
        'page': page,
        'sort_by': 'popularity.desc',
        'vote_count.gte': 50  # At least 50 votes for quality
    }
    try:
        response = session.get(url, params=params, timeout=10)
        if response.ok:
            return response.json().get('results', [])
    except Exception as e:
        print(f"Error fetching year {year} page {page}: {e}")
    return []

def fetch_movie_details(movie_id, session):
    """Fetch detailed info for a movie including budget, revenue, and credits."""
    url = f'{TMDB_BASE_URL}/movie/{movie_id}'
    params = {
        'api_key': TMDB_API_KEY,
        'append_to_response': 'credits'
    }
    try:
        response = session.get(url, params=params, timeout=10)
        if response.ok:
            return response.json()
    except Exception as e:
        print(f"Error fetching movie {movie_id}: {e}")
    return None

def extract_director(credits):
    """Extract director name from credits."""
    if credits and 'crew' in credits:
        for person in credits['crew']:
            if person.get('job') == 'Director':
                return person.get('name', 'Unknown')
    return 'Unknown'

def extract_top_cast(credits, limit=5):
    """Extract top cast members."""
    if credits and 'cast' in credits:
        cast_list = credits['cast'][:limit]
        return ', '.join([c.get('name', '') for c in cast_list])
    return ''

def process_movie(movie_basic, session):
    """Get full details for a movie and return clean data dict."""
    movie_id = movie_basic['id']
    details = fetch_movie_details(movie_id, session)
    
    if not details:
        return None
    
    # Extract data
    budget = details.get('budget', 0)
    revenue = details.get('revenue', 0)
    
    # Only include movies with box office data
    if budget == 0 and revenue == 0:
        return None
    
    # Extract credits
    credits = details.get('credits', {})
    director = extract_director(credits)
    cast = extract_top_cast(credits, limit=5)
    
    # Extract genres
    genres = ', '.join([g['name'] for g in details.get('genres', [])])
    
    # Extract production companies (top 3)
    companies = [c['name'] for c in details.get('production_companies', [])[:3]]
    production_companies = ', '.join(companies) if companies else 'Unknown'
    
    # Extract production countries
    countries = [c['name'] for c in details.get('production_countries', [])]
    production_countries = ', '.join(countries) if countries else 'Unknown'
    
    return {
        'tmdb_id': details.get('id'),
        'imdb_id': details.get('imdb_id', ''),
        'title': details.get('title', ''),
        'release_date': details.get('release_date', ''),
        'runtime': details.get('runtime', 0),
        'budget': budget,
        'revenue': revenue,
        'genres': genres,
        'director': director,
        'cast': cast,
        'production_companies': production_companies,
        'production_countries': production_countries,
        'original_language': details.get('original_language', ''),
        'vote_average': details.get('vote_average', 0),
        'vote_count': details.get('vote_count', 0),
        'popularity': details.get('popularity', 0)
    }

def main():
    print("=" * 80)
    print("Collecting movies from TMDB (1990-2024)")
    print("Target: ~200 movies per year based on popularity & ratings")
    print("=" * 80)
    
    # 1990-2024 = 35 years, 10 pages per year = ~7,000 movies discovered
    years = range(1990, 2025)
    pages_per_year = 10  # 20 movies per page = 200 per year
    batch_size = 500  # Save every 500 movies
    
    session = requests.Session()
    
    # Phase 1: Discover movies
    print("\nPhase 1: Discovering movies...")
    all_movies = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for year in years:
            for page in range(1, pages_per_year + 1):
                futures.append(executor.submit(fetch_movies_for_year_page, year, page, session))
        
        completed = 0
        for future in as_completed(futures):
            movies = future.result()
            all_movies.extend(movies)
            completed += 1
            if completed % 50 == 0:
                print(f"  Progress: {completed}/{len(futures)} pages, {len(all_movies)} movies discovered")
    
    print(f"\n✓ Discovered {len(all_movies)} movies")
    
    # Deduplicate by movie_id
    unique_movies = list({m['id']: m for m in all_movies}.values())
    print(f"✓ {len(unique_movies)} unique movies after deduplication")
    
    # Phase 2: Fetch detailed info in batches
    print(f"\nPhase 2: Fetching movie details in {batch_size}-movie batches...")
    all_movie_data = []
    output_file = 'data/raw/tmdb_movies_clean.csv'
    
    for batch_num in range(0, len(unique_movies), batch_size):
        batch = unique_movies[batch_num:batch_num + batch_size]
        batch_number = (batch_num // batch_size) + 1
        print(f"\n--- Batch {batch_number} ({len(batch)} movies) ---")
        
        movie_data = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_movie, movie, session): movie for movie in batch}
            
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                if result:
                    movie_data.append(result)
                completed += 1
                if completed % 100 == 0:
                    print(f"  Progress: {completed}/{len(batch)} processed, {len(movie_data)} valid")
        
        print(f"✓ Batch {batch_number}: {len(movie_data)} valid movies")
        
        # Add to cumulative data
        all_movie_data.extend(movie_data)
        
        # Save cumulative results
        df = pd.DataFrame(all_movie_data)
        df = df.sort_values('popularity', ascending=False).reset_index(drop=True)
        df.to_csv(output_file, index=False)
        
        print(f"✓ Saved {len(df)} total movies to {output_file}")
    
    print("\n" + "=" * 80)
    print("COLLECTION COMPLETE!")
    print("=" * 80)
    print(f"Total movies: {len(df)}")
    print(f"Date range: {df['release_date'].min()} to {df['release_date'].max()}")
    print(f"Average movies per year: {len(df) / 35:.0f}")
    print(f"\nBreakdown by year:")
    df['year'] = pd.to_datetime(df['release_date']).dt.year
    year_counts = df['year'].value_counts().sort_index()
    print(year_counts.to_string())
    
    print(f"\n✅ Saved to: {output_file}")
    print(f"\nTop 10 most popular movies:")
    print(df[['title', 'release_date', 'popularity', 'vote_average', 'revenue']].head(10).to_string(index=False))

if __name__ == '__main__':
    main()
