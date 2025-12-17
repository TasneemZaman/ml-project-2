import os

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time

class PreReleaseFirstWeekCollector:
    """
    Collect training data: For historical movies, get their first 7 days as TARGET
    Then use pre-release features (budget, genres, YouTube, etc.) as INPUTS
    """
    
    def __init__(self):
        self.base_url = 'https://www.boxofficemojo.com'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def collect_first_week_for_training(self, input_csv='data/raw/movies_with_youtube.csv', 
                                       output_csv='data/processed/first_week_targets.csv',
                                       year_from=2020, max_movies=500):
        """
        For historical movies in your dataset:
        1. Scrape their first 7 days from BOM
        2. Calculate first week total
        3. Save as target variable for training
        
        Then you already have pre-release features:
        - budget, genres, director, cast
        - YouTube trailer views/likes/comments
        - TMDB popularity, vote_average
        """
        
        df = pd.read_csv(input_csv)
        df['release_date'] = pd.to_datetime(df['release_date'])
        
        # Filter movies we can train on
        mask = (
            (df['release_date'] >= f'{year_from}-01-01') &
            (df['bom_url'].notna()) &
            (df['release_date'] < '2025-01-01')  # Only movies already released
        )
        
        training_movies = df[mask].copy()
        
        if max_movies:
            training_movies = training_movies.head(max_movies)
        
        print(f"Collecting first week data for {len(training_movies)} movies...")
        
        results = []
        
        for idx, row in training_movies.iterrows():
            try:
                release_date = row['release_date']
                title = row['title']
                
                # Scrape 7 days after release
                week1_data = []
                for day in range(7):
                    date = release_date + timedelta(days=day)
                    date_str = date.strftime('%Y-%m-%d')
                    
                    daily = self.scrape_daily_data(date_str)
                    if daily is not None:
                        # Find this movie
                        movie_row = daily[daily['release'].str.contains(title, case=False, na=False, regex=False)]
                        if len(movie_row) > 0:
                            week1_data.append(movie_row.iloc[0])
                    
                    time.sleep(2)
                
                if len(week1_data) >= 3:  # At least opening weekend
                    result = {
                        'tmdb_id': row['tmdb_id'],
                        'title': title,
                        'release_date': release_date,
                        
                        # TARGET: First week revenue
                        'first_week_gross': sum([d['daily_gross'] for d in week1_data if pd.notna(d['daily_gross'])]),
                        
                        # Opening metrics (could also be features if predicting beyond day 1)
                        'opening_day_gross': week1_data[0]['daily_gross'] if len(week1_data) > 0 else None,
                        'opening_weekend_gross': sum([week1_data[i]['daily_gross'] for i in range(min(3, len(week1_data))) if pd.notna(week1_data[i]['daily_gross'])]),
                        'opening_theaters': week1_data[0]['theaters'] if len(week1_data) > 0 else None,
                        'opening_per_theater': week1_data[0]['per_theater_avg'] if len(week1_data) > 0 else None,
                        
                        # Days tracked
                        'days_collected': len(week1_data)
                    }
                    results.append(result)
                    print(f"✓ {title[:40]:40s} - Week 1: ${result['first_week_gross']:,.0f}")
                else:
                    print(f"✗ {title[:40]:40s} - Insufficient data")
                    
            except Exception as e:
                print(f"✗ Error: {title} - {e}")
                continue
        
        # Save results
        if results:
            results_df = pd.DataFrame(results)
            results_df.to_csv(output_csv, index=False)
            print(f"\n✅ Saved {len(results)} movies to {output_csv}")
            
            # Merge with original features
            df_merged = df.merge(results_df[['tmdb_id', 'first_week_gross', 'opening_weekend_gross']], 
                                on='tmdb_id', how='left')
            df_merged.to_csv(input_csv, index=False)
            print(f"✅ Updated {input_csv} with first week targets")
            
            return results_df
        
        return None
    
    def scrape_daily_data(self, date_str):
        """Scrape single day"""
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
                    rows.append({
                        'release': cols[2].text.strip(),
                        'daily_gross': self._parse_money(cols[3].text),
                        'theaters': self._parse_int(cols[6].text),
                        'per_theater_avg': self._parse_money(cols[7].text),
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
    
    def _parse_int(self, text):
        try:
            text = text.strip().replace(',', '')
            return int(text) if text and text != '-' else None
        except:
            return None


if __name__ == '__main__':
    collector = PreReleaseFirstWeekCollector()
    
    # Collect first week data for recent movies to use as training targets
    collector.collect_first_week_for_training(
        year_from=2024,
        max_movies=10  # Start with just 10 movies for testing (10 movies × 7 days × 2 sec = ~2.5 min)
    )
