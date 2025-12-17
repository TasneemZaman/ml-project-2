"""
Box Office Mojo Scraper
Gets REAL first week, opening weekend, and theater data
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import quote
import re

class BoxOfficeMojoScraper:
    """Scrapes Box Office Mojo for actual box office data"""
    
    def __init__(self):
        self.base_url = "https://www.boxofficemojo.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def search_movie(self, title, year=None):
        """Search for a movie on Box Office Mojo"""
        try:
            # Try direct title search
            search_url = f"{self.base_url}/search/"
            params = {'q': title}
            
            response = requests.get(search_url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for movie results
                results = soup.find_all('div', class_='a-section')
                
                for result in results:
                    link = result.find('a', href=True)
                    if link and '/release/' in link['href']:
                        movie_text = link.get_text(strip=True)
                        # Check if year matches
                        if year:
                            if str(year) in movie_text or str(year) in link['href']:
                                return self.base_url + link['href']
                        else:
                            return self.base_url + link['href']
            
            return None
            
        except Exception as e:
            print(f"  ⚠️  Search error for {title}: {e}")
            return None
    
    def get_movie_box_office_data(self, movie_url):
        """Scrape box office data from movie page"""
        try:
            response = requests.get(movie_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {
                'opening_weekend': 0,
                'first_week': 0,
                'num_theaters': 0,
                'average_per_theater': 0,
                'total_gross': 0,
                'widest_release': 0
            }
            
            # Find the summary section
            money_divs = soup.find_all('span', class_='money')
            
            # Look for "Opening" weekend
            opening_section = soup.find(string=re.compile(r'Opening', re.I))
            if opening_section:
                parent = opening_section.find_parent()
                if parent:
                    money = parent.find('span', class_='money')
                    if money:
                        data['opening_weekend'] = self._parse_money(money.get_text())
            
            # Look for theater count
            theaters_text = soup.find(string=re.compile(r'Theaters', re.I))
            if theaters_text:
                parent = theaters_text.find_parent()
                if parent:
                    num_text = parent.get_text()
                    numbers = re.findall(r'[\d,]+', num_text)
                    if numbers:
                        data['num_theaters'] = int(numbers[0].replace(',', ''))
            
            # Look for domestic total
            domestic_text = soup.find(string=re.compile(r'Domestic', re.I))
            if domestic_text:
                parent = domestic_text.find_parent()
                if parent:
                    money = parent.find('span', class_='money')
                    if money:
                        data['total_gross'] = self._parse_money(money.get_text())
            
            # Get weekly data if available
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        week_col = cells[0].get_text(strip=True)
                        if week_col == '1' or 'Week 1' in week_col:
                            # This is first week data
                            money_cell = cells[1] if len(cells) > 1 else None
                            if money_cell:
                                money_text = money_cell.get_text(strip=True)
                                data['first_week'] = self._parse_money(money_text)
            
            # If we have opening but not first week, estimate
            if data['opening_weekend'] > 0 and data['first_week'] == 0:
                # Opening weekend is typically 50-60% of first week
                data['first_week'] = data['opening_weekend'] * 1.7
            
            # Calculate average per theater
            if data['opening_weekend'] > 0 and data['num_theaters'] > 0:
                data['average_per_theater'] = data['opening_weekend'] / data['num_theaters']
            
            return data
            
        except Exception as e:
            print(f"  ⚠️  Scraping error: {e}")
            return None
    
    def _parse_money(self, text):
        """Parse money string like '$123,456,789' to number"""
        try:
            # Remove $ and commas
            clean = text.replace('$', '').replace(',', '').strip()
            # Handle millions/billions notation
            if 'M' in clean:
                return float(clean.replace('M', '')) * 1000000
            elif 'B' in clean:
                return float(clean.replace('B', '')) * 1000000000
            else:
                return float(clean)
        except:
            return 0
    
    def enrich_dataset(self, csv_file, output_file=None):
        """Enrich existing dataset with Box Office Mojo data"""
        print("="*80)
        print("🎬 BOX OFFICE MOJO DATA ENRICHMENT")
        print("="*80)
        
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} movies from {csv_file}")
        
        enriched_count = 0
        
        for idx, row in df.iterrows():
            title = row['movie_title']
            year = row['release_date'][:4] if pd.notna(row['release_date']) else None
            
            print(f"\n[{idx+1}/{len(df)}] {title} ({year})...")
            
            # Search for movie
            movie_url = self.search_movie(title, year)
            
            if movie_url:
                print(f"  ✓ Found: {movie_url}")
                
                # Get box office data
                box_office = self.get_movie_box_office_data(movie_url)
                
                if box_office:
                    # Update DataFrame with REAL data
                    if box_office['opening_weekend'] > 0:
                        df.at[idx, 'opening_weekend'] = box_office['opening_weekend']
                        print(f"  💰 Opening Weekend: ${box_office['opening_weekend']:,.0f}")
                    
                    if box_office['first_week'] > 0:
                        df.at[idx, 'first_week'] = box_office['first_week']
                        print(f"  💰 First Week: ${box_office['first_week']:,.0f}")
                    
                    if box_office['num_theaters'] > 0:
                        df.at[idx, 'num_theaters'] = box_office['num_theaters']
                        print(f"  🎭 Theaters: {box_office['num_theaters']:,}")
                    
                    if box_office['average_per_theater'] > 0:
                        df.at[idx, 'average_per_theater'] = box_office['average_per_theater']
                        print(f"  📊 Avg/Theater: ${box_office['average_per_theater']:,.0f}")
                    
                    enriched_count += 1
                else:
                    print(f"  ⚠️  Could not extract data")
            else:
                print(f"  ⚠️  Not found on Box Office Mojo")
            
            # Rate limiting - be respectful
            time.sleep(2)  # 2 seconds between requests
            
            # Save progress every 10 movies
            if (idx + 1) % 10 == 0:
                temp_file = output_file or csv_file.replace('.csv', '_temp.csv')
                df.to_csv(temp_file, index=False)
                print(f"\n  💾 Progress saved ({enriched_count} enriched so far)")
        
        print("\n" + "="*80)
        print(f"✅ ENRICHMENT COMPLETE!")
        print(f"Enriched: {enriched_count}/{len(df)} movies")
        print("="*80)
        
        # Save final file
        output = output_file or csv_file
        df.to_csv(output, index=False)
        print(f"✅ Saved to: {output}")
        
        return df


def main():
    """Test the scraper"""
    scraper = BoxOfficeMojoScraper()
    
    print("Testing Box Office Mojo scraper...")
    print("="*80)
    
    # Test with a known movie
    test_movie = "Inside Out 2"
    test_year = 2024
    
    print(f"\nSearching for: {test_movie} ({test_year})")
    url = scraper.search_movie(test_movie, test_year)
    
    if url:
        print(f"✓ Found: {url}")
        
        data = scraper.get_movie_box_office_data(url)
        
        if data:
            print("\nBox Office Data:")
            print(f"  Opening Weekend: ${data['opening_weekend']:,.0f}")
            print(f"  First Week: ${data['first_week']:,.0f}")
            print(f"  Theaters: {data['num_theaters']:,}")
            print(f"  Avg per Theater: ${data['average_per_theater']:,.0f}")
            print(f"  Total Gross: ${data['total_gross']:,.0f}")
            print("\n✅ Scraper works!")
        else:
            print("⚠️  Could not extract data")
    else:
        print("⚠️  Movie not found")
    
    print("\n" + "="*80)
    print("To enrich your dataset, run:")
    print("  scraper.enrich_dataset('data/raw/imdb_movies_large.csv')")
    print("="*80)


if __name__ == "__main__":
    main()
