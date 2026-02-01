import pandas as pd
import os

img_dir = 'static/images'
csv_file = 'data/movies.csv'

# Threshold for a "good" image
MIN_SIZE = 15000

try:
    df = pd.read_csv(csv_file)
    updated_count = 0
    
    for index, row in df.iterrows():
        current_url = row['Poster_URL']
        if pd.isna(current_url): continue
        
        # Extract filename from URL (e.g., /static/images/foo.jpg -> foo.jpg)
        current_filename = os.path.basename(current_url)
        current_path = os.path.join(img_dir, current_filename)
        
        # Check if current is bad (doesn't exist or small)
        is_bad = True
        if os.path.exists(current_path) and os.path.getsize(current_path) > MIN_SIZE:
            is_bad = False
            
        if is_bad:
            # Look for better alternatives with same basename
            # e.g. foo.jpg -> foo.png, foo.jpeg
            name_part = os.path.splitext(current_filename)[0]
            
            candidates = [
                f"{name_part}.png",
                f"{name_part}.jpeg",
                f"{name_part}.jpg"
            ]
            
            found_better = False
            for cand in candidates:
                cand_path = os.path.join(img_dir, cand)
                if os.path.exists(cand_path) and os.path.getsize(cand_path) > MIN_SIZE:
                    # Found a good one!
                    new_url = f"/static/images/{cand}"
                    df.at[index, 'Poster_URL'] = new_url
                    print(f"Fixed {row['Title']}: {current_filename} ({os.path.getsize(current_path) if os.path.exists(current_path) else 'Missing'}) -> {cand} ({os.path.getsize(cand_path)})")
                    updated_count += 1
                    found_better = True
                    break
            
            if not found_better:
                # If we have a small file but no big file, well, we keep the small one or generic?
                pass

    if updated_count > 0:
        df.to_csv(csv_file, index=False)
        print(f"\nUpdated {updated_count} CSV entries to point to valid images.")
    else:
        print("\nNo CSV updates needed.")

except Exception as e:
    print(f"Error: {e}")
