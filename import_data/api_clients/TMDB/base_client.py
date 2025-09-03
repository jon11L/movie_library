import os
from dotenv import load_dotenv
import requests
import datetime
import random

load_dotenv()


class TMDBClient:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        '''
        instantiate the ACCESS_TOKEN and HEADERS authorization for the TMDB API
        in order get  access to their apis endpoints.
        '''
        self.ACCESS_TOKEN = os.getenv('TMDB_READ_ACCESS_KEY')
        if not self.ACCESS_TOKEN:
            raise ValueError("TMDB API key not found")
        
        self.HEADERS =  {
                "accept": "application/json",
                "Authorization": f"Bearer {self.ACCESS_TOKEN}"
                }


    def get_authorization(self):
        ''' this function check the authorization of the user , validtiy of the api key '''
        suffixe_url = "authentication"
        try:
            url = self.BASE_URL + suffixe_url
            headers = self.HEADERS

            response = requests.get(url, headers=headers)
            time = datetime.datetime.now() # to add some logging purposes

            print(response.text, "\n") # log the response
            print(f"API call was made on the {time}.\n{response}") # log the time taken to call the API

            return response.json()

        except Exception as e:
            print(f"An error occurred while calling the TMDb API: {e}")
            return None


    def generate_url(self, *args, **kwargs):
        '''
        Allow to receive different keyword argument to build the corresponding url.
        to hit the tmdb api.\n
        Different kwargs: page, endoints, tmdb_id, t_type(target_type eg. movie_list or serie)
        '''
        # this i could create generic function to return the URL for all type)
        page = kwargs.get("page")
        endpoint = kwargs.get("endpoint")
        t_type = kwargs.get("t_type")
        # update = kwargs.get("update")
        print(f"{page} -- {endpoint} --- {t_type} --- {kwargs.get('update')} --{kwargs.get('tmdb_id')}")
        try:
            if t_type == 'movie_list':
                if endpoint == 'discover':
                    sort_by = random.choice(["popularity.desc", "popularity.asc","release_date.desc", "vote_count.desc"])
                    url = f"{self.BASE_URL}/discover/movie?include_adult=false&language=en-US&page={page}&sort_by={sort_by}"
                elif endpoint == 'changes':
                    url = f"{self.BASE_URL}/movie/{endpoint}?language=en-US&page={page}&{kwargs.get('select_date')}"
                else:
                    url = f"{self.BASE_URL}/movie/{endpoint}?language=en-US&page={page}" 

            elif t_type == 'movie_detail':
                    url = f"{self.BASE_URL}/movie/{kwargs.get('tmdb_id')}?append_to_response=videos,credits,images"


            elif t_type == 'tv': # api call for list of series.
                if endpoint == "discover":
                    sort_by = random.choice(["popularity.desc", "popularity.asc","release_date.desc", "vote_count.desc"])
                    url =f"{self.BASE_URL}/discover/tv?include_adult=false&include_null_first_air_dates=false&language=en-US&page={page}&sort_by={sort_by}"
                elif endpoint == 'changes':# updates
                    url = f"{self.BASE_URL}/tv/{endpoint}?language=en-US&page={page}&{kwargs.get('select_date')}" 
                else:
                    url = f"{self.BASE_URL}/tv/{endpoint}?page={page}" 

            elif t_type == 'serie': # serie detail
                url = f"{self.BASE_URL}/tv/{kwargs.get('tmdb_id')}?append_to_response=videos,credits,external_ids,images"
            elif t_type == 'season': # season and episode details
                url = f"{self.BASE_URL}/tv/{kwargs.get('tmdb_id')}/season/{kwargs.get('season_number')}?append_to_response=videos,credits,images"

        except KeyError as e:
            print(f"Missing required argument: {e}\n")
            return None

        except Exception as e:
            print(f"An error occurred while generating the URL: {e}\n")
            return None
        

        print(f"Url: {url}")
        return url