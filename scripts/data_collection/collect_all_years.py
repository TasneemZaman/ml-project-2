#!/usr/bin/env python3
"""
Collect first week Box Office Mojo data for ALL movies (1990-2024)
Uses batch collection by date to efficiently scrape 4,793 movies
"""

import pandas as pd
import sys
from datetime import datetime
from collect_year_batch import YearBatchCollector, aggregate_movie_features

def collect_all_years(strategy='biweekly', start_year=1990, end_year=2024):
    """
    Collect data for all years in the dataset
    
    Args:
        strategy: 'biweekly' (27 dates/year, ~30min total) or 
                 'weekly' (52 dates/year, ~1hr total)
        start_year: First year to collect
        end_year: Last year to collect
    """
    print("="*80)
    print(f"COLLECTING FIRST WEEK DATA FOR ALL MOVIES ({start_year}-{end_year})")
    print("="*80)
    
    collector = YearBatchCollector()
    all_batch_data = []
    years = list(range(start_year, end_year + 1))
    
    print(f"\nStrategy: {strategy.upper()}")
    print(f"Years to collect: {len(years)}")
    
    if strategy == 'biweekly':
        total_dates = len(years) * 27
        est_time = total_dates * 2 / 60
    else:  # weekly
        total_dates = len(years) * 52
        est_time = total_dates * 2 / 60
    
    print(f"Total dates to scrape: {total_dates:,}")
    print(f"Estimated time: {est_time:.1f} minutes")
    print(f"\nStarting collection at {datetime.now().strftime('%H:%M:%S')}...")
    print("-" * 80)
    
    start_time = datetime.now()
    
    for i, year in enumerate(years, 1):
        print(f"\n[{i}/{len(years)}] Collecting {year}...")
        
        try:
            # Collect batch data for this year
            batch_df = collector.collect_year_batch(
                year=year, 
                strategy=strategy,
                verbose=False  # Less output per year
            )
            
            if batch_df is not None and len(batch_df) > 0:
                all_batch_data.append(batch_df)
                print(f"  ✅ {year}: {len(batch_df)} records, {batch_df['release'].nunique()} movies")
            else:
                print(f"  ⚠️  {year}: No data")
                
        except Exception as e:
            print(f"  ❌ {year}: Error - {e}")
            continue
        
        # Progress update every 5 years
        if i % 5 == 0:
            elapsed = (datetime.now() - start_time).total_seconds() / 60
            remaining = (len(years) - i) * (elapsed / i)
            print(f"\n  Progress: {i}/{len(years)} years ({elapsed:.1f}m elapsed, ~{remaining:.1f}m remaining)")
    
    print("\n" + "="*80)
    print("COMBINING ALL YEARS")
    print("="*80)
    
    if not all_batch_data:
        print("❌ No data collected!")
        return None
    
    # Combine all years
    combined_df = pd.concat(all_batch_data, ignore_index=True)
    
    # Save combined raw data
    output_file = 'data/processed/bom_all_years_batch.csv'
    combined_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Combined batch data saved: {output_file}")
    print(f"   Total records: {len(combined_df):,}")
    print(f"   Unique movies: {combined_df['release'].nunique():,}")
    print(f"   Date range: {combined_df['date'].min()} to {combined_df['date'].max()}")
    
    # Aggregate features
    print("\n" + "="*80)
    print("AGGREGATING FIRST WEEK FEATURES")
    print("="*80)
    
    # Load main dataset
    movies_df = pd.read_csv('data/raw/movies_with_youtube.csv')
    features_df = aggregate_movie_features(combined_df, movies_df)
    
    if features_df is None or len(features_df) == 0:
        print("❌ No movies with complete first week data")
        return combined_df
    
    # Save aggregated features
    features_file = 'data/processed/first_week_features_all_years.csv'
    features_df.to_csv(features_file, index=False)
    
    print(f"\n✅ First week features saved: {features_file}")
    print(f"   Movies with features: {len(features_df):,}")
    
    # Update main dataset
    print("\n" + "="*80)
    print("UPDATING MAIN DATASET")
    print("="*80)
    
    movies_df = pd.read_csv('data/raw/movies_with_youtube.csv')
    print(f"Original dataset: {len(movies_df):,} movies")
    
    # Merge features
    movies_df = movies_df.merge(
        features_df[['title', 'opening_theaters', 'opening_gross', 'opening_per_theater',
                     'first_week_gross', 'first_week_avg_daily', 'first_week_days_tracked',
                     'avg_yd_change', 'avg_lw_change', 'max_yd_gain', 'max_yd_drop',
                     'peak_theaters_week1', 'min_theaters_week1']],
        on='title',
        how='left',
        suffixes=('', '_new')
    )
    
    # Update columns (prefer new data)
    for col in ['opening_theaters', 'opening_gross', 'opening_per_theater',
                'first_week_gross', 'first_week_avg_daily', 'first_week_days_tracked',
                'avg_yd_change', 'avg_lw_change', 'max_yd_gain', 'max_yd_drop',
                'peak_theaters_week1', 'min_theaters_week1']:
        if f'{col}_new' in movies_df.columns:
            movies_df[col] = movies_df[f'{col}_new'].combine_first(movies_df.get(col, pd.Series()))
            movies_df.drop(columns=[f'{col}_new'], inplace=True)
    
    movies_df.to_csv('data/raw/movies_with_youtube.csv', index=False)
    
    movies_with_features = movies_df['first_week_gross'].notna().sum()
    print(f"✅ Updated dataset saved")
    print(f"   Movies with first week data: {movies_with_features:,} ({movies_with_features/len(movies_df)*100:.1f}%)")
    
    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    total_time = (datetime.now() - start_time).total_seconds() / 60
    
    print(f"\nCollection completed in {total_time:.1f} minutes")
    print(f"\nFirst week gross statistics:")
    print(f"  Mean: ${features_df['first_week_gross'].mean():,.0f}")
    print(f"  Median: ${features_df['first_week_gross'].median():,.0f}")
    print(f"  Min: ${features_df['first_week_gross'].min():,.0f}")
    print(f"  Max: ${features_df['first_week_gross'].max():,.0f}")
    
    print(f"\nOpening theaters statistics:")
    print(f"  Mean: {features_df['opening_theaters'].mean():.0f}")
    print(f"  Median: {features_df['opening_theaters'].median():.0f}")
    
    print(f"\n" + "="*80)
    print("READY FOR MODEL TRAINING!")
    print("="*80)
    print(f"\n✅ You now have {len(features_df):,} movies with first week data")
    print(f"✅ Train model: pre-release features → first_week_gross")
    print(f"✅ Predict Avatar: Fire & Ash first week revenue!")
    
    return combined_df, features_df


if __name__ == "__main__":
    # Get strategy from command line or use default
    strategy = sys.argv[1] if len(sys.argv) > 1 else 'biweekly'
    
    if strategy not in ['biweekly', 'weekly', 'smart']:
        print(f"Invalid strategy: {strategy}")
        print("Usage: python3 collect_all_years.py [biweekly|weekly|smart]")
        print("\nOptions:")
        print("  biweekly - Every 14 days (27 dates/year, ~30min total) [RECOMMENDED]")
        print("  weekly   - Every 7 days (52 dates/year, ~1hr total)")
        print("  smart    - Fridays + holidays (52 dates/year, ~1hr total)")
        sys.exit(1)
    
    collect_all_years(strategy=strategy)
