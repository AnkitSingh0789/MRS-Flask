from flask import Flask, request, render_template
import pickle
import pandas as pd
import requests
import gzip
import urllib.parse  # For encoding movie titles in URLs

app = Flask(__name__)

# Function to fetch movie details using The Movie Database (TMDb) API
def fetch_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        data = requests.get(url).json()
        poster_path = data['poster_path']
        full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
        overview = data['overview']
        release_date = data['release_date']
        rating = data['vote_average']
    except Exception as e:
        print(f"Error fetching movie details: {e}")
        return None, None, None, None

    return full_path, overview, release_date, rating

# Function to recommend movies
def recommend(movie, min_rating=5.0):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_details = []

    for i in distances[1:11]:  # Start from 1 to skip the selected movie itself
        movie_id = movies.iloc[i[0]].movie_id  # Ensure you use the correct column name for the movie ID
        title = movies.iloc[i[0]].title
        poster, overview, release_date, rating = fetch_details(movie_id)

        # Filter recommendations based on the minimum rating
        if rating is not None and rating >= min_rating:
            recommended_movie_details.append((title, poster, overview, release_date, rating))
    
    return recommended_movie_details

# Load movies and similarity matrix
with open('movies.pkl', 'rb') as f:
    movies_list = pickle.load(f)
movies = pd.DataFrame(movies_list)

with gzip.open('similarity.pkl.gz', 'rb') as f:
    similarity = pickle.load(f)

@app.route('/')
def index():
    movie_list = movies['title'].values
    return render_template('index.html', movie_list=movie_list)

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    movie = request.form['movie']
    min_rating = float(request.form.get('min_rating', 5.0))  # Get minimum rating from the form
    recommended_movies = recommend(movie, min_rating=min_rating)
    return render_template('recommend.html', recommended_movies=recommended_movies)

if __name__ == '__main__':
    app.run(debug=True)
