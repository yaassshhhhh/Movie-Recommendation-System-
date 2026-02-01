import pandas as pd
import requests
import os
import time
from urllib.parse import quote

img_dir = 'static/images'
if not os.path.exists(img_dir):
    os.makedirs(img_dir)

FALLBACK_URL = "https://placehold.co/300x450/333/FFF.png?text=No+Poster"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def try_download(url, filepath):
    try:
        res = requests.get(url, headers=HEADERS, timeout=5, allow_redirects=True)
        if res.status_code == 200 and len(res.content) > 1000: # Ensure not empty/error page
            with open(filepath, 'wb') as f:
                f.write(res.content)
            return True
    except:
        pass
    return False

def get_wiki_variations(title):
    # Heuristics for Wikipedia file paths
    t = quote(title.replace(' ', '_'))
    
    # Generate variations
    base_names = [
        f"{t}_poster",
        f"{t}_(film)_poster",
        f"{t}_theatrical_poster",
        f"{t}_(TV_series)_poster",
        f"{t}_(season_1)_poster",
        f"{t}_key_visual",
        f"{t}_Volume_1",
        f"{t}_manga_Volume_1",
        f"{t}_cover",
        f"{t}",
        # Try some recent years often used in filenames
        f"{t}_2023_poster",
        f"{t}_2024_poster",
        f"{t}_2022_poster",
        f"{t}_(2023_film)_poster",
        f"{t}_(2024_film)_poster"
    ]
    
    urls = []
    for p in base_names:
        urls.append(f"https://en.wikipedia.org/wiki/Special:FilePath/{p}.jpg")
        urls.append(f"https://en.wikipedia.org/wiki/Special:FilePath/{p}.png")
        urls.append(f"https://en.wikipedia.org/wiki/Special:FilePath/{p}.jpeg") # Added jpeg
        
    return urls

# Specific overrides for tricky ones
manual_overrides = {
    "Sacred Games": "https://upload.wikimedia.org/wikipedia/en/3/3b/Sacred_Games_Season_2.jpg",
    "Mirzapur": "https://upload.wikimedia.org/wikipedia/en/3/3c/Mirzapur_poster.jpeg",
    "Fullmetal Alchemist: Brotherhood": "https://upload.wikimedia.org/wikipedia/en/7/7e/Fullmetal_Alchemist_Brotherhood_Key_Visual.png",
    "Demon Slayer": "https://upload.wikimedia.org/wikipedia/en/0/09/Demon_Slayer_-_Kimetsu_no_Yaiba%2C_volume_1.jpg", 
    "Breaking Bad": "https://upload.wikimedia.org/wikipedia/en/6/61/Breaking_Bad_title_card.png",
    "Hera Pheri": "https://upload.wikimedia.org/wikipedia/en/2/22/Hera_Pheri_2000_poster.jpg"
}

try:
    df = pd.read_csv('data/movies.csv')
    total = len(df)
    print(f"Processing {total} movies...")
    
    for index, row in df.iterrows():
        title = row['Title']
        
        # Determine local filename
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip().lower().replace(' ', '_')
        filename = f"{safe_title}.jpg" # Default to jpg
        filepath = os.path.join(img_dir, filename)
        
        # Check if exists and valid (> 15KB)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 15000:
            # Update CSV path just in case
            df.at[index, 'Poster_URL'] = f"/static/images/{filename}"
            continue
            
        print(f"[{index+1}/{total}] Downloading: {title}...", end=" ")
        
        success = False
        
        # 1. Try Manual Override
        if title in manual_overrides:
            if try_download(manual_overrides[title], filepath):
                print("Success (Manual)")
                success = True
        
        # 2. Try Wiki Heuristics
        if not success:
            variations = get_wiki_variations(title)
            for url in variations:
                if try_download(url, filepath):
                    print(f"Success (Wiki: {url.split('/')[-1]})")
                    success = True
                    break
        
        # 3. Fallback
        if not success:
            print("Failed -> Using Fallback")
            try_download(FALLBACK_URL, filepath)
            
        # Update CSV
        df.at[index, 'Poster_URL'] = f"/static/images/{filename}"
        
        # Scan-friendliness
        # time.sleep(0.1) 

    df.to_csv('data/movies.csv', index=False)
    print("\nBatch processing complete.")

except Exception as e:
    print(f"Error: {e}")
