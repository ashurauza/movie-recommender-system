import pickle
import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image, ImageDraw
import io
import base64

# Create a requests session with retry strategy
def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

@st.cache_resource
def get_session():
    return create_session()

def create_movie_poster(title):
    """Create an attractive movie poster with title"""
    import random
    
    # Color palette for movie posters
    colors = [
        (25, 50, 100),    # Dark blue
        (139, 0, 0),      # Dark red
        (34, 139, 34),    # Dark green
        (75, 0, 130),     # Indigo
        (184, 134, 11),   # Dark goldenrod
        (47, 79, 79),     # Dark slate gray
        (105, 105, 105),  # Dim gray
        (220, 20, 60),    # Crimson
    ]
    
    # Select a random color for variation
    bg_color = random.choice(colors)
    
    img = Image.new('RGB', (500, 750), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Add a gradient-like effect with semi-transparent rectangles
    for i in range(0, 750, 50):
        alpha = int(50 * (i / 750))
        overlay = Image.new('RGB', (500, 50), color=(255, 255, 255))
        img.paste(overlay, (0, i), Image.new('L', (500, 50), alpha))
    
    # Draw title with better formatting
    title_lines = []
    words = title.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if len(test_line) > 20:
            if current_line:
                title_lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    
    if current_line:
        title_lines.append(current_line)
    
    # Calculate starting y position
    line_height = 60
    total_height = len(title_lines) * line_height
    start_y = (750 - total_height) // 2
    
    # Draw each line of text
    for i, line in enumerate(title_lines):
        y_position = start_y + (i * line_height)
        draw.text(
            (250, y_position),
            line,
            fill=(255, 255, 255),
            anchor="mm",
            font=None
        )
    
    # Add a frame/border effect
    draw.rectangle([(10, 10), (490, 740)], outline=(255, 255, 255), width=3)
    
    return img

def fetch_poster(movie_id, movie_title=None):
    """Generate a custom movie poster without API calls"""
    if movie_title:
        return create_movie_poster(movie_title)
    return create_movie_poster("Movie Poster")

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters


st.header('Movie Recommender System')
movies = pickle.load(open('model/movie_list.pkl','rb'))
similarity = pickle.load(open('model/similarity.pkl','rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(recommended_movie_names[0])
        st.image(recommended_movie_posters[0])
    with col2:
        st.text(recommended_movie_names[1])
        st.image(recommended_movie_posters[1])
    with col3:
        st.text(recommended_movie_names[2])
        st.image(recommended_movie_posters[2])
    with col4:
        st.text(recommended_movie_names[3])
        st.image(recommended_movie_posters[3])
    with col5:
        st.text(recommended_movie_names[4])
        st.image(recommended_movie_posters[4])





