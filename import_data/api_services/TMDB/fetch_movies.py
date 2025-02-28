from .base_client import TMDBClient

import requests


def get_movie_data(tmdb_id):
    ''' Finds and Return the datas for single movie.
    Get movie data details from the TMDB API using the 'movie_id' parameter.
    Also, the  extra credits datas are being retrieved using '?append_to_response=credits'
    in adding it at the end of the url parameter.
    '''
    tmdb_client = TMDBClient() # instance of TMDB to create the authorization and Token retrieval.

    # append credits to the movie to get those extra datas about casting and videos for the youtube trailer id.
    url = f"{tmdb_client.BASE_URL}movie/{tmdb_id}?append_to_response=videos,credits"
    headers = tmdb_client.HEADERS # send the headers with bearer Token

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print("response api ok!")
            return response.json()
        else:
            return None

    except Exception as e:
        print(f"Error getting movie details: {e}")
        return None


def fetch_movies(page, endpoint):
    """
    Fetch paginated list of popular movies
    """
    tmdb_client = TMDBClient()

    # url = f"{tmdb_client.BASE_URL}/movie/popular?page={page}"
    url = f"{tmdb_client.BASE_URL}/movie/{endpoint}?page={page}"
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



# get url endpoint for top rated and upcoming 

# https://api.themoviedb.org/3/movie/top_rated
# https://api.themoviedb.org/3/movie/now_playing    # currently in theater



# series url:
# https://api.themoviedb.org/3/tv/top_rated
# https://api.themoviedb.org/3/tv/on_the_air      # -- series that air in next 7days

# def search_movies_by_title(title: str):
#     """
#     Search for movies by title, if the movie is not found in the database,
#     fetch the details from the TMDB API and add it to the database.
#     """

#     # TODO: call for a search query
#     # get the id reference
#     # get the details by the id
#     # add it to the database

#     # if not already stored in the database look for it with TMDB api 
#     tmdb_client = TMDBClient()

#     url = f"{tmdb_client.BASE_URL}/search/movie?query={title}"
#     headers = tmdb_client.HEADERS
#     print(f"Url set up.\n")  # debug print
#     try:
#         response = requests.get(url, headers=headers)

# # use: ["results"] ["id"] 

#     except Exception as e:
#         print(f"An error occurred while fetching the list of popular movies: {e}")
#         return None
