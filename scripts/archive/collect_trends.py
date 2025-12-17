"""
Collect Google Trends data with limits and safety measures
Use this to add trends data to a limited number of movies
"""
import pandas as pd
import time
from tqdm import tqdm
from collectors import GoogleTrendsCollector

def collect_trends_limited(
    input_file='data/raw/movies_with_youtube.csv',
    output_file='data/raw/movies_with_trends.csv',
    max_movies=50,
    delay=5,
    start_from=0,
    auto_confirm=False
):
    """
    Collect Google Trends data with strict limits.
    
    Args:
        input_file: Input CSV file
        output_file: Output CSV file
        max_movies: Maximum number of movies to process (default: 50)
        delay: Seconds to wait between requests (minimum: 5, default: 5)
        start_from: Row index to start from (for resuming)
        auto_confirm: Skip confirmation prompt (default: False)
    """
    
    # Enforce minimum 5-second delay
    if delay < 5:
        print(f"⚠️  Delay must be at least 5 seconds. Setting to 5.")
        delay = 5
    
    print("\n" + "="*80)
    print("GOOGLE TRENDS COLLECTION (LIMITED)")
    print("="*80)
    print(f"⚠️  WARNING: Google Trends requires minimum 5-second delay!")
    print(f"    Processing only {max_movies} movies with {delay}s delay")
    print(f"    This will take approximately {max_movies * delay / 60:.1f} minutes")
    print("="*80 + "\n")
    
    # Load data
    print(f"Loading data from: {input_file}")
    df = pd.read_csv(input_file)
    print(f"Total movies in dataset: {len(df)}\n")
    
    # Add trends columns if they don't exist
    trends_cols = ['trends_avg_interest', 'trends_peak_interest', 'trends_timeframe']
    for col in trends_cols:
        if col not in df.columns:
            df[col] = None
    
    # Find movies that need trends data
    needs_trends = df['trends_avg_interest'].isna()
    available_movies = df[needs_trends].iloc[start_from:]
    
    print(f"Movies without trends data: {needs_trends.sum()}")
    print(f"Starting from row: {start_from}")
    print(f"Will process: {min(max_movies, len(available_movies))} movies\n")
    
    if len(available_movies) == 0:
        print("✅ All movies already have trends data!")
        return
    
    # Limit to max_movies
    movies_to_process = available_movies.head(max_movies)
    
    # Confirm before starting
    print("Sample movies to process:")
    for idx, row in movies_to_process.head(5).iterrows():
        print(f"  - {row['title']} ({row['release_date'][:4]})")
    
    print("\n" + "-"*80)
    
    if not auto_confirm:
        response = input(f"\nProceed with collecting trends for {len(movies_to_process)} movies? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    else:
        print(f"\nAuto-confirming: Proceeding with {len(movies_to_process)} movies...")
    
    print()
    
    # Initialize collector
    trends_collector = GoogleTrendsCollector()
    
    # Track stats
    successful = 0
    failed = 0
    rate_limited = 0
    
    # Process movies
    print("Starting collection...\n")
    for idx, row in tqdm(movies_to_process.iterrows(), total=len(movies_to_process), desc="Collecting trends"):
        try:
            # Get trends data
            trends_data = trends_collector.get_movie_trends(row['title'], row['release_date'])
            
            # Update dataframe
            for col, value in trends_data.items():
                df.at[idx, col] = value
            
            # Track success
            if trends_data['trends_avg_interest'] is not None:
                successful += 1
                tqdm.write(f"✅ {row['title']}: {trends_data['trends_avg_interest']}/100")
            else:
                failed += 1
                tqdm.write(f"❌ {row['title']}: No data available")
            
            # Save progress every 10 movies
            if (successful + failed) % 10 == 0:
                df.to_csv(output_file, index=False)
                tqdm.write(f"💾 Progress saved ({successful} successful, {failed} failed)")
            
            # Rate limiting delay (enforced by collector, but added here too for safety)
            time.sleep(delay)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user!")
            df.to_csv(output_file, index=False)
            print(f"Progress saved to: {output_file}")
            break
            
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg or 'TooManyRequests' in error_msg:
                rate_limited += 1
                tqdm.write(f"⚠️  Rate limited on {row['title']} - stopping collection")
                break
            else:
                failed += 1
                tqdm.write(f"❌ Error on {row['title']}: {type(e).__name__}")
    
    # Final save
    df.to_csv(output_file, index=False)
    
    # Summary
    print("\n" + "="*80)
    print("COLLECTION COMPLETE")
    print("="*80)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Rate limited: {rate_limited}")
    print(f"📊 Success rate: {successful/(successful+failed)*100:.1f}%")
    print(f"\n💾 Data saved to: {output_file}")
    print(f"📈 Total movies with trends: {df['trends_avg_interest'].notna().sum()}/{len(df)}")
    
    if rate_limited > 0:
        print("\n⚠️  Collection stopped due to rate limiting.")
        print("   Wait 1-2 hours before trying again.")
        print("   Consider using YouTube views or TMDB popularity instead.")
    
    print("="*80 + "\n")


def main():
    """Main entry point with options."""
    print("\n🔍 GOOGLE TRENDS DATA COLLECTION")
    print("\n⚠️  Minimum 5-second delay enforced between requests!")
    print("\nOptions:")
    print("1. Collect for 50 movies (recommended, ~4 minutes)")
    print("2. Collect for 100 movies (~8 minutes)")
    print("3. Collect for 200 movies (~17 minutes)")
    print("4. Custom amount")
    print("5. Resume from specific row")
    
    choice = input("\nEnter choice (1-5): ")
    
    if choice == '1':
        collect_trends_limited(max_movies=50, delay=5)
    elif choice == '2':
        collect_trends_limited(max_movies=100, delay=5)
    elif choice == '3':
        collect_trends_limited(max_movies=200, delay=5)
    elif choice == '4':
        max_movies = int(input("How many movies? (max 500): "))
        max_movies = min(max_movies, 500)
        delay = int(input("Delay between requests in seconds (minimum 5): "))
        delay = max(5, delay)  # Enforce minimum
        collect_trends_limited(max_movies=max_movies, delay=delay)
    elif choice == '5':
        start_from = int(input("Start from row number: "))
        max_movies = int(input("How many movies from that point? "))
        collect_trends_limited(max_movies=max_movies, delay=5, start_from=start_from)
    else:
        print("Invalid choice.")


if __name__ == '__main__':
    main()
