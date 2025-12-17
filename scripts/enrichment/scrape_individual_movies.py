#!/usr/bin/env python3
"""
Scrape individual movie pages on Box Office Mojo for first week data
This fills in the gaps from batch collection
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import sys

class IndividualMovieScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.base_url = 'https://www.boxofficemojo.com'
    
    def scrape_movie_daily_data(self, bom_url, release_date):
        """
        Scrape daily data for a specific movie
        Returns first week data if available
        """
        try:
            # Construct daily page URL
            # BOM URLs are like: https://www.boxofficemojo.com/title/tt0499549/?ref_=bo_se_r_1
            # Daily page: https://www.boxofficemojo.com/title/tt0499549/daily/
            
            # Extract the title ID
            if '/title/' in bom_url:
                title_id = bom_url.split('/title/')[1].split('?')[0].strip('/')
                daily_url = f"{self.base_url}/title/{title_id}/daily/"
            else:
                # Old format: https://www.boxofficemojo.com/movies/?id=avatar.htm
                daily_url = bom_url.replace('.htm', '-daily.htm')
            
            response = requests.get(daily_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the daily table
            table = soup.find('div', class_='a-section a-spacing-none mojo-performance-summary-table')
            if not table:
                table = soup.find('table')
            
            if not table:
                return None
            
            # Parse table rows
            rows = table.find_all('tr')
            daily_data = []
            
            for row in rows[1:]:  # Skip header
                cols = row.find_all('td')
                if len(cols) < 4:
                    continue
                
                try:
                    # Extract data
                    date_str = cols[0].get_text(strip=True)
                    
                    # Parse date
                    if ',' in date_str:  # Format: "Dec 16, 2009"
                        date_obj = datetime.strptime(date_str, "%b %d, %Y")
                    else:
                        continue
                    
                    # Extract gross (remove $ and commas)
                    gross_str = cols[3].get_text(strip=True) if len(cols) > 3 else cols[1].get_text(strip=True)
                    gross = float(gross_str.replace('$', '').replace(',', '')) if gross_str and gross_str != '-' else 0
                    
                    # Extract theaters if available
                    theaters = None
                    for col in cols:
                        text = col.get_text(strip=True)
                        if text.replace(',', '').isdigit() and int(text.replace(',', '')) > 100:
                            theaters = int(text.replace(',', ''))
                            break
                    
                    daily_data.append({
                        'date': date_obj,
                        'gross': gross,
                        'theaters': theaters
                    })
                    
                except Exception as e:
                    continue
            
            if not daily_data:
                return None
            
            # Calculate days since release
            release_dt = pd.to_datetime(release_date)
            first_week_data = []
            
            for entry in daily_data:
                days_since = (entry['date'] - release_dt).days
                if 0 <= days_since <= 6:  # First week (days 0-6)
                    first_week_data.append(entry)
            
            if not first_week_data:
                return None
            
            # Aggregate first week
            first_week_gross = sum(d['gross'] for d in first_week_data)
            opening_day = first_week_data[0] if first_week_data else {}
            
            return {
                'first_week_gross': first_week_gross,
                'opening_gross': opening_day.get('gross'),
                'opening_theaters': opening_day.get('theaters'),
                'first_week_days_tracked': len(first_week_data),
                'peak_theaters_week1': max((d['theaters'] for d in first_week_data if d['theaters']), default=None),
            }
            
        except Exception as e:
            print(f"Error scraping {bom_url}: {e}")
            return None
    
    def scrape_movies_batch(self, df, start_idx=0, batch_size=100, max_movies=None):
        """
        Scrape multiple movies in batches
        Saves progress periodically
        """
        # Filter movies that need scraping
        needs_scraping = df['bom_url'].notna() & df['first_week_gross'].isna()
        has_budget = df['budget'].notna() & (df['budget'] > 0)
        has_youtube = df['youtube_views'].notna() & (df['youtube_views'] > 0)
        
        to_scrape = needs_scraping & has_budget & has_youtube
        movies_to_scrape = df[to_scrape].iloc[start_idx:].copy()
        
        if max_movies:
            movies_to_scrape = movies_to_scrape.head(max_movies)
        
        print("="*80)
        print(f"SCRAPING INDIVIDUAL MOVIES FOR FIRST WEEK DATA")
        print("="*80)
        print(f"\nTotal to scrape: {len(movies_to_scrape):,}")
        print(f"Starting from index: {start_idx}")
        print(f"Estimated time: {len(movies_to_scrape) * 3 / 60:.1f} minutes")
        print("="*80)
        
        results = []
        success_count = 0
        fail_count = 0
        
        start_time = datetime.now()
        
        for idx, (_, movie) in enumerate(movies_to_scrape.iterrows(), 1):
            print(f"[{idx}/{len(movies_to_scrape)}] {movie['title'][:40]:<40}", end='')
            
            first_week_data = self.scrape_movie_daily_data(
                movie['bom_url'], 
                movie['release_date']
            )
            
            if first_week_data:
                results.append({
                    'tmdb_id': movie['tmdb_id'],
                    'title': movie['title'],
                    **first_week_data
                })
                success_count += 1
                print(f" ✅ ${first_week_data['first_week_gross']:,.0f}")
            else:
                fail_count += 1
                print(" ❌")
            
            # Rate limiting
            time.sleep(2.5)
            
            # Progress update every 50 movies
            if idx % 50 == 0:
                elapsed = (datetime.now() - start_time).total_seconds() / 60
                remaining = (len(movies_to_scrape) - idx) * (elapsed / idx)
                success_rate = success_count / idx * 100
                
                print(f"\n{'─'*80}")
                print(f"Progress: {idx}/{len(movies_to_scrape)} | "
                      f"Success: {success_count} ({success_rate:.1f}%) | "
                      f"Failed: {fail_count}")
                print(f"Time: {elapsed:.1f}m elapsed, ~{remaining:.1f}m remaining")
                print(f"{'─'*80}\n")
                
                # Save intermediate results
                if results:
                    self._save_intermediate_results(results, start_idx + idx)
        
        # Final summary
        print("\n" + "="*80)
        print("SCRAPING COMPLETE")
        print("="*80)
        
        total_time = (datetime.now() - start_time).total_seconds() / 60
        
        print(f"\nTotal scraped: {len(movies_to_scrape)}")
        print(f"Successful: {success_count} ({success_count/len(movies_to_scrape)*100:.1f}%)")
        print(f"Failed: {fail_count}")
        print(f"Time taken: {total_time:.1f} minutes")
        
        return pd.DataFrame(results) if results else None
    
    def _save_intermediate_results(self, results, progress_idx):
        """Save intermediate results to avoid data loss"""
        df_temp = pd.DataFrame(results)
        temp_file = f'data/processed/individual_scrape_progress_{progress_idx}.csv'
        df_temp.to_csv(temp_file, index=False)
        print(f"   💾 Saved progress: {temp_file}")


def update_main_dataset(scraped_df):
    """Update the main dataset with newly scraped data"""
    
    print("\n" + "="*80)
    print("UPDATING MAIN DATASET")
    print("="*80)
    
    # Load main dataset
    df_main = pd.read_csv('data/raw/movies_with_youtube.csv')
    print(f"\nOriginal dataset: {len(df_main):,} movies")
    print(f"  With first_week_gross: {df_main['first_week_gross'].notna().sum()}")
    
    # Merge new data
    df_main = df_main.merge(
        scraped_df[['title', 'first_week_gross', 'opening_gross', 'opening_theaters',
                    'first_week_days_tracked', 'peak_theaters_week1']],
        on='title',
        how='left',
        suffixes=('', '_new')
    )
    
    # Update columns (prefer new data)
    for col in ['first_week_gross', 'opening_gross', 'opening_theaters',
                'first_week_days_tracked', 'peak_theaters_week1']:
        if f'{col}_new' in df_main.columns:
            df_main[col] = df_main[f'{col}_new'].combine_first(df_main.get(col, pd.Series()))
            df_main.drop(columns=[f'{col}_new'], inplace=True)
    
    # Save
    df_main.to_csv('data/raw/movies_with_youtube.csv', index=False)
    
    new_count = df_main['first_week_gross'].notna().sum()
    print(f"\n✅ Updated dataset saved")
    print(f"  Movies with first_week_gross: {new_count} (+{new_count - df_main['first_week_gross'].notna().sum()})")
    
    return df_main


if __name__ == '__main__':
    # Get parameters from command line
    start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    
    print(f"\nStarting from index: {start_idx}")
    print(f"Batch size: {batch_size}")
    print(f"\nPress Ctrl+C to stop (progress will be saved)\n")
    
    # Load dataset
    df = pd.read_csv('data/raw/movies_with_youtube.csv')
    
    # Create scraper
    scraper = IndividualMovieScraper()
    
    try:
        # Scrape movies
        scraped_df = scraper.scrape_movies_batch(
            df, 
            start_idx=start_idx,
            max_movies=batch_size
        )
        
        if scraped_df is not None and len(scraped_df) > 0:
            # Save scraped data
            output_file = f'data/processed/individual_scrape_batch_{start_idx}.csv'
            scraped_df.to_csv(output_file, index=False)
            print(f"\n✅ Saved scraped data: {output_file}")
            
            # Update main dataset
            update_main_dataset(scraped_df)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Progress has been saved.")
        sys.exit(0)
