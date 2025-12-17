"""
Enrich movie dataset with Box Office Mojo daily data.
This collects daily box office performance (theaters, daily gross, YD/LW changes)
and aggregates them into meaningful features for prediction.
"""
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import numpy as np

class BOMDailyCollector:
    """
    Scrape daily box office data from Box Office Mojo date pages.
    Example: https://www.boxofficemojo.com/date/2025-12-13/
    """
    
    def __init__(self):
        self.base_url = "https://www.boxofficemojo.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def scrape_daily_data(self, date_str):
        """
        Scrape daily box office data for a specific date.
        
        Args:
            date_str: Date in format 'YYYY-MM-DD' (e.g., '2025-12-13')
        
        Returns:
            DataFrame with daily box office data for all movies
        """
        try:
            url = f"{self.base_url}/date/{date_str}/"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the main table
            table = soup.find('table')
            if not table:
                return None
            
            # Parse table
            rows = []
            for tr in table.find_all('tr')[1:]:  # Skip header
                cols = tr.find_all('td')
                if len(cols) >= 9:
                    # Extract movie URL for matching
                    movie_link = cols[2].find('a')
                    movie_url = movie_link['href'] if movie_link else None
                    movie_title = cols[2].text.strip()
                    
                    row_data = {
                        'date': date_str,
                        'rank': self._parse_int(cols[0].text),
                        'release': movie_title,
                        'movie_url': self.base_url + movie_url if movie_url else None,
                        'daily_gross': self._parse_money(cols[3].text),
                        'yd_change_pct': self._parse_percent(cols[4].text),
                        'lw_change_pct': self._parse_percent(cols[5].text),
                        'theaters': self._parse_int(cols[6].text),
                        'per_theater_avg': self._parse_money(cols[7].text),
                        'to_date_gross': self._parse_money(cols[8].text),
                        'days_in_release': self._parse_int(cols[9].text) if len(cols) > 9 else None,
                        'distributor': cols[10].text.strip() if len(cols) > 10 else None
                    }
                    rows.append(row_data)
            
            if rows:
                return pd.DataFrame(rows)
            
        except Exception as e:
            print(f"  ✗ Error scraping {date_str}: {e}")
        
        return None
    
    def scrape_date_range(self, start_date, end_date, max_days=None):
        """
        Scrape daily data for a range of dates.
        
        Args:
            start_date: Start date string 'YYYY-MM-DD'
            end_date: End date string 'YYYY-MM-DD'
            max_days: Maximum number of days to scrape (optional)
        
        Returns:
            Combined DataFrame with all daily data
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        all_data = []
        current = start
        days_scraped = 0
        
        print(f"\n{'='*80}")
        print(f"Scraping Box Office Mojo Daily Data: {start_date} to {end_date}")
        print(f"{'='*80}\n")
        
        while current <= end:
            if max_days and days_scraped >= max_days:
                break
                
            date_str = current.strftime('%Y-%m-%d')
            df = self.scrape_daily_data(date_str)
            
            if df is not None:
                all_data.append(df)
                print(f"✓ {date_str}: {len(df):3d} movies | Total scraped: {days_scraped+1} days", end='\r')
            else:
                print(f"✗ {date_str}: No data", end='\r')
            
            current += timedelta(days=1)
            days_scraped += 1
            time.sleep(2)  # Rate limiting - be respectful!
        
        print()  # New line after progress
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            print(f"\n✅ Collected {len(combined):,} daily records across {len(all_data)} days")
            return combined
        
        print("\n⚠️  No data collected")
        return None
    
    def _parse_money(self, text):
        """Parse money string to float."""
        try:
            text = text.strip().replace('$', '').replace(',', '')
            if not text or text == '-':
                return None
            return float(text)
        except:
            return None
    
    def _parse_percent(self, text):
        """Parse percentage string to float."""
        try:
            text = text.strip().replace('%', '').replace('+', '')
            if not text or text == '-' or text == 'n/a':
                return None
            return float(text)
        except:
            return None
    
    def _parse_int(self, text):
        """Parse integer string."""
        try:
            text = text.strip().replace(',', '')
            if not text or text == '-':
                return None
            return int(text)
        except:
            return None


def aggregate_daily_features(daily_data, movie_title, movie_url=None):
    """
    Aggregate daily box office data into features for a single movie.
    
    Args:
        daily_data: DataFrame with daily box office records
        movie_title: Movie title to filter for
        movie_url: Optional BOM URL for more precise matching
    
    Returns:
        Dictionary of aggregated features
    """
    # Try to match by URL first (most reliable), then by title
    if movie_url and pd.notna(movie_url):
        movie_data = daily_data[daily_data['movie_url'] == movie_url]
    
    # Fallback to title matching
    if movie_url is None or len(movie_data) == 0:
        movie_data = daily_data[daily_data['release'].str.contains(movie_title, case=False, na=False, regex=False)]
    
    if len(movie_data) == 0:
        return None
    
    # Sort by date
    movie_data = movie_data.sort_values('date').copy()
    
    features = {
        # Theater metrics
        'daily_opening_theaters': movie_data['theaters'].iloc[0] if len(movie_data) > 0 else None,
        'daily_peak_theaters': movie_data['theaters'].max(),
        'daily_avg_theaters': movie_data['theaters'].mean(),
        'daily_min_theaters': movie_data['theaters'].min(),
        'daily_theater_std': movie_data['theaters'].std(),
        
        # Revenue metrics
        'daily_opening_day_gross': movie_data['daily_gross'].iloc[0] if len(movie_data) > 0 else None,
        'daily_peak_gross': movie_data['daily_gross'].max(),
        'daily_avg_gross': movie_data['daily_gross'].mean(),
        'daily_gross_std': movie_data['daily_gross'].std(),
        
        # Per-theater performance
        'daily_opening_per_theater': movie_data['per_theater_avg'].iloc[0] if len(movie_data) > 0 else None,
        'daily_peak_per_theater': movie_data['per_theater_avg'].max(),
        'daily_avg_per_theater': movie_data['per_theater_avg'].mean(),
        'daily_per_theater_std': movie_data['per_theater_avg'].std(),
        
        # Momentum indicators (day-to-day and week-to-week changes)
        'daily_avg_yd_change': movie_data['yd_change_pct'].mean(),
        'daily_avg_lw_change': movie_data['lw_change_pct'].mean(),
        'daily_yd_volatility': movie_data['yd_change_pct'].std(),
        'daily_max_yd_gain': movie_data['yd_change_pct'].max(),
        'daily_max_yd_drop': movie_data['yd_change_pct'].min(),
        
        # Opening weekend performance (first 3 days)
        'daily_opening_3day_gross': movie_data['daily_gross'].iloc[:3].sum() if len(movie_data) >= 3 else None,
        'daily_opening_3day_per_theater': movie_data['per_theater_avg'].iloc[:3].mean() if len(movie_data) >= 3 else None,
        
        # Weekly trends
        'daily_week1_avg_gross': movie_data['daily_gross'].iloc[:7].mean() if len(movie_data) >= 7 else None,
        'daily_week2_avg_gross': movie_data['daily_gross'].iloc[7:14].mean() if len(movie_data) >= 14 else None,
        'daily_week1_avg_theaters': movie_data['theaters'].iloc[:7].mean() if len(movie_data) >= 7 else None,
        
        # Release tracking
        'daily_days_tracked': len(movie_data),
        'daily_max_days_in_release': movie_data['days_in_release'].max() if 'days_in_release' in movie_data.columns else None,
        
        # Cumulative totals
        'daily_final_gross': movie_data['to_date_gross'].iloc[-1] if len(movie_data) > 0 else None,
    }
    
    # Calculate derived features
    if features['daily_week1_avg_gross'] and features['daily_week2_avg_gross'] and features['daily_week2_avg_gross'] > 0:
        features['daily_week2_week1_ratio'] = features['daily_week2_avg_gross'] / features['daily_week1_avg_gross']
    else:
        features['daily_week2_week1_ratio'] = None
    
    if features['daily_peak_theaters'] and features['daily_opening_theaters'] and features['daily_opening_theaters'] > 0:
        features['daily_theater_expansion_ratio'] = features['daily_peak_theaters'] / features['daily_opening_theaters']
    else:
        features['daily_theater_expansion_ratio'] = None
    
    if features['daily_opening_3day_gross'] and features['daily_final_gross'] and features['daily_final_gross'] > 0:
        features['daily_opening_to_total_ratio'] = features['daily_opening_3day_gross'] / features['daily_final_gross']
    else:
        features['daily_opening_to_total_ratio'] = None
    
    # Theater efficiency (revenue per theater trend)
    if features['daily_opening_per_theater'] and features['daily_avg_per_theater'] and features['daily_opening_per_theater'] > 0:
        features['daily_per_theater_decline_rate'] = (features['daily_avg_per_theater'] - features['daily_opening_per_theater']) / features['daily_opening_per_theater']
    else:
        features['daily_per_theater_decline_rate'] = None
    
    return features


def enrich_dataset_with_daily_data(input_file='data/raw/movies_with_youtube.csv',
                                   output_file=None,
                                   start_date='2024-01-01',
                                   end_date='2025-12-13',
                                   sample_size=None):
    """
    Enrich movie dataset with Box Office Mojo daily features.
    
    Args:
        input_file: Path to input CSV
        output_file: Path to output CSV (if None, overwrites input)
        start_date: Start date for daily data collection
        end_date: End date for daily data collection
        sample_size: Number of movies to process (None = all)
    """
    print("=" * 80)
    print("ENRICH DATASET WITH BOX OFFICE MOJO DAILY DATA")
    print("=" * 80)
    
    # Load dataset
    df = pd.read_csv(input_file)
    print(f"\nLoaded {len(df):,} movies from {input_file}")
    
    # Initialize collector
    collector = BOMDailyCollector()
    
    # Collect daily data for date range
    print(f"\nStep 1: Collecting daily box office data")
    daily_data = collector.scrape_date_range(start_date, end_date)
    
    if daily_data is None or len(daily_data) == 0:
        print("No daily data collected. Exiting.")
        return
    
    # Save raw daily data
    daily_data_file = 'data/processed/bom_daily_data.csv'
    daily_data.to_csv(daily_data_file, index=False)
    print(f"✓ Saved raw daily data to {daily_data_file}")
    
    # Match movies and aggregate features
    print(f"\nStep 2: Matching movies and aggregating daily features")
    print("=" * 80)
    
    # Filter movies that have BOM URLs (easier to match)
    movies_with_bom = df[df['bom_url'].notna()].copy()
    
    if sample_size:
        movies_with_bom = movies_with_bom.head(sample_size)
    
    print(f"Processing {len(movies_with_bom):,} movies with BOM URLs...")
    
    # Process each movie
    enriched_features = []
    matched_count = 0
    
    for idx, row in movies_with_bom.iterrows():
        title = row['title']
        bom_url = row['bom_url']
        
        # Aggregate daily features
        features = aggregate_daily_features(daily_data, title, bom_url)
        
        if features:
            features['index'] = idx
            enriched_features.append(features)
            matched_count += 1
            
        print(f"Progress: {matched_count}/{len(movies_with_bom)} movies matched", end='\r')
    
    print()
    print(f"\n✓ Matched {matched_count} movies with daily data")
    
    # Convert to DataFrame and merge
    if enriched_features:
        features_df = pd.DataFrame(enriched_features)
        features_df.set_index('index', inplace=True)
        
        # Merge with original dataset
        df_enriched = df.join(features_df, how='left')
        
        # Save
        if output_file is None:
            output_file = input_file
        
        df_enriched.to_csv(output_file, index=False)
        print(f"✅ Saved enriched dataset to {output_file}")
        
        # Summary
        new_cols = [col for col in features_df.columns]
        print(f"\nAdded {len(new_cols)} new daily features:")
        for col in new_cols:
            non_null = df_enriched[col].notna().sum()
            print(f"  - {col:40s}: {non_null:5,} movies ({non_null/len(df)*100:5.1f}%)")
    
    else:
        print("⚠️  No features extracted")


if __name__ == "__main__":
    # Example usage
    import sys
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            # Test mode - just scrape one day
            collector = BOMDailyCollector()
            df = collector.scrape_daily_data('2025-12-13')
            if df is not None:
                print("\nSample data:")
                print(df.head(10))
        elif sys.argv[1] == 'range':
            # Scrape a date range
            start = sys.argv[2] if len(sys.argv) > 2 else '2025-12-01'
            end = sys.argv[3] if len(sys.argv) > 3 else '2025-12-13'
            collector = BOMDailyCollector()
            df = collector.scrape_date_range(start, end)
            if df is not None:
                print("\nSample data:")
                print(df.head(10))
                df.to_csv('data/processed/bom_daily_sample.csv', index=False)
                print(f"\n✓ Saved to data/processed/bom_daily_sample.csv")
    else:
        # Full enrichment
        enrich_dataset_with_daily_data(
            input_file='data/raw/movies_with_youtube.csv',
            start_date='2024-01-01',
            end_date='2025-12-13',
            sample_size=None  # None = process all movies
        )
