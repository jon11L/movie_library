# import requests
import logging
import datetime
import time
import random
import os

from django.core.management.base import BaseCommand

from movie.models import Movie
from import_data.api_clients.TMDB.fetch_data import get_api_data
from import_data.services.create_movies import save_or_update_movie


# Configure Logging
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure the directory exists
LOG_FILE = os.path.join(LOG_DIR, "tmdb_import.log")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Create a logger instance for this module
logger = logging.getLogger(__name__)

# Create a FileHandler and attach it to the logger
file_handler = logging.FileHandler(LOG_FILE, mode="a")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

# Prevent duplicate logs (avoid propagation to the root logger)
logger.propagate = False


class Command(BaseCommand):
    help = 'Import movies from TMDB'

    def handle(self, *args, **kwargs):
        self.import_movies()

    def import_movies(self):
        """
        Bulk import strategy:
        1. Fetch a list of movies varying upon on the selected endpoint
        2. On specific days, force fetch from page 1 & 2 to grab latest content.
        3.  call: loop through each movie to query their data 
        4. Check if the movies already exists otherwise saves it in the database.
        5. Log result and differentiate between imported and skipped.
        """
        MAX_RETRIES = 3
        FETCH_PAGE = 5 # the amount of pages we will check to get movies imported

        # to keep track of the import,
        # passed & returned in process_batch_movies(). Then logged at the end.
        imported = {
            'count' : 0,
            'created' : 0,
            'skipped' : 0
        }

        endpoints = ("popular", "top_rated", "now_playing", "upcoming", "discover")

        def select_endpoint(endpoint):
            '''Takes a list of endpoints and return a random one'''
            return random.choice(endpoint)

        # adjust the number of pages based on the selected endpoint
        def get_max_page(endpoint):
            ''' Return the max amount of pages available in the TMDB api 
            according to the endpoint selected.
            '''
            if endpoint == "now_playing":
                return 200
            elif  endpoint == "upcoming":
                return 50
            else:
                return 500

        # ------TRIAL/ once every 5 days add page 1&2 to get latest content ------
        today = datetime.date.today()
        if today.day in [1, 5, 10, 20, 25]:
            new_pages = (1, 2)

            endpoint = select_endpoint(endpoints)
            for page in new_pages:
                try:
                    self.stdout.write(
                        f"Special date new pages"
                        f"Fetching movies from '{endpoint}' list, With Newer pages n: {page}\n"
                        ) # debug print
                    
                    list_movies = get_api_data(
                        page=page,
                        endpoint=endpoint,
                        t_type = 'movie_list'
                        # update=False
                        )

                    if not list_movies or len(list_movies['results']) <= 5:
                            raise ValueError("No movies list found or too few results to loop over.")

                    batch = self.process_movies_batch(list_movies, imported)
                    imported = batch

                except ValueError as value_e:
                    self.stdout.write(
                        f"(Exception value) No movies list found or too few results. page={page}, endpoint={endpoint}."
                        f"Error message: '{value_e}'"
                        )
                    time.sleep(4)  # wait before retrying
                    continue

                except Exception as e:
                    self.stdout.write(
                        f"(Exception) No movies list found or too few results. page={page}, endpoint={endpoint}."
                        f"(Exception) Error message: '{e}'"
                        )
                    time.sleep(4)
                    continue

            # Loop over pages
        for i in range(FETCH_PAGE):

            retry = 0  # Track the number of retries in case of failure
            while retry < MAX_RETRIES:
                try:
                    # select a new endpoint+page for each loop page fetch / also if one fails.
                    endpoint = select_endpoint(endpoints)
                    max_pages = get_max_page(endpoint)
                    page = random.randint(1, max_pages) # change the page to send in get_movie_list():
                    self.stdout.write(
                        f"----------------------------\n"
                        f"Fetching movies from '{endpoint}' list, With page n: {page}\n"
                        ) # debug print

                    list_movies = get_api_data(
                        page=page,
                        endpoint=endpoint,
                        t_type='movie_list'
                        # update=False
                        )

                    if not list_movies or (list_movies['results'] and len(list_movies['results']) <= 5):
                        raise ValueError(f"No movies list found or too few results to loop over.")

                    break # break the while Loop if page is reached

                except ValueError as value_e:
                    retry += 1
                    self.stdout.write(
                        f"(Exception) No movies list found or too few results. page={page}, endpoint={endpoint}."
                        f"Error: {value_e}"
                        f"Retrying... Attempt {retry}/{MAX_RETRIES} in {retry*4}seconds"
                        )
                    time.sleep(retry*4)  # wait before retrying

                except Exception as e:
                    retry += 1
                    self.stdout.write(
                        f"(Exception) Error getting list of imported movies: {e}"
                        f"Retrying... Attempt {retry}/{MAX_RETRIES} in {retry*4}seconds"
                        )
                    time.sleep(retry*4)

            # If all retries failed, exit early
            if retry == MAX_RETRIES:
                self.stdout.write(self.style.ERROR("Max retries reached. Could not fetch updated movies. -- Task ending.\n"))
                continue # Skip this page and go to the next.

            # --- Fetch and process each movie from the selected endpoint ----
            self.stdout.write("Processing the list of movies and pass the Ids to get the datas.\n")

            # pass the movie list process batch into it's own function
            batch = self.process_movies_batch(list_movies, imported)
            imported = batch
            time.sleep(5) # give some time between fetching a new page list of movies.

        # final summary, logs result into file:
        self.stdout.write(self.style.SUCCESS(f"\nImport batch of movies completed: '{imported['count']}' movies processed\n"))
        logger.info(f"SUMMARY: Movies (import) -- {imported['created']} Created. -- 0 Updated. -- {imported['skipped']}  Skipped/Failed.")
        self.stdout.write(f"SUMMARY: Movies (import) -- {imported['created']} Created. -- 0 Updated. -- {imported['skipped']}  Skipped/Failed.")
        self.stdout.write(f"\n--------------\n\n") # debug print


    def process_movies_batch(self, list_movies, imported: dict):
        '''
        Process a batch of movies from TMDB api response
        return the count of imported/saved movies and skipped

        - count, created, skipped
        '''
        for movie in list_movies['results']:
            time.sleep(1)  
            imported['count'] += 1
            movie_id = movie['id']
            movie_title = movie['title']
            self.stdout.write(
                f"passing movie {imported['count']}\n"
                f"Importing Movie title: {movie_title} (ID: {movie_id})\n"
                )

            if movie['adult']:
                self.stdout.write(self.style.WARNING(f"Movie {movie_id} is marked as adult content. Skipping..."))
                imported['skipped'] += 1
                continue

            # Check if movie exists
            time.sleep(0.5)  # Wait for 1 second before checking the database
            if not Movie.objects.filter(tmdb_id=movie_id).exists():
                time.sleep(1)  
                try:
                    # uncomment below when Feature is correct
                    save_or_update_movie(movie_id) # grab and save Datas from api into a new single movie's instance 
                    imported['created'] += 1
                    # self.stdout.write(self.style.SUCCESS(f"Imported movie: **{new_movie['title']}** \n"))  # not sure it is imported if already exist
                    # logger.info(f"Imported: {movie_title} (ID: {movie_id})")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing {movie['title']}: {e}"))
                    imported['skipped'] += 1
                    # logger.error(f"Error importing {movie_id}: {e}")
                    continue
            else:
                self.stdout.write(self.style.WARNING(f"'{movie['title']}' already exists in DB."))
                print("-----------")
                imported['skipped'] += 1

        return imported


#   # Determine appropriate HTTP status code
#   status_code = {
#       'added': 201,
#       'exists': 200,
#       'error': 404
