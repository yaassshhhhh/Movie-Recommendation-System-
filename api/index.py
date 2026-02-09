from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Get the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load pre-computed data
try:
    with open(os.path.join(BASE_DIR, 'data/movies.json'), 'r') as f:
        movies_list = json.load(f)
        
    with open(os.path.join(BASE_DIR, 'data/recommendations.json'), 'r') as f:
        recommendations = json.load(f)
        
    print("Loaded data successfully.")
except Exception as e:
    print(f"Error loading data: {e}")
    movies_list = []
    recommendations = {}

# Helper to optimize lookups
movies_by_title = {m['Title'].lower(): m for m in movies_list}

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/metadata')
def metadata():
    categories = sorted(list(set(m['Category'] for m in movies_list)))
    
    genres_set = set()
    for m in movies_list:
        if m['Genre']:
            for g in m['Genre'].split(','):
                genres_set.add(g.strip())
                
    genres = sorted(list(genres_set))
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

    filtered_movies = movies_list

    if category != 'All':
        filtered_movies = [
            m for m in filtered_movies 
            if m['Category'].lower() == category.lower()
        ]

    if genre != 'All':
        filtered_movies = [
            m for m in filtered_movies 
            if genre.lower() in m['Genre'].lower()
        ]

    if query:
        # Check specific fields first (mimicking original logic)
        categories = set(m['Category'].lower() for m in movies_list)
        
        genres = set()
        for m in movies_list:
            if m['Genre']:
                for g in m['Genre'].split(','):
                    genres.add(g.strip().lower())

        if query in categories:
            filtered_movies = [
                m for m in filtered_movies 
                if m['Category'].lower() == query
            ]
        elif query in genres:
            filtered_movies = [
                m for m in filtered_movies 
                if query in m['Genre'].lower()
            ]
        else:
            filtered_movies = [
                m for m in filtered_movies 
                if query in m['Title'].lower()
            ]

    return jsonify(filtered_movies)


@app.route('/api/autocomplete')
def autocomplete():
    q = request.args.get('q', '').lower()
    suggestions = set()

    for m in movies_list:
        if m['Category'].lower().startswith(q):
            suggestions.add(m['Category'])
            
        if m['Genre']:
            for g in m['Genre'].split(','):
                if g.strip().lower().startswith(q):
                    suggestions.add(g.strip())

    # Add matching titles (limit to 5)
    title_matches = [
        m['Title'] for m in movies_list 
        if m['Title'].lower().startswith(q)
    ][:5]
    
    suggestions.update(title_matches)

    return jsonify(list(suggestions)[:8])


@app.route('/api/recommend', methods=['POST'])
def recommend():
    title = request.json.get('title', '')
    
    # Direct lookup in pre-computed dictionary
    if title in recommendations:
        return jsonify(recommendations[title])
        
    return jsonify([])


# This is required for Vercel
if __name__ != '__main__':
    # Vercel will use this
    application = app

if __name__ == '__main__':
    app.run(debug=True)
