import html
import json
import pickle
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(
    page_title="CinePulse — Movie Recommender System",
    page_icon="🎬",
    layout="wide",
)

API_KEY = "315fdd58b5fa554d31eacaa4b41d4a80"
FALLBACK_POSTER = "https://image.tmdb.org/t/p/w500/8uO0gUM8aNqYLs1OsTBQiXu0fEv.jpg"

st.markdown(
    """
<style>
.block-container {
    max-width: 1140px;
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}
.brand-logo {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.5rem;
}
.brand-mark {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: #e50914;
    color: #ffffff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
}
.brand-name {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: 0.04em;
    color: #ffffff;
}
.movie-title {
    font-size: 0.92rem;
    font-weight: 500;
    line-height: 1.35;
    min-height: 2.75em;
    margin-bottom: 0.45rem;
    color: #fafafa;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>
<div class="brand-logo">
  <span class="brand-mark">🎬</span>
  <span class="brand-name">CinePulse</span>
</div>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_movies():
    with open("movies_dict.pkl", "rb") as f:
        movies_dict = pickle.load(f)
    return pd.DataFrame(movies_dict)


@st.cache_resource
def compute_similarity(tags):
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vectors = cv.fit_transform(tags)
    return cosine_similarity(vectors).astype("float32")


@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}?api_key={API_KEY}&language=en-US"
    try:
        data = requests.get(url, timeout=5).json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except Exception:
        pass
    return FALLBACK_POSTER


@st.cache_data(show_spinner=False)
def fetch_hero_slides(movie_ids_and_titles):
    slides = []
    for movie_id, title in movie_ids_and_titles:
        url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}?api_key={API_KEY}&language=en-US"
        img_url = None
        try:
            data = requests.get(url, timeout=5).json()
            path = data.get("backdrop_path") or data.get("poster_path")
            if path:
                img_url = f"https://image.tmdb.org/t/p/w1280{path}"
        except Exception:
            pass
        if img_url:
            slides.append({"title": title, "image": img_url})
    return slides


movies = load_movies()
similarity = compute_similarity(movies["tags"])

preferred_titles = ["Spider-Man 2", "The Dark Knight", "Interstellar", "Inception"]
hero_df = movies[movies["title"].isin(preferred_titles)]
hero_df = movies.head(4) if len(hero_df) < 4 else hero_df.head(4)

hero_slides = fetch_hero_slides(
    tuple((int(row.movie_id), str(row.title)) for _, row in hero_df.iterrows())
)

if hero_slides:
    slides_json = json.dumps(hero_slides)
    components.html(
        f"""
        <style>
          * {{ box-sizing: border-box; margin: 0; padding: 0; }}
          body {{ background: transparent; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
          .hero {{
            position: relative;
            width: 100%;
            height: 340px;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.12);
            background: #141720;
          }}
          .slide {{
            position: absolute;
            inset: 0;
            opacity: 0;
            transition: opacity 0.7s ease-in-out;
          }}
          .slide.active {{ opacity: 1; }}
          .slide img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
          }}
          .scrim {{
            position: absolute;
            inset: 0;
            background: linear-gradient(to top, rgba(14,17,23,0.9) 0%, rgba(14,17,23,0.25) 55%, transparent 100%);
          }}
          .overlay {{
            position: absolute;
            left: 24px;
            right: 24px;
            bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
          }}
          .caption {{
            color: #e4e4e7;
            font-size: 15px;
            font-weight: 500;
          }}
          .dots {{
            display: flex;
            gap: 6px;
          }}
          .dot {{
            height: 6px;
            width: 8px;
            border-radius: 999px;
            background: rgba(255,255,255,0.35);
            transition: all 0.3s ease;
          }}
          .dot.active {{
            width: 28px;
            background: #ffffff;
          }}
        </style>
        <div class="hero" id="hero">
          <div class="scrim"></div>
          <div class="overlay">
            <div class="caption" id="caption"></div>
            <div class="dots" id="dots"></div>
          </div>
        </div>
        <script>
          const slides = {slides_json};
          const hero = document.getElementById("hero");
          const caption = document.getElementById("caption");
          const dotsWrap = document.getElementById("dots");

          slides.forEach((s, i) => {{
            const div = document.createElement("div");
            div.className = "slide" + (i === 0 ? " active" : "");
            const img = document.createElement("img");
            img.src = s.image;
            img.alt = s.title;
            div.appendChild(img);
            hero.insertBefore(div, hero.firstChild);

            const dot = document.createElement("div");
            dot.className = "dot" + (i === 0 ? " active" : "");
            dotsWrap.appendChild(dot);
          }});

          const slideEls = hero.querySelectorAll(".slide");
          const dotEls = dotsWrap.querySelectorAll(".dot");
          let idx = 0;
          caption.textContent = slides[0].title;

          setInterval(() => {{
            slideEls[idx].classList.remove("active");
            dotEls[idx].classList.remove("active");
            idx = (idx + 1) % slides.length;
            slideEls[idx].classList.add("active");
            dotEls[idx].classList.add("active");
            caption.textContent = slides[idx].title;
          }}, 3500);
        </script>
        """,
        height=355,
    )


def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters


selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movies["title"].values,
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.markdown(
                f'<div class="movie-title">{html.escape(names[idx])}</div>',
                unsafe_allow_html=True,
            )
            st.image(posters[idx], use_container_width=True)
