from .base_client import TMDBClient
import time
import requests

def get_movie_data(tmdb_id: int):
    ''' Finds and Return the datas for single movie.
    Get movie data details from the TMDB API using the 'movie_id' parameter.
    Also, the  extra credits datas are being retrieved using '?append_to_response=credits'
    in adding it at the end of the url parameter.
    '''
    MAX_RETRIES = 3
    attempt = 0
    
    tmdb_client = TMDBClient() # instance of TMDB to create the authorization and Token retrieval.

    # append credits to the movie to get those extra datas about casting and videos for the youtube trailer id.
    url = f"{tmdb_client.BASE_URL}/movie/{tmdb_id}?append_to_response=videos,credits"
    headers = tmdb_client.HEADERS # send the headers with bearer Token
    print(f"Url called: {url}")  # debug print

    while attempt < MAX_RETRIES:
        try:
            response = requests.get(url, headers=headers)
        
            if response.status_code == 200:
                print(f"response api (movie) ok! Status: {response.status_code}")
                # print("---------")
                return response.json()
            
            # if Url response fails, it try agains and to catch exception why it failed 
            print(f"Response api call failed. Status:{response.status_code}")

        except Exception as e:
            print(f"Fail, an error occured getting the movie data. Reason: {e}")
            print("---------")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request exception Error getting serie details: {e}")
            return None
        
        attempt += 1
        print(f"Retrying... Attempt {attempt}/{MAX_RETRIES}")
        time.sleep(attempt*3)



def get_movie_list(page: int, endpoint: str):
    """
    Fetch paginated list of popular movies
    """
    MAX_RETRIES = 3
    attempt = 0
    
    tmdb_client = TMDBClient()

    # add date at the end of url for the updated movies call.
    #  Date should only be for the update not for other endpoints.. need to work with that constraint
    url = f"{tmdb_client.BASE_URL}/movie/{endpoint}?page={page}" # &start_date=2025-03-22&end_date=2025-03-23
    headers = tmdb_client.HEADERS

    # Retry logic
    while attempt < MAX_RETRIES:
        print(f"Url called: {url}\n")  # debug print
        try:
            response = requests.get(url, headers=headers)
            print(f"API call made.\n")  # debug print
            if response.status_code == 200:
                print(f"Response received. success: {response.status_code}\n")  # debug print
                print("---------")
                return response.json()
            
            # if Url response fails, it try agains and to catch exception why it failed 
            print(f"Response api call failed. Status:{response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Request exception Error getting movie list: {e}")
            return None
        except Exception as e:
            print(f"Failed, An error occurred while fetching the list of popular movies. Reason: {e}")
            print("---------")
            return None
    
        attempt += 1
        print(f"Retrying... Attempt {attempt}/{MAX_RETRIES}")
        time.sleep(3)
    print("--------Max retries reached. Exiting.----(Check for possible error with URL)")
    return None
