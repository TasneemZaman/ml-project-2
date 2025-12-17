"""
STANDALONE YOUTUBE STATISTICS COLLECTOR
Run this on ANY computer to bypass your local quota limit!

SETUP (ONE-TIME):
1. Copy this file to another computer/server
2. Install dependencies: pip install pandas requests tqdm
3. Download movies_with_youtube.csv from your local machine
4. Run: python3 standalone_youtube_collector.py
5. Upload the completed file back to your local machine

This script is 100% portable and works anywhere!
"""

import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import sys

# ============================================================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================================================

# Put YOUR YouTube API key here (or get a new one from Google Cloud Console)
YOUTUBE_API_KEY = 'AIzaSyCYTc07IYBQ3zciaJmEQlF63IsFW94Y_v4'

# Input/Output files (will be in same directory as this script)
INPUT_CSV = 'movies_with_youtube.csv'
OUTPUT_CSV = 'movies_with_youtube_complete.csv'

# Performance settings
WORKERS = 10  # Parallel workers
BATCH_SIZE = 500  # Save progress every N movies

# ============================================================================
# CODE - NO NEED TO EDIT BELOW THIS LINE
# ============================================================================

def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    if pd.isna(url) or not url:
        return None
    if 'watch?v=' in url:
        return url.split('watch?v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    return None

def get_youtube_stats(video_id):
    """Get statistics for a YouTube video. Uses 1 quota unit."""
    url = 'https://www.googleapis.com/youtube/v3/videos'
    params = {
        'part': 'statistics',
        'id': video_id,
        'key': YOUTUBE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 403:
            error_data = response.json()
            if 'quota' in str(error_data).lower():
                print("\n❌ API quota exhausted! Process stopped.")
                return 'QUOTA_EXCEEDED'
        
        if response.status_code == 200:
            items = response.json().get('items', [])
            if items:
                stats = items[0].get('statistics', {})
                return {
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'comments': int(stats.get('commentCount', 0))
                }
    except Exception as e:
        pass
    return None

def process_row(row):
    """Process one movie row."""
    idx = row.name
    url = row.get('youtube_trailer_url')
    
    # Skip if already has views data
    if pd.notna(row.get('youtube_views')):
        return None
    
    video_id = extract_video_id(url)
    if not video_id:
        return None
    
    stats = get_youtube_stats(video_id)
    
    if stats == 'QUOTA_EXCEEDED':
        return 'QUOTA_EXCEEDED'
    
    if stats:
        return {
            'idx': idx,
            'youtube_views': stats['views'],
            'youtube_likes': stats['likes'],
            'youtube_comments': stats['comments']
        }
    return None

def main():
    """Main function."""
    print("="*80)
    print("STANDALONE YOUTUBE STATISTICS COLLECTOR")
    print("="*80)
    print(f"Input file: {INPUT_CSV}")
    print(f"Output file: {OUTPUT_CSV}")
    print(f"Workers: {WORKERS}")
    print()
    
    # Load data
    try:
        print("Loading dataset...")
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"❌ ERROR: {INPUT_CSV} not found!")
        print("\nInstructions:")
        print("1. Download movies_with_youtube.csv from your local machine")
        print("2. Put it in the same folder as this script")
        print("3. Run again")
        sys.exit(1)
    
    # Find rows that need stats
    needs_stats = df[df['youtube_trailer_url'].notna() & df['youtube_views'].isna()]
    print(f"Total movies: {len(df):,}")
    print(f"With trailer URLs: {df['youtube_trailer_url'].notna().sum():,}")
    print(f"Need statistics: {len(needs_stats):,}")
    
    if len(needs_stats) == 0:
        print("✅ All movies already have YouTube statistics!")
        return
    
    print(f"\n🚀 Fetching YouTube statistics:")
    print(f"   - Quota cost: 1 unit per movie = {len(needs_stats):,} units total")
    print(f"   - Daily limit: 10,000 units")
    
    if len(needs_stats) > 10000:
        print(f"   ⚠️  Will need multiple days or multiple API keys")
    
    total_batches = (len(needs_stats) + BATCH_SIZE - 1) // BATCH_SIZE
    quota_exceeded = False
    
    for batch_num in range(total_batches):
        if quota_exceeded:
            break
            
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(needs_stats))
        batch = needs_stats.iloc[start_idx:end_idx]
        
        print(f"\n--- Batch {batch_num + 1}/{total_batches} ({len(batch)} movies) ---")
        
        results = []
        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            futures = [executor.submit(process_row, row) for _, row in batch.iterrows()]
            
            for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching stats"):
                result = future.result()
                
                if result == 'QUOTA_EXCEEDED':
                    quota_exceeded = True
                    print("\n⚠️  Quota exceeded - saving progress and stopping")
                    break
                    
                if result:
                    results.append(result)
        
        # Update DataFrame
        for result in results:
            if result != 'QUOTA_EXCEEDED':
                idx = result['idx']
                df.at[idx, 'youtube_views'] = result['youtube_views']
                df.at[idx, 'youtube_likes'] = result['youtube_likes']
                df.at[idx, 'youtube_comments'] = result['youtube_comments']
        
        # Save progress
        df.to_csv(OUTPUT_CSV, index=False)
        completed = df['youtube_views'].notna().sum()
        print(f"✓ Saved to {OUTPUT_CSV}")
        print(f"  Total with stats: {completed:,}/{len(df):,} ({completed/len(df)*100:.1f}%)")
    
    print("\n" + "="*80)
    if quota_exceeded:
        print("QUOTA EXCEEDED - PARTIAL COMPLETION")
        remaining = df['youtube_views'].isna().sum()
        print(f"Remaining movies: {remaining:,}")
        print("\nOptions:")
        print("1. Wait 24 hours and run again")
        print("2. Get a new API key from Google Cloud Console")
        print("3. Run this script on a different computer with a different API key")
    else:
        print("COLLECTION COMPLETE!")
    print("="*80)
    
    # Final summary
    with_stats = df['youtube_views'].notna()
    print(f"\nTotal movies: {len(df):,}")
    print(f"With YouTube statistics: {with_stats.sum():,} ({with_stats.sum()/len(df)*100:.1f}%)")
    
    if with_stats.sum() > 0:
        print()
        print("YouTube Engagement Stats:")
        print(f"  Average views: {df.loc[with_stats, 'youtube_views'].mean():,.0f}")
        print(f"  Median views: {df.loc[with_stats, 'youtube_views'].median():,.0f}")
        print(f"  Average likes: {df.loc[with_stats, 'youtube_likes'].mean():,.0f}")
        print(f"  Average comments: {df.loc[with_stats, 'youtube_comments'].mean():,.0f}")
        
        if len(df.nlargest(10, 'youtube_views')) > 0:
            print()
            print("🏆 TOP 10 MOST VIEWED TRAILERS:")
            top10 = df.nlargest(10, 'youtube_views')[['title', 'release_date', 'youtube_views', 'youtube_likes']]
            for i, row in top10.iterrows():
                print(f"  {row['title']:40s} ({row['release_date'][:4]}) - {row['youtube_views']/1e6:.1f}M views, {row['youtube_likes']/1e6:.1f}M likes")
    
    print(f"\n✅ Output saved to: {OUTPUT_CSV}")
    print("   Upload this file back to your local machine!")

if __name__ == '__main__':
    main()
