import streamlit as st
import logging
import google.generativeai as genai

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

                    # Debugging: print the raw AI response
                    st.write("Raw AI Response:", recommendations)

                    # Adjust regex pattern after seeing the raw output
                    pattern = re.compile(
                        r'Title:\s*(.*?)\s*Genre:\s*(.*?)\s*Actor/Actress:\s*(.*?)\s*Director:\s*(.*?)\s*Plot Summary:\s*(.*?)\s*Image URL:\s*(.*?)\s*Available Platforms:\s*(.*)'
                    )
                    movies = pattern.findall(recommendations)

                    if movies:
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

                        for movie in movies:
                            title, genre, actor, director, plot, image_url, platforms = movie

                            st.markdown(f"""
                            <div class="movie-card">
                                <img src="{image_url.strip()}" alt="{title}" style="border-radius:10px;">
                                <h4>{title}</h4>
                                <p><strong>Genre:</strong> {genre.strip()}</p>
                                <p><strong>Actor/Actress:</strong> {actor.strip()}</p>
                                <p><strong>Director:</strong> {director.strip()}</p>
                                <p><strong>Plot Summary:</strong> {plot.strip()}</p>
                                <p class="platforms"><strong>Available Platforms:</strong> {platforms.strip()}</p>
                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown('</div>', unsafe_allow_html=True)

                    else:
                        st.warning("No movie recommendations were generated.")
                    
                    logging.info(recommendations)
                else:
                    st.warning("No recommendations were generated. Please try again.")
            except Exception as e:
                st.error("Failed to generate AI recommendations.")
                st.write(str(e))
