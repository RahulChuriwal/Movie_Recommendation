import streamlit as st
import pickle
import requests

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path', '')
        if poster_path:
            return f"http://image.tmdb.org/t/p/w500/{poster_path}"
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750?text=Poster+Not+Available"


def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        videos = data.get('results', [])
        for video in videos:
            if video.get('type', '').lower() == 'trailer' and video.get('site', '').lower() == 'youtube':
                return f"https://www.youtube.com/watch?v={video['key']}"
    except requests.exceptions.RequestException:
        return None


def fetch_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        director = "Unknown"
        cast = []
        credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=8265bd1679663a7ea12ac168da84d2e8"
        credits_response = requests.get(credits_url, timeout=10)
        if credits_response.status_code == 200:
            credits = credits_response.json()
            for member in credits.get('crew', []):
                if member.get('job', '').lower() == 'director':
                    director = member.get('name', 'Unknown')
                    break
            cast = [actor.get('name', '') for actor in credits.get('cast', [])[:5]]
        return director, cast
    except requests.exceptions.RequestException:
        return "Unknown", []


def fetch_wikipedia_url(movie_title):
    return f"https://en.wikipedia.org/wiki/{movie_title.replace(' ', '_')}"


def recommend(movie):
    index_value = movies_list[movies_list['title'] == movie].index[0]
    index = int(index_value)
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    recommended_movie_posters = []
    recommended_movie_urls = []
    recommended_movie_trailers = []
    recommended_movie_details = []
    for i in distances:
        movie_id = movies_list.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        movie_title = movies_list.iloc[i[0]].title
        recommended_movies.append(movie_title)
        recommended_movie_urls.append(fetch_wikipedia_url(movie_title))
        recommended_movie_trailers.append(fetch_trailer(movie_id))
        director, cast = fetch_details(movie_id)
        recommended_movie_details.append({"director": director, "cast": cast})
    return recommended_movies, recommended_movie_posters, recommended_movie_urls, recommended_movie_trailers, recommended_movie_details


movies_list = pickle.load(open('movie_list.pkl', 'rb'))
movie_list = movies_list['title'].values
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title("Movie Recommender System")

selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button("Recommend"):
    recommended_movie_names, recommended_movie_posters, recommended_movie_urls, recommended_movie_trailers, recommended_movie_details = recommend(
        selected_movie)

    # Horizontal layout for displaying movie recommendations
    for idx in range(len(recommended_movie_names)):
        col = st.container()  # Each movie in its container for horizontal alignment
        with col:
            poster = recommended_movie_posters[idx]
            trailer = recommended_movie_trailers[idx]
            wiki = recommended_movie_urls[idx]
            title = recommended_movie_names[idx]
            details = recommended_movie_details[idx]

            cols = st.columns([1, 3])  # Two-column layout within each container
            with cols[0]:  # Poster section
                if trailer:
                    st.markdown(
                        f'<a href="{trailer}" target="_blank" style="text-decoration:none;" title="Watch Trailer">'
                        f'<img src="{poster}" alt="{title}" width="100%"></a>',
                        unsafe_allow_html=True
                    )
                else:
                    st.image(poster, caption="Trailer not available")

            with cols[1]:  # Movie details
                st.markdown(
                    f'<a href="{wiki}" target="_blank" style="text-decoration:none;font-size:24px;color:blue;" '
                    f'title="Go to Wikipedia">{title}</a>',
                    unsafe_allow_html=True
                )
                st.write(f"**Director:** {details['director']}")
                st.write("**Main Cast:**")
                for actor in details['cast']:
                    st.write(f"- {actor}")
            st.markdown("---")  # Horizontal separator between movies
