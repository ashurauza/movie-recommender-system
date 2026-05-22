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

def create_placeholder_image(text="No Poster"):
    """Create a simple placeholder image"""
    img = Image.new('RGB', (500, 750), color=(70, 130, 180))
    draw = ImageDraw.Draw(img)
    draw.text((250, 375), text, fill=(255, 255, 255), anchor="mm")
    
    # Convert to bytes for Streamlit
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img

def fetch_poster(movie_id):
    try:
        session = get_session()
        url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            poster_path = data['poster_path']
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            # Try to fetch the actual poster image
            try:
                poster_response = session.get(full_path, timeout=10)
                poster_response.raise_for_status()
                return Image.open(io.BytesIO(poster_response.content))
            except:
                return create_placeholder_image("Poster Available")
        else:
            return create_placeholder_image("No Poster Available")
    except requests.exceptions.Timeout:
        print(f"Timeout fetching poster for movie {movie_id}")
        return create_placeholder_image("Timeout")
    except requests.exceptions.ConnectionError:
        print(f"Connection error fetching poster for movie {movie_id}")
        return create_placeholder_image("API Unreachable")
    except Exception as e:
        print(f"Error fetching poster for movie {movie_id}: {str(e)}")
        return create_placeholder_image("Error")

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





