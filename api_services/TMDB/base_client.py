import os
from dotenv import load_dotenv
import requests
import datetime

load_dotenv()


class TMDBClient:
    
    BASE_URL = "https://api.themoviedb.org/3/"

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
            print(f"API call was made on the {time}.   \n{response}") # log the time taken to call the API

            return response.json()

        except Exception as e:
            print(f"An error occurred while calling the TMDb API: {e}")
            return None



    # def fetch_popular_movies(self, page=1):
    #     """
    #     Fetch paginated list of popular movies
    #     """
    #     url = f"{self.BASE_URL}/movie/popular?page={page}"

    #     response = requests.get(url, params={'api_key': self.ACCESS_TOKEN})
    #     return response.json()

