import streamlit as st
import pickle
import requests

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    try:
        response = requests.get(url, timeout=10)  # Set a timeout of 10 seconds
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        poster_path = data.get('poster_path', '')
        if poster_path:
            return f"http://image.tmdb.org/t/p/w500/{poster_path}"
    except requests.exceptions.Timeout:
        st.error("The request to TMDB timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
    return "https://via.placeholder.com/500x750?text=Poster+Not+Available"  # Fallback poster

def recommend(movie):
    index_value = movies_list[movies_list['title'] == movie].index[0]
    index=int(index_value)
    distances = sorted(list(enumerate(similarity[index])),reverse=True,key = lambda x: x[1])[1:6]

    recommended_movies=[]
    recommended_movie_posters = []
    for i in distances:
        movie_id = movies_list.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movies.append(movies_list.iloc[i[0]].title)
    return recommended_movies,recommended_movie_posters

movies_list = pickle.load(open('movie_list.pkl', 'rb'))
movie_list = movies_list['title'].values
similarity=pickle.load(open('similarity.pkl', 'rb'))

st.title("Movie Recommender System")

selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button("Recommend"):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(recommended_movie_names[0])
        st.image(recommended_movie_posters[0])
    with col2:
        st.text(recommended_movie_names[1])
        st.image(recommended_movie_posters[1])

    with col3:
        st.text(recommended_movie_names[2])
        st.image(recommended_movie_posters[2])
    with col4:
        st.text(recommended_movie_names[3])
        st.image(recommended_movie_posters[3])
    with col5:
        st.text(recommended_movie_names[4])
        st.image(recommended_movie_posters[4])


