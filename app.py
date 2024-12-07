import streamlit as st
import pickle
import requests
import webbrowser

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path', '')
        if poster_path:
            return f"http://image.tmdb.org/t/p/w500/{poster_path}"
    except requests.exceptions.Timeout:
        st.error("The request to TMDB timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
    return "https://via.placeholder.com/500x750?text=Poster+Not+Available"

def fetch_wikipedia_url(movie_title):
    search_url = f"https://en.wikipedia.org/wiki/{movie_title.replace(' ', '_')}"
    return search_url

def recommend(movie):
    index_value = movies_list[movies_list['title'] == movie].index[0]
    index = int(index_value)
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    recommended_movie_posters = []
    recommended_movie_urls = []
    for i in distances:
        movie_id = movies_list.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        movie_title = movies_list.iloc[i[0]].title
        recommended_movies.append(movie_title)
        recommended_movie_urls.append(fetch_wikipedia_url(movie_title))
    return recommended_movies, recommended_movie_posters, recommended_movie_urls

movies_list = pickle.load(open('movie_list.pkl', 'rb'))
movie_list = movies_list['title'].values
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title("Movie Recommender System")

selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button("Recommend"):
    recommended_movie_names, recommended_movie_posters, recommended_movie_urls = recommend(selected_movie)
    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]

    for idx, col in enumerate(columns):
        with col:
            link = recommended_movie_urls[idx]
            text = recommended_movie_names[idx]
            image = recommended_movie_posters[idx]
            st.markdown(
                f'<a href="{link}" target="_blank" style="text-decoration:none;" title="Go to Wikipedia"><img src="{image}" alt="{text}" width="100%"></a>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<a href="{link}" target="_blank" style="text-decoration:none;" title="Go to Wikipedia">{text}</a>',
                unsafe_allow_html=True
            )
