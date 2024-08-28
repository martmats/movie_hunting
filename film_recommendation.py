import streamlit as st
import logging
import os
import requests
import pandas as pd
from datetime import datetime
import google.generativeai as genai

# Configure logging (local logging)
logging.basicConfig(level=logging.INFO)

# My API Key
api_key = os.getenv('tmdb_api_key')

# Base URL
base_url = 'https://api.themoviedb.org/3'
# Base URL for poster images
poster_base_url = 'https://image.tmdb.org/t/p/w500'

# Function to fetch data from TMDB
def fetch_data(url, params):
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

# Function to fetch movies
def fetch_movies(url, params, pages):
    movies = []
    for page in range(1, pages + 1):
        params['page'] = page
        page_movies = fetch_data(url, params)['results']
        movies.extend(page_movies)
    return movies

# Function to fetch genres
def fetch_genres():
    genres_url = f'{base_url}/genre/movie/list'
    params = {'api_key': api_key, 'language': 'en-US'}
    genre_data = fetch_data(genres_url, params)['genres']
    genre_dict = {genre['id']: genre['name'] for genre in genre_data}
    return genre_dict

# Function to fetch watch providers
def fetch_watch_providers(movie_id):
    providers_url = f'{base_url}/movie/{movie_id}/watch/providers'
    params = {
        'api_key': api_key,
        'watch_region': 'GB'
    }
    providers_data = fetch_data(providers_url, params).get('results', {}).get('GB', {}).get('flatrate', [])
    provider_names = [provider['provider_name'] for provider in providers_data]
    provider_release_dates = [provider.get('release_date', None) for provider in providers_data]
    return provider_names, provider_release_dates

# Fetch trending movies
def fetch_trending_movies(media_type, time_window, pages):
    trending_url = f'{base_url}/trending/{media_type}/{time_window}'
    params = {'api_key': api_key, 'region': 'GB'}
    trending_movies = fetch_movies(trending_url, params, pages)
    for movie in trending_movies:
        movie['trending'] = True
    return trending_movies

# Discover movies by year
def discover_movies_by_year(year_from, year_to, pages, genres):
    discover_url = f'{base_url}/discover/movie'
    params = {
        'api_key': api_key,
        'region': 'GB',
        'primary_release_date.gte': f'{year_from}-01-01',
        'primary_release_date.lte': f'{year_to}-12-31',
        'with_genres': genres
    }
    discovered_movies = fetch_movies(discover_url, params, pages)
    for movie in discovered_movies:
        movie['trending'] = False
    return discovered_movies

# Configure Google Generative AI
def configure_genai(api_key):
    try:
        genai.configure(api_key=api_key)
        st.sidebar.success("Successfully configured Google Generative AI!")
    except Exception as e:
        st.sidebar.error("Failed to configure Google Generative AI.")
        st.sidebar.write(str(e))

# Sidebar for User Input
st.sidebar.title("AI-Powered Movie Recommendation Engine")
st.sidebar.subheader("Personalize Your Movie Recommendations")

# Input field for Google API Key
google_api_key = st.sidebar.text_input("Please enter your Google API key:")

if google_api_key:
    configure_genai(google_api_key)

# Sidebar for movie preferences
genre = st.sidebar.selectbox(
    "What genre of movies do you prefer?",
    ("Action", "Comedy", "Drama", "Horror", "Romantic", "Sci-Fi", "Thriller"),
    placeholder="Select your preferred genre."
)
actor = st.sidebar.text_input(
    "Favourite actor/actress:",
    value="Leonardo DiCaprio"
)
director = st.sidebar.text_input(
    "Favourite director:",
    value="Christopher Nolan"
)
movie = st.sidebar.text_input(
    "Enter a movie you like:",
    value="Inception"
)

# Button to generate recommendations
generate_recommendations = st.sidebar.button("Generate my movie recommendations", key="generate_recommendations")

# Main content area
st.header("AI-Powered Movie Recommendation Engine", divider="gray")

if generate_recommendations:
    with st.spinner("Fetching movie data from TMDB..."):
        try:
            # Fetch data for the Database
            trending_movies = fetch_trending_movies('movie', 'day', 10)  # Fetch 10 pages of trending movies
            genres_dict = fetch_genres()
            discovered_movies = discover_movies_by_year(2010, datetime.now().year, 5, '28')  # Fetch 5 pages of action movies from 2010 to present

            # Combine data
            all_movies = trending_movies + discovered_movies
            movies_df = pd.DataFrame(all_movies)

            # Add genres
            movies_df['genres'] = movies_df['genre_ids'].apply(lambda ids: [genres_dict.get(id) for id in ids])

            # Fetch providers and provider release dates
            provider_data = movies_df['id'].apply(fetch_watch_providers)
            movies_df['providers'], movies_df['provider_release_dates'] = zip(*provider_data)

            # Convert provider release dates to datetime.date and handle NaT
            def convert_to_date(dates):
                converted_dates = []
                for date in dates:
                    try:
                        converted_dates.append(pd.to_datetime(date).date() if date else None)
                    except Exception as e:
                        print(f"Error converting date: {date}, Error: {e}")
                        converted_dates.append(None)
                return converted_dates

            movies_df['provider_release_dates'] = movies_df['provider_release_dates'].apply(convert_to_date)

            # Add poster image URL
            movies_df['poster_image'] = movies_df['poster_path'].apply(lambda path: f"{poster_base_url}{path}" if path else None)

            # Add timestamp
            movies_df['timestamp'] = datetime.now()

            # Use Generative AI to generate personalized movie recommendations
            with st.spinner("Generating your movie recommendations using Gemini..."):
                movie_summaries = "\n".join([f"Title: {row['title']}, Plot: {row['overview']}" for _, row in movies_df.iterrows()])
                prompt = f"""
                Recommend some movies based on the following preferences:
                - Genre: {genre}
                - Actor/Actress: {actor}
                - Director: {director}
                - A movie they liked: {movie}
                - Here are some example movies with plots: {movie_summaries}
                Please include the title, a brief plot summary, the main cast, an image URL, and available platforms.
                """

                config = {
                    "temperature": 0.7,
                    "max_output_tokens": 2048,
                }

                response = genai.generate_text(prompt=prompt, temperature=config["temperature"], max_output_tokens=config["max_output_tokens"])

                if response and response.result:
                    recommendations = response.result

                    # Display the movie recommendations
                    st.markdown(
                        """
                        <style>
                        .movies-container {
                            display: flex;
                            flex-direction: column;
                            gap: 20px;
                        }
                        .movie-card {
                            background-color: #f9f9f9;
                            border: 1px solid #ddd;
                            border-radius: 10px;
                            padding: 15px;
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                            transition: transform 0.3s ease;
                        }
                        .movie-card:hover {
                            transform: translateY(-5px);
                        }
                        .movie-card img {
                            width: 100%;
                            height: auto;
                            border-radius: 10px;
                            margin-bottom: 15px;
                        }
                        .movie-card h4 {
                            margin-top: 10px;
                            font-size: 1.25rem;
                            color: #333;
                        }
                        .movie-card p {
                            font-size: 0.9rem;
                            color: #555;
                            margin-bottom: 10px;
                        }
                        .movie-card .platforms {
                            font-weight: bold;
                            color: #2a9d8f;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown('<div class="movies-container">', unsafe_allow_html=True)

                    # Parse AI response and display the recommendations
                    pattern = re.compile(
                        r'Title:\s*(.*?)\s*Genre:\s*(.*?)\s*Actors:\s*(.*?)\s*Director:\s*(.*?)\s*Plot summary:\s*(.*?)\s*Image URL:\s*(.*?)\s*Available platforms:\s*(.*)'
                    )
                    movies = pattern.findall(recommendations)

                    for movie in movies:
                        title, genre, actor, director, plot, image_url, platforms = movie

                        st.markdown(f"""
                        <div class="movie-card">
                            <h4>{title}</h4>
                            <p><strong>Genre:</strong> {genre.strip()}</p>
                            <p><strong>Actors:</strong> {actor.strip()}</p>
                            <p><strong>Director:</strong> {director.strip()}</p>
                            <p><strong>Plot Summary:</strong> {plot.strip()}</p>
                            <p class="platforms"><strong>Available Platforms:</strong> {platforms.strip()}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        if image_url.strip():
                            st.image(image_url.strip(), use_column_width=True)

                    st.markdown('</div>', unsafe_allow_html=True)

                else:
                    st.warning("No recommendations were generated. Please try again.")
                    
        except Exception as e:
            st.error("Failed to fetch movie data or generate recommendations.")
            st.write(str(e))
