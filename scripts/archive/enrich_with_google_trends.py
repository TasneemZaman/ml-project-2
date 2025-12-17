"""
Enrich movie dataset with Google Trends data using parallel processing.
"""
import pandas as pd
from google_trends_collector import get_movie_trends
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def fetch_trends_for_movie(movie_data):
    """Helper function for parallel processing."""
    idx, title, release_date = movie_data
    
    trends = get_movie_trends(title, release_date)
    
    result = {
        'idx': idx,
        'trends_avg_interest': trends['trends_avg_interest'],
        'trends_peak_interest': trends['trends_peak_interest'],
        'trends_timeframe': trends['trends_timeframe']
    }
    
    time.sleep(2)  # Rate limiting for Google Trends
    return result

def enrich_with_google_trends(input_csv='data/raw/movies_with_youtube.csv', 
                               output_csv='data/raw/movies_complete.csv',
                               batch_size=500,
                               workers=10,
                               year_filter=None):
    """Add Google Trends data to movie dataset using parallel processing."""
    
    print("Loading dataset...")
    df = pd.read_csv(input_csv)
    
    # Check if already has trends columns
    trends_cols = ['trends_avg_interest', 'trends_peak_interest', 'trends_timeframe']
    existing_data = all(col in df.columns for col in trends_cols)
    
    if existing_data:
        # Find movies without trends data
        needs_trends = df['trends_avg_interest'].isna()
        rows_to_process = df[needs_trends]
        print(f"Found {needs_trends.sum()} movies without Trends data")
    else:
        # Add new columns
        for col in trends_cols:
            df[col] = None
        rows_to_process = df
        print(f"Processing all {len(df)} movies")
    
    # Optional: filter by year
    if year_filter:
        rows_to_process = rows_to_process[
            rows_to_process['release_date'].str[:4].astype(int) >= year_filter
        ]
        print(f"Filtered to {len(rows_to_process)} movies from {year_filter} onwards")
    
    if len(rows_to_process) == 0:
        print("All movies already have Trends data!")
        return
    
    print(f"\nFetching Google Trends data with {workers} concurrent workers...")
    print(f"Estimated time: {len(rows_to_process) * 2 / workers / 60:.1f} minutes")
    print("⚠️  Note: Google Trends may rate limit. This is normal.\n")
    
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
            futures = {executor.submit(fetch_trends_for_movie, data): data for data in movie_data}
            
            for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching trends"):
                try:
                    result = future.result()
                    if result:
                        results[result['idx']] = result
                except Exception as e:
                    print(f"Error: {e}")
        
        # Update dataframe
        for idx, data in results.items():
            df.at[idx, 'trends_avg_interest'] = data['trends_avg_interest']
            df.at[idx, 'trends_peak_interest'] = data['trends_peak_interest']
            df.at[idx, 'trends_timeframe'] = data['trends_timeframe']
        
        # Save after each batch
        df.to_csv(output_csv, index=False)
        completed = df['trends_avg_interest'].notna().sum()
        print(f"✓ Batch saved. Total with Trends data: {completed}/{len(df)}")
    
    print("\n" + "=" * 100)
    print("GOOGLE TRENDS ENRICHMENT COMPLETE!")
    print("=" * 100)
    print(f"Total movies: {len(df)}")
    print(f"With Trends data: {df['trends_avg_interest'].notna().sum()} ({df['trends_avg_interest'].notna().sum()/len(df)*100:.1f}%)")
    print(f"Saved to: {output_csv}")
    
    # Show statistics
    if df['trends_avg_interest'].notna().sum() > 0:
        print(f"\n📊 GOOGLE TRENDS STATISTICS:")
        print(f"   Average interest: {df['trends_avg_interest'].mean():.1f}/100")
        print(f"   Average peak: {df['trends_peak_interest'].mean():.1f}/100")
        
        print(f"\n🔥 TOP 10 HIGHEST TRENDING MOVIES:")
        top10 = df.nlargest(10, 'trends_peak_interest')[['title', 'release_date', 'trends_avg_interest', 'trends_peak_interest']]
        for _, movie in top10.iterrows():
            if pd.notna(movie['trends_peak_interest']):
                print(f"   {movie['title']} ({movie['release_date'][:4]}): Peak {movie['trends_peak_interest']:.0f}/100")

if __name__ == '__main__':
    import sys
    
    # Check if year filter provided
    year_filter = int(sys.argv[1]) if len(sys.argv) > 1 else None
    
    if year_filter:
        print(f"Running with year filter: {year_filter}+")
    
    enrich_with_google_trends(year_filter=year_filter)
