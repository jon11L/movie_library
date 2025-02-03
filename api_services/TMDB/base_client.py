import os
from dotenv import load_dotenv
import requests
import datetime

load_dotenv()


class TMDBClient:
    
    BASE_URL = "https://api.themoviedb.org/3/"

    def __init__(self):
        '''
        Call the TMDb API to get the read access to their apis.
        '''
        self.ACCESS_TOKEN = os.getenv('TMDB_READ_ACCESS_KEY')
        if not self.ACCESS_TOKEN:
            raise ValueError("TMDB API key not found")



    def get_authorization(self):
        ''' this function check the authorization of the user , validtiy of the api key '''
        suffixe_url = "authentication"

        try:
            url = self.BASE_URL + suffixe_url

            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {self.ACCESS_TOKEN}"
                }

            response = requests.get(url, headers=headers)
            time = datetime.datetime.now() # to add some logging purposes

            print(response.text, "\n") # log the response
            print(f"API call was made on the {time}.   \n{response}") # log the time taken to call the API

            return response.json()

        except Exception as e:
            print(f"An error occurred while calling the TMDb API: {e}")
            return None
        



    def get_movie_details(self, movie_id):
        ''' get movie details from the TMDB API using the movie_id parameter.'''

        url = f"{self.BASE_URL}movie/{movie_id}"

        headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {self.ACCESS_TOKEN}"
        }

        try:

            response = requests.get(url, headers=headers)
            # response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={access_token}&language=en-US')

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Error getting movie details: {e}")
            return None