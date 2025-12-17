"""
Google Trends Collection - Multiple Workarounds
Choose the method that works best for you
"""
import pandas as pd
import time
from pytrends.request import TrendReq
from datetime import datetime, timedelta
import random

# ============================================================================
# WORKAROUND 1: Use Proxies (Most Effective)
# ============================================================================

class TrendsWithProxies:
    """Use rotating proxies to avoid rate limiting."""
    
    def __init__(self, proxies=None):
        """
        proxies: list of proxy URLs like ['http://proxy1:port', 'http://proxy2:port']
        """
        self.proxies = proxies or []
        self.current_proxy_index = 0
    
    def _get_next_proxy(self):
        """Rotate to next proxy."""
        if not self.proxies:
            return None
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return self.proxies[self.current_proxy_index]
    
    def collect_with_proxy_rotation(self, movies_df, max_movies=100):
        """Collect trends using proxy rotation."""
        results = []
        
        for idx, row in movies_df.head(max_movies).iterrows():
            proxy = self._get_next_proxy()
            
            try:
                # Initialize with proxy
                pytrends = TrendReq(
                    hl='en-US',
                    tz=360,
                    timeout=(10, 25),
                    proxies=[proxy] if proxy else None,
                    retries=2,
                    backoff_factor=0.1
                )
                
                # Get trends
                release = pd.to_datetime(row['release_date'])
                start_date = (release - timedelta(days=30)).strftime('%Y-%m-%d')
                end_date = (release + timedelta(days=60)).strftime('%Y-%m-%d')
                timeframe = f'{start_date} {end_date}'
                
                pytrends.build_payload([row['title']], timeframe=timeframe, geo='US')
                data = pytrends.interest_over_time()
                
                if not data.empty and row['title'] in data.columns:
                    results.append({
                        'title': row['title'],
                        'trends_avg': int(data[row['title']].mean()),
                        'trends_peak': int(data[row['title']].max())
                    })
                    print(f"✅ {row['title']}: {results[-1]['trends_avg']}/100")
                else:
                    print(f"❌ {row['title']}: No data")
                
                # Random delay 10-15 seconds
                time.sleep(random.uniform(10, 15))
                
            except Exception as e:
                print(f"⚠️  {row['title']}: {type(e).__name__}")
                time.sleep(20)  # Longer delay on error
        
        return pd.DataFrame(results)


# ============================================================================
# WORKAROUND 2: VPN + Long Delays (Manual but Reliable)
# ============================================================================

def collect_with_vpn_manual(input_file='data/raw/movies_with_youtube.csv',
                            output_file='data/raw/movies_with_trends.csv',
                            batch_size=10,
                            delay_between_movies=15,
                            delay_between_batches=300):
    """
    Collect in small batches with VPN changes.
    
    Instructions:
    1. Run this script
    2. It will collect 10 movies
    3. Then pause for 5 minutes
    4. During pause: manually change your VPN location
    5. Script continues with next batch
    
    Args:
        batch_size: Movies per batch (default: 10)
        delay_between_movies: Seconds between movies (default: 15)
        delay_between_batches: Seconds between batches for VPN change (default: 300 = 5 min)
    """
    
    print("\n" + "="*80)
    print("GOOGLE TRENDS - VPN ROTATION METHOD")
    print("="*80)
    print(f"Collecting in batches of {batch_size} movies")
    print(f"Delay: {delay_between_movies}s between movies, {delay_between_batches//60} min between batches")
    print("\n⚠️  INSTRUCTIONS:")
    print("   1. Start with VPN connected")
    print("   2. Script collects 10 movies (~2.5 minutes)")
    print("   3. Script pauses for 5 minutes")
    print("   4. During pause: Change VPN location")
    print("   5. Script resumes automatically")
    print("="*80 + "\n")
    
    df = pd.read_csv(input_file)
    
    # Add columns if needed
    if 'trends_avg_interest' not in df.columns:
        df['trends_avg_interest'] = None
        df['trends_peak_interest'] = None
    
    # Find movies without trends
    needs_trends = df['trends_avg_interest'].isna()
    movies_to_process = df[needs_trends]
    
    print(f"Movies needing trends: {len(movies_to_process)}\n")
    
    batch_num = 0
    total_successful = 0
    
    for start_idx in range(0, len(movies_to_process), batch_size):
        batch_num += 1
        batch = movies_to_process.iloc[start_idx:start_idx + batch_size]
        
        print(f"\n{'='*80}")
        print(f"BATCH {batch_num} - Processing {len(batch)} movies")
        print(f"{'='*80}\n")
        
        # Process batch
        pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25), retries=2)
        
        for idx, row in batch.iterrows():
            try:
                release = pd.to_datetime(row['release_date'])
                start_date = (release - timedelta(days=30)).strftime('%Y-%m-%d')
                end_date = (release + timedelta(days=60)).strftime('%Y-%m-%d')
                timeframe = f'{start_date} {end_date}'
                
                pytrends.build_payload([row['title']], timeframe=timeframe, geo='US')
                data = pytrends.interest_over_time()
                
                if not data.empty and row['title'] in data.columns:
                    avg_interest = int(data[row['title']].mean())
                    max_interest = int(data[row['title']].max())
                    
                    df.at[idx, 'trends_avg_interest'] = avg_interest
                    df.at[idx, 'trends_peak_interest'] = max_interest
                    
                    total_successful += 1
                    print(f"✅ {row['title']}: {avg_interest}/100")
                else:
                    print(f"❌ {row['title']}: No data")
                
                # Random delay with jitter
                delay = random.uniform(delay_between_movies, delay_between_movies + 5)
                time.sleep(delay)
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Stopped by user!")
                df.to_csv(output_file, index=False)
                return
            
            except Exception as e:
                error_msg = str(e)
                if '429' in error_msg:
                    print(f"⚠️  Rate limited on {row['title']}")
                else:
                    print(f"❌ Error on {row['title']}: {type(e).__name__}")
                time.sleep(30)
        
        # Save after each batch
        df.to_csv(output_file, index=False)
        print(f"\n💾 Batch {batch_num} complete. Saved progress.")
        print(f"   Total successful so far: {total_successful}")
        
        # Pause for VPN change if not last batch
        if start_idx + batch_size < len(movies_to_process):
            print(f"\n{'='*80}")
            print(f"⏸️  PAUSING FOR {delay_between_batches//60} MINUTES")
            print(f"{'='*80}")
            print(f"\n🔄 ACTION REQUIRED:")
            print(f"   1. Change your VPN to a different location")
            print(f"   2. Wait for script to resume automatically")
            print(f"   3. Next batch will start in {delay_between_batches//60} minutes\n")
            
            # Countdown
            for remaining in range(delay_between_batches, 0, -60):
                print(f"   Resuming in {remaining//60} minutes...", end='\r')
                time.sleep(60)
            
            print(f"\n   ▶️  Resuming collection...\n")
    
    print(f"\n{'='*80}")
    print("COLLECTION COMPLETE")
    print(f"{'='*80}")
    print(f"Total successful: {total_successful}/{len(movies_to_process)}")
    print(f"Success rate: {total_successful/len(movies_to_process)*100:.1f}%")
    print(f"Saved to: {output_file}")


# ============================================================================
# WORKAROUND 3: Spread Over Multiple Days (Most Reliable)
# ============================================================================

def collect_daily_quota(input_file='data/raw/movies_with_youtube.csv',
                       output_file='data/raw/movies_with_trends.csv',
                       daily_limit=50,
                       delay=15):
    """
    Collect a limited number per day to avoid blocking.
    
    Strategy:
    - Only collect 50 movies per day
    - Use longer delays (15+ seconds)
    - Track last collection date
    - Run once per day for multiple days
    
    For 4,901 movies: Would take ~100 days
    For realistic subset (500 movies): ~10 days
    """
    
    import os
    from datetime import date
    
    progress_file = 'collection_progress.txt'
    
    # Check if already collected today
    today = date.today().isoformat()
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            last_date = f.read().strip()
            if last_date == today:
                print(f"\n⚠️  Already collected trends today ({today})")
                print("   Come back tomorrow for next batch!")
                return
    
    print("\n" + "="*80)
    print("GOOGLE TRENDS - DAILY QUOTA METHOD")
    print("="*80)
    print(f"Today's quota: {daily_limit} movies")
    print(f"Delay: {delay} seconds between requests")
    print(f"Estimated time: {daily_limit * delay / 60:.0f} minutes")
    print("="*80 + "\n")
    
    df = pd.read_csv(input_file)
    
    # Add columns if needed
    if 'trends_avg_interest' not in df.columns:
        df['trends_avg_interest'] = None
        df['trends_peak_interest'] = None
    
    # Find movies without trends
    needs_trends = df['trends_avg_interest'].isna()
    movies_to_process = df[needs_trends].head(daily_limit)
    
    if len(movies_to_process) == 0:
        print("✅ All movies have trends data!")
        return
    
    print(f"Processing {len(movies_to_process)} movies today")
    print(f"Remaining after today: {needs_trends.sum() - len(movies_to_process)}\n")
    
    successful = 0
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
    
    for idx, row in movies_to_process.iterrows():
        try:
            release = pd.to_datetime(row['release_date'])
            start_date = (release - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = (release + timedelta(days=60)).strftime('%Y-%m-%d')
            timeframe = f'{start_date} {end_date}'
            
            pytrends.build_payload([row['title']], timeframe=timeframe, geo='US')
            data = pytrends.interest_over_time()
            
            if not data.empty and row['title'] in data.columns:
                avg_interest = int(data[row['title']].mean())
                max_interest = int(data[row['title']].max())
                
                df.at[idx, 'trends_avg_interest'] = avg_interest
                df.at[idx, 'trends_peak_interest'] = max_interest
                
                successful += 1
                print(f"✅ {row['title']}: {avg_interest}/100")
            else:
                print(f"❌ {row['title']}: No data")
            
            # Save every 10
            if successful % 10 == 0:
                df.to_csv(output_file, index=False)
            
            time.sleep(random.uniform(delay, delay + 5))
            
        except KeyboardInterrupt:
            print("\n\nStopped by user!")
            break
        
        except Exception as e:
            print(f"❌ {row['title']}: {type(e).__name__}")
            time.sleep(30)
    
    # Save final
    df.to_csv(output_file, index=False)
    
    # Record today's date
    with open(progress_file, 'w') as f:
        f.write(today)
    
    print(f"\n{'='*80}")
    print("TODAY'S COLLECTION COMPLETE")
    print(f"{'='*80}")
    print(f"Successful: {successful}/{len(movies_to_process)}")
    print(f"Total with trends: {df['trends_avg_interest'].notna().sum()}/{len(df)}")
    print(f"\n💡 Run this script again tomorrow for next batch!")


# ============================================================================
# WORKAROUND 4: Use Google Trends CSV Export (Manual)
# ============================================================================

def process_manual_trends_export(trends_csv='manual_trends.csv',
                                 movies_csv='data/raw/movies_with_youtube.csv',
                                 output_csv='data/raw/movies_with_trends.csv'):
    """
    Process manually downloaded Google Trends CSV files.
    
    Steps:
    1. Go to trends.google.com
    2. Search for movie titles one by one
    3. Download CSV for each
    4. Combine into one CSV with columns: title, avg_interest, peak_interest
    5. Run this function to merge with your dataset
    """
    
    print("Processing manually exported trends data...")
    
    # Load data
    trends_df = pd.read_csv(trends_csv)
    movies_df = pd.read_csv(movies_csv)
    
    # Merge
    merged = movies_df.merge(
        trends_df,
        on='title',
        how='left',
        suffixes=('', '_trends')
    )
    
    merged.to_csv(output_csv, index=False)
    
    print(f"✅ Merged trends data")
    print(f"   Movies with trends: {merged['avg_interest'].notna().sum()}/{len(merged)}")
    print(f"   Saved to: {output_csv}")


# ============================================================================
# MAIN - Choose Your Workaround
# ============================================================================

def main():
    print("\n🔧 GOOGLE TRENDS COLLECTION WORKAROUNDS\n")
    print("Choose a method:")
    print("\n1. VPN + Manual Rotation (Most Reliable)")
    print("   - Collect 10 movies at a time")
    print("   - Pause for VPN change between batches")
    print("   - Best success rate (~60-80%)")
    
    print("\n2. Daily Quota Method (Slow but Sure)")
    print("   - Collect 50 movies per day")
    print("   - Run once daily over multiple days")
    print("   - Avoids rate limiting completely")
    
    print("\n3. Use Proxies (Advanced)")
    print("   - Requires paid proxy service")
    print("   - Fast but needs setup")
    
    print("\n4. Manual Export (No automation)")
    print("   - Download from trends.google.com manually")
    print("   - 100% success but time-consuming")
    
    choice = input("\nEnter choice (1-4): ")
    
    if choice == '1':
        print("\n📋 INSTRUCTIONS:")
        print("1. Connect to a VPN")
        print("2. Script will collect 10 movies")
        print("3. When it pauses, change VPN location")
        print("4. Script resumes automatically\n")
        input("Press Enter when ready...")
        collect_with_vpn_manual()
    
    elif choice == '2':
        print("\n📋 INSTRUCTIONS:")
        print("1. Run this script once per day")
        print("2. It will collect 50 movies each time")
        print("3. Come back tomorrow for next batch\n")
        collect_daily_quota()
    
    elif choice == '3':
        print("\n⚠️  This requires setting up paid proxies")
        print("Recommended proxy services:")
        print("  - Bright Data: https://brightdata.com")
        print("  - Oxylabs: https://oxylabs.io")
        print("  - SmartProxy: https://smartproxy.com")
        print("\nAdd proxies to the code and run")
    
    elif choice == '4':
        print("\n📋 INSTRUCTIONS:")
        print("1. Visit trends.google.com")
        print("2. Search for each movie title")
        print("3. Download CSV")
        print("4. Combine all into one CSV with columns:")
        print("   title, avg_interest, peak_interest")
        print("5. Save as 'manual_trends.csv'")
        print("6. Run this script again and choose option 4")
    
    else:
        print("Invalid choice")


if __name__ == '__main__':
    main()
