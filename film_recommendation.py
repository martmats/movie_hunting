import streamlit as st
import requests

# Load the API key from secrets
api_key = st.secrets["tmdb_api_key"]

# CSS Styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# TMDB API Endpoints
base_url = "https://api.themoviedb.org/3"
discover_url = f"{base_url}/discover/movie"
genre_url = f"{base_url}/genre/movie/list"

# Get list of genres
def get_genres():
    response = requests.get(genre_url, params={"api_key": api_key})
    genres = response.json().get('genres', [])
    return {genre['name']: genre['id'] for genre in genres}

# Fetch movies based on filters
def fetch_movies(genre_id, min_rating, similar_to):
    params = {
        "api_key": api_key,
        "with_genres": genre_id,
        "vote_average.gte": min_rating,
        "include_adult": False,
    }
    if similar_to:
        params["with_keywords"] = similar_to

    response = requests.get(discover_url, params=params)
    return response.json().get('results', [])

# Streamlit App Layout
st.sidebar.title("Find Your Movie")
genres_dict = get_genres()

# Check if genres are available
if not genres_dict:
    st.error("Failed to load genres. Please try again later.")
else:
    genre = st.sidebar.selectbox("Genre", list(genres_dict.keys()))
    min_rating = st.sidebar.slider("Minimum Rating", 0, 10, 5)
    similar_to = st.sidebar.text_input("Similar to (Keyword)")

    if st.sidebar.button("Find Movies"):
        genre_id = genres_dict.get(genre)
        
        # Verify that genre_id was correctly retrieved
        if genre_id:
            movies = fetch_movies(genre_id, min_rating, similar_to)
            
            if movies:
                st.write(f"Showing movies for genre: **{genre}** with rating **{min_rating}** and similar to **{similar_to}**")

                for movie in movies:
                    st.write(f"**{movie['title']}** - Rating: {movie['vote_average']}")
                    st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}")
            else:
                st.warning("No movies found with the selected filters.")
        else:
            st.error("Selected genre is not available. Please try again.")
