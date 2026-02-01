import pandas as pd

# Define the new valid URLs
poster_updates = {
    "Inception": "https://upload.wikimedia.org/wikipedia/en/2/2e/Inception_%282010%29_theatrical_poster.jpg",
    "The Dark Knight": "https://upload.wikimedia.org/wikipedia/en/8/8a/Dark_Knight.jpg",
    "Interstellar": "https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg",
    "Parasite": "https://upload.wikimedia.org/wikipedia/en/5/53/Parasite_%282019_film%29.png",
    "Avengers: Endgame": "https://upload.wikimedia.org/wikipedia/en/0/0d/Avengers_Endgame_poster.jpg",
    "3 Idiots": "https://upload.wikimedia.org/wikipedia/en/d/df/3_idiots_poster.jpg",
    "Dangal": "https://upload.wikimedia.org/wikipedia/en/9/99/Dangal_Poster.jpg",
    "PK": "https://upload.wikimedia.org/wikipedia/en/c/c3/PK_poster.jpg",
    "Sholay": "https://upload.wikimedia.org/wikipedia/en/5/52/Sholay-poster.jpg",
    "Sacred Games": "https://upload.wikimedia.org/wikipedia/en/1/1f/Sacred_Games_Season_1.jpg",
    "Attack on Titan": "https://upload.wikimedia.org/wikipedia/en/d/d6/Shingeki_no_Kyojin_manga_volume_1.jpg",
    "Death Note": "https://upload.wikimedia.org/wikipedia/en/6/6f/Death_Note_Vol_1.jpg",
    "Naruto": "https://upload.wikimedia.org/wikipedia/en/9/94/NarutoCoverTankobon1.jpg",
    "One Piece": "https://upload.wikimedia.org/wikipedia/en/a/a3/One_Piece%2C_Volume_1.jpg",
    "Your Name": "https://upload.wikimedia.org/wikipedia/en/0/0b/Your_Name_poster.png",
    "Spirited Away": "https://upload.wikimedia.org/wikipedia/en/d/db/Spirited_Away_Japanese_poster.png",
    "Breaking Bad": "https://upload.wikimedia.org/wikipedia/en/6/61/Breaking_Bad_title_card.png",
    "Stranger Things": "https://upload.wikimedia.org/wikipedia/en/7/78/Stranger_Things_season_4.jpg",
    "Friends": "https://upload.wikimedia.org/wikipedia/en/d/d6/Friends_season_one_cast.jpg",
    "Mirzapur": "https://upload.wikimedia.org/wikipedia/en/3/3c/Mirzapur_poster.jpeg",
    "Demon Slayer": "https://upload.wikimedia.org/wikipedia/en/0/09/Demon_Slayer_-_Kimetsu_no_Yaiba%2C_volume_1.jpg",
    "Hera Pheri": "https://upload.wikimedia.org/wikipedia/en/2/22/Hera_Pheri_2000_poster.jpg",
    "Fullmetal Alchemist: Brotherhood": "https://upload.wikimedia.org/wikipedia/en/7/7e/Fullmetal_Alchemist_Brotherhood_Key_Visual.png",
    "The Godfather": "https://upload.wikimedia.org/wikipedia/en/1/1c/Godfather_ver1.jpg",
    "Shutter Island": "https://upload.wikimedia.org/wikipedia/en/7/76/Shutterislandposter.jpg"
}

try:
    df = pd.read_csv('data/movies.csv')
    
    # Update URLs where title matches
    for title, url in poster_updates.items():
        mask = df['Title'] == title
        if mask.any():
            df.loc[mask, 'Poster_URL'] = url
            print(f"Updated: {title}")
        else:
            print(f"Not Found: {title}")
            
    df.to_csv('data/movies.csv', index=False)
    print("CSV updated successfully.")
    
except Exception as e:
    print(f"Error: {e}")
