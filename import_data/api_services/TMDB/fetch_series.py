from .base_client import TMDBClient

import requests
import time

def get_series_list(page, endpoint):
    """
    Fetch paginated list of popular series
    """
    tmdb_client = TMDBClient()
    url = f"{tmdb_client.BASE_URL}/tv/{endpoint}?page={page}" # &start_date=2025-03-22&end_date=2025-03-23
    headers = tmdb_client.HEADERS
    print(f"Url called: {url}\n")  # debug print

    try:
        response = requests.get(url, headers=headers)
        print(f"API call made.\n")  # debug print
        if response.status_code == 200:
            print(f"Response received. success\n")  # debug print
            return response.json()
        else:
            print(f"Error: {response}\n")  # debug print
            # print(f"Error: {response.status_code}\n")  # debug print
            return None
    
    except Exception as e:
        print(f"An error occurred while fetching the list of popular movies: {e}")
        return None


def get_serie_data(tmdb_id: int):
    ''' Finds and Return the datas for single movie.
    Get movie data details from the TMDB API using the 'movie_id' parameter.
    Also, the  extra credits datas are being retrieved using '?append_to_response=credits'
    in adding it at the end of the url parameter.
    '''

    MAX_RETRIES = 3
    attempt = 0
    
    tmdb_client = TMDBClient() # instance of TMDB to create the authorization and Token retrieval.
    # append credits to the movie to get those extra datas about casting and videos for the youtube trailer id.
    url = f"{tmdb_client.BASE_URL}/tv/{tmdb_id}?append_to_response=videos,credits,external_ids"
    headers = tmdb_client.HEADERS # send the headers with bearer Token

    # Retry logic
    while attempt < MAX_RETRIES:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                print(f"response api (serie) ok! -- Status: {response.status_code}")
                return response.json()
            
            # if Url response fails, it try agains and to catch exception why it failed 
            print(f"Response api call failed. Status:{response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Request exception Error getting serie details: {e}")

        except Exception as e:
            print(f"(Exception) Error getting serie details: {e}")
            return None
        
        attempt += 1
        print(f"Retrying... Attempt {attempt}/{MAX_RETRIES}")
        time.sleep(attempt*3)  # wait for 1 second before retrying

    print("--------Max retries reached. Exiting.----(Check for possible error with URL)")
    return None


# episodes data can be retrieved with season directly, it sufficent 
def get_season_data(tmdb_id: int, season_number: int):
    ''' Finds and Return the datas for the seasons of a serie.
    Get serie data details from the TMDB API using the 'serie.tmdb_id' parameter.
    - The  extra credits datas are being retrieved using '?append_to_response=credits'
    at the end of the url parameter.
    '''

    MAX_RETRIES = 3
    attempt = 0
    
    tmdb_client = TMDBClient() # instance of TMDB to create the authorization and Token retrieval.
    url = f"{tmdb_client.BASE_URL}/tv/{tmdb_id}/season/{season_number}?append_to_response=videos,credits"
    headers = tmdb_client.HEADERS # send the headers with bearer Token
    print(f"Url called: {url}\n")  # debug print

    # Retry logic
    while attempt < MAX_RETRIES:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                print(f"Response api call (season) success. Status:{response.status_code}")
                return response.json()
            
            # if Url response fails, it try agains and to catch exception why it failed 
            print(f"Response api call failed. Status:{response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request exception: {e}")

        except Exception as e:
            print(f"(Exception) Error getting season details: {e}")
            return None
        
        attempt += 1
        print(f"Retrying... Attempt {attempt}/{MAX_RETRIES}")
        time.sleep(attempt*3)  # wait for 1 second before retrying

    print("--------Max retries reached. Exiting.----(Check for possible error with URL)")
    return None
