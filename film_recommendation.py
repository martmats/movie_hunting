import streamlit as st
import logging
import google.generativeai as genai
import re

# Configure logging (local logging)
logging.basicConfig(level=logging.INFO)

# Sidebar for User Input
st.sidebar.title("AI-Powered Movie Recommendation Engine")
st.sidebar.subheader("Personalize Your Movie Recommendations")

# Input field for Google API Key
google_api_key = st.sidebar.text_input("Please enter your Google API key:")

if google_api_key:
    # Configure Google Generative AI
    try:
        genai.configure(api_key=google_api_key)
        st.sidebar.success("Successfully configured Google Generative AI!")
    except Exception as e:
        st.sidebar.error("Failed to configure Google Generative AI.")
        st.sidebar.write(str(e))

    # Sidebar for movie preferences
    genre = st.sidebar.selectbox(
        "What genre of movies do you prefer?",
        ("Action", "Comedy", "Drama", "Horror", "Romantic", "Sci-Fi", "Thriller"),
        placeholder="Select your preferred genre."
    )
    actor = st.sidebar.text_input(
        "Favorite actor/actress:",
        value="Leonardo DiCaprio"
    )
    director = st.sidebar.text_input(
        "Favorite director:",
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
        with st.spinner("Generating your movie recommendations using Gemini..."):
            try:
                # Simplified prompt for movie recommendations
                prompt = f"""
                Recommend some movies based on the following preferences:
                - Genre: {genre}
                - Actor/Actress: {actor}
                - Director: {director}
                - A movie they liked: {movie}
                Please include the title, a brief plot summary, the main cast, an image URL, and available platforms.
                """

                config = {
                    "temperature": 0.7,
                    "max_output_tokens": 2048,
                }

                # Using genai to generate recommendations
                response = genai.generate_text(prompt=prompt, temperature=config["temperature"], max_output_tokens=config["max_output_tokens"])

                if response and response.result:  # Ensure the response is valid
                    recommendations = response.result

                    # Print the raw AI response to debug the format
                    st.write("Debug - Raw AI Response:", recommendations)

                    # Adjusted regex pattern to capture movie recommendations
                    pattern = re.compile(
                        r'Title:\s*(.*?)\nPlot:\s*(.*?)\nCast:\s*(.*?)\nPoster URL:\s*(.*?)\nPlatforms:\s*(.*?)\n'
                    )
                    movies = pattern.findall(recommendations)

                    if movies:
                        st.write("Your movie recommendations:")

                        cols = st.columns(2)  # Create 2 columns for displaying recommendations in rows
                        for i, movie in enumerate(movies):
                            title, plot, cast, image_url, platforms = movie

                            with cols[i % 2]:  # Distribute recommendations across columns
                                st.markdown(f"""
                                <div style="padding: 10px; border: 1px solid #ddd; border-radius: 10px; margin-bottom: 10px;">
                                    <img src="{image_url.strip()}" alt="{title}" style="width:100%; height:auto; border-radius:10px;">
                                    <h4>{title}</h4>
                                    <p><strong>Plot:</strong> {plot.strip()}</p>
                                    <p><strong>Cast:</strong> {cast.strip()}</p>
                                    <p><strong>Platforms:</strong> {platforms.strip()}</p>
                                </div>
                                """, unsafe_allow_html=True)

                    else:
                        st.warning("No movie recommendations were generated.")
                    
                    logging.info(recommendations)
                else:
                    st.warning("No recommendations were generated. Please try again.")
            except Exception as e:
                st.error("Failed to generate AI recommendations.")
                st.write(str(e))
