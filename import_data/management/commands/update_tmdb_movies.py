import requests
import logging
import time
import datetime
import random
import os

from django.core.management.base import BaseCommand



from movie.models import Movie
from import_data.api_services.TMDB.fetch_movies import get_movie_list
from import_data.services import save_or_update_movie

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
    help = 'Import movie and series data from TMDB'

    def handle(self, *args, **kwargs):
        self.get_updated_movies()


    def get_updated_movies(self):
        """
        Bulk import strategy:
        1. Fetch a page of updated movies
        2. Loop through each movie to query their data 
        3. Update the movies 
        """

        endpoint = "changes"
        MAX_RETRIES = 3
        attempt = 0

        created = 0  # Tracks how many movies were created
        updated = 0  # .................... updated
        imported_count = 0  # Tracks how many movies passed through
        skipped_count = 0  # Tracks how many movies passed through


        while attempt < MAX_RETRIES:
            page = str(random.randint(1, 30))  # Randomly select a page
            # calculate date up to two weeks before now for the list of updated movies
            today = datetime.datetime.now()
            start_date = (today - datetime.timedelta(days=random.randint(2, 14)))
            end_date = start_date + datetime.timedelta(days=1)

            start_date = start_date.strftime("%Y-%m-%d")
            end_date = end_date.strftime("%Y-%m-%d")

            # adding date parameters for wider choices of updated movies
            select_date = f"end_date={start_date}&start_date={end_date}" 
            self.stdout.write(select_date)
            page_date = page + select_date # concatenate the date to the page until finding a better solution.
            self.stdout.write(f"-- page_date: {page_date}") # debug print

            try:
                # for page in pages_to_fetch:
                self.stdout.write(f"Fetching movies from '{endpoint}' endpoint, With page: {page}\n") # debug print
                updated_movie_list = get_movie_list(page, endpoint)

                if not updated_movie_list  or "results" not in updated_movie_list:
                    self.stdout.write(f"Error: -- The query could not fetch a list of updated movies, check the url.\nstatus=404") # debug print
                    attempt += 1
                    self.stdout.write(f"Retrying... Attempt {attempt}/{MAX_RETRIES} in {attempt*3}seconds")
                    time.sleep(attempt*3)  # wait for 1 second before retrying
                    continue

                break  # if list is correct break out of the loop and fetch movies individually

            except Exception as e:
                self.stdout.write(f"(Exception) Error getting list of updated movies: {e}")
                attempt += 1
                self.stdout.write(f"Retrying... Attempt {attempt}/{MAX_RETRIES} in {attempt*3}seconds")
                time.sleep(attempt*3)  # wait for 1 second before retrying

        # If all retries failed, exit early
        if attempt == MAX_RETRIES:
            self.stdout.write("Error: -- Max retries reached. Could not fetch updated movies. -- Task ending.\n")
            return

        self.stdout.write("Looping through the list of updated movies and pass the Ids to fetch the datas.\n")
        for tmdb_movie_id in updated_movie_list['results']: # add a random index to go through
            time.sleep(1) 
            imported_count += 1
            if imported_count > 50:
                break # stop the iteration to fetch for updated movies.

            tmdb_id = tmdb_movie_id['id']
            # print(f"movie adult: '{adult}'.") # debug print
            self.stdout.write(f"Processing movie ({imported_count} in {len(updated_movie_list['results'])})")
            if tmdb_movie_id['adult']:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"-- Movie {tmdb_id} is marked as adult content. --"))
                self.stdout.write(self.style.WARNING(f"Skipping...."))
                self.stdout.write("---------")
                continue

            try:
                new_movie, is_created = save_or_update_movie(tmdb_id)
                # check if the movie worked
                if new_movie and is_created:
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f"Imported! Added new movie: **{new_movie}**"))
                    self.stdout.write("---------")
                elif new_movie and not is_created:
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(f"Imported! Updated movie: **{new_movie}** \n"))
                    self.stdout.write("---------")
                else:
                    self.stdout.write(self.style.WARNING(f"**failed to register in DB.**"))
                    skipped_count += 1
                    self.stdout.write("---------")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error importing {new_movie['title']}: {e}"))
                logger.error(f"Error importing {tmdb_id}: {e}")
                continue

        time.sleep(3) # give some time between fetching a new page list of movies. // to correct
        self.stdout.write(self.style.SUCCESS(f"Imported list of updated movies successfully\n"))
        self.stdout.write(f"{imported_count-1} movie imported.")
        logger.info(f"SUMMARY: Movies (update) -- {created} Created. -- {updated} Updated. -- {skipped_count} Skipped/Failed.")
        self.stdout.write(f"SUMMARY: Movies (update) -- {created} Created. -- {updated} Updated. -- {skipped_count} Skipped/Failed.")
        self.stdout.write(f"-----") # debug print

            # except Exception as e:
            #     # messages.error(request, "the page seem to experience some issue, please try again later")
            #     self.stdout.write(self.style.WARNING(f" error :{e}"))
