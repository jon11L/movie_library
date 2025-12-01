import logging
import datetime
import time
import random
import os

from django.core.management.base import BaseCommand

from movie.models import Movie
from import_data.api_clients.TMDB.fetch_data import get_api_data
from import_data.services.create_movies import save_or_update_movie
from import_data.tools.media_update_check import check_update_since
from import_data.tools.build_endpoint_import import get_page


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
        2. On specific days,fetch from top pages eg. 1 or 2 to grab latest content.
        3.  call: loop through each movie from the TMDB Id provided to query their data 
        4. Check if the movies already exists otherwise saves it in the database.
        5. Log results for created, updated and skipped.
        """
        MAX_RETRIES = 3
        retry = 0  # Track the number of retries in case of failure
        start_time = time.time()

        # to keep track of the import,
        # passed & returned in process_batch_movies(). Then logged at the end.
        imported = {
            'count' : 0,
            'created' : 0,
            'skipped' : 0,
            'updated' : 0,
            'runtime': 0.0
        }

        endpoints = ("popular", "top_rated", "now_playing", "upcoming", "discover")

        while retry < MAX_RETRIES:
            endpoint = random.choice(endpoints)

            # select a date depending on the endpoint and if a date for top pages.
            page = get_page(endpoint)


            self.stdout.write(
                f"Fetching movies from '{endpoint}' list, With page n: {page}\n"
            )

            try:
                list_movies = get_api_data(
                    page=page,
                    endpoint=endpoint,
                    t_type = 'movie_list'
                    # update=False
                    )

                if not list_movies or len(list_movies['results']) <= 5:
                    raise ValueError(
                        "No movies list found or too few results."
                    )

                self.stdout.write(
                    "Processing the list of movies.\n"
                    f"\n" + "=" * 50 + "\n\n"
                )

                batch = self.process_movie_list(list_movies, imported)
                imported = batch

                break # break the while Loop if page is reached

            except ValueError as value_e:
                retry += 1
                self.stdout.write(
                    f"(ValueError Exception) No movies list found or too few results."
                    f" page={page}, endpoint={endpoint}."
                    f"\nError message: '{value_e}'"
                    )
                self.stdout.write(self.style.WARNING(
                    f"Retrying... Attempt {retry}/{MAX_RETRIES} in {retry*4}seconds"
                    ))
                time.sleep(retry*4)  # wait before retrying

            except Exception as e:
                retry += 1
                self.stdout.write(
                    f"(Exception) No movies list found or too few results."
                    f"page={page}, endpoint={endpoint}."
                    f"\n(Exception) Error message: '{e}'"
                    )
                self.stdout.write(self.style.WARNING(
                    f"Retrying... Attempt {retry}/{MAX_RETRIES} in {retry*4}seconds"
                    ))
                time.sleep(retry*4)

        # If all retries failed, exit early
        if retry == MAX_RETRIES:
            self.stdout.write(
                self.style.ERROR(
                    "Max retries reached. Could not fetch updated movies."
                    "-- Task ending.\n"
                )
            )
            return 

        end_time = time.time()
        elapsed_time = end_time - start_time
        imported['runtime'] = round(elapsed_time, 2)
        # final summary, logs result into file:
        self.stdout.write(
            self.style.SUCCESS(
                f"\nImport batch of movies completed: "
                f"\n'{imported['count']}' movies processed\n"
            )
        )

        log_import = (
            f"SUMMARY: Movies (import)"
            f" -- {imported['created']} Created"
            f" -- {imported['updated']} updated"
            f" -- {imported['skipped']}  Skipped/Failed"
            f" -- runtime: {imported['runtime']} seconds"
        )

        # saved log in file report import.
        logger.info(log_import)
        self.stdout.write(self.style.SUCCESS(log_import))

    def process_movie_list(self, list_movies, imported: dict):
        '''
        Process a batch of movies from TMDB api response.\n
        return the count of imported/saved movies and skipped
        - count, created, updated, skipped
        '''
        for movie in list_movies['results']:
            # time.sleep(1)
            imported['count'] += 1
            tmdb_id = movie['id']
            title = movie['title']
            self.stdout.write(
                f"\n" + "=" * 50 + "\n\n"
                f"passing movie {imported['count']}\n"
                f"Importing Movie title: {title} (ID: {tmdb_id})\n"
                )

            if movie['adult']:
                self.stdout.write(
                    self.style.WARNING(
                        f"Movie {tmdb_id} is marked as adult content. Skipping..."
                    )
                )
                imported["skipped"] += 1
                continue

            # Check if media does not exists
            if not Movie.objects.filter(tmdb_id=tmdb_id).exists():
                time.sleep(0.5)

                try:
                    # grab and save Datas from api query in a new single movie's instance
                    new_movie, created = save_or_update_movie(tmdb_id)
                    if new_movie:
                        imported['created'] += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"Imported movie: **{new_movie}** \n")
                        )
                    else:
                        imported["skipped"] += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f"Cancel import of movie ID: {tmdb_id}. "
                                f"No sufficient data returned."
                            )
                        )

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing {movie['title']}: {e}"))
                    imported['skipped'] += 1
                    continue

            else:
                # if the movie already exist, check when it was released and updated
                # and if it necessit a new update
                # Reduces unnecessary api calls if movie was recently updated in DB
                exist_movie = Movie.objects.get(tmdb_id=tmdb_id)
                need_update, desired_updt_days = check_update_since(exist_movie, "Movie")

                if need_update == False:
                    self.stdout.write(self.style.WARNING(
                        f"{movie['title']} already exists in DB"
                        f"and was updated less than {desired_updt_days} days ago. "
                        " -- Skipping....\n"
                        f"\n" + "=" * 50 + "\n\n"
                        ))
                    imported['skipped'] += 1
                    continue

                else:
                    # proceed to update the serie's object data
                    time.sleep(0.5)

                    self.stdout.write(
                        self.style.WARNING(
                            f"'{movie['title']}' already exists in DB. "
                            f"-- Min-delay update of {desired_updt_days} days passed. "
                            f"-- Updating!\n"
                        )
                    )
                    new_movie, is_created = save_or_update_movie(tmdb_id)

                    if new_movie and not is_created:
                        imported['updated'] += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Updated  movie: **{new_movie}**"
                                f"\n" + "=" * 50 + "\n\n"
                            )
                        )

                    elif not new_movie:
                        imported['skipped'] += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"**Cancel to save in DB. "
                                f"No movie or no sufficient data. Probably deleted. **"
                                f"\n" + "=" * 50 + "\n\n"
                            )
                        )

        return imported


#   # Determine appropriate HTTP status code
#   status_code = {
#       'added': 201,
#       'exists': 200,
#       'error': 404
