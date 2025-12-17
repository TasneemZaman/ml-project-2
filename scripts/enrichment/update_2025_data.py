"""
Update dataset with 2025 movies up to December 12, 2025
Collects new movies from TMDB and enriches with Box Office + YouTube data
"""
import pandas as pd
import time
from collectors import TMDBCollector, BoxOfficeMojoCollector, YouTubeCollector
from datetime import datetime

def collect_2025_movies():
    """Collect movies released from Dec 25, 2024 to Dec 12, 2025"""
    
    print("=" * 80)
    print("COLLECTING 2025 MOVIES")
    print("=" * 80)
    
    # Initialize collectors
    tmdb = TMDBCollector()
    bom = BoxOfficeMojoCollector()
    youtube = YouTubeCollector()
    
    # Get movies from TMDB for 2025
    print("\n1. Fetching movies from TMDB (2025)...")
    movies = []
    page = 1
    
    while page <= 20:  # Limit to 20 pages (~400 movies)
        try:
            url = f"{tmdb.base_url}/discover/movie"
            params = {
                'api_key': tmdb.api_key,
                'language': 'en-US',
                'sort_by': 'release_date.desc',
                'page': page,
                'primary_release_date.gte': '2024-12-25',
                'primary_release_date.lte': '2025-12-12',
                'vote_count.gte': 10  # At least some votes
            }
            
            import requests
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'results' not in data or not data['results']:
                break
            
            for movie in data['results']:
                # Get detailed info
                details = tmdb.get_movie_details(movie['id'])
                if details:
                    movies.append(details)
            
            print(f"  Page {page}: {len(movies)} movies collected", end='\r')
            page += 1
            time.sleep(0.3)
            
        except Exception as e:
            print(f"\n  Error on page {page}: {e}")
            break
    
    print(f"\n  Collected {len(movies)} movies from TMDB")
    
    if len(movies) == 0:
        print("\nNo new movies found. Exiting.")
        return None
    
    df = pd.DataFrame(movies)
    
    # 2. Enrich with Box Office Mojo data
    print(f"\n2. Enriching with Box Office Mojo data...")
    print("   Note: This is slow (~3-5 seconds per movie)")
    
    bom_data = []
    for idx, row in df.iterrows():
        try:
            title = row['title']
            year = pd.to_datetime(row['release_date']).year
            
            # Search for movie on BOM
            movie_url = bom.search_movie(title, year)
            
            if movie_url:
                box_office = bom.get_box_office_data(movie_url)
                bom_data.append({
                    'bom_url': movie_url,
                    'bom_opening_weekend': box_office.get('opening_weekend') if box_office else None,
                    'bom_domestic_total': box_office.get('domestic_gross') if box_office else None,
                    'bom_worldwide_total': box_office.get('worldwide_gross') if box_office else None,
                    'bom_international_total': box_office.get('international_gross') if box_office else None
                })
            else:
                bom_data.append({
                    'bom_url': None,
                    'bom_opening_weekend': None,
                    'bom_domestic_total': None,
                    'bom_worldwide_total': None,
                    'bom_international_total': None
                })
            
            print(f"  {idx+1}/{len(df)}: {title[:30]:30s} - {'Found' if movie_url else 'Not found'}", end='\r')
            time.sleep(3)  # Rate limiting
            
        except Exception as e:
            print(f"\n  Error processing {title}: {e}")
            bom_data.append({
                'bom_url': None,
                'bom_opening_weekend': None,
                'bom_domestic_total': None,
                'bom_worldwide_total': None,
                'bom_international_total': None
            })
    
    df_bom = pd.DataFrame(bom_data)
    df = pd.concat([df, df_bom], axis=1)
    
    bom_found = df['bom_url'].notna().sum()
    print(f"\n  Box Office data found for {bom_found}/{len(df)} movies")
    
    # 3. Enrich with YouTube data
    print(f"\n3. Enriching with YouTube trailer stats...")
    
    youtube_data = []
    for idx, row in df.iterrows():
        try:
            title = row['title']
            release_date = row['release_date']
            
            yt_stats = youtube.get_movie_youtube_data(title, release_date)
            youtube_data.append(yt_stats)
            
            views = yt_stats.get('youtube_views')
            status = f"{views:,} views" if views else "Not found"
            print(f"  {idx+1}/{len(df)}: {title[:30]:30s} - {status}", end='\r')
            time.sleep(1)
            
        except Exception as e:
            print(f"\n  Error getting YouTube data for {title}: {e}")
            youtube_data.append({
                'youtube_trailer_url': None,
                'youtube_views': None,
                'youtube_likes': None,
                'youtube_comments': None
            })
    
    df_youtube = pd.DataFrame(youtube_data)
    df = pd.concat([df, df_youtube], axis=1)
    
    youtube_found = df['youtube_views'].notna().sum()
    print(f"\n  YouTube data found for {youtube_found}/{len(df)} movies")
    
    return df


def merge_with_existing(new_df, existing_path='data/raw/movies_with_youtube.csv'):
    """Merge new data with existing dataset"""
    
    print("\n" + "=" * 80)
    print("MERGING WITH EXISTING DATA")
    print("=" * 80)
    
    # Load existing data
    existing_df = pd.read_csv(existing_path)
    print(f"\nExisting dataset: {len(existing_df):,} movies")
    print(f"New dataset: {len(new_df):,} movies")
    
    # Remove duplicates based on tmdb_id
    combined = pd.concat([existing_df, new_df], ignore_index=True)
    combined = combined.drop_duplicates(subset=['tmdb_id'], keep='last')
    
    print(f"\nCombined dataset: {len(combined):,} movies")
    print(f"  New movies added: {len(combined) - len(existing_df):,}")
    
    # Sort by release date
    combined['release_date'] = pd.to_datetime(combined['release_date'])
    combined = combined.sort_values('release_date', ascending=False)
    
    # Save to new file (backup original)
    backup_path = existing_path.replace('.csv', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    existing_df.to_csv(backup_path, index=False)
    print(f"\n  Original backed up to: {backup_path}")
    
    combined.to_csv(existing_path, index=False)
    print(f"  Updated dataset saved to: {existing_path}")
    
    # Show summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total movies: {len(combined):,}")
    print(f"Date range: {combined['release_date'].min()} to {combined['release_date'].max()}")
    print(f"Movies with Box Office data: {combined['bom_opening_weekend'].notna().sum():,}")
    print(f"Movies with YouTube data: {combined['youtube_views'].notna().sum():,}")
    
    return combined


if __name__ == "__main__":
    # Collect new 2025 movies
    new_movies = collect_2025_movies()
    
    if new_movies is not None and len(new_movies) > 0:
        # Merge with existing data
        response = input("\nMerge with existing dataset? (y/n): ")
        if response.lower() == 'y':
            final_df = merge_with_existing(new_movies)
            print("\n✓ Data update complete!")
        else:
            # Save new movies separately
            output_path = f'data/raw/movies_2025_new_{datetime.now().strftime("%Y%m%d")}.csv'
            new_movies.to_csv(output_path, index=False)
            print(f"\n✓ New movies saved to: {output_path}")
    else:
        print("\nNo new data to merge.")
