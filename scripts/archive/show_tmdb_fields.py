"""
Show what fields TMDB API returns for a sample movie.
"""
import requests
import json

TMDB_API_KEY = 'd429e3e7a57fe68708d1380b99dbdf43'

# Test with a few different movies
test_movies = [
    (19995, "Avatar (2009)"),
    (299534, "Avengers: Endgame (2019)"),
    (1184918, "The Wild Robot (2024)")
]

for movie_id, title in test_movies:
    print("\n" + "=" * 100)
    print(f"TMDB API DATA FOR: {title}")
    print("=" * 100)
    
    url = f'https://api.themoviedb.org/3/movie/{movie_id}'
    params = {
        'api_key': TMDB_API_KEY,
        'append_to_response': 'credits,videos,keywords,release_dates'
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # Show main fields
    print("\n📊 FINANCIAL DATA:")
    print(f"  budget: ${data.get('budget', 0):,}")
    print(f"  revenue: ${data.get('revenue', 0):,}")
    
    print("\n🎬 BASIC INFO:")
    print(f"  title: {data.get('title')}")
    print(f"  original_title: {data.get('original_title')}")
    print(f"  release_date: {data.get('release_date')}")
    print(f"  runtime: {data.get('runtime')} minutes")
    print(f"  status: {data.get('status')}")
    print(f"  original_language: {data.get('original_language')}")
    
    print("\n⭐ RATINGS & POPULARITY:")
    print(f"  vote_average: {data.get('vote_average')}/10")
    print(f"  vote_count: {data.get('vote_count'):,}")
    print(f"  popularity: {data.get('popularity')}")
    
    print("\n🎭 CREATIVE INFO:")
    genres = [g['name'] for g in data.get('genres', [])]
    print(f"  genres: {', '.join(genres)}")
    
    # Get director from credits
    credits = data.get('credits', {})
    directors = [c['name'] for c in credits.get('crew', []) if c.get('job') == 'Director']
    print(f"  director(s): {', '.join(directors) if directors else 'N/A'}")
    
    # Top cast
    cast = credits.get('cast', [])[:5]
    cast_names = [c['name'] for c in cast]
    print(f"  top_cast: {', '.join(cast_names)}")
    
    print("\n🏢 PRODUCTION:")
    companies = [c['name'] for c in data.get('production_companies', [])]
    print(f"  production_companies: {', '.join(companies[:3])}")
    
    countries = [c['name'] for c in data.get('production_countries', [])]
    print(f"  production_countries: {', '.join(countries)}")
    
    print("\n🔗 IDS & LINKS:")
    print(f"  tmdb_id: {data.get('id')}")
    print(f"  imdb_id: {data.get('imdb_id')}")
    print(f"  homepage: {data.get('homepage', 'N/A')}")
    
    # Check if part of collection
    collection = data.get('belongs_to_collection')
    if collection:
        print(f"  collection: {collection.get('name')}")
    
    print("\n🎥 VIDEOS/TRAILERS:")
    videos = data.get('videos', {}).get('results', [])
    trailers = [v for v in videos if v.get('type') == 'Trailer']
    print(f"  trailer_count: {len(trailers)}")
    if trailers:
        print(f"  sample_trailer: https://youtube.com/watch?v={trailers[0].get('key')}")
    
    print("\n🏷️ KEYWORDS:")
    keywords = data.get('keywords', {}).get('keywords', [])
    keyword_names = [k['name'] for k in keywords[:10]]
    print(f"  keywords: {', '.join(keyword_names)}")
    
    print("\n📅 RELEASE INFO:")
    release_dates = data.get('release_dates', {}).get('results', [])
    us_releases = [r for r in release_dates if r.get('iso_3166_1') == 'US']
    if us_releases and us_releases[0].get('release_dates'):
        for rel in us_releases[0]['release_dates'][:3]:
            print(f"  US Release Type {rel.get('type')}: {rel.get('release_date', 'N/A')[:10]}")
    
    print("\n" + "-" * 100)
    print("AVAILABLE TOP-LEVEL FIELDS:")
    print(", ".join(sorted(data.keys())))
    print("-" * 100)

print("\n\n" + "=" * 100)
print("SUMMARY: WHAT TMDB PROVIDES")
print("=" * 100)
print("""
✅ FINANCIAL DATA:
   - Budget (production cost)
   - Revenue (worldwide total box office)
   
✅ RATINGS & ENGAGEMENT:
   - Vote average (user rating 0-10)
   - Vote count (number of ratings)
   - Popularity score
   
✅ MOVIE INFO:
   - Title, release date, runtime
   - Genres, director, cast
   - Production companies, countries
   - Original language
   - IMDb ID
   
✅ ADDITIONAL DATA:
   - Trailers/videos
   - Keywords/tags
   - Release dates by country
   - Collection info (if part of franchise)
   
❌ NOT PROVIDED BY TMDB:
   - Opening weekend box office
   - First week box office
   - Domestic vs International breakdown
   - Weekly box office progression
   - Theater counts
   - Per-theater averages
   
💡 That's why we need Box Office Mojo for detailed box office breakdowns!
""")
