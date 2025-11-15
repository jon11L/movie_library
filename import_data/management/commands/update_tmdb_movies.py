import requests
import logging
import time
import datetime
import random
import os

from django.core.management.base import BaseCommand

from movie.models import Movie

from import_data.api_clients.TMDB.fetch_data import get_api_data
from import_data.services.create_movies import save_or_update_movie
from import_data.tools.media_update_check import check_update_since


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
        start_time = time.time()

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
            end_date = (today - datetime.timedelta(days=random.randint(2, 14)))
            start_date = end_date - datetime.timedelta(days=1)

            end_date = end_date.strftime("%Y-%m-%d")
            start_date = start_date.strftime("%Y-%m-%d")

            # adding date parameters for wider choices of updated movies
            select_date = f"end_date={end_date}&start_date={start_date}" 
            self.stdout.write(select_date)
            page_date = page + select_date # concatenate the date to the page until finding a better solution.
            self.stdout.write(f"-- page_date: {page_date}")
            try:
                # for page in pages_to_fetch:
                self.stdout.write(f"Fetching movies from '{endpoint}' endpoint, With page: {page}\n") 

                updated_movie_list = get_api_data(
                    page=page,
                    endpoint=endpoint,
                    t_type = 'movie_list',
                    # update = True,
                    select_date=select_date
                    )

                if not updated_movie_list  or "results" not in updated_movie_list:
                    self.stdout.write(f"Error: -- The query could not fetch a list of updated movies, check the url.\n")
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

        if updated_movie_list != None:
            self.stdout.write("Looping through the list of updated movies and pass the Ids to fetch the datas.\n")
            for tmdb_movie in updated_movie_list['results']: # add a random index to go through
                # time.sleep(1) 
                imported_count += 1
                if imported_count > 50:
                    break # stop the iteration to fetch for updated movies.

                tmdb_id = tmdb_movie['id']
                self.stdout.write(f"Processing movie Nr.{imported_count}")
                
                if tmdb_movie['adult'] == True or tmdb_movie['adult'] == None:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"--- Movie-id: '{tmdb_id}' is marked as adult content {tmdb_movie['adult']}. ---\n"
                            f"Skipping....\n"
                            f"\n" + "=" * 50 + "\n\n"
                        )
                    )
                    continue

                try:
                    # If Movie already existing.
                    if Movie.objects.filter(tmdb_id=tmdb_id).exists():
                        exist_movie = Movie.objects.get(tmdb_id=tmdb_id)

                        need_update, desired_updt_days = check_update_since(exist_movie, "Movie")

                        if need_update == False:
                            self.stdout.write(self.style.WARNING(
                                f"{tmdb_id} was already updated less {desired_updt_days} days ago.\n"
                                "Skipping this movie....\n"
                                f"\n" + "=" * 50 + "\n\n"
                                ))
                            skipped_count += 1
                            continue

                        time.sleep(0.5) 
                        new_movie, is_created = save_or_update_movie(tmdb_id)
                    
                    else:
                        # Movie does not exist, creating it
                        time.sleep(0.5) 
                        new_movie, is_created = save_or_update_movie(tmdb_id)

                    # check if the movie wwas created
                    if new_movie and is_created:
                        created += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Imported! Added new movie: **{new_movie}**"
                                f"\n" + "=" * 50 + "\n\n"
                            )
                        )

                    elif new_movie and not is_created:
                        updated += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Imported! Updated movie: **{new_movie}** \n"
                                f"\n" + "=" * 50 + "\n\n"
                            )
                        )
                    elif not new_movie:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"**Cancel to save in DB. Mo movie or no sufficient data**"
                                f"\n" + "=" * 50 + "\n\n"
                            )
                        )

                    else:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"**failed to register in DB.**"
                                f"\n" + "=" * 50 + "\n\n"
                            )
                        )

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing movie with id:'{tmdb_id}'"))
                    logger.error(f"Error importing {tmdb_id}: {e}")
                    continue

        end_time = time.time()
        elapsed_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f"time: {elapsed_time:.2f} seconds."))

        # time.sleep(3) # give some time between fetching a new page list of movies. // to correct
        logger.info(
            f"SUMMARY: Movies (update) "
            f"-- {created} Created -- {updated} Updated"
            f" -- {skipped_count} Skipped/Failed"
            f" -- runtime: {elapsed_time:.2f} seconds"
            
            )
        self.stdout.write(
            self.style.SUCCESS(f"Imported list of updated movies successfully\n")
        )
        self.stdout.write(
            f"{imported_count-1} movie imported.\n"
            f"SUMMARY: Movies (update) -- {created} Created. -- {updated} Updated. -- {skipped_count} Skipped/Failed.\n"
            f"\n" + "=" * 50 + "\n\n"
            )