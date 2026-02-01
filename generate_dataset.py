import os
import csv
import time
import requests
from tqdm import tqdm

# ================== CONFIG ==================
TMDB_API_KEY = "409a299076e3ebc47dbd75e04636bc3a"

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
IMAGES_DIR = "static/images"
CSV_PATH = "data/movies.csv"

MOVIES_PER_CATEGORY = 100

# TMDB filters
BOLLYWOOD_LANG = "hi"
HOLLYWOOD_LANG = "en"
ANIME_GENRE_ID = 16  # Animation

# Genre mapping
GENRE_MAP = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    18: "Drama",
    14: "Fantasy",
    27: "Horror",
    10749: "Romance",
    878: "Sci-Fi",
    53: "Thriller",
    9648: "Mystery"
}
# ===========================================

os.makedirs(IMAGES_DIR, exist_ok=True)


def fetch_movies(language=None, genre=None, limit=100):
    page = 1
    results = []

    while len(results) < limit:
        try:
            url = "https://api.themoviedb.org/3/discover/movie"
            params = {
                "api_key": TMDB_API_KEY,
                "page": page,
                "with_original_language": language,
                "with_genres": genre,
                "sort_by": "popularity.desc"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            movies = data.get("results", [])
            if not movies:
                break

            results.extend(movies)
            page += 1
            time.sleep(0.4)  # rate-limit

        except Exception:
            print("⚠️ Network issue, retrying...")
            time.sleep(2)

    return results[:limit]


def download_poster(movie_id, poster_path):
    if not poster_path:
        return "/static/images/placeholder.jpg"

    filename = f"{movie_id}.jpg"
    filepath = os.path.join(IMAGES_DIR, filename)

    if os.path.exists(filepath):
        return f"/static/images/{filename}"

    try:
        img_url = POSTER_BASE_URL + poster_path
        response = requests.get(img_url, timeout=10)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(response.content)

        time.sleep(0.2)

    except Exception:
        return "/static/images/placeholder.jpg"

    return f"/static/images/{filename}"


def extract_genres(movie):
    genre_ids = movie.get("genre_ids", [])
    genres = [GENRE_MAP[g] for g in genre_ids if g in GENRE_MAP]
    return ", ".join(genres) if genres else "Drama"


def main():
    rows = []

    print("🎬 Fetching Bollywood movies...")
    bollywood = fetch_movies(language=BOLLYWOOD_LANG, limit=MOVIES_PER_CATEGORY)

    print("🎬 Fetching Hollywood movies...")
    hollywood = fetch_movies(language=HOLLYWOOD_LANG, limit=MOVIES_PER_CATEGORY)

    print("🎬 Fetching Anime...")
    anime = fetch_movies(genre=ANIME_GENRE_ID, limit=MOVIES_PER_CATEGORY)

    all_sets = [
        (bollywood, "Bollywood"),
        (hollywood, "Hollywood"),
        (anime, "Anime")
    ]

    for movies, category in all_sets:
        for movie in tqdm(movies, desc=f"Processing {category}"):
            poster_url = download_poster(
                movie["id"],
                movie.get("poster_path")
            )

            rows.append([
                movie.get("title", ""),
                category,
                extract_genres(movie),
                movie.get("overview", ""),
                poster_url
            ])

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Category", "Genre", "Description", "Poster_URL"])
        writer.writerows(rows)

    print("✅ Dataset generated successfully!")


if __name__ == "__main__":
    main()
