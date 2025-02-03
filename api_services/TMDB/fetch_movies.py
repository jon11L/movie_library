from .base_client import TMDBClient


import requests

def get_movie_details(movie_id):
    ''' get movie details from the TMDB API using the movie_id parameter.'''
    try:

        # Get an access token to use the API
        access_token = TMDBClient()

        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={access_token}&language=en-US')

        if response.status_code == 200:
            return response.json()
        else:
            return None
        
    except Exception as e:
        print(f"Error getting movie details: {e}")
        return None