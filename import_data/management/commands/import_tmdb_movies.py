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
            'skipped' : 0,
            'updated' : 0,
            'runtime': 0
        }
        start_time = time.time()

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
            new_pages = random.sample(range(1, 4), 2)

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
                        f"(Exception value) No movies list found or too few results."
                        f" page={page}, endpoint={endpoint}."
                        f"Error message: '{value_e}'"
                        )
                    time.sleep(4)  # wait before retrying
                    continue

                except Exception as e:
                    self.stdout.write(
                        f"(Exception) No movies list found or too few results."
                        f"page={page}, endpoint={endpoint}."
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
                        f"\n" + "=" * 50 + "\n\n"
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
            print(f"\n" + "=" * 50 + "\n\n")

            # pass the movie list process batch into it's own function
            batch = self.process_movies_batch(list_movies, imported)
            imported = batch
            time.sleep(4) # give some time between fetching a new page list of movies.

        end_time = time.time()
        elapsed_time = end_time - start_time

        # final summary, logs result into file:
        self.stdout.write(
            self.style.SUCCESS(
                f"\nImport batch of movies completed: '{imported['count']}' movies processed\n"
            )
        )
        # saved log.
        logger.info(
            f"SUMMARY: Movies (import)"
            f" -- {imported['created']} Created"
            f" -- {imported['updated']} updated"
            f" -- {imported['skipped']}  Skipped/Failed"
            f" -- runtime: {elapsed_time:.2f} seconds"
        )

        self.stdout.write(self.style.SUCCESS(f"time: {elapsed_time:.2f} seconds."))
        self.stdout.write(
            self.style.SUCCESS(
                f"SUMMARY: Movies (import) -- {imported['created']} Created. -- {imported['updated']} Updated. -- {imported['skipped']} Skipped/Failed."
            )
        )
        self.stdout.write(f"\n" + "=" * 50 + "\n\n")  # debug print


    def process_movies_batch(self, list_movies, imported: dict):
        '''
        Process a batch of movies from TMDB api response
        return the count of imported/saved movies and skipped

        - count, created, skipped
        '''

        for movie in list_movies['results']:
            time.sleep(1)  
            imported['count'] += 1
            tmdb_id = movie['id']
            title = movie['title']
            self.stdout.write(
                f"\n" + "=" * 50 + "\n\n"
                f"passing movie {imported['count']}\n"
                f"Importing Movie title: {title} (ID: {tmdb_id})\n"
                )

            if movie['adult']:
                self.stdout.write(self.style.WARNING(f"Movie {tmdb_id} is marked as adult content. Skipping..."))
                imported['skipped'] += 1
                continue

            # Check if movie exists
            if not Movie.objects.filter(tmdb_id=tmdb_id).exists():
                time.sleep(1)
                try:
                    # uncomment below when Feature is correct
                    new_movie, created = save_or_update_movie(tmdb_id) # grab and save Datas from api into a new single movie's instance 
                    if new_movie:
                        imported['created'] += 1
                        self.stdout.write(self.style.SUCCESS(f"Imported movie: **{new_movie}** \n"))  # not sure it is imported if already exist
                    else:
                        self.stdout.write(self.style.ERROR(f"Cancel import of movie ID: {tmdb_id}. No sufficient data returned."))
                        imported['skipped'] += 1
                    # logger.info(f"Imported: {movie_title} (ID: {movie_id})")

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing {movie['title']}: {e}"))
                    imported['skipped'] += 1
                    # logger.error(f"Error importing {movie_id}: {e}")
                    continue

            # else:
            #     self.stdout.write(self.style.WARNING(f"'{movie['title']}' already exists in DB."))
            #     # print("\n" + "=" * 50 + "\n\n")
            #     imported['skipped'] += 1

            # -- New version with time check. in progress...
            else:
                existing_movie = Movie.objects.get(tmdb_id=tmdb_id)
                updated_at = existing_movie.updated_at.date()
                updated_since = datetime.datetime.now(datetime.timezone.utc).date() - updated_at 
                
                print(f"- Movie {tmdb_id} - {title} exists.")
                print(f"- Last updated {updated_since.days} days ago. {updated_at}")
                print(f"- release on: {existing_movie.release_date}")
                
                is_released = False
                is_update_after_release = False
                is_recently_released = False
                # check if release date is in the past
                if existing_movie.release_date:
                    when_release =  datetime.date.today() - existing_movie.release_date
                    if when_release.days < 0:
                        # Movies is not released yet.
                        print(f"- Movie is not released yet... -- In '{when_release.days} days'")

                    else:
                        # Movie is already released.
                        print(f"- Movie already released. -- Since '{when_release.days} days'")
                        is_released = True
                        is_recently_released = True if when_release.days <= 40 else False

                        # check if updated_at is after release date
                        if updated_at >= existing_movie.release_date and updated_at.strftime("%d/%m/%Y") != existing_movie.created_at.date().strftime("%d/%m/%Y"):
                            is_update_after_release = True
                            print(f"- Movie was updated after the release date updt:{updated_at}")  
                        else:
                            print(f"- Movie was updated before the release date or never updated. updt:{updated_at}") 
                            
                desired_updt_days = 15 # gives a minimum of 14 days before updating again
                print(f"is_released, is_recently_released, is_update_after_release")
                print(f"{is_released}, {is_recently_released}, {is_update_after_release}")
                
                # set how long before a movie get updated again depending on certain conditons 
                # eg. when was it released? was it updated after release?
                if is_recently_released and is_update_after_release:
                    # Movie rencently released and updated already
                    desired_updt_days = 7 
                    # print(f"3 conditions reunited, 7 days before update.")

                elif is_recently_released and not is_update_after_release:
                    # movie recently released but not updated since release, need updates
                    desired_updt_days = 1

                # to modify (give low num) or comment this condition if Db structure and import has changed,
                elif is_released and not is_recently_released and is_update_after_release:
                    # movie released since a while and updated already, no need to reupdate often
                    desired_updt_days = 10 
                    
                elif not is_released  and when_release.days <= -100:
                    # movie not releasing soon so more info may be added or wait to get close the release
                    desired_updt_days = 30
                else:
                    pass # probably does not have a release.date /  will remain to the standard update delay


                if updated_since.days <= desired_updt_days:
                # if time_difference.days < 14:
                    self.stdout.write(self.style.WARNING(
                        f"{movie['title']} already exists in DB and was updated less than {desired_updt_days} days ago.\n"
                        "Skipping....\n"
                        f"\n" + "=" * 50 + "\n\n"
                        ))
                    imported['skipped'] += 1
                    continue

                else:
                    # proceed to update the serie data
                    save_or_update_movie(tmdb_id)
                    self.stdout.write(self.style.WARNING(f"'{movie['title']}' already exists in DB, delay update is {desired_updt_days} days."))
                    self.stdout.write(self.style.WARNING(f"Updated!"))
                    # print("\n" + "=" * 50 + "\n\n")
                    imported['updated'] += 1


        return imported


#   # Determine appropriate HTTP status code
#   status_code = {
#       'added': 201,
#       'exists': 200,
#       'error': 404
