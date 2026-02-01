import requests
from urllib.parse import quote

title = "12th Fail"
t = quote(title.replace(' ', '_'))

base_names = [
    f"{t}_poster",
    f"{t}_(film)_poster",
    f"{t}_theatrical_poster",
    f"{t}_key_visual",
    f"{t}_cover",
    f"{t}",
    f"{t}_2023_poster",
    f"{t}_(2023_film)_poster"
]

print(f"Testing for '{title}'...")

for p in base_names:
    for ext in ['.jpg', '.png', '.jpeg']:
        url = f"https://en.wikipedia.org/wiki/Special:FilePath/{p}{ext}"
        try:
            r = requests.head(url, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=True)
            print(f"{url} -> {r.status_code}")
            if r.status_code == 200:
                print("FOUND!")
                final_url = r.url
                print(f"Final URL: {final_url}")
        except Exception as e:
            print(f"{url} -> Error: {e}")
