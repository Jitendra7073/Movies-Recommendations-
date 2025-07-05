import streamlit as st
import pickle
import requests
import time
import warnings

warnings.filterwarnings("ignore")


# Load Data

try:
    movies_list = pickle.loads(open("movies.pkl", "rb").read())
    similarity = pickle.loads(open("similarity.pkl", "rb").read())
except Exception:
    movies_list = None
    similarity = None


# Custom CSS for Better UI

st.markdown(
    """
    <style>
    body {
        background-color: #f4f4f4;
    }
    .main-container {
        max-width: 1300px;
        margin: auto;
        padding: 20px;
    }
    .main-title {
        text-align: center;
        font-size: 32px;
        color: #fff;
        margin-top: 10px;
    }
    .nav-selectbox label {
        font-weight: bold;
    }
    .stButton > button {
        background-color: #222;
        border: 2px solid #555;
        margin:5% 0;
        color: white;
        width: 100%;
        border-radius: 10px;
        font-size: 16px;
        padding: 10px 20px;
    }
    .stButton > button:hover {
        color: white;
    }
    .stAlert { display: none; }
    .css-ffhzg2 { visibility: hidden; height: 0px; } /* Hide warnings */
    </style>
    <div class='main-container'>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='main-title'> Movie Recommendation System</div>", unsafe_allow_html=True
)


# Unified Navigation

with st.container():

    selected_page = st.selectbox(
        "📁 Choose a Page", ["Home", "All Movies", "About"], key="nav_select"
    )

    # Poster Fetching with Retry and Silent Failure

    session = requests.Session()
    session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))

    @st.cache_data(show_spinner=False)
    def fetch_poster(movie_id):
        try:
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=f08c02018ef8953ae4df4ad889984b67&language=en-US"
            response = session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get("poster_path")
            return (
                f"https://image.tmdb.org/t/p/w500/{poster_path}"
                if poster_path
                else "https://via.placeholder.com/500x750?text=No+Image"
            )
        except:
            return "https://via.placeholder.com/500x750?text=Error"

    def fetch_background(movie_id):
        try:
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=f08c02018ef8953ae4df4ad889984b67&language=en-US"
            response = session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get("backdrop_path")
            return (
                f"https://image.tmdb.org/t/p/w500/{poster_path}"
                if poster_path
                else "https://via.placeholder.com/500x750?text=No+Image"
            )
        except:
            return "https://via.placeholder.com/500x750?text=Error"

    # Recommendation Function

    def recommend_movies(movie):
        try:
            index = movies_list[movies_list["title"] == movie].index[0]
            distances = similarity[index]
            recommended = sorted(
                list(enumerate(distances)), reverse=True, key=lambda x: x[1]
            )[1:6]
            movie_names, movie_posters = [], []
            for i in recommended:
                movie_id = movies_list.iloc[i[0]].movie_id
                movie_names.append(movies_list.iloc[i[0]].title)
                movie_posters.append(fetch_poster(movie_id))
                time.sleep(0.3)
            return movie_names, movie_posters
        except:
            return [], []

    # Pages

    if selected_page == "Home":
        if movies_list is not None:
            st.subheader(" Find Similar Movies")
            selected_movie = st.selectbox(
                "🎞 Select a Movie", movies_list["title"].values
            )

            if st.button(" Recommend"):
                with st.spinner("Fetching recommendations..."):
                    names, posters = recommend_movies(selected_movie)
                    if names:
                        # Display hero section with background image
                        movie_index = movies_list[
                            movies_list["title"] == selected_movie
                        ].index[0]
                        movie_id = movies_list.iloc[movie_index].movie_id
                        backdrop_url = f"https://image.tmdb.org/t/p/original/{movie_id}"

                        st.markdown("### Top 5 Recommendations")
                        cols = st.columns(5)
                        for i in range(len(names)):
                            with cols[i]:
                                st.image(posters[i], use_column_width=True)
                                st.caption(names[i])
                    else:
                        st.info("No recommendations found. Please try another movie.")
        else:
            st.error(" Failed to load movie data. Please check your dataset.")

    elif selected_page == "All Movies":
        if movies_list is not None:
            st.subheader(" All Movies in the Dataset")

            if "visible_count" not in st.session_state:
                st.session_state.visible_count = 10

            visible_movies = movies_list.iloc[: st.session_state.visible_count]
            cols = st.columns(5)
            for idx, row in visible_movies.iterrows():
                with cols[idx % 5]:
                    poster = fetch_poster(row.movie_id)
                    st.image(poster, use_column_width=True)
                    st.caption(row.title)

            if st.session_state.visible_count < len(movies_list):
                if st.button(" Show More"):
                    st.session_state.visible_count += 10
        else:
            st.error("Movie list unavailable.")

    elif selected_page == "About":
        st.subheader(" About This App")
        st.markdown(
            """
            Welcome to the **Movie Recommendation System**! 
    
            This app helps you discover new movies based on content-based filtering powered by machine learning.
    
            ---
    
            ### Technologies Used
            - **pandas** for data manipulation
            - **numpy** for numerical computation
            - **scikit-learn** for vectorization & similarity
            - **NLTK** for text preprocessing
            - **pickle** for saved models
            - **Streamlit** for UI
            - **ast** for string to list conversion
    
            ---
    
            ### How it Works
            - Input: Movie title
            - Processing: Tag creation, vectorization, cosine similarity
            - Output: 5 most similar movies with posters
    
            ---
    
            ### Developer
            **Jitendra Suthar**  
            Final-year B.Tech CSE Student passionate about:
            - AI/ML
            - Data Analytics
            - Full Stack Development
        """
        )
