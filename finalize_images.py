import pandas as pd
import requests
import os
import random
from PIL import Image, ImageDraw, ImageFont
from urllib.parse import quote

img_dir = 'static/images'
csv_file = 'data/movies.csv'

# Threshold for "missing"
MIN_SIZE = 15000

# 1. Manual Overrides (Found via search)
# Use Special:FilePath with EXACT filenames found
manual_fixes = {
    "Barbie": "https://en.wikipedia.org/wiki/Special:FilePath/Barbie_2023_poster.jpeg",
    "12th Fail": "https://en.wikipedia.org/wiki/Special:FilePath/12th_Fail_poster.jpeg",
    "Jawan": "https://en.wikipedia.org/wiki/Special:FilePath/Jawan_film_poster.jpg",
    "Chhichhore": "https://en.wikipedia.org/wiki/Special:FilePath/Chhichhore_Poster.jpg",
    "Akame ga Kill!": "https://upload.wikimedia.org/wikipedia/en/b/b3/Akame_ga_Kill!_anime_poster.jpg", # Trying direct guess
    "American Fiction": "https://en.wikipedia.org/wiki/Special:FilePath/American_Fiction_2023_poster.jpg",
    "Anatomy of a Fall": "https://en.wikipedia.org/wiki/Special:FilePath/Anatomy_of_a_Fall_2023_poster.jpg",
}

def download_image(url, filepath):
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, allow_redirects=True)
        if res.status_code == 200 and len(res.content) > MIN_SIZE:
            with open(filepath, 'wb') as f:
                f.write(res.content)
            return True
    except:
        pass
    return False

def generate_placeholder(title, filepath):
    # Aesthetically pleasing dark colors
    colors = [
        (20, 33, 61), (0, 0, 0), (38, 70, 83), (42, 157, 143), 
        (231, 111, 81), (244, 162, 97), (85, 91, 110)
    ]
    bg_color = random.choice(colors)
    
    img = Image.new('RGB', (300, 450), color=bg_color)
    d = ImageDraw.Draw(img)
    
    # Try to verify font otherwise default
    try:
        # Load a default font usually available or fallback
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
        
    # Wrap text roughly
    words = title.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        # Check width (rough estimation if font metrics hard)
        if len(" ".join(current_line)) > 12: # Break line
            lines.append(" ".join(current_line[:-1]))
            current_line = [word]
    lines.append(" ".join(current_line))
    
    # Draw centered text
    text = "\n".join(lines)
    
    # Simple centering logic
    w, h = 300, 450
    # Center calculation is tricky without consistent font metrics across OS, 
    # so we place roughly in middle
    d.multiline_text((w/2, h/2), text, fill=(255, 255, 255), anchor="mm", align="center", font=font)
    
    img.save(filepath)
    print(f"Generated placeholder for: {title}")
    return True

try:
    df = pd.read_csv(csv_file)
    
    updated = 0
    for index, row in df.iterrows():
        title = row['Title']
        
        # Determine current status
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip().lower().replace(' ', '_')
        filename = f"{safe_title}.jpg"
        filepath = os.path.join(img_dir, filename)
        
        # Check if needs fixing
        needs_fix = True
        if os.path.exists(filepath) and os.path.getsize(filepath) > MIN_SIZE:
            needs_fix = False
            
        # Also check if CSV points to a different valid file (e.g. .png)
        current_csv_path = row['Poster_URL']
        if not pd.isna(current_csv_path):
            csv_fname = os.path.basename(current_csv_path)
            csv_fpath = os.path.join(img_dir, csv_fname)
            if os.path.exists(csv_fpath) and os.path.getsize(csv_fpath) > MIN_SIZE:
                needs_fix = False
        
        if needs_fix:
            print(f"Fixing: {title}...", end=" ")
            
            # 1. Try Manual Download
            success = False
            if title in manual_fixes:
                print("Downloading Manual...", end=" ")
                if download_image(manual_fixes[title], filepath):
                    print("Success.")
                    success = True
            
            # 2. Generate Placeholder if download failed
            if not success:
                print("Generating Art...", end=" ")
                generate_placeholder(title, filepath)
                success = True
                
            # Update CSV always to the .jpg (since manual/generated both save to filepath)
            df.at[index, 'Poster_URL'] = f"/static/images/{filename}"
            updated += 1
            print("Done.")

    df.to_csv(csv_file, index=False)
    print(f"\nFinalized. Updated {updated} images.")

except Exception as e:
    print(f"Error: {e}")
