"""
Smart Batch Collection: Get 2024 movies opening week + momentum data
Strategy: Scrape strategic dates to capture all movies efficiently
"""
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time

class YearBatchCollector:
    def __init__(self):
        self.base_url = 'https://www.boxofficemojo.com'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def collect_year_batch(self, year=2024, strategy='smart', verbose=True):
        """
        Collect batch data for entire year
        
        Strategies:
        - 'smart': 52 Fridays + key dates (fastest, ~2 min)
        - 'weekly': Every 7 days (~52 dates, ~2 min)
        - 'biweekly': Every 14 days (~26 dates, ~1 min)
        
        Args:
            year: Year to collect
            strategy: Collection strategy
            verbose: Whether to print detailed progress (default: True)
        """
        
        if strategy == 'smart':
            dates = self._generate_smart_dates(year)
        elif strategy == 'weekly':
            dates = self._generate_weekly_dates(year)
        elif strategy == 'biweekly':
            dates = self._generate_biweekly_dates(year)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        if verbose:
            print(f"="*80)
            print(f"BATCH COLLECTION: {year} - {strategy.upper()} STRATEGY")
            print(f"="*80)
            print(f"Dates to scrape: {len(dates)}")
            print(f"Estimated time: {len(dates) * 2 / 60:.1f} minutes")
            print(f"="*80)
        
        all_data = []
        
        for i, date_str in enumerate(dates, 1):
            daily_df = self.scrape_daily_data(date_str)
            
            if daily_df is not None:
                all_data.append(daily_df)
                if verbose:
                    print(f"[{i:3d}/{len(dates)}] {date_str}: {len(daily_df):3d} movies", end='\r')
            else:
                if verbose:
                    print(f"[{i:3d}/{len(dates)}] {date_str}: NO DATA", end='\r')
            
            time.sleep(2)
        
        if verbose:
            print()  # New line
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            output_file = f'data/processed/bom_{year}_batch.csv'
            combined.to_csv(output_file, index=False)
            
            if verbose:
                print(f"\n✅ Collected {len(combined):,} records from {len(dates)} dates")
                print(f"✅ Unique movies: {combined['release'].nunique()}")
                print(f"✅ Saved to: {output_file}")
            
            return combined
        
        return None
    
    def _generate_smart_dates(self, year):
        """Generate Fridays (main release day) + major holidays"""
        dates = []
        
        # All Fridays
        start = datetime(year, 1, 1)
        # Find first Friday
        while start.weekday() != 4:  # 4 = Friday
            start += timedelta(days=1)
        
        current = start
        end = datetime(year, 12, 31)
        
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=7)
        
        # Add major holiday weeks (if not already included)
        holidays = [
            f'{year}-01-01',  # New Year
            f'{year}-02-14',  # Valentine's
            f'{year}-03-29',  # Easter weekend (approximate)
            f'{year}-05-24',  # Memorial Day
            f'{year}-07-04',  # July 4th
            f'{year}-11-28',  # Thanksgiving
            f'{year}-12-25',  # Christmas
        ]
        
        for holiday in holidays:
            if holiday not in dates:
                dates.append(holiday)
        
        return sorted(dates)
    
    def _generate_weekly_dates(self, year):
        """Every 7 days"""
        dates = []
        current = datetime(year, 1, 1)
        end = datetime(year, 12, 31)
        
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=7)
        
        return dates
    
    def _generate_biweekly_dates(self, year):
        """Every 14 days"""
        dates = []
        current = datetime(year, 1, 1)
        end = datetime(year, 12, 31)
        
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=14)
        
        return dates
    
    def scrape_daily_data(self, date_str):
        """Scrape single date"""
        try:
            url = f'{self.base_url}/date/{date_str}/'
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table')
            if not table:
                return None
            
            rows = []
            for tr in table.find_all('tr')[1:]:
                cols = tr.find_all('td')
                if len(cols) >= 9:
                    movie_link = cols[2].find('a')
                    movie_url = movie_link['href'] if movie_link else None
                    
                    rows.append({
                        'date': date_str,
                        'rank': self._parse_int(cols[0].text),
                        'release': cols[2].text.strip(),
                        'movie_url': self.base_url + movie_url if movie_url else None,
                        'daily_gross': self._parse_money(cols[3].text),
                        'yd_change_pct': self._parse_percent(cols[4].text),
                        'lw_change_pct': self._parse_percent(cols[5].text),
                        'theaters': self._parse_int(cols[6].text),
                        'per_theater_avg': self._parse_money(cols[7].text),
                        'to_date_gross': self._parse_money(cols[8].text),
                        'days_in_release': self._parse_int(cols[9].text) if len(cols) > 9 else None,
                    })
            
            return pd.DataFrame(rows) if rows else None
        except:
            return None
    
    def _parse_money(self, text):
        try:
            text = text.strip().replace('$', '').replace(',', '')
            return float(text) if text and text != '-' else None
        except:
            return None
    
    def _parse_percent(self, text):
        try:
            text = text.strip().replace('%', '').replace('+', '')
            return float(text) if text and text != '-' and text != 'n/a' else None
        except:
            return None
    
    def _parse_int(self, text):
        try:
            text = text.strip().replace(',', '')
            return int(text) if text and text != '-' else None
        except:
            return None


def aggregate_movie_features(batch_df, df_main):
    """
    Aggregate batch data into features for each movie
    Focus on: opening week + momentum indicators
    """
    
    results = []
    
    # Load main dataset to match movies
    df_main['release_date'] = pd.to_datetime(df_main['release_date'])
    
    for idx, movie in df_main.iterrows():
        if pd.isna(movie['bom_url']):
            continue
        
        title = movie['title']
        release_date = movie['release_date']
        
        # Find this movie in batch data
        # Match by title (fuzzy) or URL
        movie_batch = batch_df[batch_df['release'].str.contains(title[:20], case=False, na=False, regex=False)]
        
        if len(movie_batch) == 0:
            continue
        
        # Sort by date
        movie_batch = movie_batch.sort_values('date')
        movie_batch['date'] = pd.to_datetime(movie_batch['date'])
        
        # Calculate days since release
        movie_batch['days_since_release'] = (movie_batch['date'] - release_date).dt.days
        
        # Get first week data (days 0-6)
        first_week = movie_batch[movie_batch['days_since_release'].between(0, 6)]
        
        if len(first_week) == 0:
            continue
        
        # Calculate features
        features = {
            'tmdb_id': movie['tmdb_id'],
            'title': title,
            
            # Opening day (Day 0)
            'opening_theaters': first_week.iloc[0]['theaters'] if len(first_week) > 0 else None,
            'opening_gross': first_week.iloc[0]['daily_gross'] if len(first_week) > 0 else None,
            'opening_per_theater': first_week.iloc[0]['per_theater_avg'] if len(first_week) > 0 else None,
            
            # First week aggregate
            'first_week_gross': first_week['daily_gross'].sum(),
            'first_week_avg_daily': first_week['daily_gross'].mean(),
            'first_week_days_tracked': len(first_week),
            
            # Momentum (YD% and LW%)
            'avg_yd_change': first_week['yd_change_pct'].mean(),
            'avg_lw_change': first_week['lw_change_pct'].mean(),
            'max_yd_gain': first_week['yd_change_pct'].max(),
            'max_yd_drop': first_week['yd_change_pct'].min(),
            
            # Theater evolution
            'peak_theaters_week1': first_week['theaters'].max(),
            'min_theaters_week1': first_week['theaters'].min(),
        }
        
        results.append(features)
    
    return pd.DataFrame(results)


if __name__ == '__main__':
    import sys
    
    strategy = sys.argv[1] if len(sys.argv) > 1 else 'biweekly'
    
    collector = YearBatchCollector()
    
    # Collect batch data
    batch_df = collector.collect_year_batch(year=2024, strategy=strategy)
    
    if batch_df is not None:
        # Aggregate into features
        print("\nAggregating features...")
        df_main = pd.read_csv('data/raw/movies_with_youtube.csv')
        
        features_df = aggregate_movie_features(batch_df, df_main)
        
        if len(features_df) > 0:
            output_file = 'data/processed/first_week_features_2024.csv'
            features_df.to_csv(output_file, index=False)
            print(f"✅ Created features for {len(features_df)} movies")
            print(f"✅ Saved to: {output_file}")
            
            # Merge with main dataset
            df_merged = df_main.merge(features_df, on='tmdb_id', how='left', suffixes=('', '_batch'))
            df_merged.to_csv('data/raw/movies_with_youtube.csv', index=False)
            print(f"✅ Updated main dataset with first week features")
