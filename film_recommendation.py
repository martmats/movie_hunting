import os
import streamlit as st
import logging
import google.generativeai as genai

# Configure logging (local logging)
logging.basicConfig(level=logging.INFO)

# Load API keys from secrets
google_api_key = st.secrets["GOOGLE_API_KEY"]

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
        recommendations_tab, prompt_tab = st.tabs(["Recommendations", "Prompt"])
        with recommendations_tab:
            try:
                # Using genai to generate recommendations
                response = genai.generate_text(prompt=prompt, temperature=config["temperature"], max_output_tokens=config["max_output_tokens"])
                
                # Extracting the text from the response
                recommendations = response.result
                st.write("Raw AI Response:", recommendations)  # For debugging

                # Splitting the response into separate movie recommendations
                movies = recommendations.split("\n\n")  # Assuming each movie block is separated by double new lines

                # Display recommendations with CSS styling
                st.write("Your movie recommendations:")
                
                st.markdown('<div class="movies-container">', unsafe_allow_html=True)
                
                cols = st.columns(2)  # Create 2 columns for displaying recommendations in rows
                for i, movie in enumerate(movies):
                    lines = movie.split("\n")
                    if len(lines) >= 4:
                        title = lines[0].strip("1. ").strip()
                        plot = lines[2].replace("A brief description of the plot:", "").strip()
                        image_url = lines[4].replace("An image URL of the movie poster:", "").strip()
                        platform = lines[6].replace("The platforms where the movie can be watched:", "").strip()

                        with cols[i % 2]:  # Distribute recommendations across columns
                            st.markdown(f"""
                            <div class="movie-card">
                                <img src="{image_url}" alt="{title}" style="width:100%; height:auto; border-radius:10px;">
                                <div class="movie-info">
                                    <h4>{title}</h4>
                                    <p><strong>Platform:</strong> {platform}</p>
                                    <p>{plot}</p>
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
