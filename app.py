from flask import Flask, request, jsonify
import pickle
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the pre-trained recommendation model and movie list
movies_list = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url)
    data = response.json()
    return f"http://image.tmdb.org/t/p/w500/{data.get('poster_path', '')}" if 'poster_path' in data else None

def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url)
    data = response.json()
    for video in data.get('results', []):
        if video.get('type', '').lower() == 'trailer' and video.get('site', '').lower() == 'youtube':
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None

def fetch_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=8265bd1679663a7ea12ac168da84d2e8"
    response = requests.get(url)
    data = response.json()
    director = next((crew['name'] for crew in data.get('crew', []) if crew['job'] == 'Director'), 'Unknown')
    cast = [actor['name'] for actor in data.get('cast', [])[:5]]
    return director, cast

def fetch_wikipedia_url(movie_title):
    return f"https://en.wikipedia.org/wiki/{movie_title.replace(' ', '_')}"

def recommend(movie):
    movie = movie.lower()
    movies_list['title'] = movies_list['title'].str.lower()
    
    if movie not in movies_list['title'].values:
        return []
    
    index = movies_list[movies_list['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:6]
    recommendations = []
    for i in distances:
        movie_id = movies_list.iloc[i[0]].movie_id
        title = movies_list.iloc[i[0]].title
        poster = fetch_poster(movie_id)
        trailer = fetch_trailer(movie_id)
        director, cast = fetch_details(movie_id)
        wiki_url = fetch_wikipedia_url(title)
        recommendations.append({
            "title": title,
            "poster": poster,
            "trailer": trailer,
            "director": director,
            "cast": cast,
            "wiki_url": wiki_url
        })
    return recommendations

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "This is the home page"})

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    data = request.json
    movie = data.get('movie', '').lower()
    
    if not movie:
        return jsonify({"error": "No movie title provided"}), 400
    
    recommendations = recommend(movie)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)