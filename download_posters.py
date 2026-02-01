import pandas as pd
import requests
import os
import time

img_dir = 'static/images'
if not os.path.exists(img_dir):
    os.makedirs(img_dir)

# Map of Title -> New High-Quality URL
# Helper: Use https://en.wikipedia.org/wiki/Special:FilePath/FILENAME for stable links
url_map = {
    # Working ones (re-verified)
    "Inception": "https://upload.wikimedia.org/wikipedia/en/2/2e/Inception_%282010%29_theatrical_poster.jpg",
    "The Dark Knight": "https://en.wikipedia.org/wiki/Special:FilePath/Dark_Knight.jpg", # Robust link
    "Interstellar": "https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg",
    "Parasite": "https://upload.wikimedia.org/wikipedia/en/5/53/Parasite_%282019_film%29.png",
    "Avengers: Endgame": "https://upload.wikimedia.org/wikipedia/en/0/0d/Avengers_Endgame_poster.jpg",
    "3 Idiots": "https://upload.wikimedia.org/wikipedia/en/d/df/3_idiots_poster.jpg",
    "Dangal": "https://upload.wikimedia.org/wikipedia/en/9/99/Dangal_Poster.jpg",
    "PK": "https://upload.wikimedia.org/wikipedia/en/c/c3/PK_poster.jpg",
    "Sholay": "https://upload.wikimedia.org/wikipedia/en/5/52/Sholay-poster.jpg",
    "Attack on Titan": "https://upload.wikimedia.org/wikipedia/en/d/d6/Shingeki_no_Kyojin_manga_volume_1.jpg",
    "Death Note": "https://upload.wikimedia.org/wikipedia/en/6/6f/Death_Note_Vol_1.jpg",
    "Naruto": "https://upload.wikimedia.org/wikipedia/en/9/94/NarutoCoverTankobon1.jpg",
    "One Piece": "https://upload.wikimedia.org/wikipedia/en/a/a3/One_Piece%2C_Volume_1.jpg",
    "Your Name": "https://upload.wikimedia.org/wikipedia/en/0/0b/Your_Name_poster.png",
    "Spirited Away": "https://upload.wikimedia.org/wikipedia/en/d/db/Spirited_Away_Japanese_poster.png",
    "Stranger Things": "https://upload.wikimedia.org/wikipedia/en/7/78/Stranger_Things_season_4.jpg",
    "Friends": "https://upload.wikimedia.org/wikipedia/en/d/d6/Friends_season_one_cast.jpg",
    "Demon Slayer": "https://upload.wikimedia.org/wikipedia/en/0/09/Demon_Slayer_-_Kimetsu_no_Yaiba%2C_volume_1.jpg",
    "The Godfather": "https://upload.wikimedia.org/wikipedia/en/1/1c/Godfather_ver1.jpg",
    "Shutter Island": "https://upload.wikimedia.org/wikipedia/en/7/76/Shutterislandposter.jpg",
    "Breaking Bad": "https://upload.wikimedia.org/wikipedia/en/6/61/Breaking_Bad_title_card.png",
    
    # Robust Fixes for previous failures
    "Sacred Games": "https://upload.wikimedia.org/wikipedia/en/3/3b/Sacred_Games_Season_2.jpg",
    "Mirzapur": "https://en.wikipedia.org/wiki/Special:FilePath/Mirzapur_poster.jpg", 
    "Hera Pheri": "https://en.wikipedia.org/wiki/Special:FilePath/Hera_Pheri_2000_poster.jpg",
    "Fullmetal Alchemist: Brotherhood": "https://en.wikipedia.org/wiki/Special:FilePath/Fullmetal_Alchemist_manga_volume_1.jpg"
}

# Fallback image (Grey placeholder)
FALLBACK_URL = "https://placehold.co/300x450/333/FFF.png?text=No+Poster"

def download_image(title, url):
    safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()
    safe_title = safe_title.replace(' ', '_').lower()
    
    # Determine extension
    ext = 'jpg'
    if '.png' in url.lower(): ext = 'png'
    if '.jpeg' in url.lower(): ext = 'jpg'
    
    filename = f"{safe_title}.{ext}"
    filepath = os.path.join(img_dir, filename)
    
    # Skip if exists and valid
    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        print(f"Skipping {title} (Exists)")
        return f"/static/images/{filename}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Downloading {title}...", end=' ')
        res = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        if res.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(res.content)
            print(f"Success")
            return f"/static/images/{filename}"
        else:
            print(f"Failed ({res.status_code})")
            # Try to save fallback
            print(f"  -> Downloading fallback...", end=' ')
            res_fb = requests.get(FALLBACK_URL, timeout=10)
            if res_fb.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(res_fb.content)
                print("Success (Fallback)")
                return f"/static/images/{filename}"
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

try:
    df = pd.read_csv('data/movies.csv')
    df['Poster_URL'] = df['Poster_URL'].astype(str) # Ensure string type

    for title, url in url_map.items():
        local_path = download_image(title, url)
        if local_path:
            mask = df['Title'] == title
            df.loc[mask, 'Poster_URL'] = local_path
            
    df.to_csv('data/movies.csv', index=False)
    print("\nCSV Updated successfully.")

except Exception as e:
    print(f"Global Error: {e}")
