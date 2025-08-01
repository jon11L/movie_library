# import requests
import logging
import time
import datetime
import random
import os

from django.core.management.base import BaseCommand

from import_data.api_clients.TMDB.fetch_series import get_series_list
from import_data.services.create_series import save_or_update_series

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
# logger.info("Logging initialized successfully!")  # Test log entry


class Command(BaseCommand):
    help = 'Import updated series from TMDB.'

    def handle(self, *args, **kwargs):
        self.get_updated_series()

    def get_updated_series(self):
        """
        Bulk import strategy:
        1. Fetch a page of updated series
        2. Loop through each serie to query their data 
        3. Update the series 
        """
        # end_date=2025-03-26&start_date=2025-03-27
        # example url call: https://api.themoviedb.org/3/tv/changes?page=1&start_date=2025-03-18&end_date=2025-03-19
        endpoint = "changes"

        MAX_RETRIES = 3
        attempt = 0
        imported_count = 0  # Tracks how many series were imported and updated
        created = 0  # Tracks how many movies were created
        updated = 0  # .................... updated
        skipped_count = 0

        while attempt < MAX_RETRIES:
            page = str(random.randint(1, 20))  # Randomly select a page
            
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
                self.stdout.write(f"Fetching series from '{endpoint}' endpoint, With page: {page}\n") # debug print
                updated_serie_list = get_series_list(page_date, endpoint)
                self.stdout.write(f"-- len list:{len(updated_serie_list['results'])}") # debug print

                if not updated_serie_list or "results" not in updated_serie_list:
                    self.stdout.write(self.style.ERROR(f"The query could not fetch a list of updated series, check the url.\n"))  # debug print
                    attempt += 1
                    self.stdout.write(f"Retrying... Attempt {attempt}/{MAX_RETRIES} in {attempt*3}seconds")
                    time.sleep(attempt*3)  # wait some seconds before retrying
                    continue

                break  # if list is correct break out of the loop and fetch series individually

            except Exception as e:
                self.stdout.write(f"(Exception) Error getting updated series: {e}")
                attempt += 1
                self.stdout.write(f"Retrying... Attempt {attempt}/{MAX_RETRIES} in {attempt*3}seconds")
                time.sleep(attempt*3)  # wait for 1 second before retrying

        # If all retries failed, exit early
        if attempt == MAX_RETRIES:
            self.stdout.write(self.style.ERROR("Max retries reached. Could not fetch updated series. -- Task ending.\n"))
            return  

        # When Url return correct response and data, pass each serie in results to create new serie instance
        r_index = random.randint(0, len(updated_serie_list['results']) - 4) # give some random to index to look through for the series. 

        for tmdb_serie_id in updated_serie_list['results'][r_index:r_index+4]:
            imported_count += 1

            if imported_count > 4:
                self.stdout.write(f"Breaking after 4 series for testing purpose.\n")
                break

            self.stdout.write(f"-------- Processing serie {imported_count} of {len(updated_serie_list)}... ---------")
            tmdb_id = tmdb_serie_id['id']
            self.stdout.write(f" Serie id: {tmdb_id}") # debug print
            time.sleep(3) # give some time between fetching a new page list of movies.

            try:
                new_serie, is_created = save_or_update_series(tmdb_id)

                if new_serie and is_created:
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f"Imported! Created new serie: **{new_serie}**"))
                    self.stdout.write("---------")
                elif new_serie and not is_created:
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(f"Imported! Updated serie: **{new_serie}**"))
                    self.stdout.write("---------")
                else:
                    self.stdout.write(self.style.WARNING(f"**failed to register in DB.**"))
                    skipped_count += 1
                    self.stdout.write("---------")

            except Exception as e:
                skipped_count += 1
                self.stdout.write(self.style.ERROR(f"Error importing serie {tmdb_serie_id}: {e}"))
                logger.error(f"Error importing serie {tmdb_serie_id}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Imported list of  updated series successful!\n"))
        self.stdout.write(f"{imported_count} serie imported.")
        logger.info(f"SUMMARY: Series (update) -- {created} Created. -- {updated} Updated. -- {skipped_count} Skipped/Failed.") # for the logs
        self.stdout.write(f"SUMMARY: Series (update) -- {created} Created. -- {updated} Updated. -- {skipped_count} Skipped/Failed.")
        self.stdout.write(f"-----") # debug print

            # except Exception as e:
            #     # messages.error(request, "the page seem to experience some issue, please try again later")
            #     self.stdout.write(self.style.WARNING(f" error :{e}"))
            #     attempt += 1
            #     print(f"Retrying... Attempt {attempt}/{MAX_RETRIES} in {attempt*3}seconds")
            #     time.sleep(attempt*3)  # wait for 1 second before retrying
