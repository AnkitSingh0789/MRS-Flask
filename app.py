from flask import Flask, request, render_template
import pickle
import pandas as pd
import requests

app = Flask(__name__)

def fetch_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
    overview = data['overview']
    release_date = data['release_date']
    rating = data['vote_average']
    return full_path, overview, release_date, rating

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_details = []
    for i in distances[1:11]:  # Start from 1 to skip the selected movie itself
        movie_id = movies.iloc[i[0]].movie_id  # Ensure you use the correct column name for the movie ID
        title = movies.iloc[i[0]].title
        poster, overview, release_date, rating = fetch_details(movie_id)
        recommended_movie_details.append((title, poster, overview, release_date, rating))
    return recommended_movie_details

# Load movies and similarity matrix
movies_list = pickle.load(open('movies.pkl', 'rb'))
movies = pd.DataFrame(movies_list)
similarity = pickle.load(open('similarity.pkl', 'rb'))

@app.route('/')
def index():
    movie_list = movies['title'].values
    return render_template('index.html', movie_list=movie_list)

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    movie = request.form['movie']
    recommended_movies = recommend(movie)
    return render_template('recommend.html', recommended_movies=recommended_movies)

if __name__ == '__main__':
    app.run(debug=True)
