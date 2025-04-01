from .base_client import TMDBClient

import requests

def get_movie_data(tmdb_id: int):
    ''' Finds and Return the datas for single movie.
    Get movie data details from the TMDB API using the 'movie_id' parameter.
    Also, the  extra credits datas are being retrieved using '?append_to_response=credits'
    in adding it at the end of the url parameter.
    '''
    tmdb_client = TMDBClient() # instance of TMDB to create the authorization and Token retrieval.

    # append credits to the movie to get those extra datas about casting and videos for the youtube trailer id.
    url = f"{tmdb_client.BASE_URL}/movie/{tmdb_id}?append_to_response=videos,credits"
    headers = tmdb_client.HEADERS # send the headers with bearer Token
    print(f"Url called: {url}")  # debug print

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print(f"response api ok! Status: {response.status_code}")
            # print("---------")
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print("---------")
            return None

    except Exception as e:
        print(f"Error getting movie details: {e}")
        print("---------")
        return None


def get_movie_list(page: int, endpoint: str):
    """
    Fetch paginated list of popular movies
    """
    tmdb_client = TMDBClient()

    # add date at the end of url for the updated movies call.
    #  Date should only be for the update not for other endpoints.. need to work with that constraint
    url = f"{tmdb_client.BASE_URL}/movie/{endpoint}?page={page}" # &start_date=2025-03-22&end_date=2025-03-23
    headers = tmdb_client.HEADERS

    print(f"Url called: {url}\n")  # debug print
    try:
        response = requests.get(url, headers=headers)
        print(f"API call made.\n")  # debug print
        if response.status_code == 200:
            print(f"Response received. success: {response.status_code}\n")  # debug print
            print("---------")
            return response.json()
        else:
            print(f"Error: {response.status_code}\n")  # debug print
            print("---------")
            return None
    
    except Exception as e:
        print(f"An error occurred while fetching the list of popular movies: {e}")
        print("---------")
        return None
