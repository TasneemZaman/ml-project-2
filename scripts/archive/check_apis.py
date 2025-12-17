"""
Check available APIs for real social media and search data.
This will help us understand what data we can collect.
"""

print("=" * 100)
print("AVAILABLE REAL DATA SOURCES")
print("=" * 100)

print("\n1. 📊 GOOGLE TRENDS (pytrends)")
print("   - Search interest over time")
print("   - Related queries")
print("   - Regional interest")
print("   - No API key required (uses unofficial API)")
print("   ⚠️ Rate limits apply - need to be careful")

print("\n2. 🎥 YOUTUBE DATA API")
print("   - Video statistics (views, likes, comments)")
print("   - Search for movie trailers")
print("   - Channel information")
print("   ✅ Free tier: 10,000 quota units per day")
print("   📝 Requires API key from Google Cloud Console")

print("\n3. 🐦 TWITTER/X API")
print("   - Tweet counts, mentions")
print("   - Sentiment analysis")
print("   ❌ Now requires paid subscription ($100+/month)")
print("   🚫 Not recommended for this project")

print("\n4. 📱 REDDIT API")
print("   - Post counts, comments")
print("   - Subreddit mentions")
print("   ✅ Free tier available")
print("   📝 Requires Reddit app credentials")

print("\n5. 🎬 IMDb (via OMDb API or Cinemagoer)")
print("   - Additional ratings")
print("   - Metascore")
print("   - Awards information")
print("   ✅ Free tier available")

print("\n" + "=" * 100)
print("RECOMMENDED APPROACH")
print("=" * 100)

print("\n✅ HIGH PRIORITY (Free & Reliable):")
print("   1. YouTube API - Trailer views/likes (requires API key)")
print("   2. Google Trends - Search interest (no key needed, but rate limited)")
print("   3. IMDb/OMDb - Additional ratings (free tier)")

print("\n⚠️ MEDIUM PRIORITY (Requires Setup):")
print("   4. Reddit API - Discussion mentions (requires app credentials)")

print("\n❌ SKIP:")
print("   - Twitter/X (too expensive)")
print("   - Instagram (restricted API)")
print("   - Facebook (restricted API)")

print("\n" + "=" * 100)
print("NEXT STEPS")
print("=" * 100)

print("\n1. Install required packages:")
print("   pip install pytrends google-api-python-client omdbapi")

print("\n2. Get API keys:")
print("   📹 YouTube: https://console.cloud.google.com/apis/credentials")
print("   🎬 OMDb: http://www.omdbapi.com/apikey.aspx")
print("   🤖 Reddit: https://www.reddit.com/prefs/apps")

print("\n3. I'll create collectors for:")
print("   ✅ YouTube trailer data (needs your API key)")
print("   ✅ Google Trends search interest (no key needed)")
print("   ✅ OMDb ratings (needs free API key)")

print("\n" + "=" * 100)
print("\nDo you want to proceed? If yes, please provide:")
print("   1. YouTube API Key (from Google Cloud Console)")
print("   2. OMDb API Key (from omdbapi.com)")
print("\nOr I can create the scripts first and you can add keys later.")
print("=" * 100)
