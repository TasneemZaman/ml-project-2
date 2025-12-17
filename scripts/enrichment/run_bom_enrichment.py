"""
Run Box Office Mojo Daily Data Enrichment
Usage: python3 run_bom_enrichment.py [mode]

Modes:
  quick   - Collect last 30 days only (~2 minutes)
  recent  - Collect last 6 months (~20 minutes)  
  full    - Collect full year 2024-2025 (~30 minutes)
  test    - Just test with sample data
"""
import sys
import subprocess

modes = {
    'test': {
        'start': '2025-12-13',
        'end': '2025-12-13',
        'desc': 'Test with single day',
        'time': '10 seconds'
    },
    'quick': {
        'start': '2025-11-21',
        'end': '2025-12-21',
        'desc': 'Last 30 days',
        'time': '~2 minutes'
    },
    'recent': {
        'start': '2025-06-21',
        'end': '2025-12-21',
        'desc': 'Last 6 months',
        'time': '~15 minutes'
    },
    'full': {
        'start': '2024-01-01',
        'end': '2025-12-21',
        'desc': 'Full year+ (2024-2025)',
        'time': '~30 minutes'
    }
}

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'quick'
    
    if mode not in modes:
        print("Invalid mode. Available modes:")
        for m, info in modes.items():
            print(f"  {m:10s} - {info['desc']:30s} (Est: {info['time']})")
        return
    
    config = modes[mode]
    
    print("=" * 80)
    print(f"BOX OFFICE MOJO DAILY DATA ENRICHMENT - {mode.upper()} MODE")
    print("=" * 80)
    print(f"Description: {config['desc']}")
    print(f"Date Range: {config['start']} to {config['end']}")
    print(f"Estimated Time: {config['time']}")
    print("=" * 80)
    
    response = input(f"\nProceed with {mode} mode? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Import and run enrichment
    from enrich_with_daily_bom import enrich_dataset_with_daily_data
    
    print("\nStarting enrichment...")
    enrich_dataset_with_daily_data(
        input_file='data/raw/movies_with_youtube.csv',
        start_date=config['start'],
        end_date=config['end'],
        sample_size=None
    )
    
    print("\n" + "=" * 80)
    print("ENRICHMENT COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Open complete_ml_pipeline.ipynb")
    print("2. Reload data: df = pd.read_csv('data/raw/movies_with_youtube.csv')")
    print("3. Add daily features to your model")
    print("4. Retrain and compare performance!")

if __name__ == '__main__':
    main()
