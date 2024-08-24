import os
import streamlit as st
import logging
import google.generativeai as genai

# Configure logging (local logging)
logging.basicConfig(level=logging.INFO)

# Load API keys from secrets
google_api_key = "AIzaSyBVkD-QgIk41F8g4Ro3l_6DwWgyXSqu4YY"
tmdb_api_key = st.secrets["tmdb_api_key"]

# Configure Google Generative AI
try:
    genai.configure(api_key=google_api_key)
    st.success("Successfully configured Google Generative AI!")
except Exception as e:
    st.error("Failed to configure Google Generative AI.")
    st.write(str(e))

# Load CSS Styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# Function to get TMDB poster image URL
def get_movie_poster(movie_title):
    search_url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": tmdb_api_key,
        "query": movie_title
    }
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results and results[0].get('poster_path'):
            return f"https://image.tmdb.org/t/p/w500{results[0]['poster_path']}"
    return "https://via.placeholder.com/220x330?text=No+Image"  # Placeholder if no image found

# User Interface
st.header("AI-Powered Movie Recommendation Engine", divider="gray")
st.subheader("Personalize Your Movie Recommendations")

# User inputs for movie preferences
genre = st.selectbox(
    "What genre of movies do you prefer?",
    ("Action", "Comedy", "Drama", "Horror", "Romantic", "Sci-Fi", "Thriller"),
    index=None,
    placeholder="Select your preferred genre."
)

actor = st.text_input(
    "Favorite actor/actress:",
    value="Leonardo DiCaprio"
)

director = st.text_input(
    "Favorite director:",
    value="Christopher Nolan"
)

movie = st.text_input(
    "Enter a movie you like:",
    value="Inception"
)

# Custom prompt for movie recommendations with specific details
prompt = f"""
I am a movie recommendation engine. Based on the following preferences, 
recommend some movies that the user might enjoy.
- Preferred genre: {genre}
- Favorite actor/actress: {actor}
- Favorite director: {director}
- A movie they liked: {movie}

For each recommended movie, please include:
1. The movie title.
2. A brief description of the plot.
3. An image URL of the movie poster.
4. The platforms where the movie can be watched (e.g., Netflix, Amazon Prime).
"""

max_output_tokens = 2048

config = {
    "temperature": 0.7,
    "max_output_tokens": max_output_tokens,
}

generate_recommendations = st.button("Generate my movie recommendations", key="generate_recommendations")
if generate_recommendations and prompt:
    with st.spinner("Generating your movie recommendations using Gemini..."):
        try:
            response = genai.generate_text(prompt=prompt, temperature=config["temperature"], max_output_tokens=config["max_output_tokens"])
            
            if response and response.result:
                recommendations = response.result
                movies = recommendations.split("\n\n")  # Assuming each movie block is separated by double new lines
                
                if movies:
                    st.write("Your movie recommendations:")
                    
                    st.markdown('<div class="movies-container">', unsafe_allow_html=True)
                    
                    cols = st.columns(2)  # Create 2 columns for displaying recommendations in rows
                    for i, movie in enumerate(movies):
                        lines = movie.split("\n")
                        if len(lines) >= 4:
                            title = lines[0].split(".")[1].strip()
                            plot = lines[2].replace("A brief description of the plot:", "").strip()
                            poster_url = get_movie_poster(title)  # Get TMDB poster URL
                            platform = lines[3].replace("Platforms:", "").strip()

                            with cols[i % 2]:  # Distribute recommendations across columns
                                st.markdown(f"""
                                <div class="movie-card">
                                    <img src="{poster_url}" alt="{title}" style="width:100%; height:auto; border-radius:10px;">
                                    <div class="movie-info">
                                        <h4>{title}</h4>
                                        <p><strong>Platform:</strong> {platform}</p>
                                        <p>{plot}</p>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)  # Close the container div
                    
                else:
                    st.warning("No movie recommendations were generated.")
            
            else:
                st.warning("No recommendations were generated. Please try again.")
        except Exception as e:
            st.error("Failed to generate AI recommendations.")
            st.write(str(e))
