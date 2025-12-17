"""
Main Data Collection Pipeline
Run this script to collect and enrich movie data from all sources.
Note: Google Trends removed - too unreliable. Using YouTube views instead.
"""
import pandas as pd
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from collectors import TMDBCollector, YouTubeCollector, BoxOfficeMojoCollector

class MovieDataPipeline:
    """Main pipeline for collecting movie data."""
    
    def __init__(self):
        self.tmdb = TMDBCollector()
        self.youtube = YouTubeCollector()
        self.box_office = BoxOfficeMojoCollector()
    
    def collect_base_data(self, output_file='data/raw/movies_base.csv', 
                         min_year=2000, max_year=2024, total_movies=5000):
        """Step 1: Collect base movie data from TMDB."""
        print("\n" + "="*80)
        print("STEP 1: COLLECTING BASE DATA FROM TMDB")
        print("="*80 + "\n")
        
        df = self.tmdb.get_popular_movies(
            min_year=min_year,
            max_year=max_year,
            total_movies=total_movies
        )
        
        df.to_csv(output_file, index=False)
        print(f"\n✅ Saved {len(df)} movies to {output_file}")
        
        return df
    
    def enrich_with_youtube(self, input_file='data/raw/movies_base.csv',
                           output_file='data/raw/movies_with_youtube.csv',
                           workers=5, batch_size=100):
        """Step 2: Add YouTube statistics."""
        print("\n" + "="*80)
        print("STEP 2: ENRICHING WITH YOUTUBE DATA")
        print("="*80 + "\n")
        
        df = pd.read_csv(input_file)
        
        # Check if already has YouTube columns
        youtube_cols = ['youtube_video_id', 'youtube_views', 'youtube_likes', 'youtube_comments']
        if all(col in df.columns for col in youtube_cols):
            needs_youtube = df['youtube_video_id'].isna()
            rows_to_process = df[needs_youtube]
            print(f"Found {needs_youtube.sum()} movies without YouTube data")
        else:
            for col in youtube_cols:
                df[col] = None
            rows_to_process = df
        
        if len(rows_to_process) == 0:
            print("All movies already have YouTube data!")
            return df
        
        print(f"Processing {len(rows_to_process)} movies with {workers} workers...")
        
        def fetch_youtube(row):
            idx, title, release_date = row
            return idx, self.youtube.get_movie_youtube_data(title, release_date)
        
        # Process in batches
        for batch_num in range(0, len(rows_to_process), batch_size):
            batch = rows_to_process.iloc[batch_num:batch_num + batch_size]
            batch_number = (batch_num // batch_size) + 1
            total_batches = (len(rows_to_process) + batch_size - 1) // batch_size
            
            print(f"\nBatch {batch_number}/{total_batches} ({len(batch)} movies)")
            
            movie_data = [(idx, row['title'], row['release_date']) 
                         for idx, row in batch.iterrows()]
            
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(fetch_youtube, data): data for data in movie_data}
                
                for future in tqdm(as_completed(futures), total=len(futures)):
                    try:
                        idx, youtube_data = future.result()
                        for col, value in youtube_data.items():
                            df.at[idx, col] = value
                    except Exception as e:
                        print(f"Error: {e}")
            
            # Save after each batch
            df.to_csv(output_file, index=False)
            completed = df['youtube_video_id'].notna().sum()
            print(f"✓ Saved. Total with YouTube: {completed}/{len(df)}")
            
            time.sleep(2)  # Brief pause between batches
        
        print(f"\n✅ YouTube enrichment complete: {output_file}")
        return df
    
    def enrich_with_box_office(self, input_file='data/raw/movies_with_youtube.csv',
                               output_file='data/raw/movies_with_boxoffice.csv',
                               delay=3):
        """Step 3: Add box office data (slow - web scraping)."""
        print("\n" + "="*80)
        print("STEP 3: ENRICHING WITH BOX OFFICE DATA")
        print("="*80 + "\n")
        print("⚠️  Warning: Box Office Mojo scraping is slow (~3-5 sec per movie)")
        print("    Consider running overnight for large datasets\n")
        
        df = pd.read_csv(input_file)
        
        # Check if already has box office columns
        bo_cols = ['domestic_gross', 'international_gross', 'worldwide_gross', 'opening_weekend']
        if all(col in df.columns for col in bo_cols):
            needs_bo = df['domestic_gross'].isna()
            rows_to_process = df[needs_bo]
            print(f"Found {needs_bo.sum()} movies without box office data")
        else:
            for col in bo_cols:
                df[col] = None
            rows_to_process = df
        
        if len(rows_to_process) == 0:
            print("All movies already have box office data!")
            return df
        
        print(f"Processing {len(rows_to_process)} movies...")
        print(f"Estimated time: {len(rows_to_process) * delay / 60:.0f} minutes\n")
        
        for idx, row in tqdm(rows_to_process.iterrows(), total=len(rows_to_process)):
            try:
                release_year = pd.to_datetime(row['release_date']).year
                movie_url = self.box_office.search_movie(row['title'], release_year)
                
                if movie_url:
                    bo_data = self.box_office.get_box_office_data(movie_url)
                    if bo_data:
                        for col, value in bo_data.items():
                            df.at[idx, col] = value
                
                time.sleep(delay)
                
                # Save every 50 movies
                if (idx + 1) % 50 == 0:
                    df.to_csv(output_file, index=False)
            
            except Exception as e:
                print(f"\nError processing {row['title']}: {e}")
        
        df.to_csv(output_file, index=False)
        completed = df['domestic_gross'].notna().sum()
        print(f"\n✅ Box office enrichment complete: {completed}/{len(df)} movies")
        print(f"Saved to: {output_file}")
        
        return df
    
    def run_full_pipeline(self, total_movies=5000):
        """Run the complete data collection pipeline."""
        print("\n" + "="*80)
        print("MOVIE DATA COLLECTION PIPELINE")
        print("="*80)
        print(f"Target: {total_movies} movies")
        print("Data sources: TMDB + YouTube + Box Office (optional)")
        print("Note: Google Trends removed - using YouTube views as engagement metric")
        print("="*80)
        
        # Step 1: TMDB base data
        df = self.collect_base_data(total_movies=total_movies)
        
        # Step 2: YouTube data
        df = self.enrich_with_youtube()
        
        # Step 3: Box Office data (optional - slow)
        response = input("\nEnrich with Box Office Mojo data? (y/n): ")
        if response.lower() == 'y':
            df = self.enrich_with_box_office()
        
        print("\n" + "="*80)
        print("✅ PIPELINE COMPLETE!")
        print("="*80)
        print(f"\nFinal dataset: {len(df)} movies")
        print(f"Columns: {list(df.columns)}")
        print(f"\nData quality:")
        print(f"  - TMDB data: {len(df)} (100%)")
        print(f"  - YouTube data: {df['youtube_video_id'].notna().sum()} ({df['youtube_video_id'].notna().sum()/len(df)*100:.1f}%)")
        if 'domestic_gross' in df.columns:
            print(f"  - Box office data: {df['domestic_gross'].notna().sum()} ({df['domestic_gross'].notna().sum()/len(df)*100:.1f}%)")
        print(f"\n💡 Use YouTube views as your engagement metric (better than Google Trends!)")



def main():
    """Main entry point."""
    pipeline = MovieDataPipeline()
    
    print("Choose an option:")
    print("1. Run full pipeline (TMDB + YouTube + Box Office)")
    print("2. Only collect TMDB base data")
    print("3. Enrich existing data with YouTube")
    print("4. Enrich existing data with Box Office")
    print("5. Show progress of existing data")
    
    choice = input("\nEnter choice (1-5): ")
    
    if choice == '1':
        pipeline.run_full_pipeline()
    elif choice == '2':
        pipeline.collect_base_data()
    elif choice == '3':
        pipeline.enrich_with_youtube()
    elif choice == '4':
        pipeline.enrich_with_box_office()
    elif choice == '5':
        # Show progress
        try:
            df = pd.read_csv('data/raw/movies_complete.csv')
            print(f"\nDataset: {len(df)} movies")
            print("\nData completeness:")
            for col in df.columns:
                complete = df[col].notna().sum()
                print(f"  {col}: {complete}/{len(df)} ({complete/len(df)*100:.1f}%)")
        except FileNotFoundError:
            print("No dataset found!")


if __name__ == '__main__':
    main()
