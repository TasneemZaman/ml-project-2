"""
Update Box Office Mojo data for existing movies
Useful for movies that have been released but didn't have BOM data initially
"""
import pandas as pd
import time
from collectors import BoxOfficeMojoCollector
from datetime import datetime

def update_bom_data(input_file='data/raw/movies_with_youtube.csv', 
                    only_missing=True,
                    only_recent=True):
    """
    Update Box Office Mojo data for movies in the dataset
    
    Args:
        input_file: Path to CSV file
        only_missing: Only update movies without BOM data
        only_recent: Only update movies from 2024 onwards
    """
    
    print("=" * 80)
    print("BOX OFFICE MOJO DATA UPDATE")
    print("=" * 80)
    
    # Load data
    df = pd.read_csv(input_file)
    df['release_date'] = pd.to_datetime(df['release_date'])
    
    print(f"\nTotal movies in dataset: {len(df):,}")
    
    # Filter movies to update
    mask = pd.Series([True] * len(df))
    
    if only_missing:
        mask = mask & df['bom_opening_weekend'].isna()
        print(f"Movies without BOM data: {mask.sum():,}")
    
    if only_recent:
        mask = mask & (df['release_date'] >= '2024-01-01')
        print(f"Movies from 2024+: {mask.sum():,}")
    
    movies_to_update = df[mask].copy()
    
    if len(movies_to_update) == 0:
        print("\nNo movies to update!")
        return df
    
    print(f"\nMovies to update: {len(movies_to_update):,}")
    print("\nNote: Box Office Mojo scraping is slow (~3-5 seconds per movie)")
    print(f"Estimated time: {len(movies_to_update) * 4 / 60:.1f} minutes")
    
    response = input("\nProceed? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return df
    
    # Initialize BOM collector
    bom = BoxOfficeMojoCollector()
    
    # Update BOM data
    print("\nUpdating Box Office Mojo data...")
    updated_count = 0
    
    for idx, row in movies_to_update.iterrows():
        try:
            title = row['title']
            year = row['release_date'].year
            
            # Search for movie
            movie_url = bom.search_movie(title, year)
            
            if movie_url:
                # Get box office data
                box_office = bom.get_box_office_data(movie_url)
                
                if box_office:
                    # Update DataFrame
                    df.at[idx, 'bom_url'] = movie_url
                    df.at[idx, 'bom_opening_weekend'] = box_office.get('opening_weekend')
                    df.at[idx, 'bom_domestic_total'] = box_office.get('domestic_gross')
                    df.at[idx, 'bom_worldwide_total'] = box_office.get('worldwide_gross')
                    df.at[idx, 'bom_international_total'] = box_office.get('international_gross')
                    
                    updated_count += 1
                    status = "✓ Updated"
                else:
                    status = "✗ No data"
            else:
                status = "✗ Not found"
            
            progress = f"{updated_count}/{len(movies_to_update)}"
            print(f"  [{progress}] {title[:40]:40s} - {status}", end='\r')
            
            time.sleep(3)  # Rate limiting
            
        except Exception as e:
            print(f"\n  Error processing {title}: {e}")
            continue
    
    print(f"\n\n✓ Updated {updated_count} movies")
    
    # Save updated data
    backup_path = input_file.replace('.csv', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    df_original = pd.read_csv(input_file)
    df_original.to_csv(backup_path, index=False)
    print(f"\n  Original backed up to: {backup_path}")
    
    df.to_csv(input_file, index=False)
    print(f"  Updated data saved to: {input_file}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total movies: {len(df):,}")
    print(f"Movies with BOM data: {df['bom_opening_weekend'].notna().sum():,}")
    print(f"Movies still missing BOM data: {df['bom_opening_weekend'].isna().sum():,}")
    
    return df


if __name__ == "__main__":
    # Update Box Office Mojo data
    print("\nOptions:")
    print("1. Update only missing BOM data (recent movies)")
    print("2. Update only missing BOM data (all movies)")
    print("3. Update all movies (refresh everything)")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        df = update_bom_data(only_missing=True, only_recent=True)
    elif choice == '2':
        df = update_bom_data(only_missing=True, only_recent=False)
    elif choice == '3':
        df = update_bom_data(only_missing=False, only_recent=False)
    else:
        print("Invalid choice.")
