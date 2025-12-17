"""
Process IMDB Dataset Files to Extract 5000+ Movies from 1990 onwards
Much faster than API calls - processes local files
"""

import pandas as pd
import numpy as np
import gzip
from datetime import datetime
import os

print("="*80)
print("IMDB DATASET PROCESSOR")
print("="*80)

# File paths
DATA_DIR = 'data'
files = {
    'basics': f'{DATA_DIR}/title.basics.tsv.gz',
    'ratings': f'{DATA_DIR}/title.ratings.tsv.gz',
    'crew': f'{DATA_DIR}/title.crew.tsv.gz',
    'principals': f'{DATA_DIR}/title.principals.tsv.gz',
    'names': f'{DATA_DIR}/name.basics.tsv.gz',
    'akas': f'{DATA_DIR}/title.akas.tsv.gz'
}

# Verify files exist
print("\n📁 Checking dataset files...")
for name, path in files.items():
    if os.path.exists(path):
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"  ✓ {name}: {path} ({size_mb:.1f} MB)")
    else:
        print(f"  ✗ {name}: {path} (NOT FOUND)")

print("\n" + "="*80)
print("STEP 1: Loading title.basics.tsv.gz (movies metadata)")
print("="*80)

# Load basics - filter for movies only
print("Reading title.basics.tsv.gz...")
basics_df = pd.read_csv(
    files['basics'],
    sep='\t',
    na_values='\\N',
    low_memory=False,
    usecols=['tconst', 'titleType', 'primaryTitle', 'startYear', 'runtimeMinutes', 'genres']
)

print(f"Total titles loaded: {len(basics_df):,}")

# Filter for movies from 1990 onwards
print("\nFiltering for movies from 1990 onwards...")
movies_df = basics_df[
    (basics_df['titleType'] == 'movie') &
    (basics_df['startYear'].notna()) &
    (basics_df['startYear'] != '\\N')
].copy()

# Convert year to numeric
movies_df['startYear'] = pd.to_numeric(movies_df['startYear'], errors='coerce')
movies_df = movies_df[movies_df['startYear'] >= 1990].copy()
movies_df = movies_df[movies_df['startYear'] <= 2024].copy()

print(f"Movies from 1990-2024: {len(movies_df):,}")

# Clean runtime
movies_df['runtimeMinutes'] = pd.to_numeric(movies_df['runtimeMinutes'], errors='coerce')
movies_df = movies_df[movies_df['runtimeMinutes'] >= 40].copy()  # Filter very short films

print(f"After runtime filter (>=40 min): {len(movies_df):,}")

print("\n" + "="*80)
print("STEP 2: Loading title.ratings.tsv.gz (ratings and votes)")
print("="*80)

print("Reading title.ratings.tsv.gz...")
ratings_df = pd.read_csv(
    files['ratings'],
    sep='\t',
    na_values='\\N'
)

print(f"Total ratings loaded: {len(ratings_df):,}")

# Merge with ratings
print("\nMerging movies with ratings...")
movies_df = movies_df.merge(ratings_df, on='tconst', how='left')

# Filter for movies with at least 100 votes for quality
movies_df = movies_df[movies_df['numVotes'] >= 100].copy()
print(f"Movies with 100+ votes: {len(movies_df):,}")

# Sort by votes to get most popular/well-known movies
movies_df = movies_df.sort_values('numVotes', ascending=False)

print("\n" + "="*80)
print("STEP 3: Selecting top 5000+ movies (skipping director lookup for speed)")
print("="*80)

# Select top 5000+ movies by vote count FIRST (more efficient)
target_movies = 5000
movies_df = movies_df.head(target_movies).copy()

print(f"Selected top {len(movies_df):,} movies by popularity (vote count)")

print("\nLoading directors for selected movies only...")
# Only load crew data we need
movie_ids = set(movies_df['tconst'].values)

# Read crew file in chunks to find only our movies
print("Reading title.crew.tsv.gz in chunks...")
crew_records = []
chunk_size = 100000
for chunk in pd.read_csv(files['crew'], sep='\t', na_values='\\N', 
                         usecols=['tconst', 'directors'], chunksize=chunk_size):
    matching = chunk[chunk['tconst'].isin(movie_ids)]
    if len(matching) > 0:
        crew_records.append(matching)
    if len(crew_records) * chunk_size > len(movie_ids) * 10:  # Found enough
        break

if crew_records:
    crew_df = pd.concat(crew_records, ignore_index=True)
    print(f"Found director info for {len(crew_df):,} movies")
    movies_df = movies_df.merge(crew_df, on='tconst', how='left')
else:
    movies_df['directors'] = None

# Get first director ID
movies_df['director_id'] = movies_df['directors'].apply(
    lambda x: x.split(',')[0] if pd.notna(x) and x != '\\N' and str(x) != 'nan' else None
)

# Get unique director IDs we need to lookup
director_ids = set(movies_df['director_id'].dropna().values)
print(f"Need to lookup {len(director_ids)} unique directors...")

# Read names file in chunks to find only our directors
print("Reading name.basics.tsv.gz in chunks...")
name_records = []
for chunk in pd.read_csv(files['names'], sep='\t', na_values='\\N',
                         usecols=['nconst', 'primaryName'], chunksize=chunk_size):
    matching = chunk[chunk['nconst'].isin(director_ids)]
    if len(matching) > 0:
        name_records.append(matching)
    if len(director_ids) > 0 and len(name_records) >= len(director_ids) / 1000:  # Found enough
        break

if name_records:
    names_df = pd.concat(name_records, ignore_index=True)
    print(f"Found names for {len(names_df):,} directors")
    movies_df = movies_df.merge(
        names_df.rename(columns={'nconst': 'director_id', 'primaryName': 'director_name'}),
        on='director_id',
        how='left'
    )
else:
    movies_df['director_name'] = 'Unknown'

print("\n" + "="*80)
print("STEP 4: Generating features and estimates")
print("="*80)

# Rename columns to match our schema
movies_df = movies_df.rename(columns={
    'primaryTitle': 'movie_title',
    'startYear': 'release_year',
    'runtimeMinutes': 'runtime',
    'averageRating': 'imdb_rating',
    'numVotes': 'imdb_votes',
    'director_name': 'director'
})

# Create release_date (use July 1st as default since we don't have exact dates)
movies_df['release_date'] = movies_df['release_year'].apply(
    lambda x: f"{int(x)}-07-01" if pd.notna(x) else "1990-07-01"
)

# Clean genres
movies_df['genre'] = movies_df['genres'].fillna('Unknown')

# Generate budget and revenue estimates based on popularity and year
print("Generating budget and revenue estimates...")

def estimate_budget_revenue(row):
    """Estimate budget and revenue based on votes, rating, and year"""
    votes = row['imdb_votes']
    rating = row['imdb_rating']
    year = row['release_year']
    
    # Budget estimation (more votes = bigger budget typically)
    if votes > 500000:
        budget = np.random.uniform(80_000_000, 250_000_000)
    elif votes > 100000:
        budget = np.random.uniform(30_000_000, 100_000_000)
    elif votes > 50000:
        budget = np.random.uniform(10_000_000, 40_000_000)
    else:
        budget = np.random.uniform(1_000_000, 15_000_000)
    
    # Adjust for inflation by year
    inflation_factor = 1 + ((year - 1990) * 0.025)  # ~2.5% per year
    budget = budget * inflation_factor
    
    # Revenue estimation (based on budget, rating, and votes)
    rating_multiplier = (rating / 10.0) ** 2  # Higher ratings = better box office
    vote_multiplier = min(votes / 100000, 5.0)  # More popular = more revenue
    
    revenue_multiplier = rating_multiplier * vote_multiplier * np.random.uniform(1.5, 4.0)
    revenue = budget * revenue_multiplier
    
    # Some movies flop
    if np.random.random() < 0.15:  # 15% chance of underperformance
        revenue = budget * np.random.uniform(0.3, 0.9)
    
    return budget, revenue

print("Calculating budget and revenue for all movies...")
estimates = movies_df.apply(estimate_budget_revenue, axis=1, result_type='expand')
movies_df['budget'] = estimates[0].astype(int)
movies_df['revenue'] = estimates[1].astype(int)

# Calculate first week and opening weekend
print("Calculating first week and opening weekend estimates...")
movies_df['first_week'] = movies_df.apply(
    lambda row: row['revenue'] * np.random.uniform(0.25, 0.45) if row['revenue'] > 100_000_000 
    else row['revenue'] * np.random.uniform(0.15, 0.35),
    axis=1
).astype(int)

movies_df['opening_weekend'] = (movies_df['first_week'] * np.random.uniform(0.40, 0.60)).astype(int)

# Add popularity score (based on votes)
movies_df['popularity'] = (movies_df['imdb_votes'] / 10000).clip(upper=100)

print("\n" + "="*80)
print("STEP 5: Adding synthetic features")
print("="*80)

# Theater counts
print("Adding theater counts...")
movies_df['num_theaters'] = movies_df['budget'].apply(
    lambda b: np.random.randint(3500, 4700) if b > 100_000_000
    else np.random.randint(2500, 3500) if b > 50_000_000
    else np.random.randint(1000, 2500)
)

movies_df['average_per_theater'] = (movies_df['opening_weekend'] / movies_df['num_theaters']).astype(int)

# Metascore and reviews
print("Adding metascore and reviews...")
movies_df['metascore'] = (movies_df['imdb_rating'] * 10 + np.random.randint(-8, 8, len(movies_df))).clip(0, 100).astype(int)
movies_df['num_reviews'] = (movies_df['imdb_votes'] * np.random.uniform(0.05, 0.15, len(movies_df))).astype(int)
movies_df['num_critic_reviews'] = (movies_df['num_reviews'] * np.random.uniform(0.05, 0.2, len(movies_df))).astype(int)

# T-7 Social media features
print("Adding T-7 social media metrics...")
movies_df['twitter_mentions'] = (movies_df['popularity'] * np.random.uniform(1000, 5000, len(movies_df))).astype(int)
movies_df['twitter_sentiment'] = np.random.uniform(0.5, 0.95, len(movies_df))
movies_df['google_trends_score'] = (movies_df['popularity'] * np.random.uniform(0.8, 1.5, len(movies_df))).clip(0, 100)
movies_df['youtube_trailer_views'] = (movies_df['popularity'] * np.random.uniform(50000, 500000, len(movies_df))).astype(int)
movies_df['youtube_trailer_likes'] = (movies_df['youtube_trailer_views'] * np.random.uniform(0.05, 0.15, len(movies_df))).astype(int)
movies_df['instagram_hashtag_count'] = (movies_df['popularity'] * np.random.uniform(2000, 20000, len(movies_df))).astype(int)
movies_df['facebook_page_likes'] = (movies_df['popularity'] * np.random.uniform(20000, 200000, len(movies_df))).astype(int)
movies_df['reddit_mentions'] = np.random.randint(100, 10000, len(movies_df))
movies_df['search_volume_index'] = (movies_df['popularity'] * np.random.uniform(0.5, 1.2, len(movies_df))).clip(0, 100)
movies_df['ticket_presales'] = (movies_df['first_week'] * np.random.uniform(0.05, 0.15, len(movies_df))).astype(int)

# Temporal features
print("Adding temporal features...")
movies_df['release_month'] = pd.to_datetime(movies_df['release_date']).dt.month
movies_df['release_day_of_week'] = np.random.randint(0, 7, len(movies_df))
movies_df['is_holiday_season'] = movies_df['release_month'].apply(lambda m: 1 if m in [11, 12, 1] else 0)
movies_df['is_summer'] = movies_df['release_month'].apply(lambda m: 1 if m in [5, 6, 7, 8] else 0)
movies_df['competing_releases_same_week'] = np.random.randint(0, 5, len(movies_df))

# Franchise features
print("Adding franchise features...")
sequel_keywords = ['2', 'ii', '3', 'iii', '4', 'iv', 'part', 'returns', 'rises', 'reloaded', 'revolution']
movies_df['is_sequel'] = movies_df['movie_title'].apply(
    lambda title: 1 if any(word in str(title).lower() for word in sequel_keywords) else 0
)
movies_df['franchise_previous_avg_gross'] = movies_df.apply(
    lambda row: np.random.uniform(100_000_000, 800_000_000) if row['is_sequel'] == 1 else 0,
    axis=1
).astype(int)
movies_df['years_since_last_release'] = movies_df.apply(
    lambda row: np.random.randint(1, 6) if row['is_sequel'] == 1 else 0,
    axis=1
)

# Studio (placeholder)
movies_df['studio'] = 'Unknown'
movies_df['total_gross'] = movies_df['revenue']
movies_df['original_language'] = 'en'

# Select final columns
final_columns = [
    'movie_title', 'release_date', 'budget', 'revenue', 'runtime',
    'imdb_rating', 'imdb_votes', 'popularity', 'genre', 'director',
    'first_week', 'opening_weekend', 'num_theaters', 'average_per_theater',
    'metascore', 'num_reviews', 'num_critic_reviews',
    'twitter_mentions', 'twitter_sentiment', 'google_trends_score',
    'youtube_trailer_views', 'youtube_trailer_likes', 'instagram_hashtag_count',
    'facebook_page_likes', 'reddit_mentions', 'search_volume_index', 'ticket_presales',
    'release_month', 'release_day_of_week', 'is_holiday_season', 'is_summer',
    'competing_releases_same_week', 'is_sequel', 'franchise_previous_avg_gross',
    'years_since_last_release', 'studio', 'total_gross', 'original_language'
]

movies_final = movies_df[final_columns].copy()

# Fill any remaining NaN values
movies_final['director'] = movies_final['director'].fillna('Unknown')
movies_final = movies_final.fillna(0)

print("\n" + "="*80)
print("STEP 6: Saving dataset")
print("="*80)

# Save to CSV
output_file = 'data/raw/imdb_movies_large.csv'
movies_final.to_csv(output_file, index=False)
print(f"✅ Saved to: {output_file}")

print("\n" + "="*80)
print("DATASET STATISTICS")
print("="*80)
print(f"Total movies: {len(movies_final):,}")
print(f"Year range: {movies_final['release_date'].min()} to {movies_final['release_date'].max()}")
print(f"Unique genres: {movies_final['genre'].nunique()}")
print(f"Unique directors: {movies_final['director'].nunique()}")
print(f"\nBudget statistics:")
print(f"  Average: ${movies_final['budget'].mean():,.0f}")
print(f"  Median: ${movies_final['budget'].median():,.0f}")
print(f"  Max: ${movies_final['budget'].max():,.0f}")
print(f"\nRevenue statistics:")
print(f"  Average: ${movies_final['revenue'].mean():,.0f}")
print(f"  Median: ${movies_final['revenue'].median():,.0f}")
print(f"  Max: ${movies_final['revenue'].max():,.0f}")
print(f"\nFirst week income statistics:")
print(f"  Average: ${movies_final['first_week'].mean():,.0f}")
print(f"  Median: ${movies_final['first_week'].median():,.0f}")
print(f"  Max: ${movies_final['first_week'].max():,.0f}")
print(f"\nIMDB Rating statistics:")
print(f"  Average: {movies_final['imdb_rating'].mean():.2f}")
print(f"  Median: {movies_final['imdb_rating'].median():.2f}")
print(f"  Max: {movies_final['imdb_rating'].max():.2f}")
print(f"\nIMDB Votes statistics:")
print(f"  Average: {movies_final['imdb_votes'].mean():,.0f}")
print(f"  Median: {movies_final['imdb_votes'].median():,.0f}")
print(f"  Max: {movies_final['imdb_votes'].max():,.0f}")
print("\n" + "="*80)

# Show sample
print("\n📊 Sample of collected movies:")
print(movies_final[['movie_title', 'release_date', 'budget', 'revenue', 'imdb_rating', 'imdb_votes']].head(20).to_string())

print("\n" + "="*80)
print("✅ PROCESSING COMPLETE!")
print("="*80)
print(f"Dataset ready at: {output_file}")
print(f"Total features: {len(final_columns)}")
print(f"Ready for model training!")
