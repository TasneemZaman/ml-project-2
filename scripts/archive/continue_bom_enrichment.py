"""
Continue BOM enrichment from where it left off.
Only processes rows that don't have BOM data yet.
"""
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from boxoffice_mojo import get_bom_data
import requests
from tqdm import tqdm
import sys

def main():
    input_file = 'data/raw/tmdb_movies_with_bom.csv'
    
    print("Loading existing data...")
    df = pd.read_csv(input_file)
    
    print(f"Total movies: {len(df)}")
    print(f"Already have BOM data: {df['bom_url'].notna().sum()}")
    
    # Find movies without BOM data
    needs_bom = df['bom_url'].isna()
    rows_to_process = df[needs_bom].copy()
    
    print(f"Need to process: {len(rows_to_process)} movies")
    
    if len(rows_to_process) == 0:
        print("All movies already have BOM data!")
        return
    
    print("\nStarting BOM enrichment...")
    session = requests.Session()
    
    # Process in batches of 500
    batch_size = 500
    for batch_start in range(0, len(rows_to_process), batch_size):
        batch_end = min(batch_start + batch_size, len(rows_to_process))
        batch = rows_to_process.iloc[batch_start:batch_end]
        
        print(f"\n--- Processing batch {batch_start//batch_size + 1}: rows {batch_start} to {batch_end} ---")
        
        results = {}
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {}
            for idx, row in batch.iterrows():
                title = row['title']
                year = int(row['release_date'][:4]) if pd.notna(row['release_date']) and len(str(row['release_date'])) >= 4 else None
                futures[executor.submit(get_bom_data, title, year, session)] = idx
            
            for fut in tqdm(as_completed(futures), total=len(futures), desc="Fetching BOM data"):
                idx = futures[fut]
                try:
                    data = fut.result()
                    results[idx] = data
                except Exception as e:
                    print(f"Error processing row {idx}: {e}")
                    results[idx] = {
                        'bom_url': None,
                        'bom_opening_weekend': None,
                        'bom_first_week': None,
                        'bom_domestic_total': None,
                        'bom_worldwide_total': None,
                        'bom_international_total': None
                    }
        
        # Update dataframe with results
        for idx, data in results.items():
            df.at[idx, 'bom_url'] = data.get('bom_url')
            df.at[idx, 'bom_opening_weekend'] = data.get('bom_opening_weekend')
            df.at[idx, 'bom_first_week'] = data.get('bom_first_week')
            df.at[idx, 'bom_domestic_total'] = data.get('bom_domestic_total')
            df.at[idx, 'bom_worldwide_total'] = data.get('bom_worldwide_total')
            df.at[idx, 'bom_international_total'] = data.get('bom_international_total')
        
        # Save after each batch
        df.to_csv(input_file, index=False)
        completed = df['bom_url'].notna().sum()
        print(f"✓ Batch saved. Total completed: {completed}/{len(df)}")
    
    print("\n" + "=" * 80)
    print("ENRICHMENT COMPLETE!")
    print("=" * 80)
    print(f"Total movies: {len(df)}")
    print(f"Movies with BOM data: {df['bom_url'].notna().sum()}")
    print(f"Match rate: {df['bom_url'].notna().sum() / len(df) * 100:.1f}%")
    print(f"Saved to: {input_file}")

if __name__ == '__main__':
    main()
