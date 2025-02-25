from .base_client import TMDBClient

import requests

def get_serie_details(tmdb_id: int):
    ''' Finds and Return the datas for single movie.
    Get movie data details from the TMDB API using the 'movie_id' parameter.
    Also, the  extra credits datas are being retrieved using '?append_to_response=credits'
    in adding it at the end of the url parameter.
    '''
    tmdb_client = TMDBClient() # instance of TMDB to create the authorization and Token retrieval.

    # append credits to the movie to get those extra datas about casting and videos for the youtube trailer id.
    url = f"{tmdb_client.BASE_URL}tv/{tmdb_id}?append_to_response=videos,credits,external_ids"
    headers = tmdb_client.HEADERS # send the headers with bearer Token

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print("response api ok!")
            return response.json()
        else:
            return None

    except Exception as e:
        print(f"Error getting serie details: {e}")
        return None
    

# episodes data can be retrieved with season directly, it sufficent 
def get_season_details(tmdb_id: int, season_number: int):
    ''' Finds and Return the datas for single movie.
    Get movie data details from the TMDB API using the 'movie_id' parameter.
    Also, the  extra credits datas are being retrieved using '?append_to_response=credits'
    in adding it at the end of the url parameter.
    '''
    tmdb_client = TMDBClient() # instance of TMDB to create the authorization and Token retrieval.

    # append credits to the movie to get those extra datas about casting and videos for the youtube trailer id.
    url = f"{tmdb_client.BASE_URL}tv/{tmdb_id}/season/{season_number}?append_to_response=videos,credits"
    headers = tmdb_client.HEADERS # send the headers with bearer Token

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print("response api ok!")
            return response.json()
        else:
            return None

    except Exception as e:
        print(f"Error getting season details: {e}")
        return None




def fetch_series(page, endpoint):
    """
    Fetch paginated list of popular series
    """
    tmdb_client = TMDBClient()

    # url = f"{tmdb_client.BASE_URL}/tv/popular?page={page}"
    url = f"{tmdb_client.BASE_URL}/tv/{endpoint}?page={page}"
    headers = tmdb_client.HEADERS
    print(f"Url set up: {url}\n")  # debug print
    try:

        response = requests.get(url, headers=headers)
        print(f"API call made.\n")  # debug print
        if response.status_code == 200:
            print(f"Response received. success\n")  # debug print
            return response.json()
        else:
            print(f"Error: {response.status_code}\n")  # debug print
            return None
    
    except Exception as e:
        print(f"An error occurred while fetching the list of popular movies: {e}")
        return None
