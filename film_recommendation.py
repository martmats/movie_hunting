import os
import streamlit as st
import logging
import google.generativeai as genai

# Configure logging (local logging)
logging.basicConfig(level=logging.INFO)

# Load API keys from secrets
google_api_key = "AIzaSyBVkD-QgIk41F8g4Ro3l_6DwWgyXSqu4YY"

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

# Custom prompt for movie recommendations
prompt = f"""
I am a movie recommendation engine. Based on the following preferences, 
recommend some movies that the user might enjoy.
- Preferred genre: {genre}
- Favorite actor/actress: {actor}
- Favorite director: {director}
- A movie they liked: {movie}

Please include the movie title, a brief description, 
and why it matches the user's preferences.
"""

max_output_tokens = 2048

config = {
    "temperature": 0.7,
    "max_output_tokens": max_output_tokens,
}

generate_recommendations = st.button("Generate my movie recommendations", key="generate_recommendations")
if generate_recommendations and prompt:
    with st.spinner("Generating your movie recommendations using Gemini..."):
        recommendations_tab, prompt_tab = st.tabs(["Recommendations", "Prompt"])
        with recommendations_tab:
            try:
                # Using genai to generate recommendations
                response = genai.generate_text(prompt=prompt, temperature=config["temperature"], max_output_tokens=config["max_output_tokens"])
                
                # Extracting the text from the response
                if response and response.generations:
                    recommendations = response.generations[0].text
                else:
                    recommendations = "No recommendations found."
                
                # Display recommendations with CSS styling
                st.write("Your movie recommendations:")
                recommendations_list = recommendations.split('\n')  # Assuming each recommendation is separated by a new line
                
                # Create the container div for the movies
                st.markdown('<div class="movies-container">', unsafe_allow_html=True)
                
                cols = st.columns(4)  # Create 4 columns for displaying recommendations in rows
                for i, recommendation in enumerate(recommendations_list):
                    with cols[i % 4]:  # Distribute recommendations across 4 columns
                        st.markdown(f"""
                        <div class="movie-card">
                            <div class="movie-info">
                                <h4>{recommendation}</h4>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)  # Close the container div
                
                logging.info(recommendations)
            except Exception as e:
                st.error("Failed to generate AI recommendations.")
                st.write(str(e))
        with prompt_tab:
            st.text(prompt)
