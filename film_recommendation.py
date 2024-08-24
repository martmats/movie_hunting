import streamlit as st
import requests
import google.generativeai as genai

# Load API keys from secrets
tmdb_api_key = st.secrets["tmdb_api_key"]
google_api_key = st.secrets["AIzaSyBVkD-QgIk41F8g4Ro3l_6DwWgyXSqu4YY"]

# Configure Google Generative AI
try:
    genai.configure(api_key=google_api_key)
    st.success("Successfully configured Google Generative AI!")
except Exception as e:
    st.error("Failed to configure Google Generative AI.")
    st.write(str(e))

# CSS Styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# TMDB API Endpoints
tmdb_base_url = "https://api.themoviedb.org/3"
search_url = f"{tmdb_base_url}/search/movie"
details_url = f"{tmdb_base_url}/movie"

# Fetch movie details from TMDB
def fetch_movie_details(movie_name):
    response = requests.get(search_url, params={"api_key": tmdb_api_key, "query": movie_name})
    response.raise_for_status()
    return response.json().get('results', [])

# Use Google Generative AI to enhance recommendations
def generate_recommendations(movie_title):
    try:
        prompt = f"Recommend me movies similar to {movie_title} with augmented details from TMDB and IMDB."
        response = genai.generate_text(prompt=prompt)
        return response['text'] if 'text' in response else "No recommendations found."
    except Exception as e:
        st.error("Failed to generate AI recommendations.")
        st.write(str(e))
        return "No recommendations found."

# Function to display AI recommendations
def display_recommendations(recommendations):
    st.write("### AI-Enhanced Recommendations")
    st.write(recommendations)

# Streamlit App Layout
st.sidebar.title("Movie Recommendation Engine")

# User input for movie they like
user_movie = st.sidebar.text_input("Enter a movie you like")

if st.sidebar.button("Get Recommendations"):
    if user_movie:
        # Fetch movie details
        movies = fetch_movie_details(user_movie)

        if movies:
            # Get the first matching movie (you can enhance this to let users select from multiple)
            movie_title = movies[0]['title']

            st.write(f"### You selected: {movie_title}")

            # Generate AI-enhanced recommendations
            recommendations = generate_recommendations(movie_title)

            # Display recommendations
            display_recommendations(recommendations)
        else:
            st.warning("No movies found with the selected name.")
    else:
        st.warning("Please enter a movie name.")

