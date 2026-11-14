# CinePulse

Live app: https://movie-recommender-system-epv7fyskqjexburnquebrh.streamlit.app

CinePulse is a movie recommender web app I built using the TMDB 5000 movies dataset. You pick any movie from the list of 5,000 films, click Recommend, and it finds the 5 closest movies based on plot, genres, keywords, cast, and director, along with their posters.

## Tech Stack

Python, Pandas, Scikit-Learn, Streamlit, TMDB API, HTML/CSS/JavaScript, Jupyter Notebook, PyCharm, GitHub

## How I Built It

I started in a notebook with the TMDB 5000 movies and credits datasets. First, I merged both files and cleaned up the columns I actually needed, which were the movie overview, genres, keywords, top three actors, and the director. I combined all of that text into a single tags column for each movie.

Next, I used CountVectorizer from scikit-learn to turn those tags into vectors and calculated cosine similarity between every movie. That gave me a quick way to look up any movie and sort the top 5 closest matches.

Once the model worked, I moved over to PyCharm to build the Streamlit interface. I signed up for a TMDB API key so the app would not just print movie titles, but actually pull real movie posters and backdrop images. On top of the recommender, I added a simple CinePulse header and a hero banner that cycles through four movie backdrops from the database every few seconds.

## Problems I Ran Into and How I Fixed Them

Pandas pickle mismatch
When I exported my cleaned DataFrame from Jupyter as movies.pkl, it crashed in PyCharm because Jupyter was using pandas 3 and my local environment had pandas 2. Instead of pickling the DataFrame object, I converted it into a regular Python dictionary first, saved it as movies_dict.pkl, and rebuilt the DataFrame inside app.py.

Similarity file too big for GitHub
My similarity.pkl file came out to around 185 MB, and GitHub blocks files over 100 MB. Rather than fighting with Git LFS or paying for extra storage, I removed similarity.pkl from the repo and let app.py calculate the cosine similarity matrix once on startup using scikit-learn with st.cache_resource and float32. That dropped the whole repo under 5 MB.

TMDB 401 error
At first my API calls kept failing with a 401 Invalid API key error because I was testing the account endpoint with the wrong header format. Switching to the /3/movie/{movie_id} endpoint with my api_key in the URL fixed it right away.

Hosting and dependency headaches
I originally planned to deploy on Heroku, which asked for billing details, and then tried Hugging Face Spaces, where my new free account hit a cpu-basic quota limit. On top of that, running pip freeze locally put Python 3.14 package versions in requirements.txt that would break on cloud servers. I replaced requirements.txt with just the four libraries the app uses and deployed directly from GitHub to Streamlit Community Cloud.

Poster alignment
Longer movie titles wrapped onto two lines and pushed some posters lower than others. Setting a fixed minimum height on the title container lined up all five posters evenly.

## Running It Locally

git clone https://github.com/amarah0051/movie-recommender-system.git
cd movie-recommender-system
pip install -r requirements.txt
streamlit run app.py
