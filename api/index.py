from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import os

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Get the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ================= LOAD DATA =================
movies_df = pd.read_csv(os.path.join(BASE_DIR, 'data/movies.csv'))

movies_df['Description'] = movies_df['Description'].fillna('')
movies_df['Genre'] = movies_df['Genre'].fillna('')
movies_df['Poster_URL'] = movies_df['Poster_URL'].replace('', None)
movies_df['Poster_URL'] = movies_df['Poster_URL'].fillna('/static/images/placeholder.jpg')

movies_df['Content'] = movies_df['Genre'] + " " + movies_df['Description']

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies_df['Content'])
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

indices = pd.Series(movies_df.index, index=movies_df['Title']).drop_duplicates()
# =============================================


def get_recommendations(title):
    if title not in indices:
        return []

    idx = indices[title]
    sim_scores = sorted(
        list(enumerate(cosine_sim[idx])),
        key=lambda x: x[1],
        reverse=True
    )[1:11]

    movie_indices = [i[0] for i in sim_scores]
    return movies_df.iloc[movie_indices][
        ['Title', 'Category', 'Genre', 'Poster_URL', 'Description']
    ].to_dict('records')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/metadata')
def metadata():
    categories = sorted(movies_df['Category'].unique())
    genres = sorted(
        set(g.strip() for sub in movies_df['Genre'].str.split(',') for g in sub)
    )
    return jsonify({'categories': categories, 'genres': genres})


@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '').lower().strip()
    category = data.get('category', 'All')
    genre = data.get('genre', 'All')

    if category.lower().startswith('all'):
        category = 'All'
    if genre.lower().startswith('all'):
        genre = 'All'

    df = movies_df.copy()

    if category != 'All':
        df = df[df['Category'].str.lower() == category.lower()]

    if genre != 'All':
        df = df[df['Genre'].str.lower().str.contains(genre.lower(), na=False)]

    if query:
        categories = movies_df['Category'].str.lower().unique()
        genres = set(
            g.strip().lower()
            for sub in movies_df['Genre'].str.split(',')
            for g in sub
        )

        if query in categories:
            df = df[df['Category'].str.lower() == query]
        elif query in genres:
            df = df[df['Genre'].str.lower().str.contains(query, na=False)]
        else:
            df = df[df['Title'].str.lower().str.contains(query, na=False)]

    return jsonify(df[
        ['Title', 'Category', 'Genre', 'Poster_URL', 'Description']
    ].to_dict('records'))


@app.route('/api/autocomplete')
def autocomplete():
    q = request.args.get('q', '').lower()
    suggestions = set()

    for c in movies_df['Category'].unique():
        if c.lower().startswith(q):
            suggestions.add(c)

    for sub in movies_df['Genre'].str.split(','):
        for g in sub:
            if g.strip().lower().startswith(q):
                suggestions.add(g.strip())

    titles = movies_df[movies_df['Title'].str.lower().str.startswith(q)]['Title'].head(5)
    suggestions.update(titles)

    return jsonify(list(suggestions)[:8])


@app.route('/api/recommend', methods=['POST'])
def recommend():
    title = request.json.get('title', '')
    return jsonify(get_recommendations(title))


# This is required for Vercel
if __name__ != '__main__':
    # Vercel will use this
    application = app
