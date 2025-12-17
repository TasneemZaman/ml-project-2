"""
SMART YouTube data collector - uses TMDB for trailer links (free) 
then YouTube API only for statistics (1 unit per movie).
This allows 10,000 movies per day instead of 95!
"""
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

YOUTUBE_API_KEY = 'AIzaSyCYTc07IYBQ3zciaJmEQlF63IsFW94Y_v4'
YOUTUBE_API_BASE = 'https://www.googleapis.com/youtube/v3'
TMDB_API_KEY = 'd429e3e7a57fe68708d1380b99dbdf43'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

def get_tmdb_trailer(tmdb_id):
    """Get YouTube trailer ID from TMDB (FREE, unlimited)."""
    url = f'{TMDB_BASE_URL}/movie/{tmdb_id}/videos'
    params = {'api_key': TMDB_API_KEY}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.ok:
            videos = response.json().get('results', [])
            # Find official trailer
            for video in videos:
                if video.get('site') == 'YouTube' and video.get('type') in ['Trailer', 'Teaser']:
                    return video.get('key')  # YouTube video ID
    except Exception as e:
        pass
    return None

def get_youtube_stats(video_id):
    """Get YouTube video statistics (1 quota unit)."""
    url = f"{YOUTUBE_API_BASE}/videos"
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
    except Exception:
        pass
    return None

def process_movie_smart(row):
    """Process one movie: TMDB for trailer link, YouTube for stats."""
    idx = row.name
    tmdb_id = row.get('tmdb_id')
    
    result = {
        'idx': idx,
        'youtube_trailer_url': None,
        'youtube_views': None,
        'youtube_likes': None,
        'youtube_comments': None
    }
    
    if pd.notna(tmdb_id):
        # Step 1: Get trailer ID from TMDB (free)
        video_id = get_tmdb_trailer(int(tmdb_id))
        
        if video_id:
            result['youtube_trailer_url'] = f'https://www.youtube.com/watch?v={video_id}'
            
            # Step 2: Get stats from YouTube (1 quota unit)
            stats = get_youtube_stats(video_id)
            if stats:
                result['youtube_views'] = stats['views']
                result['youtube_likes'] = stats['likes']
                result['youtube_comments'] = stats['comments']
    
    return result

def enrich_smart(input_csv='data/raw/tmdb_movies_with_bom.csv',
                 output_csv='data/raw/movies_with_youtube.csv',
                 workers=10,
                 batch_size=500):
    """Smart enrichment: TMDB + YouTube."""
    
    print("Loading dataset...")
    df = pd.read_csv(input_csv)
    
    # Add YouTube columns if needed
    youtube_cols = ['youtube_trailer_url', 'youtube_views', 'youtube_likes', 'youtube_comments']
    for col in youtube_cols:
        if col not in df.columns:
            df[col] = None
    
    # Check if we have existing YouTube data
    if 'youtube_trailer_url' in df.columns:
        needs_youtube = df['youtube_trailer_url'].isna()
        rows_to_process = df[needs_youtube]
        print(f"Already processed: {(~needs_youtube).sum()} movies")
    else:
        rows_to_process = df
    
    print(f"Total movies: {len(df)}")
    print(f"Need to process: {len(rows_to_process)}")
    
    if len(rows_to_process) == 0:
        print("✅ All movies already have YouTube data!")
        return
    
    print(f"\n🚀 SMART MODE:")
    print(f"   - TMDB API for trailer links (FREE, unlimited)")
    print(f"   - YouTube API only for statistics (1 unit per movie)")
    print(f"   - Using {workers} parallel workers")
    print(f"   - Daily limit: ~10,000 movies (vs 95 with old method)")
    print(f"   - Estimated time: {len(rows_to_process) / (workers * 20) / 60:.1f} minutes\n")
    
    total_processed = 0
    
    for batch_num in range(0, len(rows_to_process), batch_size):
        batch = rows_to_process.iloc[batch_num:batch_num + batch_size]
        batch_number = (batch_num // batch_size) + 1
        total_batches = (len(rows_to_process) + batch_size - 1) // batch_size
        
        print(f"--- Batch {batch_number}/{total_batches} ({len(batch)} movies) ---")
        
        results = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(process_movie_smart, row): row for _, row in batch.iterrows()}
            
            for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching data"):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    row = futures[future]
                    results.append({
                        'idx': row.name,
                        'youtube_trailer_url': None,
                        'youtube_views': None,
                        'youtube_likes': None,
                        'youtube_comments': None
                    })
        
        # Update dataframe
        for result in results:
            idx = result['idx']
            df.at[idx, 'youtube_trailer_url'] = result['youtube_trailer_url']
            df.at[idx, 'youtube_views'] = result['youtube_views']
            df.at[idx, 'youtube_likes'] = result['youtube_likes']
            df.at[idx, 'youtube_comments'] = result['youtube_comments']
        
        total_processed += len(batch)
        
        # Save progress
        df.to_csv(output_csv, index=False)
        completed = df['youtube_trailer_url'].notna().sum()
        print(f"✓ Saved. Total: {completed}/{len(df)} ({completed/len(df)*100:.1f}%)")
        print(f"Progress: {total_processed}/{len(rows_to_process)}\n")
    
    print("=" * 100)
    print("ENRICHMENT COMPLETE!")
    print("=" * 100)
    print(f"Total movies: {len(df)}")
    print(f"With YouTube data: {df['youtube_trailer_url'].notna().sum()} ({df['youtube_trailer_url'].notna().sum()/len(df)*100:.1f}%)")
    
    if df['youtube_views'].notna().sum() > 0:
        print(f"\n📊 STATISTICS:")
        print(f"   Average views: {df['youtube_views'].mean():,.0f}")
        print(f"   Max views: {df['youtube_views'].max():,.0f}")
        print(f"   Average likes: {df['youtube_likes'].mean():,.0f}")

if __name__ == '__main__':
    enrich_smart()
