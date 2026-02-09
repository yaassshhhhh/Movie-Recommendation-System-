import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import json
import os

def precompute_data():
    print("Loading data...")
    # Load data
    movies_df = pd.read_csv('data/movies.csv')

    # Data Cleaning (Keep consistent with original app.py)
    movies_df['Description'] = movies_df['Description'].fillna('')
    movies_df['Genre'] = movies_df['Genre'].fillna('')
    movies_df['Poster_URL'] = movies_df['Poster_URL'].replace('', None)
    movies_df['Poster_URL'] = movies_df['Poster_URL'].fillna('/static/images/placeholder.jpg')
    movies_df['Content'] = movies_df['Genre'] + " " + movies_df['Description']

    print("Computing TF-IDF and Cosine Similarity...")
    # Compute TF-IDF
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies_df['Content'])

    # Compute Cosine Similarity
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Create indices
    indices = pd.Series(movies_df.index, index=movies_df['Title']).drop_duplicates()

    print("Generating recommendations...")
    recommendations = {}
    
    # Generate recommendations for ALL movies
    for title in movies_df['Title'].unique():
        if title not in indices:
            continue
            
        idx = indices[title]
        
        # Handle duplicate titles by taking the first one
        if isinstance(idx, pd.Series):
             idx = idx.iloc[0]

        sim_scores = sorted(
            list(enumerate(cosine_sim[idx])),
            key=lambda x: x[1],
            reverse=True
        )[1:11]
        
        movie_indices = [i[0] for i in sim_scores]
        
        # Get the recommended movies details
        recomm_movies = movies_df.iloc[movie_indices][
            ['Title', 'Category', 'Genre', 'Poster_URL', 'Description']
        ].to_dict('records')
        
        recommendations[title] = recomm_movies

    print("Saving json files...")
    
    # Save movies list for display and search
    movies_list = movies_df[['Title', 'Category', 'Genre', 'Poster_URL', 'Description']].to_dict('records')
    
    with open('data/movies.json', 'w') as f:
        json.dump(movies_list, f)
        
    with open('data/recommendations.json', 'w') as f:
        json.dump(recommendations, f)

    print("Done! Files saved to data/movies.json and data/recommendations.json")

if __name__ == "__main__":
    precompute_data()
