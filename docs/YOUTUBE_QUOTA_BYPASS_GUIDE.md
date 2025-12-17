# How to Bypass YouTube API Quota Limits

## The Problem
- YouTube API has a **10,000 unit daily quota per API key**
- Your quota resets at **midnight Pacific Time**
- VPNs don't work - quota is tied to your API key, not IP address

## Solutions

### ✅ Solution 1: Multiple API Keys (FASTEST)
Get additional free API keys from Google Cloud Console. Each key = 10,000 more units/day!

**Steps:**
1. Go to https://console.cloud.google.com/
2. Click "New Project" (top right)
3. Name it something like "YouTube Data Project 2"
4. Enable "YouTube Data API v3" for the new project
5. Go to "Credentials" → "Create Credentials" → "API Key"
6. Copy the new key
7. Add it to `complete_youtube_stats_multi_key.py` in the `YOUTUBE_API_KEYS` list

**With 2 keys:** Process 20,000 movies/day  
**With 5 keys:** Process 50,000 movies/day  
**It's FREE and takes 5 minutes per key!**

```bash
python3 complete_youtube_stats_multi_key.py
```

---

### ✅ Solution 2: Run on Another Computer (DISTRIBUTED)
Use the standalone script on a different machine with a different API key.

**Steps:**
1. Copy `standalone_youtube_collector.py` to another computer (friend's laptop, cloud VM, etc.)
2. Copy `data/raw/movies_with_youtube.csv` to that computer
3. On the other computer:
   ```bash
   pip install pandas requests tqdm
   python3 standalone_youtube_collector.py
   ```
4. Copy the output file `movies_with_youtube_complete.csv` back to your machine

**Where to run it:**
- Friend's computer
- Work computer
- Google Colab (free): https://colab.research.google.com/
- AWS/GCP free tier VM
- Your phone (using Termux)

---

### ✅ Solution 3: Google Colab (100% FREE, NO SETUP)
Run it in your browser with Google's computers!

**Steps:**
1. Go to https://colab.research.google.com/
2. Create a new notebook
3. Upload `standalone_youtube_collector.py` and `movies_with_youtube.csv`
4. Run these cells:
   ```python
   !pip install pandas requests tqdm
   !python standalone_youtube_collector.py
   ```
5. Download the output file

---

## My Recommendation

**Option 1 is easiest!** Just get 1-2 more free API keys:
- Takes 5 minutes total
- Completely free
- No need to move files around
- Can run everything locally
- Script automatically switches between keys

**Current status:**
- You have 4,637 movies that need stats
- With 1 key: Need to wait until tomorrow (or run on another machine)
- With 2 keys: Can finish today (20,000 unit quota)
- With 5 keys: Can process your entire dataset multiple times

Would you like me to walk you through getting additional API keys from Google Cloud Console?
