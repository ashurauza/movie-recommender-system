import pickle
import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image, ImageDraw, ImageFont
import io
import base64

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
    import random
    
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
    
    bg_color = random.choice(colors)
    
    img = Image.new('RGB', (500, 750), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    for i in range(0, 750, 50):
        overlay = Image.new('RGB', (500, 50), color=(255, 255, 255))
        img.paste(overlay, (0, i), Image.new('L', (500, 50), int(50 * (i / 750))))
    
    # Try to load large fonts
    font_size = 60
    font = None
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Split title into lines intelligently with better wrapping
    title_lines = []
    words = title.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        # Shorter max chars to ensure text fits within poster
        max_chars = 12 if len(title) > 25 else 15
        if len(test_line) > max_chars:
            if current_line:
                title_lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    
    if current_line:
        title_lines.append(current_line)
    
    # If text is too long or too many lines, reduce font size
    if len(title_lines) > 2 or any(len(line) > 15 for line in title_lines):
        font_size = 45
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                pass
    
    if len(title_lines) > 3:
        font_size = 32
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                pass
    
    # Calculate starting y position with safe bounds
    line_height = font_size + 12
    total_height = len(title_lines) * line_height
    
    # More generous margins to ensure text stays within bounds
    top_margin = 100
    bottom_margin = 100
    available_height = 750 - top_margin - bottom_margin
    
    # If text is too tall, adjust line height
    if total_height > available_height:
        line_height = available_height // len(title_lines)
        total_height = len(title_lines) * line_height
    
    # Calculate safe starting position
    start_y = (750 - total_height) // 2
    start_y = max(top_margin, start_y)
    
    # Ensure the last line doesn't go past bottom margin
    last_line_y = start_y + (len(title_lines) - 1) * line_height
    if last_line_y + font_size // 2 + 20 > 750 - bottom_margin:
        start_y = 750 - bottom_margin - total_height
    
    start_y = max(top_margin, start_y)
    
    # Draw each line of text with outline for better visibility
    outline_range = 1
    for i, line in enumerate(title_lines):
        y_position = start_y + (i * line_height)
        
        # Draw text outline
        for adj_x in range(-outline_range, outline_range + 1):
            for adj_y in range(-outline_range, outline_range + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text(
                        (250 + adj_x, y_position + adj_y),
                        line,
                        fill=(0, 0, 0),
                        anchor="mm",
                        font=font
                    )
        
        # Draw main text in white
        draw.text(
            (250, y_position),
            line,
            fill=(255, 255, 255),
            anchor="mm",
            font=font
        )
    
    # Add border only
    draw.rectangle([(10, 10), (490, 740)], outline=(255, 255, 255), width=4)
    
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
        movie_title = movies.iloc[i[0]].title
        recommended_movie_posters.append(fetch_poster(movie_id, movie_title))
        recommended_movie_names.append(movie_title)

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





