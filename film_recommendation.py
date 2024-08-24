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
    try:
        response = requests.get(genre_url, params={"api_key": api_key})
        response.raise_for_status()  # Raise an error for bad status codes
        genres = response.json().get('genres', [])
        
        if not genres:
            st.error("No genres found. Please try again later.")
            return {}
        
        return {genre['name']: genre['id'] for genre in genres}
    
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        st.error(f"An error occurred: {err}")
    
    return {}

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

# Function to display films in rows and columns
def display_films_in_rows(films, card_class="movie-card"):
    cols = st.columns(4)  # Adjust the number of columns
    for i, film in enumerate(films):
        with cols[i % 4]:  # Place the film in one of the 4 columns
            st.markdown(f"""
            <div class="{card_class}">
                <img src="https://image.tmdb.org/t/p/w500{film['poster_path']}" alt="{film['title']}">
                <div class="movie-info">
                    <h4>{film['title']}</h4>
                    <p>Rating: {film['vote_average']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Streamlit App Layout
st.sidebar.title("Find Your Movie")
genres_dict = get_genres()

if not genres_dict:
    st.error("Failed to load genres. Please try again later.")
else:
    genre = st.sidebar.selectbox("Genre", list(genres_dict.keys()))
    min_rating = st.sidebar.slider("Minimum Rating", 0, 10, 5)
    similar_to = st.sidebar.text_input("Similar to (Keyword)")

    if st.sidebar.button("Find Movies"):
        genre_id = genres_dict.get(genre)
        
        if genre_id:
            movies = fetch_movies(genre_id, min_rating, similar_to)
            
            if movies:
                st.write(f"Showing movies for genre: **{genre}** with rating **{min_rating}** and similar to **{similar_to}**")
                display_films_in_rows(movies)  # Display films in rows and columns
            else:
                st.warning("No movies found with the selected filters.")
        else:
            st.error("Selected genre is not available. Please try again.")
