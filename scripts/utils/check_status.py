"""
Check current data collection status
Quick overview of what data you have collected
"""
import pandas as pd
import os

def check_status():
    """Check the status of data collection."""
    print("\n" + "="*80)
    print("DATA COLLECTION STATUS")
    print("="*80 + "\n")
    
    data_files = {
        'Base (TMDB)': 'data/raw/movies_base.csv',
        'With YouTube': 'data/raw/movies_with_youtube.csv',
        'With Box Office': 'data/raw/movies_with_boxoffice.csv',
        'Complete': 'data/raw/movies_complete.csv',
        'TMDB with BOM (old)': 'data/raw/tmdb_movies_with_bom.csv',
        'With YouTube (old)': 'data/raw/movies_with_youtube.csv'
    }
    
    found_any = False
    
    for name, filepath in data_files.items():
        if os.path.exists(filepath):
            found_any = True
            try:
                df = pd.read_csv(filepath)
                print(f"📊 {name}")
                print(f"   File: {filepath}")
                print(f"   Movies: {len(df):,}")
                print(f"   Columns: {len(df.columns)}")
                
                # Check data completeness for key columns
                key_cols = {
                    'youtube_video_id': 'YouTube',
                    'youtube_views': 'YouTube Views',
                    'domestic_gross': 'Box Office',
                    'trends_avg_interest': 'Google Trends'
                }
                
                for col, label in key_cols.items():
                    if col in df.columns:
                        complete = df[col].notna().sum()
                        pct = (complete / len(df)) * 100
                        print(f"   {label}: {complete:,}/{len(df):,} ({pct:.1f}%)")
                
                print()
            except Exception as e:
                print(f"   ⚠️  Error reading file: {e}\n")
    
    if not found_any:
        print("❌ No data files found!")
        print("\nRun 'python data_pipeline.py' to start collecting data.\n")
    else:
        print("="*80)
        print("\n💡 To collect more data, run: python data_pipeline.py")
        print("💡 To train models, open: complete_ml_pipeline.ipynb\n")

if __name__ == '__main__':
    check_status()
