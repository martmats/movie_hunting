import streamlit as st
import logging
import google.generativeai as genai
import re

# Configure logging (local logging)
logging.basicConfig(level=logging.INFO)

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
        index=None,
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
    st.subheader("Personalize Your Movie Recommendations")

    if generate_recommendations:
        with st.spinner("Generating your movie recommendations using Gemini..."):
            try:
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
                3. The main cast.
                4. An image URL of the movie poster.
                5. The platforms where the movie can be watched (e.g., Netflix, Amazon Prime).
                """

                max_output_tokens = 2048

                config = {
                    "temperature": 0.7,
                    "max_output_tokens": max_output_tokens,
                }

                # Using genai to generate recommendations
                response = genai.generate_text(prompt=prompt, temperature=config["temperature"], max_output_tokens=config["max_output_tokens"])

                if response and response.result:  # Ensure the response is valid
                    recommendations = response.result
                    
                    # Regex pattern to capture multiple movies correctly
                    pattern = re.compile(
                        r'\#\#\s*(.*?)\s*\((\d{4})\)\s*\*\s*A brief description of the plot:\s*(.*?)\s*\*\s*The main cast:\s*(.*?)\s*\*\s*An image URL of the movie poster:\s*(.*?)\s*\*\s*The platforms where the movie can be watched:\s*(.*?)\n'
                    )
                    movies = pattern.findall(recommendations)

                    if movies:
                        st.write("Your movie recommendations:")
                        
                        st.markdown('<div class="movies-container">', unsafe_allow_html=True)
                        
                        cols = st.columns(2)  # Create 2 columns for displaying recommendations in rows
                        for i, movie in enumerate(movies):
                            title, year, plot, cast, image_url, platform_raw = movie
                            platform = ', '.join([p.strip() for p in platform_raw.split('*') if p.strip()])

                            with cols[i % 2]:  # Distribute recommendations across columns
                                st.markdown(f"""
                                <div class="movie-card">
                                    <img src="{image_url.strip()}" alt="{title} ({year})" style="width:100%; height:auto; border-radius:10px;">
                                    <div class="movie-info">
                                        <h4>{title} ({year})</h4>
                                        <p><strong>Platform:</strong> {platform}</p>
                                        <p><strong>Cast:</strong> {cast.strip()}</p>
                                        <p>{plot.strip()}</p>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)  # Close the container div
                        
                    else:
                        st.warning("No movie recommendations were generated.")
                    
                    logging.info(recommendations)
                else:
                    st.warning("No recommendations were generated. Please try again.")
            except Exception as e:
                st.error("Failed to generate AI recommendations.")
                st.write(str(e))
