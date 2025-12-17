"""
Enrich movie dataset with real YouTube trailer statistics.
"""
import pandas as pd
from youtube_collector import get_best_trailer
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def fetch_trailer_for_movie(movie_data):
    """Helper function for parallel processing."""
    idx, title, release_date = movie_data
    year = int(release_date[:4]) if pd.notna(release_date) and len(str(release_date)) >= 4 else None
    
    trailer = get_best_trailer(title, year)
    
    result = {
        'idx': idx,
        'youtube_trailer_url': trailer['url'] if trailer else None,
        'youtube_views': trailer['views'] if trailer else None,
        'youtube_likes': trailer['likes'] if trailer else None,
        'youtube_comments': trailer['comments'] if trailer else None
    }
    
    time.sleep(0.3)  # Small delay to be polite
    return result

def enrich_with_youtube(input_csv='data/raw/tmdb_movies_with_bom.csv', 
                        output_csv='data/raw/movies_with_youtube.csv',
                        batch_size=500,
                        workers=10):
    """Add YouTube trailer data to movie dataset using parallel processing."""
    
    print("Loading dataset...")
    df = pd.read_csv(input_csv)
    
    # Check if already has YouTube columns
    youtube_cols = ['youtube_trailer_url', 'youtube_views', 'youtube_likes', 'youtube_comments']
    existing_data = all(col in df.columns for col in youtube_cols)
    
    if existing_data:
        # Find movies without YouTube data
        needs_youtube = df['youtube_trailer_url'].isna()
        print(f"Found {needs_youtube.sum()} movies without YouTube data")
        rows_to_process = df[needs_youtube]
    else:
        # Add new columns
        for col in youtube_cols:
            df[col] = None
        rows_to_process = df
        print(f"Processing all {len(df)} movies")
    
    if len(rows_to_process) == 0:
        print("All movies already have YouTube data!")
        return
    
    print(f"\nFetching YouTube data with {workers} concurrent workers...")
    print(f"Estimated time: {len(rows_to_process) * 0.3 / workers / 60:.1f} minutes")
    
    # Process in batches
    for batch_num in range(0, len(rows_to_process), batch_size):
        batch = rows_to_process.iloc[batch_num:batch_num + batch_size]
        batch_number = (batch_num // batch_size) + 1
        total_batches = (len(rows_to_process) + batch_size - 1) // batch_size
        
        print(f"\n--- Batch {batch_number}/{total_batches} ({len(batch)} movies) ---")
        
        # Prepare data for parallel processing
        movie_data = [(idx, row['title'], row['release_date']) for idx, row in batch.iterrows()]
        
        # Process in parallel
        results = {}
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(fetch_trailer_for_movie, data): data for data in movie_data}
            
            for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching trailers"):
                result = future.result()
                if result:
                    results[result['idx']] = result
        
        # Update dataframe
        for idx, data in results.items():
            df.at[idx, 'youtube_trailer_url'] = data['youtube_trailer_url']
            df.at[idx, 'youtube_views'] = data['youtube_views']
            df.at[idx, 'youtube_likes'] = data['youtube_likes']
            df.at[idx, 'youtube_comments'] = data['youtube_comments']
        
        # Save after each batch
        df.to_csv(output_csv, index=False)
        completed = df['youtube_trailer_url'].notna().sum()
        print(f"✓ Batch saved. Total with YouTube data: {completed}/{len(df)}")
    
    print("\n" + "=" * 100)
    print("YOUTUBE ENRICHMENT COMPLETE!")
    print("=" * 100)
    print(f"Total movies: {len(df)}")
    print(f"With YouTube data: {df['youtube_trailer_url'].notna().sum()} ({df['youtube_trailer_url'].notna().sum()/len(df)*100:.1f}%)")
    print(f"Saved to: {output_csv}")
    
    # Show statistics
    print(f"\n📊 YOUTUBE DATA STATISTICS:")
    if df['youtube_views'].notna().sum() > 0:
        print(f"   Average views: {df['youtube_views'].mean():,.0f}")
        print(f"   Average likes: {df['youtube_likes'].mean():,.0f}")
        print(f"   Average comments: {df['youtube_comments'].mean():,.0f}")
        
        print(f"\n🏆 TOP 10 MOST VIEWED TRAILERS:")
        top10 = df.nlargest(10, 'youtube_views')[['title', 'release_date', 'youtube_views', 'youtube_likes']]
        for _, movie in top10.iterrows():
            if pd.notna(movie['youtube_views']):
                print(f"   {movie['title']} ({movie['release_date'][:4]}): {movie['youtube_views']:,.0f} views")

if __name__ == '__main__':
    enrich_with_youtube()
