# import requests
import logging
import datetime
import time
import random
import os

from django.core.management.base import BaseCommand

from serie.models import Serie
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


class Command(BaseCommand):
    help = 'Import series data from TMDB'

    def handle(self, *args, **kwargs):
        self.import_list_series()

    def import_list_series(self):
        """
        Bulk import strategy:
        1. Fetch a list of series varying upon on the selected endpoint
        2.  loop through each serie to query their data 
        3. Check if the series already exists otherwise saves it in the database.
        """
        # instantiate variable to keep track of import and retry policy
        MAX_RETRIES = 3
        attempt = 0
        imported_count = 0  # Tracks how many series were imported
        skipped_count = 0  # Tracks how many series already existed
        created = 0

        endpoint = ("popular", "top_rated", "on_the_air", "discover", "airing_today")
        selected_endpoint = random.choice(endpoint)
        # Define the range of pages to fetch
        # set on max available pages with the corresponding query of TMDB Api.
        if  selected_endpoint == "on_the_air":
            max_pages = 50
        elif  selected_endpoint == "top_rated":
            max_pages = 100
        else:
            max_pages = 500

        # ------TRIAL/ once every 10 days ensure it takes from page 1&2 to get latest content ------
        today = datetime.date.today()
        # if today.day == 1 or today.day == 10 or today.day == 29:
        if today.day in [1, 10, 20, 25]:
            page = 1
        else:
            page = random.randint(1, max_pages) # Randomly select a page

        # retry feature if the url page brings error.
        while attempt < MAX_RETRIES:
            try:
                self.stdout.write(f"Fetching series from '{selected_endpoint}' list, With page n: {page}") # debug print
                list_series = get_series_list(page, selected_endpoint)

                if not list_series:
                    self.stdout.write(self.style.ERROR(f"No serie page found... Check the url for possible error (or outside range)."))
                    attempt += 1
                    self.stdout.write(f"Retrying... Attempt {attempt}/{MAX_RETRIES} in {attempt*3}seconds")
                    time.sleep(attempt*3)  # wait for 1 second before retrying
                    continue

                break # if list_series exist then break out of the Loop

            except Exception as e:
                self.stdout.write(f"(Exception) Error getting updated series: {e}")
                attempt += 1
                self.stdout.write(f"Retrying... Attempt {attempt}/{MAX_RETRIES} in {attempt*3}seconds")
                time.sleep(attempt*3)  # wait for 1 second before retrying

        # If all retries failed, exit early
        if attempt == MAX_RETRIES:
            self.stdout.write(self.style.ERROR("Max retries reached. Could not fetch updated series. -- Task ending."))
            return  

        # give some random to index to look through for the series list.
        r_index = random.randint(0, len(list_series['results']) - 5) 

        self.stdout.write(f"Processing the list of series to get the individual serie's data.")
        for new_serie in list_series['results'][r_index:r_index+5]:
            imported_count += 1
            
            #------- temporary break here after 5 series to check feature is going well with adding episode--------
            if imported_count > 5:
                self.stdout.write(f"Breaking after 5 series for testing purpose.\n")
                break

            # tmdb_title = new_serie['title']
            self.stdout.write(f"-----") # debug print
            self.stdout.write(f"Importing *Serie {imported_count} of {len(list_series['results'])}* (id: {new_serie['id']})") # debug print
            # serie_id = new_serie['id']

            # Check if serie exists
            if not Serie.objects.filter(tmdb_id=new_serie['id']).exists():
                try:
                    save_or_update_series(new_serie['id'])
                    created += 1
                    self.stdout.write(f"Imported serie: {new_serie['name']}\n")  # not sure it is imported if already exist
                    self.stdout.write("-----------")  # not sure it is imported if already exist
                except Exception as e:
                    self.stdout.write(f"Error importing {new_serie['id']}- {new_serie['name']}: {e}")
                    skipped_count += 1
                    continue
            else:
                self.stdout.write(self.style.WARNING(f"{new_serie['name']} already exists in DB.\n"))
                self.stdout.write(f"Skipping....")
                skipped_count += 1
                print("-----------")

            # give some time between fetching new series.
            time.sleep(3) 

        self.stdout.write(self.style.SUCCESS(f"Imported list of **{selected_endpoint}** series done!\n"))
        logger.info(f"SUMMARY: Series (import) -- {created} Created. -- 0 Updated. -- {skipped_count} Skipped/Failed.")
        self.stdout.write(f"SUMMARY: Series (import) -- {created} Created. -- 0 Updated. -- {skipped_count} Skipped/Failed.")
        self.stdout.write(f"-----") # debug print




# ------ To import a single serie ---- Not in use.
# def import_serie(request, tmdb_id):
#     '''Import a movie in making a request to TMDB api and store it in the database'''
#     print(f"request importing a new serie")
#     try:
#         if request.method == 'GET' and request.user.is_superuser:

#             try:
#                 # check if the movie is already in our database
#                 exisiting_serie = Serie.objects.get(tmdb_id=tmdb_id)
#                 print(f"Serie already exists: serie {exisiting_serie.id}: {exisiting_serie.title}")
#                 return JsonResponse({
#                     'status': 'already exists in DB', 
#                     'tmdb_id': exisiting_serie.tmdb_id, 
#                     'serie_id': exisiting_serie.id,
#                     'title': exisiting_serie.title
#                 }, status=200)
            
#             # if the movie is not then we try to fetch it.
#             except Serie.DoesNotExist:

#                 result = add_series_from_tmdb(tmdb_id)

#                 # Determine appropriate HTTP status code
#                 status_code = {
#                     'added': 201,
#                     'exists': 200,
#                     'error': 404
#                 }.get(result['status'], 400)

#                 return JsonResponse(result, status=status_code)
#         else:
#             print(f"Unauthorized access to 'import_serie' page.")
#             messages.error(request, "You are not authorized to import series")
#             return redirect('main:home')

#     except Exception as e:
#         messages.error(request, "the page seem to experience some issue, please try again later")
#         print(f" error :{e}")
#         return JsonResponse({
#             'status': 'error',
#             'message': 'An unexpected error occurred'
#         }, status=500)
