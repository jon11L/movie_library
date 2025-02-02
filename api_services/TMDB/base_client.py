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

    def get_access(self):

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