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
logger = logging.getLogger(__name__)

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure the directory exists

LOG_FILE = os.path.join(LOG_DIR, "tmdb_import.log")


logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",  # Append to existing log file
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


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

        # calculate date up to two weeks before now for the list of updated movies
        # today = datetime.datetime.now().strftime("%Y-%m-%d")
        # two_weeks_ago = (datetime.datetime.now() - datetime.timedelta(days=14)).strftime("%Y-%m-%d")

        # self.stdout.write(f"Fetching movies from '{endpoint}' endpoint, from {two_weeks_ago} to {today}\n") # debug print

        created = 0  # Tracks how many movies were created
        updated = 0  # .................... updated
        imported_count = 0  # Tracks how many movies passed through
        skipped_count = 0  # Tracks how many movies passed through
        page = random.randint(1, 40)

        try:
            # for page in pages_to_fetch:
            self.stdout.write(f"Fetching movies from '{endpoint}' endpoint, With page: {page}\n") # debug print
            updated_movie_list = get_movie_list(page, endpoint)

            if not updated_movie_list:
                self.stdout.write(self.style.ERROR(f" The query could not fetch a list of updated movies, check the url.\nstatus=404"))  # debug print

            self.stdout.write("Looping through the list of updated movies and pass the Ids to fetch the datas.\n")
            for tmdb_movie_id in updated_movie_list['results']: # add a random index to go through
                tmdb_id = tmdb_movie_id['id']
                adult = tmdb_movie_id['adult']
                print(f"movie adult: '{adult}'.")
                if adult:
                    self.stdout.write(self.style.WARNING(f"Movie {tmdb_id} is marked as adult content. Skipping..."))
                    skipped_count += 1
                    continue

                imported_count += 1
                print(f"passing movie {imported_count} in {len(updated_movie_list['results'])}")
                try:
                    if imported_count >= 30:
                        break # stop the iteration to fetch for updated movies.

                    new_movie, is_created = save_or_update_movie(tmdb_id)


                    # check if the movie worked
                    if new_movie and is_created:
                        created += 1
                        self.stdout.write(self.style.SUCCESS(f"Imported! Created new movie: **{new_movie}**"))
                        print("---------")
                    elif new_movie and not is_created:
                        updated += 1
                        self.stdout.write(self.style.SUCCESS(f"Imported! Updated movie: **{new_movie}** \n"))
                        print("---------")
                    else:
                        self.stdout.write(self.style.WARNING(f"**failed to register in DB.**"))
                        skipped_count += 1
                        print("---------")

                    # self.stdout.write(f" Movie {imported_count} in {len(updated_movie_list['results'])}") # debug print
                    # save_or_update_movie(tmdb_id)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing {new_movie['title']}: {e}"))
                    continue

                    # Check if movie exists
                    # if not Movie.objects.filter(tmdb_id=tmdb_id).exists():
                    #     try:
                    #         add_movies_from_tmdb(tmdb_id)
                    #         self.stdout.write(self.style.SUCCESS(f"Imported movie: **{tmdb_movie['title']}** \n"))  # not sure it is imported if already exist
                    #     except Exception as e:
                    #         self.stdout.write(self.style.ERROR(f"Error importing {tmdb_movie['title']}: {e}"))
                    # else:
                    #     self.stdout.write(self.style.WARNING(f"{tmdb_movie['title']} already exists in DB."))

            time.sleep(2) # give some time between fetching a new page list of movies.
            self.stdout.write(self.style.SUCCESS(f"Imported list of updated movies successfully\n"))
            logger.info(f"{imported_count} movie imported.")
            logger.info(f"SUMMARY: {updated} updated movies -- {created} created movies. -- {skipped_count} skipped/failed movies")

        except Exception as e:
            # messages.error(request, "the page seem to experience some issue, please try again later")
            self.stdout.write(self.style.WARNING(f" error :{e}"))
