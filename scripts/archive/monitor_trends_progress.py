"""
Monitor Google Trends Enrichment Progress
"""

import pandas as pd
import time
import os

def monitor_progress(csv_path='data/raw/movies_complete.csv', check_interval=30):
    """Monitor the Google Trends enrichment progress."""
    
    print("📊 GOOGLE TRENDS PROGRESS MONITOR")
    print("="*70)
    print(f"Monitoring: {csv_path}")
    print(f"Checking every {check_interval} seconds")
    print("Press Ctrl+C to stop monitoring\n")
    
    last_count = 0
    start_time = time.time()
    
    try:
        while True:
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                
                if 'trends_avg_interest' in df.columns:
                    current_count = df['trends_avg_interest'].notna().sum()
                    total = len(df)
                    percentage = (current_count / total) * 100
                    
                    # Calculate rate
                    elapsed_time = time.time() - start_time
                    if current_count > last_count and elapsed_time > 0:
                        rate = (current_count - last_count) / (elapsed_time / 60)  # per minute
                        remaining = total - current_count
                        eta_minutes = remaining / rate if rate > 0 else 0
                        
                        print(f"\r[{time.strftime('%H:%M:%S')}] Progress: {current_count:,}/{total:,} ({percentage:.1f}%) | "
                              f"Rate: {rate:.1f}/min | ETA: {eta_minutes:.0f} min", end='', flush=True)
                    else:
                        print(f"\r[{time.strftime('%H:%M:%S')}] Progress: {current_count:,}/{total:,} ({percentage:.1f}%)", 
                              end='', flush=True)
                    
                    last_count = current_count
                    start_time = time.time()
                    
                    if current_count >= total:
                        print("\n\n✅ Collection complete!")
                        break
                else:
                    print("Waiting for trends column to be created...", end='\r')
            else:
                print("Waiting for output file...", end='\r')
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if 'trends_avg_interest' in df.columns:
                current_count = df['trends_avg_interest'].notna().sum()
                print(f"Final count: {current_count:,}/{len(df):,} ({current_count/len(df)*100:.1f}%)")

if __name__ == '__main__':
    monitor_progress()
