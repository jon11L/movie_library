from .base_client import TMDBClient


import requests

def get_movie_details(tmdb_id):
    ''' Return a single movie!
    Get movie data details from the TMDB API using the movie_id parameter.
    Also adding the credits data using append_to_Response
    '''
    tmdb_client = TMDBClient()

    url = f"{tmdb_client.BASE_URL}movie/{tmdb_id}?append_to_response=credits"

    headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {tmdb_client.ACCESS_TOKEN}"
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except Exception as e:
        print(f"Error getting movie details: {e}")
        return None