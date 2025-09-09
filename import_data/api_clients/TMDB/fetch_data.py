from .base_client import TMDBClient
import time
import random
import requests

def get_api_data(*args, **kwargs): 
    """
    Pass on kwargs argument to generate_url()\n
    Build the Headers connection for TMDB api\n
    send a request, check the success of the response\n
    3 Retry attempts if the response fails\n

    Fetch paginated list of popular movies
    With the following variable arguments:
    - endpoint -> for filter selection (eg. popular, upcoming)
    - page -> the page to hit the api
    - t_type -> the model type that is targeted (eg. Movie, Serie, Season)

    """
    MAX_RETRIES = 3
    retry = 0
    
    tmdb_client = TMDBClient()

    # page = kwargs.get("page")
    # endpoint = kwargs.get("endpoint")
    # t_type = kwargs.get("t_type")
    # update = kwargs.get("update")

    # Retry logic
    while retry < MAX_RETRIES:
        # pass the same data as in get_api_data(*args, **kwargs) 
        url = tmdb_client.generate_url(*args, **kwargs)
        headers = tmdb_client.HEADERS

        try:
            response = requests.get(url, headers=headers)
            print(f"API call made: {url}")  # debug print
            if response.status_code == 200:
                # Successful response. Returns the json data and stops here.
                print(
                    f"Response received. success: {response.status_code}\n"
                    "---------"
                    )
                return response.json()
            elif response.status_code == 34:
                retry += 1
                print(
                    'Reason: The resource you requested could not be found.\n'
                    f'response: "{response}", status: "{response.status_code}"\n'
                    f'Retrying... Attempt {retry}/{MAX_RETRIES} in {retry*3}seconds\n'
                    )
                time.sleep(retry*3)
            else:
                retry += 1
                # if Url response fails, it try agains and to catch exception why it failed 
                print(
                    f"Response api call failed.\n"
                    f"Response:'{response}', status:{response.status_code}\n"
                    f"Retrying... Attempt {retry}/{MAX_RETRIES} in {retry*3}seconds\n"
                )
                time.sleep(retry*3)

        except requests.exceptions.RequestException as e:
            retry += 1
            print(
                f"Request exception Error getting '{kwargs.get('t_type')}' with url: {url}\n"
                f"Error Reason: {e}\n"
                f"trying again sane endpoint: in {retry*3}\n"
                "--------------\n"
                )
            time.sleep(retry*3)

        except Exception as e:
            retry += 1
            print(
                f"Failed, An error occurred while fetching the '{kwargs.get('t_type')}' of movies with url: {url}\n"
                f"Error Reason: {e}\n"
                f"Retrying... Attempt {retry}/{MAX_RETRIES}\n"
                f"trying again endpoint:{kwargs.get("endpoint")}-page{kwargs.get("page")} in {retry*3}seconds\n"
                "---------------\n"
                )
            time.sleep(retry*3)
        
    if retry == MAX_RETRIES:
        print(
            "Max retries reached. Call failed.\n"
            f"Could not fetch successful result for '{kwargs.get('t_type')}' with url: \n{url}."
            )
        return None # exit this query call if max retries reached

    print("--------Max retries reached. Exiting.----(Check for possible error with URL)")