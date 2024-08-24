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

                # Create the container div for the movies
                st.markdown('<div class="movies-container">', unsafe_allow_html=True)

                # Iterate through movies and render them in the grid
                for index, movie in enumerate(movies):
                    movie_card = f"""
                    <div class="movie-card">
                        <img src="https://image.tmdb.org/t/p/w500{movie['poster_path']}" alt="{movie['title']} poster">
                        <div class="movie-info">
                            <h4>{movie['title']}</h4>
                            <p>Rating: {movie['vote_average']}</p>
                        </div>
                    </div>
                    """
                    # Insert a new row after every 4 movies
                    if index % 4 == 0 and index != 0:
                        st.markdown('</div><div class="movies-container">', unsafe_allow_html=True)
                    
                    st.markdown(movie_card, unsafe_allow_html=True)

                # Close the container div
                st.markdown('</div>', unsafe_allow_html=True)

            else:
                st.warning("No movies found with the selected filters.")
        else:
            st.error("Selected genre is not available. Please try again.")

