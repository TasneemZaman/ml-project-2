"""
Complete YouTube Statistics for Movies
Fetches statistics for movies that already have trailer URLs but missing views/likes/comments.
Only uses 1 API quota unit per movie.
"""

import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

YOUTUBE_API_KEY = 'AIzaSyCYTc07IYBQ3zciaJmEQlF63IsFW94Y_v4'

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
    
    print(f"\n🚀 Fetching YouTube statistics:")
    print(f"   - Using {workers} parallel workers")
    print(f"   - Quota cost: 1 unit per movie")
    print(f"   - Total quota needed: {len(needs_stats):,} units")
    print(f"   - Processing in batches of {batch_size}")
    
    total_batches = (len(needs_stats) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(needs_stats))
        batch = needs_stats.iloc[start_idx:end_idx]
        
        print(f"\n--- Batch {batch_num + 1}/{total_batches} ({len(batch)} movies) ---")
        
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
    
    print("\n" + "="*80)
    print("STATISTICS COMPLETE!")
    print("="*80)
    
    # Final summary
    with_stats = df['youtube_views'].notna()
    print(f"Total movies: {len(df):,}")
    print(f"With YouTube statistics: {with_stats.sum():,} ({with_stats.sum()/len(df)*100:.1f}%)")
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
