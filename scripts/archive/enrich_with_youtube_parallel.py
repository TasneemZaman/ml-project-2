"""
Enrich movie dataset with real YouTube trailer statistics using parallel workers.
Much faster with 10 concurrent workers!
"""
import pandas as pd
from youtube_collector import get_best_trailer
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def process_movie_youtube(row):
    """Process a single movie to get YouTube data."""
    idx = row.name
    title = row['title']
    year = int(row['release_date'][:4]) if pd.notna(row['release_date']) and len(str(row['release_date'])) >= 4 else None
    
    trailer = get_best_trailer(title, year)
    
    result = {
        'idx': idx,
        'youtube_trailer_url': None,
        'youtube_views': None,
        'youtube_likes': None,
        'youtube_comments': None
    }
    
    if trailer:
        result['youtube_trailer_url'] = trailer['url']
        result['youtube_views'] = trailer['views']
        result['youtube_likes'] = trailer['likes']
        result['youtube_comments'] = trailer['comments']
    
    return result

def enrich_with_youtube_parallel(input_csv='data/raw/movies_with_youtube.csv', 
                                  output_csv='data/raw/movies_with_youtube.csv',
                                  workers=10,
                                  batch_size=500):
    """Add YouTube trailer data to movie dataset using parallel processing."""
    
    print("Loading dataset...")
    df = pd.read_csv(input_csv)
    
    # Check if already has YouTube columns
    youtube_cols = ['youtube_trailer_url', 'youtube_views', 'youtube_likes', 'youtube_comments']
    
    if not all(col in df.columns for col in youtube_cols):
        # Add new columns
        for col in youtube_cols:
            df[col] = None
    
    # Find movies without YouTube data
    needs_youtube = df['youtube_trailer_url'].isna()
    rows_to_process = df[needs_youtube]
    
    print(f"Total movies: {len(df)}")
    print(f"Already have YouTube data: {(~needs_youtube).sum()}")
    print(f"Need to process: {len(rows_to_process)}")
    
    if len(rows_to_process) == 0:
        print("✅ All movies already have YouTube data!")
        return
    
    print(f"\n🚀 Using {workers} parallel workers")
    print(f"Estimated time: {len(rows_to_process) / (workers * 10) / 60:.1f} minutes")
    print("Starting YouTube enrichment...\n")
    
    # Process in batches to save progress
    total_processed = 0
    
    for batch_num in range(0, len(rows_to_process), batch_size):
        batch = rows_to_process.iloc[batch_num:batch_num + batch_size]
        batch_number = (batch_num // batch_size) + 1
        total_batches = (len(rows_to_process) + batch_size - 1) // batch_size
        
        print(f"--- Batch {batch_number}/{total_batches} ({len(batch)} movies) ---")
        
        results = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all tasks
            futures = {executor.submit(process_movie_youtube, row): row for _, row in batch.iterrows()}
            
            # Collect results with progress bar
            for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching YouTube data"):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    row = futures[future]
                    print(f"Error processing {row['title']}: {e}")
                    results.append({
                        'idx': row.name,
                        'youtube_trailer_url': None,
                        'youtube_views': None,
                        'youtube_likes': None,
                        'youtube_comments': None
                    })
        
        # Update dataframe with results
        for result in results:
            idx = result['idx']
            df.at[idx, 'youtube_trailer_url'] = result['youtube_trailer_url']
            df.at[idx, 'youtube_views'] = result['youtube_views']
            df.at[idx, 'youtube_likes'] = result['youtube_likes']
            df.at[idx, 'youtube_comments'] = result['youtube_comments']
        
        total_processed += len(batch)
        
        # Save after each batch
        df.to_csv(output_csv, index=False)
        completed = df['youtube_trailer_url'].notna().sum()
        print(f"✓ Batch saved. Total with YouTube data: {completed}/{len(df)} ({completed/len(df)*100:.1f}%)")
        print(f"Progress: {total_processed}/{len(rows_to_process)} movies processed\n")
    
    print("=" * 100)
    print("YOUTUBE ENRICHMENT COMPLETE!")
    print("=" * 100)
    print(f"Total movies: {len(df)}")
    print(f"With YouTube data: {df['youtube_trailer_url'].notna().sum()} ({df['youtube_trailer_url'].notna().sum()/len(df)*100:.1f}%)")
    print(f"Saved to: {output_csv}")
    
    # Show statistics
    if df['youtube_views'].notna().sum() > 0:
        print(f"\n📊 YOUTUBE DATA STATISTICS:")
        print(f"   Average views: {df['youtube_views'].mean():,.0f}")
        print(f"   Median views: {df['youtube_views'].median():,.0f}")
        print(f"   Max views: {df['youtube_views'].max():,.0f}")
        print(f"   Average likes: {df['youtube_likes'].mean():,.0f}")
        print(f"   Average comments: {df['youtube_comments'].mean():,.0f}")
        
        print(f"\n🏆 TOP 10 MOST VIEWED TRAILERS:")
        top10 = df.nlargest(10, 'youtube_views')[['title', 'release_date', 'youtube_views', 'youtube_likes']]
        for _, movie in top10.iterrows():
            if pd.notna(movie['youtube_views']):
                year = movie['release_date'][:4] if pd.notna(movie['release_date']) else 'N/A'
                print(f"   {movie['title']} ({year}): {movie['youtube_views']:,.0f} views")

if __name__ == '__main__':
    enrich_with_youtube_parallel()
