import requests
import pandas as pd
import streamlit as st
import time


links_dataset = r"C:\Users\Sairaj\OneDrive\Desktop\Movie Recommendation Project\Datasets\links.csv"


try:
    links = pd.read_csv(links_dataset)
except Exception:
    links = pd.DataFrame(columns = ["movieId", "tmdbId"])


tmdb_api = "........."  
tmdb_images = "https://image.tmdb.org/t/p/w500"


@st.cache_data(ttl = 86400, show_spinner = False)
def tmdb_fetch(tmdb_id: int) -> dict:
    fallback_img = "https://dummyimage.com/300x450/20202f/e4e4f0?text=No+Poster"
    
    try:
        time.sleep(0.2) 
        
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={tmdb_api}&append_to_response=credits"
        response = requests.get(url, timeout = 5)
        
        if response.status_code != 200:
            return {"poster_url": "https://dummyimage.com/300x450/20202f/e4e4f0?text=Rate+Limited"}
            
        data = response.json()
        
        crew = data.get("credits", {}).get("crew", [])
        cast = data.get("credits", {}).get("cast", [])
        director = next((p["name"] for p in crew if p.get("job") == "Director"), "Unknown")
        poster = data.get("poster_path")
        
        return {
            "title": data.get("title", "Unknown"),
            "overview": data.get("overview", "No description available."),
            "release_date": data.get("release_date", ""),
            "runtime": data.get("runtime", 0),
            "poster_url": f"{tmdb_images}{poster}" if poster else fallback_img,
            "director": director,
            "top_cast": [a["name"] for a in cast[:3]],
            "vote_average": data.get("vote_average", 0.0),
        }
    except Exception:
        return {"poster_url": "https://dummyimage.com/300x450/20202f/e4e4f0?text=Error"}


def get_full_movie_data(movielens_id):
    try:
        search_id = int(movielens_id)
        row = links[links['movieId'] == search_id]
        
        if row.empty:
            return {"title": "Not Found", "poster_url": "https://dummyimage.com/300x450/20202f/e4e4f0?text=Not+in+DB"}
            
        tmdb_id = int(row['tmdbId'].values[0])
        return tmdb_fetch(tmdb_id)
        
    except Exception:
        return {"title": "Error", "poster_url": "https://dummyimage.com/300x450/20202f/e4e4f0?text=Translation+Error"}