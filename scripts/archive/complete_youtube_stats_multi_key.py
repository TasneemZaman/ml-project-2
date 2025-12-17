"""
Complete YouTube Statistics with Multiple API Keys
Automatically switches between API keys when quota is exhausted.

HOW TO GET MORE API KEYS (FREE):
1. Go to: https://console.cloud.google.com/
2. Create a new project (different from your existing one)
3. Enable YouTube Data API v3
4. Create credentials → API Key
5. Add the new key to the YOUTUBE_API_KEYS list below

Each key gives you 10,000 units/day = 10,000 movies per key!
"""

import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

# ADD YOUR API KEYS HERE - Each key can process ~10,000 movies/day
YOUTUBE_API_KEYS = [
    'AIzaSyAq1_WBOc8oxH6aLJRvfZ7qYXvnTXW8SvY',  # Key 2 (WORKING - starting here)
    'AIzaSyDzC_9SSisjBqIxzyoSW2o0ZXxDY28X5k0',   # Key 3 (WORKING)
    'AIzaSyD3ly3VRJM9v3U1d6-U_YjiR3HYxHkUgNQ',  # Key 4 (WORKING)
    'AIzaSyCYTc07IYBQ3zciaJmEQlF63IsFW94Y_v4',  # Key 1 (exhausted - will work tomorrow)
]

current_key_index = 0

def get_current_api_key():
    """Get the current API key."""
    return YOUTUBE_API_KEYS[current_key_index]

def switch_to_next_key():
    """Switch to the next available API key."""
    global current_key_index
    if current_key_index < len(YOUTUBE_API_KEYS) - 1:
        current_key_index += 1
        print(f"\n⚠️  Switching to API Key #{current_key_index + 1}")
        return get_current_api_key()
    return None

def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    if pd.isna(url) or not url:
        return None
    if 'watch?v=' in url:
        return url.split('watch?v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    return None

def get_youtube_stats(video_id, retry_count=0):
    """Get statistics for a YouTube video. Uses 1 quota unit."""
    url = 'https://www.googleapis.com/youtube/v3/videos'
    params = {
        'part': 'statistics',
        'id': video_id,
        'key': get_current_api_key()
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        # Handle quota exceeded
        if response.status_code == 403:
            error_data = response.json()
            if 'quota' in str(error_data).lower():
                if current_key_index < len(YOUTUBE_API_KEYS) - 1:
                    print(f"\n⚠️  Quota exhausted for Key #{current_key_index + 1}")
                    new_key = switch_to_next_key()
                    if new_key:
                        time.sleep(1)
                        return get_youtube_stats(video_id, retry_count + 1)
                
                print(f"\n❌ All {len(YOUTUBE_API_KEYS)} API keys exhausted!")
                return None
        
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
    if stats:
        return {
            'idx': idx,
            'youtube_views': stats['views'],
            'youtube_likes': stats['likes'],
            'youtube_comments': stats['comments']
        }
    return None

def complete_stats(csv_path='data/raw/movies_with_youtube.csv', workers=10, batch_size=500):
    """Complete YouTube statistics for movies with URLs but missing stats."""
    
    print("="*80)
    print("MULTI-KEY YOUTUBE STATISTICS COLLECTOR")
    print("="*80)
    print(f"Available API keys: {len(YOUTUBE_API_KEYS)}")
    print(f"Total daily quota: {len(YOUTUBE_API_KEYS) * 10000:,} units")
    print(f"Max movies per day: {len(YOUTUBE_API_KEYS) * 10000:,}")
    print()
    
    print("Loading dataset...")
    df = pd.read_csv(csv_path)
    
    # Find rows that need stats
    needs_stats = df[df['youtube_trailer_url'].notna() & df['youtube_views'].isna()]
    print(f"Total movies: {len(df):,}")
    print(f"With trailer URLs: {df['youtube_trailer_url'].notna().sum():,}")
    print(f"Need statistics: {len(needs_stats):,}")
    
    if len(needs_stats) == 0:
        print("✅ All movies already have YouTube statistics!")
        return
    
    # Check if we have enough quota
    total_quota = len(YOUTUBE_API_KEYS) * 10000
    if len(needs_stats) > total_quota:
        print(f"\n⚠️  WARNING: Need {len(needs_stats):,} units but only have {total_quota:,} units today")
        print(f"   Will process first {total_quota:,} movies, remaining tomorrow")
    
    print(f"\n🚀 Fetching YouTube statistics:")
    print(f"   - Using {workers} parallel workers")
    print(f"   - Starting with API Key #1")
    print(f"   - Processing in batches of {batch_size}")
    
    total_batches = (len(needs_stats) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(needs_stats))
        batch = needs_stats.iloc[start_idx:end_idx]
        
        print(f"\n--- Batch {batch_num + 1}/{total_batches} ({len(batch)} movies) ---")
        print(f"Current API Key: #{current_key_index + 1}/{len(YOUTUBE_API_KEYS)}")
        
        results = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(process_row, row) for _, row in batch.iterrows()]
            
            for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching stats"):
                result = future.result()
                if result:
                    results.append(result)
        
        # Update DataFrame
        for result in results:
            idx = result['idx']
            df.at[idx, 'youtube_views'] = result['youtube_views']
            df.at[idx, 'youtube_likes'] = result['youtube_likes']
            df.at[idx, 'youtube_comments'] = result['youtube_comments']
        
        # Save progress
        df.to_csv(csv_path, index=False)
        completed = df['youtube_views'].notna().sum()
        print(f"✓ Saved. Total with stats: {completed:,}/{len(df):,} ({completed/len(df)*100:.1f}%)")
        
        # Check if all keys exhausted
        if current_key_index == len(YOUTUBE_API_KEYS) - 1:
            remaining = df['youtube_views'].isna().sum()
            if remaining > 0:
                print(f"\n⚠️  All API keys exhausted. Remaining movies: {remaining:,}")
                print("   Get more API keys or wait until tomorrow")
                break
    
    print("\n" + "="*80)
    print("STATISTICS COLLECTION COMPLETE!")
    print("="*80)
    
    # Final summary
    with_stats = df['youtube_views'].notna()
    print(f"Total movies: {len(df):,}")
    print(f"With YouTube statistics: {with_stats.sum():,} ({with_stats.sum()/len(df)*100:.1f}%)")
    
    if with_stats.sum() > 0:
        print()
        print("YouTube Engagement Stats:")
        print(f"  Average views: {df.loc[with_stats, 'youtube_views'].mean():,.0f}")
        print(f"  Median views: {df.loc[with_stats, 'youtube_views'].median():,.0f}")
        print(f"  Average likes: {df.loc[with_stats, 'youtube_likes'].mean():,.0f}")
        print(f"  Average comments: {df.loc[with_stats, 'youtube_comments'].mean():,.0f}")
        print()
        print("🏆 TOP 10 MOST VIEWED TRAILERS:")
        top10 = df.nlargest(10, 'youtube_views')[['title', 'release_date', 'youtube_views', 'youtube_likes']]
        for i, row in top10.iterrows():
            print(f"  {row['title']:40s} ({row['release_date'][:4]}) - {row['youtube_views']/1e6:.1f}M views, {row['youtube_likes']/1e6:.1f}M likes")

if __name__ == '__main__':
    complete_stats()
